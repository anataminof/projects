/**
 * Jobs page - list of discovered jobs with filtering and pagination
 */

import { useState, useEffect } from "react";
import { apiClient } from "../api/client";
import type { Job, JobsList } from "../types";

export function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [companyFilter, setCompanyFilter] = useState<string>("");
  const [minFitFilter, setMinFitFilter] = useState<number | undefined>();

  // Fetch jobs whenever filters or pagination changes
  useEffect(() => {
    loadJobs();
  }, [page, pageSize, statusFilter, companyFilter, minFitFilter]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const result = await apiClient.getJobs(
        page,
        pageSize,
        statusFilter || undefined,
        companyFilter || undefined,
        minFitFilter
      );
      setJobs(result.jobs);
      setTotalCount(result.total_count);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      new: "⚪",
      rejected: "🔴",
      to_apply: "🟢",
      verification_needed: "🟡",
      already_applied: "🔵",
    };
    return badges[status] || "❓";
  };

  return (
    <div className="jobs-page">
      <h1>Job Listings</h1>

      {error && <div className="error">{error}</div>}

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <label>Status</label>
          <select value={statusFilter} onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}>
            <option value="">All Statuses</option>
            <option value="new">New (⚪)</option>
            <option value="to_apply">To Apply (🟢)</option>
            <option value="verification_needed">Verification Needed (🟡)</option>
            <option value="already_applied">Already Applied (🔵)</option>
            <option value="rejected">Rejected (🔴)</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Company</label>
          <input
            type="text"
            placeholder="Search by company..."
            value={companyFilter}
            onChange={(e) => {
              setCompanyFilter(e.target.value);
              setPage(1);
            }}
          />
        </div>

        <div className="filter-group">
          <label>Minimum Fit Score</label>
          <input
            type="number"
            min="0"
            max="100"
            placeholder="e.g., 70"
            value={minFitFilter || ""}
            onChange={(e) => {
              setMinFitFilter(e.target.value ? parseInt(e.target.value) : undefined);
              setPage(1);
            }}
          />
        </div>

        <button onClick={() => loadJobs()} className="btn btn-secondary">
          Refresh
        </button>
      </div>

      {/* Jobs List */}
      {loading ? (
        <div>Loading jobs...</div>
      ) : (
        <>
          <div className="jobs-count">
            Showing {jobs.length} of {totalCount} jobs
          </div>

          {jobs.length === 0 ? (
            <div className="no-jobs">No jobs found matching your filters.</div>
          ) : (
            <div className="jobs-list">
              {jobs.map((job) => (
                <div key={job.job_id} className="job-card">
                  <div className="job-header">
                    <span className="status-badge">{getStatusBadge(job.status)}</span>
                    <h3>{job.title}</h3>
                    <span className="source">{job.source}</span>
                  </div>

                  <div className="job-info">
                    <div className="info-row">
                      <span className="label">Company:</span>
                      <span>{job.company}</span>
                    </div>
                    {job.location && (
                      <div className="info-row">
                        <span className="label">Location:</span>
                        <span>{job.location}</span>
                      </div>
                    )}
                    {job.work_model && (
                      <div className="info-row">
                        <span className="label">Work Model:</span>
                        <span>{job.work_model}</span>
                      </div>
                    )}
                    {job.fit_score !== undefined && (
                      <div className="info-row">
                        <span className="label">Fit Score:</span>
                        <span className="fit-score">
                          {job.fit_score.toFixed(0)}%
                        </span>
                      </div>
                    )}
                    {job.fit_reason && (
                      <div className="info-row">
                        <span className="label">Why it fits:</span>
                        <span>{job.fit_reason}</span>
                      </div>
                    )}
                    {job.gaps && job.gaps.length > 0 && (
                      <div className="info-row">
                        <span className="label">Gaps:</span>
                        <div className="gaps">
                          {job.gaps.map((gap) => (
                            <span key={gap} className="gap-tag">
                              {gap}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="job-actions">
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-small"
                    >
                      View Job
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn"
              >
                Previous
              </button>

              <span className="page-info">
                Page {page} of {totalPages}
              </span>

              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="btn"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Navigation */}
      <nav className="page-nav">
        <a href="/">Back to Dashboard</a>
      </nav>
    </div>
  );
}
