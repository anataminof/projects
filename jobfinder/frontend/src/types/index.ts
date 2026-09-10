/**
 * Type definitions for Job Search System API responses
 */

export type JobStatus = "new" | "rejected" | "to_apply" | "verification_needed" | "already_applied";
export type RunStatus = "pending" | "in_progress" | "completed" | "failed" | "partial";

export interface Job {
  job_id: string;
  title: string;
  company: string;
  location?: string;
  work_model?: string;
  url: string;
  source: string;
  status: JobStatus;
  fit_score?: number;
  fit_reason?: string;
  gaps?: string[];
  discovered_at: string;
}

export interface Run {
  run_id: string;
  task: string;
  status: RunStatus;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  total_planned: number;
  total_processed: number;
  total_jobs_found: number;
  total_duplicates: number;
  total_already_applied: number;
  total_errors: number;
}

export interface Dashboard {
  total_jobs: number;
  total_companies: number;
  recent_runs: Run[];
  last_run_status?: string;
  last_run_at?: string;
  coverage_percentage: number;
}

export interface JobsList {
  jobs: Job[];
  total_count: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface StartRunRequest {
  task: "task1" | "task2";
}

export interface StartRunResponse {
  run_id: string;
  task: string;
  status: RunStatus;
  message: string;
}
