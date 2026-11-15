import type { Customer, InventoryItem, Order, Product, SalesSummary, User } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('eomp.accessToken')
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  })
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string }
    throw new ApiError(body.detail ?? `Request failed (${response.status})`, response.status)
  }
  return response.json() as Promise<T>
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; user: User }>('/auth/token', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<User>('/auth/me'),
  customers: () => request<Customer[]>('/customers?limit=100'),
  products: () => request<Product[]>('/products?limit=100'),
  inventory: () => request<InventoryItem[]>('/inventory'),
  orders: () => request<Order[]>('/orders?limit=100'),
  salesSummary: () => request<SalesSummary>('/reports/sales-summary'),
  createOrder: (customerId: string, productId: string, quantity: number) =>
    request<Order>('/orders', {
      method: 'POST',
      body: JSON.stringify({
        customer_id: customerId,
        items: [{ product_id: productId, quantity }],
      }),
    }),
}
