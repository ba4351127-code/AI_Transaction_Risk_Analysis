import api from './api';

export const transactionService = {
  /**
   * Evaluate a financial transaction in real-time.
   * Dual-mode payload: accepts simple 5-field inputs or advanced analyst payloads.
   * @param {Object} data - TransactionAnalyzeRequest
   * @returns {Promise<Object>} RiskAssessmentResponse
   */
  analyzeTransaction: async (data) => {
    return await api.post('/transactions/analyze', data);
  },

  /**
   * Retrieve paginated transaction audit history.
   * @param {Object} params - { page, limit, risk_category, min_score }
   * @returns {Promise<Object>} { page, limit, records: [...] }
   */
  getTransactionHistory: async (params = {}) => {
    return await api.get('/transactions/history', { params });
  },

  /**
   * Run What-If simulation comparing baseline vs modified scenario.
   * @param {Object} scenarioData - SimulatorScenarioRequest
   * @returns {Promise<Object>} SimulatorComparisonResponse
   */
  evaluateSimulatorScenario: async (scenarioData) => {
    return await api.post('/simulator/evaluate', scenarioData);
  },

  /**
   * Retrieve real-time security alerts triage feed.
   * @param {Object} params - { status_filter, limit }
   * @returns {Promise<Array>} List of security alerts
   */
  getAlertsFeed: async (params = {}) => {
    return await api.get('/alerts/feed', { params });
  },

  /**
   * Update an alert's status (OPEN -> ACKNOWLEDGED -> RESOLVED / FALSE_POSITIVE)
   * @param {string} alertId
   * @param {Object} payload - { status, analyst_notes }
   * @returns {Promise<Object>}
   */
  updateAlertStatus: async (alertId, payload) => {
    return await api.patch(`/alerts/${alertId}/status`, payload);
  },

  /**
   * Retrieve official model evaluation benchmarks from ML training pipeline.
   * @returns {Promise<Object>} evaluation_metrics.json content
   */
  getModelMetrics: async () => {
    return await api.get('/intelligence/metrics');
  },

  /**
   * Retrieve trained XGBoost feature importance distribution.
   * @returns {Promise<Object>}
   */
  getGlobalFeatures: async () => {
    return await api.get('/intelligence/global-features');
  },

  /**
   * Upload CSV batch file for non-blocking risk scoring.
   * @param {FormData} formData
   * @returns {Promise<Object>} { job_id, message, filename }
   */
  uploadBulkTransactions: async (formData) => {
    return await api.post('/bulk/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Query status of a bulk processing batch job.
   * @param {string} jobId
   * @returns {Promise<Object>}
   */
  getBulkJobStatus: async (jobId) => {
    return await api.get(`/bulk/job/${jobId}`);
  },

  /**
   * List recent bulk upload jobs.
   * @returns {Promise<Array>}
   */
  getBulkJobs: async () => {
    return await api.get('/bulk/jobs');
  },

  /**
   * Check backend server health status.
   * @returns {Promise<Object>}
   */
  getHealth: async () => {
    const res = await fetch('/health');
    if (!res.ok) throw new Error(`Health check returned status ${res.status}`);
    return await res.json();
  },

  /**
   * Helpers for export URLs and authenticated CSV download.
   */
  getCsvExportUrl: () => '/api/v1/reports/export/csv',
  getPdfExportUrl: (transactionId) => `/api/v1/reports/export/pdf/${transactionId}`,
  downloadCsv: async () => {
    const data = await api.get('/reports/export/csv', {
      responseType: 'blob'
    });
    const blob = new Blob([data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transaction_risk_audit_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
  downloadPdf: async (transactionRef) => {
    const data = await api.get(`/reports/export/pdf/${transactionRef}`, {
      responseType: 'blob'
    });
    const blob = new Blob([data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `risk_report_${transactionRef}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
};

export default transactionService;
