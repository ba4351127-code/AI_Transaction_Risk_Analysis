import io
from datetime import datetime, timezone
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_risk_report(transactions: List[Dict[str, Any]], stats: Dict[str, Any]) -> bytes:
    """Generates institutional-style PDF transaction risk report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#3B82F6"),
        spaceAfter=15
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#172554"),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#334155")
    )
    bold_style = ParagraphStyle(
        "DocBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title & Header
    story.append(Paragraph("TransactionGuard AI — Risk Intelligence Audit", title_style))
    story.append(Paragraph("OFFICIAL AUDIT REPORT | Generated on " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=15))

    # Executive Summary Card
    story.append(Paragraph("1. Executive Summary & Fleet Metrics", section_title))
    summary_data = [
        [
            Paragraph("<b>Total Transactions Audited</b>", body_style),
            Paragraph(str(stats.get("total", len(transactions))), bold_style),
            Paragraph("<b>Average Risk Score</b>", body_style),
            Paragraph(f"{stats.get('avg_score', 0.0):.1f} / 100", bold_style)
        ],
        [
            Paragraph("<b>Low Risk (Approved)</b>", body_style),
            Paragraph(str(stats.get("low_count", 0)), bold_style),
            Paragraph("<b>High / Critical Risk (Blocked)</b>", body_style),
            Paragraph(str(stats.get("high_count", 0)), bold_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[150, 100, 150, 100])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Detailed Transactions Table
    story.append(Paragraph("2. Evaluated Transactions & Anomaly Diagnostics", section_title))
    table_headers = [
        Paragraph("<b>Ref #</b>", bold_style),
        Paragraph("<b>Amount</b>", bold_style),
        Paragraph("<b>Method</b>", bold_style),
        Paragraph("<b>Location</b>", bold_style),
        Paragraph("<b>Score</b>", bold_style),
        Paragraph("<b>Category</b>", bold_style),
        Paragraph("<b>Action</b>", bold_style)
    ]
    
    rows = [table_headers]
    for tx in transactions[:40]:  # Limit page overflow
        score = tx.get("risk_score", 0.0)
        cat = tx.get("risk_category", "LOW")
        action = tx.get("recommended_action", "APPROVE")
        
        # Color code category
        cat_color = "#10B981" if cat == "LOW" else "#F59E0B" if cat == "MEDIUM" else "#EF4444"
        cat_p = Paragraph(f"<font color='{cat_color}'><b>{cat}</b></font>", body_style)

        rows.append([
            Paragraph(str(tx.get("transaction_ref", "N/A")), body_style),
            Paragraph(f"${tx.get('amount', 0.0):,.2f}", body_style),
            Paragraph(str(tx.get("payment_method", "N/A")), body_style),
            Paragraph(str(tx.get("location_city", "N/A")), body_style),
            Paragraph(f"{score:.1f}", body_style),
            cat_p,
            Paragraph(f"<b>{action}</b>", body_style)
        ])

    tx_table = Table(rows, colWidths=[85, 75, 75, 80, 50, 75, 75])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tx_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
