import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.database.session import get_db, async_session_factory
from backend.app.database.models.batch_job import BatchJob
from backend.app.database.models.transaction import Transaction, RiskAssessment
from backend.app.ml.predictor import predict_transaction_risk
from backend.app.engine.scorer import compute_composite_risk
from backend.app.utils.geo import resolve_city_coordinates

router = APIRouter()


async def process_bulk_csv_task(job_id: str, csv_content: str):
    """Asynchronous background worker to parse and evaluate bulk transaction CSVs."""
    async with async_session_factory() as db:
        # Load job
        job_q = await db.execute(select(BatchJob).where(BatchJob.id == job_id))
        job = job_q.scalar_one_or_none()
        if not job:
            return

        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        job.total_records = len(rows)
        job.status = "PROCESSING"
        await db.commit()

        total_score = 0.0
        low_c = 0
        med_c = 0
        high_c = 0
        crit_c = 0

        for r in rows:
            try:
                amt = float(r.get("amount", 100.0))
                method = r.get("payment_method", "credit_card")
                city = r.get("location_city", "Mumbai")
                device_str = r.get("is_device_familiar", "1").lower()
                is_device_familiar = device_str in ("1", "true", "yes")
                cat = r.get("merchant_category", "general")
                tx_ref = r.get("transaction_ref") or f"TX-{uuid.uuid4().hex[:8].upper()}"
                
                # ML prediction
                xgb_p, iforest_s, top_shap = predict_transaction_risk(
                    amount=amt,
                    payment_method=method,
                    merchant_category=cat,
                    is_device_familiar=is_device_familiar
                )

                # Composite score
                assessment = compute_composite_risk(
                    amount=amt,
                    payment_method=method,
                    location_city=city,
                    is_device_familiar=is_device_familiar,
                    curr_timestamp=datetime.now(timezone.utc),
                    xgb_fraud_prob=xgb_p,
                    iforest_outlier_score=iforest_s,
                    raw_shap_list=top_shap,
                    transaction_ref=tx_ref
                )

                score = assessment.overall_risk_score
                total_score += score

                if assessment.risk_category == "LOW":
                    low_c += 1
                elif assessment.risk_category == "MEDIUM":
                    med_c += 1
                elif assessment.risk_category == "HIGH":
                    high_c += 1
                else:
                    crit_c += 1

                # Persist transaction
                lat, lon = resolve_city_coordinates(city)
                tx = Transaction(
                    transaction_ref=tx_ref,
                    batch_job_id=job.id,
                    amount=amt,
                    payment_method=method,
                    location_city=city,
                    latitude=lat,
                    longitude=lon,
                    is_device_familiar=is_device_familiar,
                    transaction_timestamp=datetime.now(timezone.utc)
                )
                db.add(tx)
                await db.flush()

                risk = RiskAssessment(
                    transaction_id=tx.id,
                    overall_risk_score=score,
                    risk_category=assessment.risk_category,
                    recommended_action=assessment.recommended_action,
                    xgb_fraud_probability=xgb_p,
                    iforest_anomaly_score=iforest_s,
                    simple_explanation="; ".join(assessment.everyday_user.simple_reasons),
                    technical_summary=assessment.risk_analyst.technical_summary,
                    confidence_score=95.0
                )
                db.add(risk)
                job.processed_records += 1

            except Exception as e:
                continue

        # Complete job
        job.status = "COMPLETED"
        job.avg_risk_score = round(total_score / max(len(rows), 1), 2)
        job.flagged_low_count = low_c
        job.flagged_medium_count = med_c
        job.flagged_high_count = high_c
        job.flagged_critical_count = crit_c
        job.completed_at = datetime.utcnow()

        await db.commit()


@router.post("/upload", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
async def upload_bulk_transactions(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts CSV batch file for non-blocking risk scoring.
    Returns tracking job_id to monitor batch execution.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only standard CSV files (.csv) are supported."
        )

    content_bytes = await file.read()
    content_str = content_bytes.decode("utf-8", errors="ignore")

    job = BatchJob(
        file_name=file.filename,
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch asynchronous background task
    background_tasks.add_task(process_bulk_csv_task, job.id, content_str)

    return {
        "job_id": job.id,
        "file_name": job.file_name,
        "status": job.status,
        "message": "CSV uploaded successfully. Background risk analysis initiated."
    }


@router.get("/jobs/{job_id}", response_model=dict)
async def get_bulk_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Returns real-time processing metrics and flagged distributions for a batch job."""
    job_q = await db.execute(select(BatchJob).where(BatchJob.id == job_id))
    job = job_q.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch job not found.")

    return {
        "job_id": job.id,
        "file_name": job.file_name,
        "status": job.status,
        "total_records": job.total_records,
        "processed_records": job.processed_records,
        "progress_percentage": round((job.processed_records / max(job.total_records, 1)) * 100, 1),
        "avg_risk_score": float(job.avg_risk_score),
        "distribution": {
            "low": job.flagged_low_count,
            "medium": job.flagged_medium_count,
            "high": job.flagged_high_count,
            "critical": job.flagged_critical_count
        },
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    }
