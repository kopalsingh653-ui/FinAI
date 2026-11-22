# FinAI — AI-Powered Financial Inclusion and Responsible Lending System

<p align="center">
  <strong>An intelligent credit risk assessment and responsible lending platform powered by Machine Learning.</strong>
</p>

<p align="center">
  Python · FastAPI · React · XGBoost · SQLAlchemy · SQLite
</p>

---

## Overview

**FinAI** is an AI-powered financial intelligence platform designed to support responsible lending and improve financial inclusion through data-driven credit risk assessment.

The system combines machine learning, borrower financial information, affordability analysis and credit scoring to evaluate loan applications and provide structured risk insights.

FinAI provides an integrated platform for borrower management, loan application processing, credit risk prediction, expected loss estimation and historical assessment monitoring.

The project aims to demonstrate how machine learning can support more informed and transparent lending decisions.

## Key Features

### 1. Machine Learning-Based Credit Risk Prediction
- XGBoost-based credit default prediction.
- Probability of default estimation.
- Risk classification based on a selected decision threshold.
- Feature engineering and preprocessing pipeline.
- Model evaluation and performance analysis.

### 2. Credit Scoring System
- Internal FinAI credit score.
- Credit score bands.
- Repayment history assessment.
- Credit utilisation analysis.
- Payment behaviour assessment.
- Affordability-based scoring.

### 3. Financial Affordability Analysis
- Monthly income and expense assessment.
- Existing EMI evaluation.
- Debt-to-income ratio calculation.
- Proposed EMI affordability analysis.
- Disposable income assessment.

### 4. Expected Credit Loss Estimation
- Probability of Default (PD).
- Loss Given Default (LGD).
- Exposure at Default (EAD).
- Expected loss estimation using:

  **Expected Loss = PD × LGD × EAD**

### 5. Borrower Management
- Borrower registration and records.
- Borrower financial profiles.
- Individual borrower assessment history.
- Historical credit score information.
- Loan application tracking.

### 6. Analytics Dashboard
- Total borrowers and applications.
- Eligible and rejected application summaries.
- Loan portfolio overview.
- Risk distribution.
- Default probability analysis.
- Expected loss insights.
- Recent application activity.

### 7. Historical Assessment Reports
- Application-specific assessment reports.
- Saved prediction history.
- Historical credit scores.
- Risk classification and expected loss records.
- CSV report export.
- Print-friendly reports.

### 8. Responsible Lending and Fairness
- Gender excluded from predictive model inputs.
- Demographic information retained separately for fairness auditing.
- Affordability considerations incorporated into eligibility assessment.
- Risk-based decision support rather than relying exclusively on a model prediction.

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Machine Learning | XGBoost, Scikit-learn |
| Data Processing | Pandas, NumPy |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Frontend | React.js |
| Frontend Tooling | Vite |
| HTTP Communication | Axios |
| Data Visualisation | Recharts |
| Icons | Lucide React |
| Model Storage | Joblib |
| Development Environment | Ubuntu, VS Code |

---

## System Architecture

```text
                FINAI PLATFORM
                      |
          +-----------+-----------+
          |                       |
     React Frontend          FastAPI Backend
          |                       |
          |                 API Routers
          |                       |
          |              +--------+--------+
          |              |        |        |
          |          Prediction Affordability
          |              |        |        |
          |          Credit Score Eligibility
          |              |                 |
          |              +--------+--------+
          |                       |
          |                ML Prediction
          |                       |
          |                  XGBoost
          |                       |
          |                Feature Pipeline
          |                       |
          |                Risk Assessment
          |                       |
          +---------------+-------+
                          |
                   SQLAlchemy ORM
                          |
                       SQLite
                          |
             Borrower and Application Data
             Prediction and Score History
```

---

## Machine Learning Approach

FinAI uses an XGBoost classification model to estimate the probability of credit default.

### Dataset

The project uses the **UCI Default of Credit Card Clients dataset**.

The dataset contains approximately 30,000 records and includes information related to:

- Credit limits.
- Education and marital status.
- Age.
- Repayment status.
- Historical bill amounts.
- Previous payment amounts.
- Default payment outcomes.

### Feature Engineering

The modelling pipeline includes engineered features derived from historical financial behaviour.

The current model uses:

- 22 raw predictive features.
- 17 engineered features.
- 39 total model input features.

Gender is excluded from predictive inputs and retained separately for fairness analysis.

