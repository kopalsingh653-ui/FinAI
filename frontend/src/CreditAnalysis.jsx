import { useState } from "react";
import api from "./api";
import "./CreditAnalysis.css";

import {
  UserRound,
  Wallet,
  CreditCard,
  BrainCircuit,
  FileText,
  Download,
  LoaderCircle,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  TrendingUp,
  IndianRupee,
  RefreshCw
} from "lucide-react";

const repaymentFields = [
  ["PAY_0", "Most recent repayment status"],
  ["PAY_2", "Previous month repayment status"],
  ["PAY_3", "Two months ago repayment status"],
  ["PAY_4", "Three months ago repayment status"],
  ["PAY_5", "Four months ago repayment status"],
  ["PAY_6", "Five months ago repayment status"]
];

const billFields = [
  ["BILL_AMT1", "Most recent bill amount"],
  ["BILL_AMT2", "Previous month bill amount"],
  ["BILL_AMT3", "Two months ago bill amount"],
  ["BILL_AMT4", "Three months ago bill amount"],
  ["BILL_AMT5", "Four months ago bill amount"],
  ["BILL_AMT6", "Five months ago bill amount"]
];

const paymentFields = [
  ["PAY_AMT1", "Most recent payment amount"],
  ["PAY_AMT2", "Previous month payment amount"],
  ["PAY_AMT3", "Two months ago payment amount"],
  ["PAY_AMT4", "Three months ago payment amount"],
  ["PAY_AMT5", "Four months ago payment amount"],
  ["PAY_AMT6", "Five months ago payment amount"]
];

const initialForm = {
  full_name: "",
  email: "",
  LIMIT_BAL: "",
  EDUCATION: "",
  MARRIAGE: "",
  AGE: "",
  monthly_income: "",
  monthly_expenses: "",
  existing_emi: "",
  other_monthly_debt: "",
  requested_loan_amount: "",
  proposed_emi: ""
};

const number = (value) => Number(value || 0);

const currency = (value) => {
  if (value === null || value === undefined || value === "") return "—";

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2
  }).format(Number(value));
};

const percent = (value) => {
  if (value === null || value === undefined || value === "") return "—";

  const numeric = Number(value);

  // Ratios returned by the API are displayed as percentages.
  return `${(numeric * 100).toFixed(2)}%`;
};

const display = (value) => {
  if (value === null || value === undefined || value === "") return "—";
  return value;
};

function FormSection({ icon: Icon, title, description, children }) {
  return (
    <section className="analysis-form-section">
      <div className="analysis-section-heading">
        <div className="analysis-section-icon">
          <Icon size={19} />
        </div>
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
      </div>

      {children}
    </section>
  );
}

function Field({ label, name, value, onChange, type = "number", ...props }) {
  return (
    <label className="analysis-field">
      <span>{label}</span>
      <input
        name={name}
        type={type}
        value={value ?? ""}
        onChange={onChange}
        required
        {...props}
      />
    </label>
  );
}

