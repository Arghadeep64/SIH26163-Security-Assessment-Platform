/**
 * Centralized API client service for communicating with the SIH26163 FastAPI backend.
 */

import {
  Assessment,
  SecurityCheck,
  Finding,
  Evidence,
  Report,
  ReportFormat,
  ScanCreateRequest,
  ScanCreateResponse,
  DatabaseHealthResponse,
  SystemHealthResponse,
} from '../types/api';

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL !== undefined
    ? (import.meta as any).env.VITE_API_BASE_URL
    : '';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl ? baseUrl.replace(/\/+$/, '') : '';
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  public setBaseUrl(url: string): void {
    this.baseUrl = url ? url.replace(/\/+$/, '') : '';
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
    const url = this.baseUrl ? `${this.baseUrl}${cleanEndpoint}` : cleanEndpoint;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...(options.headers || {}),
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData?.detail) {
            errorMessage = errorData.detail;
          }
        } catch {
          // Ignore JSON parse error on non-JSON response
        }
        throw new Error(errorMessage);
      }

      return (await response.json()) as T;
    } catch (err: any) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        const target = this.baseUrl || 'same-origin server';
        throw new Error(
          `Unable to connect to the assessment backend at ${target}. Please verify the backend is running.`
        );
      }
      throw err;
    }
  }

  // ==========================================
  // Assessment / Scan APIs
  // ==========================================

  public async createAssessment(payload: ScanCreateRequest): Promise<ScanCreateResponse> {
    return this.request<ScanCreateResponse>('/api/scans', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  public async getAssessments(limit: number = 50): Promise<Assessment[]> {
    return this.request<Assessment[]>(`/api/scans?limit=${limit}`);
  }

  public async getAssessment(assessmentId: number): Promise<Assessment> {
    return this.request<Assessment>(`/api/scans/${assessmentId}`);
  }

  public async getChecks(assessmentId: number): Promise<SecurityCheck[]> {
    return this.request<SecurityCheck[]>(`/api/scans/${assessmentId}/checks`);
  }

  public async getScanFindings(assessmentId: number): Promise<Finding[]> {
    return this.request<Finding[]>(`/api/scans/${assessmentId}/findings`);
  }

  public async getEvidence(
    assessmentId: number,
    checkId?: number,
    findingId?: number
  ): Promise<Evidence[]> {
    const params = new URLSearchParams();
    if (checkId !== undefined) params.append('check_id', checkId.toString());
    if (findingId !== undefined) params.append('finding_id', findingId.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<Evidence[]>(`/api/scans/${assessmentId}/evidence${query}`);
  }

  // ==========================================
  // Global Findings APIs
  // ==========================================

  public async getFindings(
    severity?: string,
    statusFilter?: string,
    limit: number = 100
  ): Promise<Finding[]> {
    const params = new URLSearchParams();
    if (severity && severity !== 'ALL') params.append('severity', severity);
    if (statusFilter && statusFilter !== 'ALL') params.append('status_filter', statusFilter);
    params.append('limit', limit.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<Finding[]>(`/api/findings${query}`);
  }

  public async getFinding(findingId: number): Promise<Finding> {
    return this.request<Finding>(`/api/findings/${findingId}`);
  }

  // ==========================================
  // Report Generation APIs
  // ==========================================

  public async generateReport(assessmentId: number, reportType: ReportFormat): Promise<Report> {
    return this.request<Report>(`/api/reports/${assessmentId}/generate`, {
      method: 'POST',
      body: JSON.stringify({ report_type: reportType }),
    });
  }

  public async getAssessmentReports(assessmentId: number): Promise<Report[]> {
    return this.request<Report[]>(`/api/reports/${assessmentId}`);
  }

  public async getAllReports(limit: number = 50): Promise<Report[]> {
    return this.request<Report[]>(`/api/reports?limit=${limit}`);
  }

  public getReportDownloadUrl(reportId: number): string {
    const base = this.baseUrl ? this.baseUrl : '';
    return `${base}/api/reports/download/${reportId}`;
  }

  public getReportViewUrl(reportId: number): string {
    const base = this.baseUrl ? this.baseUrl : '';
    return `${base}/api/reports/view/${reportId}`;
  }

  // ==========================================
  // World Monitor Dedicated APIs
  // ==========================================

  public async getWorldMonitorOverview(): Promise<import('../types/api').WorldMonitorOverview> {
    return this.request<import('../types/api').WorldMonitorOverview>('/api/worldmonitor/overview');
  }

  public async getWorldMonitorSourceAudit(): Promise<import('../types/api').WorldMonitorSourceAudit> {
    return this.request<import('../types/api').WorldMonitorSourceAudit>('/api/worldmonitor/source-audit');
  }

  // ==========================================
  // System Health APIs
  // ==========================================

  public async getSystemHealth(): Promise<SystemHealthResponse> {
    return this.request<SystemHealthResponse>('/health');
  }

  public async getDatabaseHealth(): Promise<DatabaseHealthResponse> {
    return this.request<DatabaseHealthResponse>('/health/database');
  }

  public async checkTargetLiveness(targetUrl: string): Promise<boolean> {
    try {
      await fetch(targetUrl, {
        method: 'GET',
        mode: 'no-cors',
      });
      return true;
    } catch {
      return false;
    }
  }
}

export const api = new ApiService();
export default api;


