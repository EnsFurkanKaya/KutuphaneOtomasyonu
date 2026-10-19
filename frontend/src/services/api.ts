import { ApiError } from '../types';

const API_BASE = '/api';

class ApiClient {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('kutuphane_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('kutuphane_token', token);
    } else {
      localStorage.removeItem('kutuphane_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Accept': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include', // HttpOnly cookie için
    });

    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errBody = data.error || {
        code: 'ISTEK_HATASI',
        message: data.detail || 'Bir hata oluştu.',
      };
      const error: ApiError = {
        code: errBody.code || 'HATA',
        message: errBody.message || 'İşlem gerçekleştirilemedi.',
        details: errBody.details,
      };
      throw error;
    }

    return data as T;
  }

  // Auth API
  async login(payload: { email: string; password: string }) {
    const res = await this.request<{ access_token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    this.setToken(res.access_token);
    return res;
  }

  async register(payload: { student_number: string; full_name: string; email: string; password: string }) {
    return this.request<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getMe() {
    return this.request<any>('/auth/me');
  }

  // Kitap API
  async getBooks(params: Record<string, string | number | boolean | undefined | null> = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, String(val));
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any>(`/books${qs}`);
  }

  async getBook(id: number) {
    return this.request<any>(`/books/${id}`);
  }

  async createBook(payload: any) {
    return this.request<any>('/books', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateBook(id: number, payload: any) {
    return this.request<any>(`/books/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  async updateBookStock(id: number, total_copies: number) {
    return this.request<any>(`/books/${id}/stock`, {
      method: 'PATCH',
      body: JSON.stringify({ total_copies }),
    });
  }

  async deleteBook(id: number) {
    return this.request<any>(`/books/${id}`, {
      method: 'DELETE',
    });
  }

  // Kategori API
  async getCategories(includeInactive = false) {
    const qs = includeInactive ? '?include_inactive=true' : '';
    return this.request<any[]>(`/categories${qs}`);
  }

  async createCategory(payload: { name: string; description?: string }) {
    return this.request<any>('/categories', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateCategory(id: number, payload: { name?: string; description?: string; is_active?: boolean }) {
    return this.request<any>(`/categories/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  async deleteCategory(id: number) {
    return this.request<any>(`/categories/${id}`, {
      method: 'DELETE',
    });
  }

  // Ödünç API
  async borrowBook(bookId: number) {
    return this.request<any>('/loans', {
      method: 'POST',
      body: JSON.stringify({ book_id: bookId }),
    });
  }

  async returnLoan(loanId: number) {
    return this.request<any>(`/loans/${loanId}/return`, {
      method: 'POST',
    });
  }

  async getMyLoans(status: string = 'all', page = 1, pageSize = 20) {
    return this.request<any>(`/loans/my?status=${status}&page=${page}&page_size=${pageSize}`);
  }

  async getAllLoans(params: Record<string, string | number | undefined | null> = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, String(val));
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any>(`/loans${qs}`);
  }

  async getLoan(id: number) {
    return this.request<any>(`/loans/${id}`);
  }

  // Profil & Kullanıcı Yönetimi
  async updateProfile(fullName: string) {
    return this.request<any>('/users/me', {
      method: 'PATCH',
      body: JSON.stringify({ full_name: fullName }),
    });
  }

  async changePassword(currentPassword: string, newPassword: string) {
    return this.request<any>('/users/me/password', {
      method: 'PATCH',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  }

  async getUsers(params: Record<string, string | number | boolean | undefined | null> = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, String(val));
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any>(`/users${qs}`);
  }

  async adminUpdateUser(id: number, payload: { full_name?: string; is_active?: boolean }) {
    return this.request<any>(`/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  // Raporlar API
  async getDashboard() {
    return this.request<any>('/reports/dashboard');
  }

  async getOverdueReport(params: Record<string, string | number | undefined | null> = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, String(val));
      }
    });
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request<any>(`/reports/overdue${qs}`);
  }
}

export const api = new ApiClient();