function SelectField({ label, name, value, onChange, options }) {
  return (
    <label className="analysis-field">
      <span>{label}</span>
      <select
        name={name}
        value={value}
        onChange={onChange}
        required
      >
        <option value="">Select an option</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function FeatureInputs({ fields, values, onChange, min, max }) {
  return (
    <div className="analysis-fields-grid">
      {fields.map(([name, label]) => (
        <Field
          key={name}
          name={name}
          label={label}
          value={values[name] ?? ""}
          onChange={onChange}
          min={min}
          max={max}
          step="any"
        />
      ))}
    </div>
  );
}

function ReportMetric({ label, value, description }) {
  return (
    <div className="report-metric">
      <span>{label}</span>
      <strong>{value}</strong>
      {description && <small>{description}</small>}
    </div>
  );
}

function Report({ report, submittedAt, onReset }) {
  const status = String(report.eligibility_status || "Assessment complete");
  const statusLower = status.toLowerCase();

  const decisionClass = statusLower.includes("not")
    ? "decision-rejected"
    : statusLower.includes("conditional")
      ? "decision-conditional"
      : "decision-approved";

  const recommendations = Array.isArray(report.recommendations)
    ? report.recommendations
    : report.recommendations
      ? [report.recommendations]
      : [];

  return (
    <div className="analysis-report" id="finai-report">
      <div className="report-toolbar no-print">
        <div>
          <span className="report-ready">
            <CheckCircle2 size={15} /> ANALYSIS COMPLETE
          </span>
          <h2>Your FinAI assessment report</h2>
        </div>

        <div className="report-actions">
          <button
            type="button"
            className="analysis-outline-button"
            onClick={onReset}
          >
            <RefreshCw size={15} /> New assessment
          </button>

          <button
            type="button"
            className="analysis-primary-button"
            onClick={() => window.print()}
          >
            <Download size={16} /> Print / Save PDF
          </button>
        </div>
      </div>

      <div className="report-document">
        <div className="report-brand">
          <div className="report-logo">
            <BrainCircuit size={22} />
          </div>
          <div>
            <h2>FinAI<span>.</span></h2>
            <p>RESPONSIBLE LENDING INTELLIGENCE</p>
          </div>
          <div className="report-label">CREDIT ASSESSMENT REPORT</div>
        </div>

        <div className="report-meta">
          <div>
            <span>Borrower reference</span>
            <strong>{display(report.borrower_reference)}</strong>
          </div>
          <div>
            <span>Application reference</span>
            <strong>{display(report.application_reference)}</strong>
          </div>
          <div>
            <span>Generated on</span>
            <strong>{submittedAt}</strong>
          </div>
        </div>

        <div className={`decision-banner ${decisionClass}`}>
          <div className="decision-symbol">
            {statusLower.includes("not")
              ? <AlertTriangle size={24} />
              : <ShieldCheck size={24} />}
          </div>
          <div>
            <span>ELIGIBILITY ASSESSMENT</span>
            <h2>{status}</h2>
            <p>{display(report.eligibility_reason)}</p>
          </div>
        </div>

        <section className="report-section">
          <div className="report-section-title">
            <h3>01. Credit risk assessment</h3>
            <span>MODEL OUTPUT</span>
          </div>

          <div className="report-metrics-grid">
            <ReportMetric
              label="FinAI credit score"
              value={display(report.credit_score)}
              description="Internal project credit score"
            />

            <ReportMetric
              label="Score band"
              value={display(report.score_band)}
              description="Score classification"
            />

            <ReportMetric
              label="Probability of default"
              value={percent(report.default_probability)}
              description="Model-estimated default probability"
            />

            <ReportMetric
              label="Risk category"
              value={display(report.risk_category)}
              description="Predicted risk classification"
            />
          </div>
        </section>

        <section className="report-section">
          <div className="report-section-title">
            <h3>02. Affordability analysis</h3>
            <span>FINANCIAL PROFILE</span>
          </div>

          <div className="report-metrics-grid">
            <ReportMetric
              label="Debt-to-income ratio"
              value={percent(report.debt_to_income_ratio)}
              description="Existing debt relative to income"
            />

            <ReportMetric
              label="Proposed EMI / income"
              value={percent(report.proposed_emi_ratio)}
              description="Proposed EMI as a share of income"
            />

            <ReportMetric
              label="Disposable income"
              value={currency(report.disposable_income)}
              description="After the assessed monthly obligations"
            />

            <ReportMetric
              label="Expected loss"
              value={currency(report.expected_loss)}
              description="Illustrative PD × LGD × EAD estimate"
            />
          </div>
        </section>

        <section className="report-section">
          <div className="report-section-title">
            <h3>03. Eligibility reasoning</h3>
            <span>DECISION SUMMARY</span>
          </div>

          <div className="report-explanation">
            <div className="explanation-icon">
              <TrendingUp size={19} />
            </div>
            <div>
              <h4>Assessment outcome</h4>
              <p>
                {display(report.eligibility_reason)}
              </p>
            </div>
          </div>
        </section>

        <section className="report-section">
          <div className="report-section-title">
            <h3>04. Recommendations</h3>
            <span>NEXT STEPS</span>
          </div>

          {recommendations.length ? (
            <ul className="recommendation-list">
              {recommendations.map((item, index) => (
                <li key={index}>
                  <CheckCircle2 size={17} />
                  <span>
                    {typeof item === "string"
                      ? item
                      : item.message || item.recommendation || JSON.stringify(item)}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="report-muted">
              No additional recommendations were returned by the assessment service.
            </p>
          )}
        </section>

        <section className="report-section report-identifiers">
          <div>
            <span>Borrower ID</span>
            <strong>{display(report.borrower_id)}</strong>
          </div>
          <div>
            <span>Application ID</span>
            <strong>{display(report.application_id)}</strong>
          </div>
        </section>

        <div className="report-disclaimer">
          <AlertTriangle size={18} />
          <div>
            <strong>Important information</strong>
            <p>
              {report.disclaimer ||
                "This report is generated using the FinAI project model and configured eligibility rules. The FinAI score is an internal model output, not an official credit-bureau score. Model predictions and illustrative expected-loss estimates are decision-support information, not a guarantee of repayment or a binding lending decision. Final decisions require appropriate human review and verification of submitted information."}
            </p>
          </div>
        </div>

        <div className="report-footer">
          <span>FinAI · Responsible Lending Intelligence</span>
          <span>End of report</span>
        </div>
      </div>
    </div>
  );
}

export default function CreditAnalysis() {
  const [form, setForm] = useState(initialForm);
  const [creditFeatures, setCreditFeatures] = useState({});
  const [result, setResult] = useState(null);
  const [submittedAt, setSubmittedAt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFormChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  };

  const handleCreditChange = (event) => {
    const { name, value } = event.target;
    setCreditFeatures((previous) => ({
      ...previous,
      [name]: value
    }));
  };

  const resetAssessment = () => {
    setForm(initialForm);
    setCreditFeatures({});
    setResult(null);
    setError("");
    setSubmittedAt("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const requiredFeatures = [
        "LIMIT_BAL",
        "EDUCATION",
        "MARRIAGE",
        "AGE",
        ...repaymentFields.map(([name]) => name),
        ...billFields.map(([name]) => name),
        ...paymentFields.map(([name]) => name)
      ];

      const missing = requiredFeatures.filter(
        (name) =>
          creditFeatures[name] === undefined ||
          creditFeatures[name] === ""
      );

      if (missing.length) {
        throw new Error(
          `Please complete all credit-history fields: ${missing.join(", ")}`
        );
      }

      const payload = {
        borrower: {
          full_name: form.full_name.trim(),
          email: form.email.trim()
        },

        credit_features: Object.fromEntries(
          requiredFeatures.map((name) => [
            name,
            Number(creditFeatures[name])
          ])
        ),

        financial_details: {
          monthly_income: number(form.monthly_income),
          monthly_expenses: number(form.monthly_expenses),
          existing_emi: number(form.existing_emi),
          other_monthly_debt: number(form.other_monthly_debt)
        },

        requested_loan_amount: number(form.requested_loan_amount),
        proposed_emi: number(form.proposed_emi)
      };

      const response = await api.post("/api/eligibility", payload);

      setResult(response.data);
      setSubmittedAt(new Date().toLocaleString("en-IN"));
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        Array.isArray(detail)
          ? detail.map((item) => `${item.loc?.join(".")}: ${item.msg}`).join(" | ")
          : typeof detail === "string"
            ? detail
            : err.message || "Unable to complete the assessment."
      );
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <Report
        report={result}
        submittedAt={submittedAt}
        onReset={resetAssessment}
      />
    );
  }

  return (
    <div className="credit-analysis-page">
      <div className="analysis-page-heading">
        <div>
          <div className="analysis-eyebrow">FINAI INTELLIGENCE ENGINE</div>
          <h2>Credit Analysis</h2>
          <p>
            Submit a borrower's financial and credit-history details
            to generate a comprehensive lending assessment.
          </p>
        </div>

        <div className="analysis-engine-status">
          <span />
          XGBoost assessment engine
        </div>
      </div>

      <div className="analysis-info-banner">
        <BrainCircuit size={21} />
        <div>
          <strong>AI-powered responsible lending assessment</strong>
          <p>
            Your information is processed by the existing FinAI eligibility
            API and its configured credit-risk model.
          </p>
        </div>
      </div>

      {error && (
        <div className="analysis-error">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <FormSection
          icon={UserRound}
          title="Borrower information"
          description="Basic identity information for the assessment record."
        >
          <div className="analysis-fields-grid">
            <Field
              label="Full name"
              name="full_name"
              type="text"
              value={form.full_name}
              onChange={handleFormChange}
              placeholder="Enter borrower's full name"
            />

            <Field
              label="Email address"
              name="email"
              type="email"
              value={form.email}
              onChange={handleFormChange}
              placeholder="borrower@example.com"
            />
          </div>
        </FormSection>

        <FormSection
          icon={Wallet}
          title="Financial information"
          description="Monthly income, expenses and existing financial obligations. Enter amounts in INR."
        >
          <div className="analysis-fields-grid">
            <Field
              label="Monthly income (₹)"
              name="monthly_income"
              value={form.monthly_income}
              onChange={handleFormChange}
              min="0"
              step="0.01"
            />

            <Field
              label="Monthly expenses (₹)"
              name="monthly_expenses"
              value={form.monthly_expenses}
              onChange={handleFormChange}
              min="0"
              step="0.01"
            />

            <Field
              label="Existing EMI (₹)"
              name="existing_emi"
              value={form.existing_emi}
              onChange={handleFormChange}
              min="0"
              step="0.01"
            />

            <Field
              label="Other monthly debt (₹)"
              name="other_monthly_debt"
              value={form.other_monthly_debt}
              onChange={handleFormChange}
              min="0"
              step="0.01"
            />
          </div>
        </FormSection>

        <FormSection
          icon={IndianRupee}
          title="Loan request"
          description="Details of the loan being evaluated."
        >
          <div className="analysis-fields-grid">
            <Field
              label="Requested loan amount (₹)"
              name="requested_loan_amount"
              value={form.requested_loan_amount}
              onChange={handleFormChange}
              min="1"
              step="0.01"
            />

            <Field
              label="Proposed monthly EMI (₹)"
              name="proposed_emi"
              value={form.proposed_emi}
              onChange={handleFormChange}
              min="0"
              step="0.01"
            />
          </div>
        </FormSection>

        <FormSection
          icon={CreditCard}
          title="Credit profile"
          description="The original demographic and credit-limit inputs used by the trained model."
        >
          <div className="analysis-fields-grid">
            <Field
              label="Credit limit (LIMIT_BAL)"
              name="LIMIT_BAL"
              value={creditFeatures.LIMIT_BAL ?? ""}
              onChange={handleCreditChange}
              min="0"
              step="any"
            />

            <SelectField
              label="Education (EDUCATION)"
              name="EDUCATION"
              value={creditFeatures.EDUCATION ?? ""}
              onChange={handleCreditChange}
              options={[
                { value: 1, label: "Graduate school (1)" },
                { value: 2, label: "University (2)" },
                { value: 3, label: "High school (3)" },
                { value: 4, label: "Others (4)" },
                { value: 5, label: "Unknown (5)" },
                { value: 6, label: "Unknown (6)" }
              ]}
            />

            <SelectField
              label="Marital status (MARRIAGE)"
              name="MARRIAGE"
              value={creditFeatures.MARRIAGE ?? ""}
              onChange={handleCreditChange}
              options={[
                { value: 1, label: "Married (1)" },
                { value: 2, label: "Single (2)" },
                { value: 3, label: "Other (3)" }
              ]}
            />

            <Field
              label="Age"
              name="AGE"
              value={creditFeatures.AGE ?? ""}
              onChange={handleCreditChange}
              min="18"
              max="100"
              step="1"
            />
          </div>
        </FormSection>

        <FormSection
          icon={TrendingUp}
          title="Repayment history"
          description="Repayment status for the six historical months in the dataset."
        >
          <div className="analysis-help">
            Repayment status codes: -2, -1 and 0 represent the dataset's
            non-positive delay categories; 1–9 represent increasing months
            of payment delay. Use the original dataset coding.
          </div>

          <div className="analysis-fields-grid">
            {repaymentFields.map(([name, label]) => (
              <Field
                key={name}
                label={`${label} (${name})`}
                name={name}
                value={creditFeatures[name] ?? ""}
                onChange={handleCreditChange}
                min="-2"
                max="9"
                step="1"
              />
            ))}
          </div>
        </FormSection>

        <FormSection
          icon={FileText}
          title="Historical bill amounts"
          description="Monthly bill amounts from the six historical periods."
        >
          <div className="analysis-fields-grid">
            {billFields.map(([name, label]) => (
              <Field
                key={name}
                label={`${label} (${name})`}
                name={name}
                value={creditFeatures[name] ?? ""}
                onChange={handleCreditChange}
                step="any"
              />
            ))}
          </div>
        </FormSection>

        <FormSection
          icon={IndianRupee}
          title="Historical payment amounts"
          description="Payment amounts recorded across the six historical periods."
        >
          <div className="analysis-fields-grid">
            {paymentFields.map(([name, label]) => (
              <Field
                key={name}
                label={`${label} (${name})`}
                name={name}
                value={creditFeatures[name] ?? ""}
                onChange={handleCreditChange}
                min="0"
                step="any"
              />
            ))}
          </div>
        </FormSection>

        <div className="analysis-submit-area">
          <div className="analysis-submit-note">
            <ShieldCheck size={18} />
            <span>
              All 22 model input fields and financial details are required.
              Submit only verified or appropriately authorised information.
            </span>
          </div>

          <button
            type="submit"
            className="analysis-submit-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <LoaderCircle className="spin" size={18} />
                Analysing borrower...
              </>
            ) : (
              <>
                <BrainCircuit size={19} />
                Generate full assessment report
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}