# TransactionGuard AI
## AI-Driven Transaction Risk Analysis

**Tagline**: *Understand Transactions. Detect Risks. Make Safer Decisions.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/Academic-B.Tech%20CSE%20Capstone-informational.svg)](#)

---

### Project Overview
TransactionGuard AI is an industry-grade financial risk intelligence and fraud detection platform. Built as a pre-final-year B.Tech CSE capstone project, it bridges cutting-edge machine learning (supervised XGBoost and unsupervised Isolation Forest) with game-theoretic Explainable AI (SHAP) and a dual-persona interface tailored for both ordinary users and specialized risk analysts.

### Core Architecture
- **Layer 1: Deterministic Rule Engine**: Velocity limits, geo-teleportation checks, blacklists.
- **Layer 2: Supervised ML (XGBoost)**: Calibrated probability estimation on card & digital transactions.
- **Layer 3: Unsupervised Anomaly Detection (Isolation Forest)**: Zero-day and novel outlier detection.
- **Layer 4: Personal Behavioral Profiler**: Rolling 30-day user baseline variance and Z-score deviation.
- **Composite Risk Scorer (0 - 100)**: Calibrated weighted multi-layer risk fusion with hard override safeguards.
- **XAI Pipeline (SHAP TreeExplainer)**: Local feature impact breakdown translated into plain English.

### Project Directory Structure
```
├── backend/            # FastAPI application, database models, ML inference & scoring engine
├── frontend/           # React + Tailwind CSS client with Dual-Persona UX
├── ml_pipeline/        # Model training scripts, synthetic data generation, and serialized artifacts
├── docs/               # Architecture diagrams and specifications
└── tests/              # End-to-end and unit test suites
```
