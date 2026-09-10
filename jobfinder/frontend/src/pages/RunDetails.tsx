/**
 * Run Details page - shows progress and metrics for a specific run
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import type { Run } from "../types";

export function RunDetails() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [run, setRun] = useState<Run | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(true);

  // Poll for run status updates
  useEffect(() => {
    if (!runId) return;

    const loadRun = async () => {
      try {
        const data = await apiClient.getRun(runId);
        setRun(data);
        setError(null);

        // Stop polling if run is completed or failed
        if (data.status === "completed" || data.status === "failed") {
          setPolling(false);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load run details");
      } finally {
        setLoading(false);
      }
    };

    loadRun();

    // Poll every 2 seconds while running
    if (polling) {
      const interval = setInterval(loadRun, 2000);
      return () => clearInterval(interval);
    }
  }, [runId, polling]);

  if (loading) {
    return <div className="run-details">Loading run details...</div>;
  }

  if (!run) {
    return (
      <div className="run-details">
        <h1>Run Not Found</h1>
        <button onClick={() => navigate("/")} className="btn">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const progress = Math.round(
    (run.total_processed / Math.max(run.total_planned, 1)) * 100
  );

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      pending: "#FFA500",
      in_progress: "#0066CC",
      completed: "#00AA00",
      failed: "#CC0000",
      partial: "#FF6600",
    };
    return colors[status] || "#999999";
  };

  return (
    <div className="run-details">
      <div className="run-header">
        <h1>Run Details</h1>
        <div className="run-id">ID: {runId}</div>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="run-grid">
        {/* Status Section */}
        <section className="status-section">
          <h2>Status</h2>
          <div className="status-display">
            <div
              className="status-badge"
              style={{ backgroundColor: getStatusColor(run.status) }}
            >
              {run.status.toUpperCase()}
            </div>
            <div className="task-info">
              <span className="label">Task:</span>
              <span>{run.task}</span>
            </div>
            {run.started_at && (
              <div className="timestamp">
                Started: {new Date(run.started_at).toLocaleString()}
              </div>
            )}
            {run.completed_at && (
              <div className="timestamp">
                Completed: {new Date(run.completed_at).toLocaleString()}
              </div>
            )}
            {run.error_message && (
              <div className="error-message">{run.error_message}</div>
            )}
          </div>
        </section>

        {/* Progress Section */}
        <section className="progress-section">
          <h2>Progress</h2>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="progress-text">
            {run.total_processed} / {run.total_planned} units processed ({progress}%)
          </div>
        </section>

        {/* Coverage Metrics */}
        <section className="coverage-section">
          <h2>Coverage</h2>
          <div className="metrics">
            <div className="metric">
              <span className="label">Jobs Found</span>
              <span className="value">{run.total_jobs_found}</span>
            </div>
            <div className="metric">
              <span className="label">Duplicates</span>
              <span className="value">{run.total_duplicates}</span>
            </div>
            <div className="metric">
              <span className="label">New Jobs</span>
              <span className="value">
                {run.total_jobs_found - run.total_duplicates - run.total_already_applied}
              </span>
            </div>
            <div className="metric">
              <span className="label">Already Applied</span>
              <span className="value">{run.total_already_applied}</span>
            </div>
            <div className="metric">
              <span className="label">Errors</span>
              <span className="value error-count">{run.total_errors}</span>
            </div>
          </div>
        </section>

        {/* Summary Statistics */}
        <section className="summary-section">
          <h2>Summary</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="label">Units Planned</span>
              <span className="value">{run.total_planned}</span>
            </div>
            <div className="summary-item">
              <span className="label">Units Processed</span>
              <span className="value">{run.total_processed}</span>
            </div>
            <div className="summary-item">
              <span className="label">Error Rate</span>
              <span className="value">
                {run.total_planned > 0
                  ? ((run.total_errors / run.total_planned) * 100).toFixed(1)
                  : 0}
                %
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Duplicate Rate</span>
              <span className="value">
                {run.total_jobs_found > 0
                  ? ((run.total_duplicates / run.total_jobs_found) * 100).toFixed(1)
                  : 0}
                %
              </span>
            </div>
          </div>
        </section>
      </div>

      {/* Actions */}
      <div className="run-actions">
        <button onClick={() => navigate("/jobs")} className="btn btn-primary">
          View Jobs from This Run
        </button>
        <button onClick={() => navigate("/")} className="btn btn-secondary">
          Back to Dashboard
        </button>
      </div>

      {/* Auto-refresh indicator */}
      {polling && run.status !== "completed" && run.status !== "failed" && (
        <div className="auto-refresh">
          Auto-refreshing... {run.status === "in_progress" ? "⏱️" : "⏳"}
        </div>
      )}
    </div>
  );
}