### Model Configuration

| Parameter | Configuration |
|---|---|
| Algorithm | XGBoost Classifier |
| Random State | 42 |
| Model Selection | ROC-AUC |
| Selected Threshold | Approximately 0.29 |
| Model Input Features | 39 |

The classification threshold is selected for the project's evaluation objective rather than automatically assuming 0.50 is optimal.

---

## Eligibility Assessment

FinAI combines predictive risk estimates with affordability and internal credit scoring criteria.

The current eligibility configuration includes:

| Criterion | Configuration |
|---|---:|
| Minimum FinAI Credit Score | 650 |
| Maximum Default Probability | 0.25 |
| Maximum Debt-to-Income Ratio | 0.40 |
| Maximum Proposed EMI Ratio | 0.30 |
| Minimum Disposable Income | ₹5,000 |

These are configurable project-level decision rules and should not be interpreted as universal lending standards.

---

## Project Structure

```text
FinAI/
│
├── app/
│   ├── main.py
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   ├── routers/
│   │   ├── prediction.py
│   │   ├── affordability.py
│   │   ├── expected_loss.py
│   │   ├── credit_score.py
│   │   ├── eligibility.py
│   │   ├── borrowers.py
│   │   └── applications.py
│   │
│   └── services/
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── eda.py
│   ├── credit_risk.py
│   ├── evaluation.py
│   ├── expected_loss.py
│   ├── affordability.py
│   ├── explainability.py
│   └── fairness.py
│
├── models/
│   ├── best_credit_model.joblib
│   ├── model_metadata.json
│   └── selected_threshold.json
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnalyticsDashboard.jsx
│   │   │   ├── AnalyticsDashboard.css
│   │   │   ├── BorrowerProfile.jsx
│   │   │   └── BorrowerProfile.css
│   │   │
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── CreditAnalysis.jsx
│   │   ├── CreditAnalysis.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
├── README.md
└── .gitignore
```

*Note: This is a representative project structure. Adjust it if your local folder names differ.*

---

## Installation and Setup

### Prerequisites

- Python 3.10 or newer.
- Node.js and npm.
- Git.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FinAI
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Install Frontend Dependencies

Open another terminal:

```bash
cd FinAI/frontend
npm install
```

### 6. Start the React Frontend

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Make sure the backend is running before using the frontend.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/eligibility` | Assess loan eligibility |
| GET | `/api/borrowers` | Retrieve borrowers |
| GET | `/api/borrowers/{id}` | Retrieve borrower profile |
| GET | `/api/borrowers/{id}/applications` | Retrieve borrower applications |
| GET | `/api/borrowers/{id}/credit-profile` | Retrieve borrower credit history |
| GET | `/api/applications` | Retrieve applications |
| GET | `/api/applications/{id}` | Retrieve application details |
| GET | `/api/applications/{id}/history` | Retrieve historical prediction records |

Additional prediction, affordability, credit scoring and expected loss endpoints are available through the FastAPI documentation.

---

## Important Model and Financial Limitations

FinAI is an academic and portfolio project intended to demonstrate machine learning-based credit risk assessment.

- The internal FinAI score is not an official CIBIL or credit bureau score.
- The model's probability estimates are not necessarily calibrated probabilities.
- Expected loss uses an illustrative LGD assumption of 45% unless configured otherwise.
- The dataset is based on historical credit card default information and may not represent every lending population.
- Income and expenses are separately supplied borrower information, not features contained in the original UCI dataset.
- Model predictions should not independently determine real-world lending decisions.
- Fairness analysis does not, by itself, establish that a model is free from bias.

---

## Future Improvements

- SHAP-based individual prediction explanations.
- Advanced feature importance visualisation.
- Expanded fairness and demographic performance reporting.
- Automated model monitoring and drift detection.
- Improved model calibration.
- Role-based access control.
- Cloud deployment and production database integration.
- Automated testing and CI/CD pipelines.

---

## Project Objective

FinAI demonstrates the integration of machine learning, financial data analysis, backend engineering and frontend development to build an intelligent lending decision-support platform.

The project explores how predictive analytics and affordability-based assessment can contribute to more responsible and data-driven lending workflows.

---

## Author

Developed By; Kopal Singh, Shaizah Labique, Tushar Harsh.

Developed as a B.Tech Computer Science and Engineering capstone project.

**FinAI — AI-Powered Financial Inclusion and Responsible Lending System**
