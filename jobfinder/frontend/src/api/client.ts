/**
 * API client for Job Search System backend
 * Single entry point for all backend communication
 */

import type {
  Job,
  Run,
  Dashboard,
  JobsList,
  StartRunRequest,
  StartRunResponse,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Run endpoints
  async startTask1(): Promise<StartRunResponse> {
    return this.request<StartRunResponse>("/runs/task1", {
      method: "POST",
      body: JSON.stringify({ task: "task1" }),
    });
  }

  async startTask2(): Promise<StartRunResponse> {
    return this.request<StartRunResponse>("/runs/task2", {
      method: "POST",
      body: JSON.stringify({ task: "task2" }),
    });
  }

  async getRun(runId: string): Promise<Run> {
    return this.request<Run>(`/runs/${runId}`);
  }

  // Job endpoints
  async getJobs(
    page: number = 1,
    pageSize: number = 20,
    status?: string,
    company?: string,
    minFit?: number
  ): Promise<JobsList> {
    const params = new URLSearchParams();
    params.append("page", page.toString());
    params.append("page_size", pageSize.toString());
    if (status) params.append("status", status);
    if (company) params.append("company", company);
    if (minFit) params.append("min_fit", minFit.toString());

    return this.request<JobsList>(`/jobs?${params}`);
  }

  async getJob(jobId: string): Promise<Job> {
    return this.request<Job>(`/jobs/${jobId}`);
  }

  // Dashboard endpoint
  async getDashboard(): Promise<Dashboard> {
    return this.request<Dashboard>("/dashboard");
  }

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.request("/health", {});
  }
}

export const apiClient = new APIClient();
