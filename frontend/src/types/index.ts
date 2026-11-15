export interface User {
  id: string
  email: string
  full_name: string
  role: string
}

export interface Customer {
  id: string
  account_number: string
  company_name: string
  contact_name: string
  email: string
  phone: string | null
  billing_address: string
  shipping_address: string
  is_active: boolean
}

export interface Product {
  id: string
  sku: string
  name: string
  description: string
  category: string
  unit_price: string
  currency: string
  is_active: boolean
}

export interface InventoryItem {
  id: string
  product_id: string
  sku: string
  product_name: string
  warehouse_code: string
  quantity_on_hand: number
  quantity_reserved: number
  available_quantity: number
  reorder_point: number
}

export interface OrderItem {
  id: string
  product_id: string
  sku: string
  product_name: string
  quantity: number
  unit_price: string
  line_total: string
}

export interface Shipment {
  id: string
  carrier: string
  tracking_number: string | null
  status: string
  shipped_at: string | null
  delivered_at: string | null
}

export interface Order {
  id: string
  order_number: string
  customer_id: string
  status: string
  currency: string
  subtotal: string
  tax_amount: string
  total_amount: string
  notes: string
  created_at: string
  items: OrderItem[]
  shipment: Shipment | null
}

export interface SalesSummary {
  order_count: number
  gross_sales: string
  average_order_value: string
  status_counts: Record<string, number>
  low_stock_items: number
}
