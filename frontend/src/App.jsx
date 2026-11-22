import React, { useEffect, useState } from "react";

import {
  LayoutDashboard,
  Users,
  FileText,
  BrainCircuit,
  ShieldCheck,
  Settings,
  Search,
  Menu,
  X,
  ArrowUpRight,
  Eye,
  RefreshCw,
  ChevronRight,
  UserRound,
  Download,
  Printer,
  LogOut,
} from "lucide-react";

import {
  getBorrowers,
  getApplications,
  getBorrower,
  getBorrowerCreditProfile,
  getApplication,
  getApplicationHistory,
} from "./api";

import CreditAnalysis from "./CreditAnalysis.jsx";
import BorrowerProfile from "./components/BorrowerProfile.jsx";
import AnalyticsDashboard from "./components/AnalyticsDashboard.jsx";

import "./index.css";

const money = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));

const dateFormat = (value) => {
  if (!value) return "—";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

// --------------------------------------------------
// STATUS BADGE
// --------------------------------------------------

function StatusBadge({ status }) {
  const value = String(status || "Pending");

  return (
    <span className={`finai-status ${value.toLowerCase()}`}>
      {value}
    </span>
  );
}

// --------------------------------------------------
// LOADING AND ERROR
// --------------------------------------------------

function LoadingState() {
  return (
    <div className="finai-loading">
      <RefreshCw className="spin" size={25} />
      <p>Loading FinAI data...</p>
    </div>
  );
}

function ErrorState({ message, retry }) {
  return (
    <div className="finai-error">
      <RefreshCw size={25} />
      <h3>Unable to load data</h3>
      <p>{message}</p>
      <button onClick={retry}>Try Again</button>
    </div>
  );
}

function PageHeader({ title, subtitle, action }) {
  return (
    <div className="finai-page-header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {action}
    </div>
  );
}

// --------------------------------------------------
// BORROWERS
// --------------------------------------------------

function BorrowersPage({ borrowers, loading, onOpen }) {
  const [search, setSearch] = useState("");

  if (loading) return <LoadingState />;

  const filtered = borrowers.filter((borrower) => {
    const query = search.toLowerCase();

    return (
      String(borrower.full_name || "").toLowerCase().includes(query) ||
      String(borrower.email || "").toLowerCase().includes(query) ||
      String(borrower.borrower_reference || "")
        .toLowerCase()
        .includes(query)
    );
  });

  return (
    <div className="finai-page">
      <PageHeader
        title="Borrowers"
        subtitle="Manage borrower records and explore their financial profiles."
      />

      <div className="finai-card">
        <div className="finai-toolbar">
          <div className="finai-search">
            <Search size={17} />
            <input
              placeholder="Search borrowers by name, email or reference..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <span className="finai-record-count">
            {filtered.length} borrowers
          </span>
        </div>

        <div className="finai-table-wrap">
          <table className="finai-table">
            <thead>
              <tr>
                <th>Borrower</th>
                <th>Reference</th>
                <th>Monthly Income</th>
                <th>Existing EMI</th>
                <th>Registration Date</th>
                <th>Profile</th>
              </tr>
            </thead>

            <tbody>
              {filtered.map((borrower) => (
                <tr key={borrower.id}>
                  <td>
                    <div className="finai-person-cell">
                      <div className="finai-small-avatar">
                        <UserRound size={17} />
                      </div>
                      <div>
                        <strong>{borrower.full_name}</strong>
                        <span>{borrower.email}</span>
                      </div>
                    </div>
                  </td>

                  <td>{borrower.borrower_reference || `BRW-${borrower.id}`}</td>
                  <td>{money(borrower.monthly_income)}</td>
                  <td>{money(borrower.existing_emi)}</td>
                  <td>{dateFormat(borrower.created_at)}</td>

                  <td>
                    <button
                      className="finai-view-btn"
                      onClick={() => onOpen(borrower.id)}
                    >
                      <Eye size={15} />
                      View Profile
                    </button>
                  </td>
                </tr>
              ))}

              {!filtered.length && (
                <tr>
                  <td colSpan="6">
                    <div className="finai-empty">
                      No matching borrowers found.
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// --------------------------------------------------
// APPLICATION TABLE
// --------------------------------------------------

function ApplicationTable({ applications, onView }) {
  return (
    <div className="finai-table-wrap">
      <table className="finai-table">
        <thead>
          <tr>
            <th>Application Reference</th>
            <th>Borrower ID</th>
            <th>Loan Amount</th>
            <th>Proposed EMI</th>
            <th>Status</th>
            <th>Date</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {applications.map((application) => (
            <tr key={application.id}>
              <td>
                <strong>{application.application_reference}</strong>
              </td>

              <td>{application.borrower_id}</td>
              <td>{money(application.requested_loan_amount)}</td>
              <td>{money(application.proposed_emi)}</td>

              <td>
                <StatusBadge status={application.application_status} />
              </td>

              <td>{dateFormat(application.created_at)}</td>

              <td>
                <button
                  className="finai-view-btn"
                  onClick={() => onView(application.id)}
                >
                  <Eye size={15} />
                  View Report
                </button>
              </td>
            </tr>
          ))}

          {!applications.length && (
            <tr>
              <td colSpan="7">
                <div className="finai-empty">
                  No applications available.
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

// --------------------------------------------------
// APPLICATIONS PAGE
// --------------------------------------------------

function ApplicationsPage({ applications, loading, onView }) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  if (loading) return <LoadingState />;

  const filtered = applications.filter((application) => {
    const query = search.toLowerCase();

    const matchesSearch =
      String(application.application_reference || "")
        .toLowerCase()
        .includes(query) ||
      String(application.borrower_id || "").includes(query);

    const matchesStatus =
      statusFilter === "all" ||
      String(application.application_status || "").toLowerCase() ===
        statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="finai-page">
      <PageHeader
        title="Loan Applications"
        subtitle="Review and manage all recorded loan applications."
      />

      <div className="finai-card">
        <div className="finai-toolbar">
          <div className="finai-search">
            <Search size={17} />
            <input
              placeholder="Search application reference or borrower ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select
            className="finai-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="eligible">Eligible</option>
            <option value="rejected">Rejected</option>
            <option value="pending">Pending</option>
          </select>
        </div>

        <ApplicationTable
          applications={filtered}
          onView={onView}
        />
      </div>
    </div>
  );
}

// --------------------------------------------------
// HISTORICAL ANALYSIS REPORT
// --------------------------------------------------

function AnalysisReport({
  applicationId,
  onBack,
  onOpenBorrower,
}) {
  const [application, setApplication] = useState(null);
  const [history, setHistory] = useState([]);
  const [borrower, setBorrower] = useState(null);
  const [creditProfile, setCreditProfile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const loadReport = async () => {
      try {
        setLoading(true);
        setError("");

        const appData = await getApplication(applicationId);

        const [historyData, borrowerData, creditData] =
          await Promise.all([
            getApplicationHistory(applicationId),
            getBorrower(appData.borrower_id),
            getBorrowerCreditProfile(appData.borrower_id),
          ]);

        if (cancelled) return;

        setApplication(appData);
        setHistory(Array.isArray(historyData) ? historyData : []);
        setBorrower(borrowerData);
        setCreditProfile(creditData);
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              "Unable to retrieve this historical report."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadReport();

    return () => {
      cancelled = true;
    };
  }, [applicationId]);

  if (loading) return <LoadingState />;

  if (error || !application) {
    return (
      <div className="finai-page">
        <ErrorState
          message={error || "Application not found."}
          retry={() => window.location.reload()}
        />

        <button className="finai-secondary-btn" onClick={onBack}>
          Go Back
        </button>
      </div>
    );
  }

  const prediction = history[0] || null;

  const credit = creditProfile?.credit_history?.find(
    (item) => item.application_id === application.id
  );

  const downloadCSV = () => {
    const rows = [
      ["FinAI Historical Credit Assessment"],
      ["Application Reference", application.application_reference],
      ["Borrower", borrower?.full_name],
      ["Borrower Email", borrower?.email],
      ["Requested Loan", application.requested_loan_amount],
      ["Proposed EMI", application.proposed_emi],
      ["Application Status", application.application_status],
      ["Credit Score", credit?.credit_score ?? "Unavailable"],
      ["Score Band", credit?.score_band ?? "Unavailable"],
      ["Default Probability", prediction?.default_probability ?? "Unavailable"],
      ["Risk Category", prediction?.risk_category ?? "Unavailable"],
      ["Expected Loss", prediction?.expected_loss ?? "Unavailable"],
      ["Model Threshold", prediction?.model_threshold ?? "Unavailable"],
      ["Assessment Date", prediction?.created_at ?? application.created_at],
    ];

    const csv = rows
      .map((row) =>
        row
          .map((cell) => `"${String(cell ?? "").replace(/"/g, '""')}"`)
          .join(",")
      )
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `${application.application_reference}-report.csv`;
    link.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="finai-page">
      <div className="finai-report-actions no-print">
        <button className="finai-secondary-btn" onClick={onBack}>
          ← Back
        </button>

        <div>
          <button className="finai-secondary-btn" onClick={downloadCSV}>
            <Download size={16} /> Export CSV
          </button>

          <button
            className="finai-primary-btn"
            onClick={() => window.print()}
          >
            <Printer size={16} /> Print Report
          </button>
        </div>
      </div>

      <div className="finai-report">
        <div className="finai-report-header">
          <div>
            <span className="finai-report-brand">FINAI</span>
            <h1>Credit Assessment Report</h1>
            <p>Historical borrower and loan risk assessment</p>
          </div>

          <div className="finai-report-reference">
            <span>Application Reference</span>
            <strong>{application.application_reference}</strong>
            <span>
              {dateFormat(prediction?.created_at || application.created_at)}
            </span>
          </div>
        </div>

        <div className="finai-report-section">
          <h3>Borrower Information</h3>

          <div className="finai-report-grid">
            <div>
              <span>Full Name</span>
              <strong>{borrower?.full_name || "—"}</strong>
            </div>

            <div>
              <span>Email</span>
              <strong>{borrower?.email || "—"}</strong>
            </div>

            <div>
              <span>Borrower Reference</span>
              <strong>{borrower?.borrower_reference || "—"}</strong>
            </div>

            <div>
              <span>Borrower ID</span>
              <strong>{application.borrower_id}</strong>
            </div>
          </div>
        </div>

        <div className="finai-report-section">
          <h3>Loan Application</h3>

          <div className="finai-report-grid">
            <div>
              <span>Requested Loan Amount</span>
              <strong>{money(application.requested_loan_amount)}</strong>
            </div>

            <div>
              <span>Proposed EMI</span>
              <strong>{money(application.proposed_emi)}</strong>
            </div>

            <div>
              <span>Application Status</span>
              <StatusBadge status={application.application_status} />
            </div>

            <div>
              <span>Application Date</span>
              <strong>{dateFormat(application.created_at)}</strong>
            </div>
          </div>
        </div>

        <div className="finai-report-section">
          <h3>Credit Assessment</h3>

          <div className="finai-report-metrics">
            <div>
              <span>FinAI Credit Score</span>
              <strong>{credit?.credit_score ?? "—"}</strong>
              <small>{credit?.score_band || "No score available"}</small>
            </div>

            <div>
              <span>Default Probability</span>
              <strong>
                {prediction
                  ? `${(Number(prediction.default_probability) * 100).toFixed(2)}%`
                  : "—"}
              </strong>
              <small>Stored model prediction</small>
            </div>

            <div>
              <span>Risk Category</span>
              <strong>{prediction?.risk_category || "—"}</strong>
              <small>Recorded risk classification</small>
            </div>
          </div>
        </div>

        <div className="finai-report-section">
          <h3>Credit Score Components</h3>

          {credit ? (
            <div className="finai-report-grid">
              <div>
                <span>Repayment History</span>
                <strong>{credit.repayment_history_score}%</strong>
              </div>

              <div>
                <span>Utilisation Score</span>
                <strong>{credit.utilisation_score}%</strong>
              </div>

              <div>
                <span>Payment Behaviour</span>
                <strong>{credit.payment_behaviour_score}%</strong>
              </div>

              <div>
                <span>Affordability Score</span>
                <strong>{credit.affordability_score}%</strong>
              </div>

              <div>
                <span>Debt-to-Income Ratio</span>
                <strong>
                  {(Number(credit.debt_to_income_ratio) * 100).toFixed(2)}%
                </strong>
              </div>

              <div>
                <span>Credit Utilisation</span>
                <strong>
                  {(Number(credit.credit_utilisation) * 100).toFixed(2)}%
                </strong>
              </div>
            </div>
          ) : (
            <p>No historical credit score record was found.</p>
          )}
        </div>

        <div className="finai-report-section">
          <h3>Risk Assessment</h3>

          <div className="finai-report-grid">
            <div>
              <span>Predicted Class</span>
              <strong>{prediction?.predicted_class ?? "—"}</strong>
            </div>

            <div>
              <span>Model Threshold</span>
              <strong>
                {prediction
                  ? Number(prediction.model_threshold).toFixed(3)
                  : "—"}
              </strong>
            </div>

            <div>
              <span>Expected Loss</span>
              <strong>
                {prediction ? money(prediction.expected_loss) : "—"}
              </strong>
            </div>

            <div>
              <span>Assessment Timestamp</span>
              <strong>{dateFormat(prediction?.created_at)}</strong>
            </div>
          </div>

          <div className="finai-report-explanation">
            <strong>Recorded Assessment Explanation</strong>
            <p>
              {prediction?.explanation ||
                "No explanation was stored for this assessment."}
            </p>
          </div>
        </div>

        {!prediction && (
          <div className="finai-report-notice">
            No saved prediction record was found. Historical prediction
            values have not been recalculated.
          </div>
        )}

        <div className="finai-report-disclaimer">
          FinAI generates internal credit risk assessments for
          decision-support purposes. Its credit score is not an official
          credit bureau score. Expected loss estimates are illustrative
          and depend on the assumptions used by the model.
        </div>

        <button
          className="finai-secondary-btn no-print"
          onClick={() => onOpenBorrower(application.borrower_id)}
        >
          <UserRound size={16} />
          Open Borrower Profile
        </button>
      </div>
    </div>
  );
}

// --------------------------------------------------
// RISK INTELLIGENCE
// --------------------------------------------------

function RiskIntelligence({ applications, onView }) {
  const [search, setSearch] = useState("");

  const filtered = applications.filter((application) => {
    const query = search.toLowerCase();

    return (
      String(application.application_reference || "")
        .toLowerCase()
        .includes(query) ||
      String(application.borrower_id || "").includes(query)
    );
  });

  return (
    <div className="finai-page">
      <PageHeader
        title="Risk Intelligence"
        subtitle="Explore recorded loan applications and their assessment status."
      />

      <div className="finai-card">
        <div className="finai-card-heading">
          <div>
            <h3>Application Monitoring</h3>
            <p>Inspect saved risk assessments for individual applications.</p>
          </div>
          <ShieldCheck size={21} />
        </div>

        <div className="finai-toolbar">
          <div className="finai-search">
            <Search size={17} />
            <input
              placeholder="Search application reference or borrower ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        <ApplicationTable
          applications={filtered}
          onView={onView}
        />
      </div>
    </div>
  );
}

// --------------------------------------------------
// SETTINGS
// --------------------------------------------------

function SettingsPage() {
  return (
    <div className="finai-page">
      <PageHeader
        title="Settings"
        subtitle="FinAI platform information and configuration."
      />

      <div className="finai-card finai-settings-card">
        <div className="finai-settings-logo">
          <BrainCircuit size={32} />
        </div>

        <h2>FinAI</h2>
        <p>AI-Powered Financial Inclusion and Responsible Lending System</p>

        <div className="finai-settings-grid">
          <div>
            <span>Platform</span>
            <strong>FinAI Financial Intelligence</strong>
          </div>

          <div>
            <span>Frontend</span>
            <strong>React + Vite</strong>
          </div>

          <div>
            <span>Backend</span>
            <strong>FastAPI</strong>
          </div>

          <div>
            <span>Database</span>
            <strong>SQLite + SQLAlchemy</strong>
          </div>

          <div>
            <span>Machine Learning</span>
            <strong>XGBoost</strong>
          </div>

          <div>
            <span>Assessment Type</span>
            <strong>Credit Risk Prediction</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

// --------------------------------------------------
// MAIN APP
// --------------------------------------------------

function App() {
  const [active, setActive] = useState("dashboard");

  const [borrowers, setBorrowers] = useState([]);
  const [applications, setApplications] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedBorrowerId, setSelectedBorrowerId] = useState(null);
  const [selectedApplicationId, setSelectedApplicationId] = useState(null);

  const [sidebarOpen, setSidebarOpen] = useState(false);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      const [borrowerData, applicationData] = await Promise.all([
        getBorrowers(),
        getApplications(),
      ]);

      setBorrowers(Array.isArray(borrowerData) ? borrowerData : []);
      setApplications(
        Array.isArray(applicationData) ? applicationData : []
      );
    } catch (err) {
      console.error("Dashboard loading error:", err);

      setError(
        err.response?.data?.detail ||
          "Could not connect to the FinAI backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const navigate = (page) => {
    setActive(page);
    setSidebarOpen(false);
  };

  const openBorrower = (id) => {
    setSelectedBorrowerId(id);
    navigate("borrower-profile");
  };

  const openReport = (id) => {
    setSelectedApplicationId(id);
    navigate("analysis-report");
  };

  const openBorrowerFromReport = (id) => {
    setSelectedBorrowerId(id);
    navigate("borrower-profile");
  };

  const pageTitles = {
    dashboard: "Analytics Dashboard",
    borrowers: "Borrowers",
    applications: "Applications",
    "credit-analysis": "Credit Analysis",
    "risk-intelligence": "Risk Intelligence",
    "borrower-profile": "Borrower Profile",
    "analysis-report": "Historical Analysis Report",
    settings: "Settings",
  };

  const navigation = [
    {
      label: "OVERVIEW",
      items: [
        {
          id: "dashboard",
          label: "Analytics Dashboard",
          icon: LayoutDashboard,
        },
      ],
    },
    {
      label: "BORROWER MANAGEMENT",
      items: [
        { id: "borrowers", label: "Borrowers", icon: Users },
        { id: "applications", label: "Applications", icon: FileText },
        {
          id: "credit-analysis",
          label: "Credit Analysis",
          icon: BrainCircuit,
        },
      ],
    },
    {
      label: "RISK MANAGEMENT",
      items: [
        {
          id: "risk-intelligence",
          label: "Risk Intelligence",
          icon: ShieldCheck,
        },
      ],
    },
    {
      label: "SYSTEM",
      items: [
        { id: "settings", label: "Settings", icon: Settings },
      ],
    },
  ];

  if (error && !borrowers.length && !applications.length) {
    return (
      <div className="finai-app">
        <ErrorState message={error} retry={loadDashboardData} />
      </div>
    );
  }

  return (
    <div className="finai-app">

      {/* SIDEBAR */}

      <aside className={`finai-sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="finai-brand">
          <div className="finai-brand-icon">
            <BrainCircuit size={25} />
          </div>

          <div>
            <h2>FinAI</h2>
            <span>Financial Intelligence</span>
          </div>

          <button
            className="finai-mobile-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="finai-sidebar-content">
          {navigation.map((group) => (
            <div className="finai-nav-group" key={group.label}>
              <p className="finai-nav-heading">{group.label}</p>

              {group.items.map((item) => {
                const Icon = item.icon;

                return (
                  <button
                    key={item.id}
                    className={`finai-nav-item ${
                      active === item.id ? "active" : ""
                    }`}
                    onClick={() => navigate(item.id)}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>

                    {active === item.id && (
                      <ChevronRight
                        size={15}
                        className="finai-nav-arrow"
                      />
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        <div className="finai-sidebar-footer">
          <div className="finai-admin-avatar">FA</div>
          <div>
            <strong>FinAI Analyst</strong>
            <span>Platform Administrator</span>
          </div>
          <LogOut size={17} />
        </div>
      </aside>

      {/* MAIN */}

      <main className="finai-main">
        <header className="finai-topbar">
          <div className="finai-topbar-left">
            <button
              className="finai-menu-btn"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={21} />
            </button>

            <span className="finai-breadcrumb">
              FinAI / {pageTitles[active] || "Dashboard"}
            </span>
          </div>

          <div className="finai-topbar-right">
            <button
              className="finai-icon-btn"
              onClick={loadDashboardData}
              title="Refresh data"
            >
              <RefreshCw size={18} />
            </button>

            <div className="finai-topbar-divider" />

            <div className="finai-topbar-user">
              <div className="finai-admin-avatar">FA</div>
              <div>
                <strong>Administrator</strong>
                <span>FinAI Workspace</span>
              </div>
            </div>
          </div>
        </header>

        <div className="finai-content">

          {/* ANALYTICS DASHBOARD */}

          {active === "dashboard" && (
            <AnalyticsDashboard
              borrowers={borrowers}
              applications={applications}
              loading={loading}
              onNavigate={navigate}
            />
          )}

          {/* BORROWERS */}

          {active === "borrowers" && (
            <BorrowersPage
              borrowers={borrowers}
              loading={loading}
              onOpen={openBorrower}
            />
          )}

          {/* BORROWER PROFILE */}

          {active === "borrower-profile" && (
            <BorrowerProfile
              borrowerId={selectedBorrowerId}
              onBack={() => navigate("borrowers")}
              onViewReport={openReport}
            />
          )}

          {/* APPLICATIONS */}

          {active === "applications" && (
            <ApplicationsPage
              applications={applications}
              loading={loading}
              onView={openReport}
            />
          )}

          {/* HISTORICAL REPORT */}

          {active === "analysis-report" && selectedApplicationId && (
            <AnalysisReport
              applicationId={selectedApplicationId}
              onBack={() =>
                selectedBorrowerId
                  ? navigate("borrower-profile")
                  : navigate("applications")
              }
              onOpenBorrower={openBorrowerFromReport}
            />
          )}

          {/* CREDIT ANALYSIS */}

          {active === "credit-analysis" && (
            <CreditAnalysis />
          )}

          {/* RISK INTELLIGENCE */}

          {active === "risk-intelligence" && (
            <RiskIntelligence
              applications={applications}
              onView={openReport}
            />
          )}

          {/* SETTINGS */}

          {active === "settings" && <SettingsPage />}

        </div>

        <footer className="finai-footer">
          <span>FinAI Financial Intelligence Platform</span>
          <span>AI-Powered Responsible Lending</span>
        </footer>
      </main>
    </div>
  );
}

export default App;