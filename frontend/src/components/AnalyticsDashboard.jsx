import React, { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

import {
  Users,
  FileText,
  ShieldCheck,
  AlertTriangle,
  Wallet,
  TrendingUp,
  Activity,
  RefreshCw,
} from "lucide-react";

import { getApplicationHistory } from "../api";
import "./AnalyticsDashboard.css";

const COLORS = ["#36c995", "#e8b65e", "#f16d78", "#71839c"];

const currency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value || 0));

const formatDate = (value) => {
  if (!value) return "—";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
  });
};

const percentage = (value) =>
  `${(Number(value || 0) * 100).toFixed(2)}%`;

function Metric({ title, value, subtitle, icon: Icon, color }) {
  return (
    <div className="analytics-metric">
      <div className={`analytics-metric-icon ${color}`}>
        <Icon size={21} />
      </div>

      <div>
        <p>{title}</p>
        <h2>{value}</h2>
        <span>{subtitle}</span>
      </div>
    </div>
  );
}

function AnalyticsDashboard({
  borrowers = [],
  applications = [],
  loading = false,
  onNavigate,
}) {
  const [predictions, setPredictions] = useState([]);
  const [predictionLoading, setPredictionLoading] = useState(true);
  const [predictionError, setPredictionError] = useState("");

  const loadPredictions = async () => {
    try {
      setPredictionLoading(true);
      setPredictionError("");

      const results = await Promise.allSettled(
        applications.map(async (application) => {
          const history = await getApplicationHistory(application.id);

          return {
            application,
            prediction:
              Array.isArray(history) && history.length
                ? history[0]
                : null,
          };
        })
      );

      const successful = results
        .filter((result) => result.status === "fulfilled")
        .map((result) => result.value);

      const failedCount = results.length - successful.length;

      setPredictions(successful);

      if (failedCount > 0) {
        setPredictionError(
          `${failedCount} application history record(s) could not be loaded. Some analytics may be incomplete.`
        );
      }
    } catch (error) {
      console.error("Analytics loading error:", error);
      setPredictionError(
        "Unable to retrieve historical prediction data."
      );
    } finally {
      setPredictionLoading(false);
    }
  };

  useEffect(() => {
    loadPredictions();
  }, [applications]);

  const analytics = useMemo(() => {
    const eligible = applications.filter(
      (item) =>
        String(item.application_status || "").toLowerCase() === "eligible"
    );

    const rejected = applications.filter(
      (item) =>
        String(item.application_status || "").toLowerCase() === "rejected"
    );

    const totalLoanValue = applications.reduce(
      (sum, item) =>
        sum + Number(item.requested_loan_amount || 0),
      0
    );

    const validPredictions = predictions.filter(
      (item) => item.prediction
    );

    const riskCounts = {
      Low: 0,
      Medium: 0,
      High: 0,
      Other: 0,
    };

    validPredictions.forEach(({ prediction }) => {
      const risk = String(
        prediction.risk_category || ""
      ).toLowerCase();

      if (risk.includes("low")) riskCounts.Low += 1;
      else if (risk.includes("medium")) riskCounts.Medium += 1;
      else if (risk.includes("high")) riskCounts.High += 1;
      else riskCounts.Other += 1;
    });

    const riskData = Object.entries(riskCounts)
      .filter(([, value]) => value > 0)
      .map(([name, value]) => ({ name, value }));

    const probabilities = validPredictions
      .map(({ prediction }) => Number(prediction.default_probability))
      .filter(Number.isFinite);

    const averageProbability = probabilities.length
      ? probabilities.reduce((sum, value) => sum + value, 0) /
        probabilities.length
      : null;

    const expectedLossValues = validPredictions
      .map(({ prediction }) => prediction.expected_loss)
      .filter(
        (value) => value !== null && value !== undefined &&
          Number.isFinite(Number(value))
      );

    const totalExpectedLoss = expectedLossValues.reduce(
      (sum, value) => sum + Number(value),
      0
    );

    const trendMap = {};

    applications.forEach((application) => {
      const date = application.created_at
        ? new Date(application.created_at).toISOString().slice(0, 10)
        : "Unknown";

      if (!trendMap[date]) {
        trendMap[date] = {
          date,
          applications: 0,
          loanValue: 0,
        };
      }

      trendMap[date].applications += 1;
      trendMap[date].loanValue += Number(
        application.requested_loan_amount || 0
      );
    });

    const trendData = Object.values(trendMap)
      .filter((item) => item.date !== "Unknown")
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(-10)
      .map((item) => ({
        ...item,
        label: formatDate(item.date),
      }));

    const probabilityData = validPredictions.map(
      ({ application, prediction }) => ({
        reference: application.application_reference,
        probability:
          Number(prediction.default_probability || 0) * 100,
        risk: prediction.risk_category || "Unclassified",
      })
    );

    const recentActivity = [...applications]
      .sort(
        (a, b) =>
          new Date(b.created_at || 0) -
          new Date(a.created_at || 0)
      )
      .slice(0, 6);

    return {
      eligible,
      rejected,
      totalLoanValue,
      riskData,
      averageProbability,
      totalExpectedLoss,
      expectedLossCount: expectedLossValues.length,
      validPredictionCount: validPredictions.length,
      trendData,
      probabilityData,
      recentActivity,
    };
  }, [applications, predictions]);

  if (loading) {
    return (
      <div className="analytics-loading">
        <RefreshCw className="analytics-spin" size={25} />
        <p>Loading platform analytics...</p>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">

      <div className="analytics-heading">
        <div>
          <h1>Analytics & Intelligence</h1>
          <p>
            Financial portfolio performance and historical credit risk insights.
          </p>
        </div>

        <button
          className="analytics-refresh"
          onClick={loadPredictions}
          disabled={predictionLoading}
        >
          <RefreshCw
            size={16}
            className={predictionLoading ? "analytics-spin" : ""}
          />
          Refresh Analytics
        </button>
      </div>

      {predictionError && (
        <div className="analytics-warning">
          <AlertTriangle size={17} />
          {predictionError}
        </div>
      )}

      <div className="analytics-metric-grid">

        <Metric
          title="Total Borrowers"
          value={borrowers.length}
          subtitle="Registered borrowers"
          icon={Users}
          color="blue"
        />

        <Metric
          title="Loan Applications"
          value={applications.length}
          subtitle="Recorded applications"
          icon={FileText}
          color="purple"
        />

        <Metric
          title="Eligible Applications"
          value={analytics.eligible.length}
          subtitle="Recorded eligible decisions"
          icon={ShieldCheck}
          color="green"
        />

        <Metric
          title="Rejected Applications"
          value={analytics.rejected.length}
          subtitle="Recorded rejected decisions"
          icon={AlertTriangle}
          color="orange"
        />

        <Metric
          title="Requested Loan Value"
          value={currency(analytics.totalLoanValue)}
          subtitle="Across recorded applications"
          icon={Wallet}
          color="blue"
        />

        <Metric
          title="Average Default Probability"
          value={
            analytics.averageProbability === null
              ? "—"
              : percentage(analytics.averageProbability)
          }
          subtitle={`${analytics.validPredictionCount} saved predictions`}
          icon={TrendingUp}
          color="purple"
        />

        <Metric
          title="Total Expected Loss"
          value={
            analytics.expectedLossCount
              ? currency(analytics.totalExpectedLoss)
              : "—"
          }
          subtitle={`${analytics.expectedLossCount} saved estimates`}
          icon={Activity}
          color="orange"
        />

        <Metric
          title="Available Risk Records"
          value={analytics.validPredictionCount}
          subtitle="Applications with saved predictions"
          icon={ShieldCheck}
          color="green"
        />

      </div>

      <div className="analytics-chart-grid">

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h3>Application Activity</h3>
              <p>Number of applications recorded over time</p>
            </div>
            <Activity size={19} />
          </div>

          {analytics.trendData.length ? (
            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={analytics.trendData}>
                  <defs>
                    <linearGradient
                      id="applicationGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor="#4c91f5"
                        stopOpacity={0.35}
                      />
                      <stop
                        offset="100%"
                        stopColor="#4c91f5"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#2b3a50"
                  />

                  <XAxis dataKey="label" stroke="#91a2ba" />
                  <YAxis allowDecimals={false} stroke="#91a2ba" />
                  <Tooltip
                    contentStyle={{
                      background: "#172337",
                      border: "1px solid #34465e",
                      borderRadius: 8,
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="applications"
                    stroke="#4c91f5"
                    fill="url(#applicationGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="analytics-empty">
              No application trend data available.
            </div>
          )}
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h3>Risk Distribution</h3>
              <p>Classification of saved model predictions</p>
            </div>
            <ShieldCheck size={19} />
          </div>

          {analytics.riskData.length ? (
            <>
              <div className="analytics-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analytics.riskData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={62}
                      outerRadius={95}
                      paddingAngle={4}
                    >
                      {analytics.riskData.map((item, index) => (
                        <Cell
                          key={item.name}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>

                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <div className="analytics-empty">
              {predictionLoading
                ? "Loading risk records..."
                : "No saved risk predictions available."}
            </div>
          )}
        </section>

      </div>

      <div className="analytics-chart-grid">

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h3>Default Probability by Application</h3>
              <p>Historical model predictions, displayed as percentages</p>
            </div>
            <TrendingUp size={19} />
          </div>

          {analytics.probabilityData.length ? (
            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={analytics.probabilityData}
                  margin={{ top: 10, right: 15, left: 0, bottom: 35 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#2b3a50"
                  />

                  <XAxis
                    dataKey="reference"
                    stroke="#91a2ba"
                    angle={-20}
                    textAnchor="end"
                    interval={0}
                    height={65}
                    tick={{ fontSize: 9 }}
                  />

                  <YAxis
                    stroke="#91a2ba"
                    unit="%"
                  />

                  <Tooltip
                    formatter={(value) => `${Number(value).toFixed(2)}%`}
                    contentStyle={{
                      background: "#172337",
                      border: "1px solid #34465e",
                      borderRadius: 8,
                    }}
                  />

                  <Bar
                    dataKey="probability"
                    name="Default Probability"
                    fill="#8a75e8"
                    radius={[5, 5, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="analytics-empty">
              {predictionLoading
                ? "Loading predictions..."
                : "No historical probability data available."}
            </div>
          )}
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-heading">
            <div>
              <h3>Requested Loan Value</h3>
              <p>Loan amounts grouped by application date</p>
            </div>
            <Wallet size={19} />
          </div>

          {analytics.trendData.length ? (
            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.trendData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#2b3a50"
                  />

                  <XAxis dataKey="label" stroke="#91a2ba" />
                  <YAxis stroke="#91a2ba" />

                  <Tooltip
                    formatter={(value) => currency(value)}
                    contentStyle={{
                      background: "#172337",
                      border: "1px solid #34465e",
                      borderRadius: 8,
                    }}
                  />

                  <Bar
                    dataKey="loanValue"
                    name="Requested Loan Value"
                    fill="#36c995"
                    radius={[5, 5, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="analytics-empty">
              No loan value data available.
            </div>
          )}
        </section>

      </div>

      <section className="analytics-panel analytics-activity-panel">
        <div className="analytics-panel-heading">
          <div>
            <h3>Recent Application Activity</h3>
            <p>Latest recorded borrower applications</p>
          </div>
          <FileText size={19} />
        </div>

        <div className="analytics-table-wrap">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Application Reference</th>
                <th>Borrower ID</th>
                <th>Loan Amount</th>
                <th>Proposed EMI</th>
                <th>Status</th>
                <th>Date</th>
                <th>Default Probability</th>
              </tr>
            </thead>

            <tbody>
              {analytics.recentActivity.map((application) => {
                const saved = predictions.find(
                  (item) =>
                    item.application.id === application.id
                );

                const prediction = saved?.prediction;

                return (
                  <tr key={application.id}>
                    <td>{application.application_reference}</td>
                    <td>{application.borrower_id}</td>
                    <td>
                      {currency(application.requested_loan_amount)}
                    </td>
                    <td>{currency(application.proposed_emi)}</td>
                    <td>{application.application_status || "Pending"}</td>
                    <td>{formatDate(application.created_at)}</td>
                    <td>
                      {prediction
                        ? percentage(prediction.default_probability)
                        : "Unavailable"}
                    </td>
                  </tr>
                );
              })}

              {!analytics.recentActivity.length && (
                <tr>
                  <td colSpan="7">
                    No application activity recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <div className="analytics-disclaimer">
        Analytics are calculated from available saved FinAI records.
        Expected loss values are illustrative model estimates, not
        guaranteed financial losses. Historical predictions are not
        recalculated when this dashboard is opened.
      </div>

    </div>
  );
}

export default AnalyticsDashboard;