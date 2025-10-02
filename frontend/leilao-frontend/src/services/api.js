const API_URL = import.meta.env.VITE_API_URL || '/api';

class ApiService {
  constructor() {
    this.baseURL = API_URL;
  }

  getHeaders(includeAuth = false) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = localStorage.getItem('token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(options.auth),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Erro na requisição');
      }

      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Auth
  async login(email, senha) {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ email, senha }),
    });
  }

  // Campanhas
  async getCampanhas(status = null) {
    const query = status ? `?status=${status}` : '';
    return this.request(`/campanhas${query}`);
  }

  async getCampanha(id) {
    return this.request(`/campanhas/${id}`);
  }

  async createCampanha(data) {
    return this.request('/campanhas', {
      method: 'POST',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async updateCampanha(id, data) {
    return this.request(`/campanhas/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async deleteCampanha(id) {
    return this.request(`/campanhas/${id}`, {
      method: 'DELETE',
      auth: true,
    });
  }

  // Categorias
  async getCategorias() {
    return this.request('/categorias');
  }

  async createCategoria(data) {
    return this.request('/categorias', {
      method: 'POST',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async updateCategoria(id, data) {
    return this.request(`/categorias/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async deleteCategoria(id) {
    return this.request(`/categorias/${id}`, {
      method: 'DELETE',
      auth: true,
    });
  }

  // Itens
  async getItens(campanhaId = null) {
    const query = campanhaId ? `?campanha_id=${campanhaId}` : '';
    return this.request(`/itens${query}`);
  }

  async getItem(id) {
    return this.request(`/itens/${id}`);
  }

  async createItem(data) {
    return this.request('/itens', {
      method: 'POST',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async updateItem(id, data) {
    return this.request(`/itens/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async deleteItem(id) {
    return this.request(`/itens/${id}`, {
      method: 'DELETE',
      auth: true,
    });
  }

  // Lances
  async getLances(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/lances?${params.toString()}`, { auth: true });
  }

  async createLance(data) {
    return this.request('/lances', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getUltimosLances() {
    return this.request('/lances/ultimos', { auth: true });
  }

  // Dashboard
  async getDashboard() {
    return this.request('/dashboard', { auth: true });
  }

  async getConfiguracoes() {
    return this.request('/configuracoes');
  }

  async updateConfiguracoes(data) {
    return this.request('/configuracoes', {
      method: 'POST',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async getAuditoria() {
    return this.request('/auditoria', { auth: true });
  }

  // Usuários
  async getUsuarios() {
    return this.request('/usuarios', { auth: true });
  }

  async createUsuario(data) {
    return this.request('/usuarios', {
      method: 'POST',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async updateUsuario(id, data) {
    return this.request(`/usuarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
      auth: true,
    });
  }

  async deleteUsuario(id) {
    return this.request(`/usuarios/${id}`, {
      method: 'DELETE',
      auth: true,
    });
  }
}

export default new ApiService();
