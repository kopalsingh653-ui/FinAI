import React, { useEffect, useState } from "react";
import {
  ArrowLeft,
  UserRound,
  Mail,
  CalendarDays,
  Wallet,
  CreditCard,
  TrendingUp,
  ShieldCheck,
  FileText,
  Eye,
  RefreshCw,
  AlertCircle,
  Activity,
} from "lucide-react";

import {
  getBorrower,
  getBorrowerApplications,
  getBorrowerCreditProfile,
} from "../api";

import "./BorrowerProfile.css";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));

const formatDate = (date) => {
  if (!date) return "—";

  return new Date(date).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const percentage = (value) =>
  `${(Number(value || 0) * 100).toFixed(2)}%`;

function StatCard({ title, value, subtitle, icon: Icon, color }) {
  return (
    <div className="bp-stat-card">
      <div className={`bp-stat-icon ${color}`}>
        <Icon size={21} />
      </div>

      <div>
        <p>{title}</p>
        <h2>{value}</h2>
        {subtitle && <span>{subtitle}</span>}
      </div>
    </div>
  );
}

function SectionHeader({ title, description }) {
  return (
    <div className="bp-section-header">
      <div>
        <h3>{title}</h3>
        {description && <p>{description}</p>}
      </div>
    </div>
  );
}

function BorrowerProfile({
  borrowerId,
  onBack,
  onViewReport,
}) {
  const [borrower, setBorrower] = useState(null);
  const [applications, setApplications] = useState([]);
  const [creditProfile, setCreditProfile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const [borrowerData, applicationData, creditData] =
        await Promise.all([
          getBorrower(borrowerId),
          getBorrowerApplications(borrowerId),
          getBorrowerCreditProfile(borrowerId),
        ]);

      setBorrower(borrowerData);
      setApplications(
        Array.isArray(applicationData) ? applicationData : []
      );
      setCreditProfile(creditData);
    } catch (err) {
      console.error("Borrower profile error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load borrower information. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (borrowerId) loadProfile();
  }, [borrowerId]);

  if (loading) {
    return (
      <div className="bp-state">
        <RefreshCw className="bp-spinner" size={28} />
        <p>Loading borrower profile...</p>
      </div>
    );
  }

  if (error || !borrower) {
    return (
      <div className="bp-state bp-error">
        <AlertCircle size={30} />
        <h3>Unable to load profile</h3>
        <p>{error || "Borrower not found."}</p>
        <button onClick={loadProfile}>Try Again</button>
        <button className="bp-secondary-btn" onClick={onBack}>
          Go Back
        </button>
      </div>
    );
  }

  const creditHistory = creditProfile?.credit_history || [];

  const latestCredit = creditHistory[0] || null;

  const eligibleCount = applications.filter(
    (app) =>
      String(app.application_status || "").toLowerCase() === "eligible"
  ).length;

  const rejectedCount = applications.filter(
    (app) =>
      String(app.application_status || "").toLowerCase() === "rejected"
  ).length;

  const disposableIncome =
    Number(borrower.monthly_income || 0) -
    Number(borrower.monthly_expenses || 0) -
    Number(borrower.existing_emi || 0) -
    Number(borrower.other_monthly_debt || 0);

  return (
    <div className="borrower-profile">

      {/* Page heading */}

      <div className="bp-topbar">
        <button className="bp-back-btn" onClick={onBack}>
          <ArrowLeft size={17} />
          Back to Borrowers
        </button>

        <button className="bp-refresh-btn" onClick={loadProfile}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Borrower identity */}

      <div className="bp-identity-card">
        <div className="bp-avatar">
          <UserRound size={34} />
        </div>

        <div className="bp-identity-info">
          <div className="bp-name-row">
            <h1>{borrower.full_name}</h1>

            <span className="bp-reference">
              {borrower.borrower_reference}
            </span>
          </div>

          <div className="bp-contact-row">
            <span>
              <Mail size={15} />
              {borrower.email}
            </span>

            <span>
              <CalendarDays size={15} />
              Registered {formatDate(borrower.created_at)}
            </span>
          </div>
        </div>

        <div className="bp-identity-badge">
          <ShieldCheck size={17} />
          Registered Borrower
        </div>
      </div>

      {/* Overview metrics */}

      <div className="bp-stats-grid">

        <StatCard
          title="Total Applications"
          value={applications.length}
          subtitle="Recorded applications"
          icon={FileText}
          color="blue"
        />

        <StatCard
          title="Eligible Applications"
          value={eligibleCount}
          subtitle="Marked eligible"
          icon={ShieldCheck}
          color="green"
        />

        <StatCard
          title="Latest Credit Score"
          value={latestCredit?.credit_score ?? "—"}
          subtitle={latestCredit?.score_band || "No score available"}
          icon={TrendingUp}
          color="purple"
        />

        <StatCard
          title="Rejected Applications"
          value={rejectedCount}
          subtitle="Recorded rejections"
          icon={Activity}
          color="orange"
        />

      </div>

      {/* Financial profile */}

      <div className="bp-panel">
        <SectionHeader
          title="Financial Overview"
          description="Borrower's recorded monthly financial information"
        />

        <div className="bp-financial-grid">

          <div className="bp-financial-item">
            <span>Monthly Income</span>
            <strong>{formatCurrency(borrower.monthly_income)}</strong>
          </div>

          <div className="bp-financial-item">
            <span>Monthly Expenses</span>
            <strong>{formatCurrency(borrower.monthly_expenses)}</strong>
          </div>

          <div className="bp-financial-item">
            <span>Existing EMI</span>
            <strong>{formatCurrency(borrower.existing_emi)}</strong>
          </div>

          <div className="bp-financial-item">
            <span>Other Monthly Debt</span>
            <strong>{formatCurrency(borrower.other_monthly_debt)}</strong>
          </div>

          <div className="bp-financial-item bp-highlight">
            <span>Calculated Disposable Income</span>
            <strong>{formatCurrency(disposableIncome)}</strong>
          </div>

          <div className="bp-financial-item">
            <span>Debt-to-Income Ratio</span>
            <strong>
              {latestCredit
                ? percentage(latestCredit.debt_to_income_ratio)
                : "—"}
            </strong>
          </div>

        </div>
      </div>

      {/* Credit profile */}

      <div className="bp-panel">
        <SectionHeader
          title="Credit Profile"
          description="Historical FinAI credit scoring information"
        />

        {latestCredit ? (
          <>
            <div className="bp-credit-summary">

              <div className="bp-credit-score">
                <span>Latest FinAI Credit Score</span>
                <strong>{latestCredit.credit_score}</strong>
                <span className="bp-score-band">
                  {latestCredit.score_band}
                </span>
              </div>

              <div className="bp-credit-components">

                <div className="bp-progress-item">
                  <div>
                    <span>Repayment History</span>
                    <strong>{latestCredit.repayment_history_score}%</strong>
                  </div>
                  <div className="bp-progress">
                    <div
                      style={{
                        width: `${latestCredit.repayment_history_score}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="bp-progress-item">
                  <div>
                    <span>Utilisation Score</span>
                    <strong>{latestCredit.utilisation_score}%</strong>
                  </div>
                  <div className="bp-progress">
                    <div
                      style={{
                        width: `${latestCredit.utilisation_score}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="bp-progress-item">
                  <div>
                    <span>Payment Behaviour</span>
                    <strong>{latestCredit.payment_behaviour_score}%</strong>
                  </div>
                  <div className="bp-progress">
                    <div
                      style={{
                        width: `${latestCredit.payment_behaviour_score}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="bp-progress-item">
                  <div>
                    <span>Affordability Score</span>
                    <strong>{latestCredit.affordability_score}%</strong>
                  </div>
                  <div className="bp-progress">
                    <div
                      style={{
                        width: `${latestCredit.affordability_score}%`,
                      }}
                    />
                  </div>
                </div>

              </div>
            </div>

            <div className="bp-credit-extra">
              <div>
                <span>Credit Utilisation</span>
                <strong>
                  {percentage(latestCredit.credit_utilisation)}
                </strong>
              </div>

              <div>
                <span>Debt-to-Income Ratio</span>
                <strong>
                  {percentage(latestCredit.debt_to_income_ratio)}
                </strong>
              </div>

              <div>
                <span>Last Updated</span>
                <strong>{formatDate(latestCredit.created_at)}</strong>
              </div>
            </div>
          </>
        ) : (
          <div className="bp-empty">
            No credit score history is available.
          </div>
        )}
      </div>

      {/* Application history */}

      <div className="bp-panel">
        <SectionHeader
          title="Application History"
          description={`${applications.length} applications associated with this borrower`}
        />

        {applications.length > 0 ? (
          <div className="bp-table-wrapper">
            <table className="bp-table">
              <thead>
                <tr>
                  <th>Application Reference</th>
                  <th>Loan Amount</th>
                  <th>Proposed EMI</th>
                  <th>Credit Score</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {applications.map((application) => {
                  const score = creditHistory.find(
                    (item) =>
                      item.application_id === application.id
                  );

                  return (
                    <tr key={application.id}>
                      <td>
                        <strong>
                          {application.application_reference}
                        </strong>
                      </td>

                      <td>
                        {formatCurrency(
                          application.requested_loan_amount
                        )}
                      </td>

                      <td>
                        {formatCurrency(application.proposed_emi)}
                      </td>

                      <td>
                        {score?.credit_score ?? "—"}
                      </td>

                      <td>
                        <span
                          className={`bp-status ${String(
                            application.application_status || "pending"
                          ).toLowerCase()}`}
                        >
                          {application.application_status || "Pending"}
                        </span>
                      </td>

                      <td>{formatDate(application.created_at)}</td>

                      <td>
                        <button
                          className="bp-view-btn"
                          onClick={() =>
                            onViewReport(application.id)
                          }
                        >
                          <Eye size={15} />
                          View Report
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="bp-empty">
            No loan applications have been recorded for this borrower.
          </div>
        )}
      </div>

      <div className="bp-disclaimer">
        <ShieldCheck size={16} />
        FinAI credit scores are internally generated assessment scores
        and are not official credit bureau scores.
      </div>

    </div>
  );
}

export default BorrowerProfile;