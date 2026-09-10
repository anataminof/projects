/**
 * Dashboard page - shows run controls and summary metrics
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import type { Dashboard as DashboardData } from "../types";

export function Dashboard() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingTask, setStartingTask] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch dashboard data on mount
  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDashboard();
      setDashboard(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleStartTask = async (task: "task1" | "task2") => {
    try {
      setStartingTask(task);
      const response =
        task === "task1" ? await apiClient.startTask1() : await apiClient.startTask2();
      // Navigate to run details
      navigate(`/runs/${response.run_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to start ${task}`);
    } finally {
      setStartingTask(null);
    }
  };

  if (loading) {
    return <div className="dashboard">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Job Search Dashboard</h1>

      {error && <div className="error">{error}</div>}

      <div className="dashboard-grid">
        {/* Run Controls */}
        <section className="run-controls">
          <h2>Start a Search</h2>
          <div className="button-group">
            <button
              onClick={() => handleStartTask("task1")}
              disabled={startingTask === "task1"}
              className="btn btn-primary"
            >
              {startingTask === "task1" ? "Starting..." : "Task 1: Company Coverage"}
            </button>
            <button
              onClick={() => handleStartTask("task2")}
              disabled={startingTask === "task2"}
              className="btn btn-primary"
            >
              {startingTask === "task2" ? "Starting..." : "Task 2: Web Discovery"}
            </button>
          </div>
        </section>

        {/* Summary Metrics */}
        {dashboard && (
          <section className="summary-metrics">
            <h2>Summary</h2>
            <div className="metrics-grid">
              <div className="metric">
                <span className="label">Total Jobs Found</span>
                <span className="value">{dashboard.total_jobs}</span>
              </div>
              <div className="metric">
                <span className="label">Companies Scanned</span>
                <span className="value">{dashboard.total_companies}</span>
              </div>
              <div className="metric">
                <span className="label">Coverage</span>
                <span className="value">{dashboard.coverage_percentage.toFixed(1)}%</span>
              </div>
              {dashboard.last_run_at && (
                <div className="metric">
                  <span className="label">Last Run</span>
                  <span className="value">
                    {new Date(dashboard.last_run_at).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Recent Runs */}
        {dashboard && dashboard.recent_runs.length > 0 && (
          <section className="recent-runs">
            <h2>Recent Runs</h2>
            <div className="runs-list">
              {dashboard.recent_runs.slice(0, 3).map((run) => (
                <div
                  key={run.run_id}
                  className="run-item"
                  onClick={() => navigate(`/runs/${run.run_id}`)}
                >
                  <div className="run-header">
                    <span className="task">{run.task}</span>
                    <span className={`status status-${run.status}`}>{run.status}</span>
                  </div>
                  <div className="run-stats">
                    <span>{run.total_jobs_found} jobs</span>
                    <span>{run.total_duplicates} duplicates</span>
                    <span>{run.total_already_applied} already applied</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <a href="/jobs">View All Jobs</a>
      </nav>
    </div>
  );
}
