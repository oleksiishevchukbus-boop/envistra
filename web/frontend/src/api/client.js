const API_BASE = '/api';

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      // FastAPI's own validation (422) sends a list of {loc, msg}; the loader's
      // ConfigError (400) sends a string.
      const detail = Array.isArray(error.detail)
        ? error.detail.map((d) => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join('\n')
        : error.detail;
      throw new Error(detail || `HTTP error ${response.status}`);
    }

    return response.json();
  }

  // Simulations
  async listSimulations() {
    return this.request('/simulations');
  }

  async getSimulation(runId) {
    return this.request(`/simulations/${runId}`);
  }

  // `seed` pins the run so it can be reproduced; omit it for a fresh one.
  // run_config.json records whichever was used.
  async createSimulation(steps = 20, seed = null) {
    return this.request('/simulations', {
      method: 'POST',
      body: JSON.stringify(seed === null ? { steps } : { steps, seed }),
    });
  }

  // Rename (renames the results folder, keeping its timestamp) and/or set the
  // favourite flag. The returned run carries the new run_id after a rename.
  async updateSimulation(runId, data) {
    return this.request(`/simulations/${encodeURIComponent(runId)}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteSimulation(runId) {
    return this.request(`/simulations/${runId}`, {
      method: 'DELETE',
    });
  }

  // Get image URL
  getImageUrl(runId, imageName) {
    return `${API_BASE}/simulations/${runId}/images/${imageName}`;
  }

  // Get config download URL
  getConfigUrl(runId) {
    return `${API_BASE}/simulations/${runId}/config`;
  }

  // Get history download URL
  getHistoryUrl(runId) {
    return `${API_BASE}/simulations/${runId}/history`;
  }

  // Strategies
  async listStrategies() {
    return this.request('/strategies');
  }

  async getStrategy(name) {
    return this.request(`/strategies/${encodeURIComponent(name)}`);
  }

  async createStrategy(data) {
    return this.request('/strategies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateStrategy(name, data) {
    return this.request(`/strategies/${encodeURIComponent(name)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteStrategy(name) {
    return this.request(`/strategies/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    });
  }

  async cloneStrategy(sourceName, newName) {
    return this.request(`/strategies/${encodeURIComponent(sourceName)}/clone`, {
      method: 'POST',
      body: JSON.stringify({ new_name: newName }),
    });
  }

  async reloadStrategies() {
    return this.request('/strategies/reload', { method: 'POST' });
  }

  // Companies (agents). New surface: the roster used to be hardcoded in Python.
  async listCompanies() {
    return this.request('/companies');
  }

  async getCompany(name) {
    return this.request(`/companies/${encodeURIComponent(name)}`);
  }

  async createCompany(data) {
    return this.request('/companies', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCompany(name, data) {
    return this.request(`/companies/${encodeURIComponent(name)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCompany(name) {
    return this.request(`/companies/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    });
  }

  // The companies the workbooks contain — what a company's dataSource may name.
  // Empty when no workbooks are present.
  async listDataSources() {
    return this.request('/data-sources');
  }

  // Run-wide settings (config/simulation.json): chart dpi, size and format.
  async getSettings() {
    return this.request('/settings');
  }

  async updateSettings(data) {
    return this.request('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Environment
  async getEnvironment() {
    return this.request('/environment');
  }

  async updateEnvironment(data) {
    return this.request('/environment', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // There is no reset: the defaults it restored were deleted deliberately,
  // having drifted out of step with the JSON. `git checkout config/` is the
  // equivalent. Reload re-reads the files from disk.
  async reloadEnvironment() {
    return this.request('/environment/reload', { method: 'POST' });
  }
}

export const api = new ApiClient();
export default api;
