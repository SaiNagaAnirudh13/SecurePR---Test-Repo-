import { useMemo, useState, type FormEvent } from 'react'
import { Plus } from 'lucide-react'
import { DataState } from '../components/DataState'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'
import { useResource } from '../hooks/useResource'
import { api } from '../services/api'
import { formatCurrency, formatDate } from '../utils/format'

export function OrdersPage() {
  const orders = useResource(api.orders)
  const customers = useResource(api.customers)
  const products = useResource(api.products)
  const [showForm, setShowForm] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [customerId, setCustomerId] = useState('')
  const [productId, setProductId] = useState('')
  const [quantity, setQuantity] = useState(1)
  const sortedOrders = useMemo(() => [...(orders.data ?? [])].sort((a, b) => b.created_at.localeCompare(a.created_at)), [orders.data])

  async function createOrder(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    try {
      await api.createOrder(customerId, productId, quantity)
      setShowForm(false)
      await orders.refresh()
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Unable to create order')
    }
  }

  return (
    <>
      <PageHeader title="Orders" description="Create, track and manage customer orders." action={<button className="primary-button" onClick={() => setShowForm((value) => !value)}><Plus size={17} />New order</button>} />
      {showForm && <form className="create-order-form panel" onSubmit={createOrder}>
        <div className="panel-heading"><div><h2>Create order</h2><p>Inventory is reserved when the order is confirmed.</p></div><button type="button" className="quiet-button" onClick={() => setShowForm(false)}>Close</button></div>
        <div className="form-grid">
          <label>Customer<select required value={customerId} onChange={(event) => setCustomerId(event.target.value)}><option value="">Select a customer</option>{(customers.data ?? []).map((customer) => <option key={customer.id} value={customer.id}>{customer.company_name}</option>)}</select></label>
          <label>Product<select required value={productId} onChange={(event) => setProductId(event.target.value)}><option value="">Select a product</option>{(products.data ?? []).map((product) => <option key={product.id} value={product.id}>{product.name} · {formatCurrency(product.unit_price)}</option>)}</select></label>
          <label>Quantity<input type="number" min={1} max={10000} required value={quantity} onChange={(event) => setQuantity(Number(event.target.value))} /></label>
        </div>
        {(customers.error || products.error || formError) && <div role="alert" className="form-error">{formError ?? customers.error ?? products.error}</div>}
        <button className="primary-button" type="submit" disabled={!customers.data?.length || !products.data?.length}>Create order</button>
      </form>}
      <section className="panel">
        <div className="panel-heading"><div><h2>All orders</h2><p>{orders.data?.length ?? 0} records in this view</p></div></div>
        <DataState loading={orders.loading} error={orders.error} empty={sortedOrders.length === 0} />
        {!orders.loading && !orders.error && sortedOrders.length > 0 && <div className="table-wrap"><table><thead><tr><th>ORDER</th><th>CUSTOMER ID</th><th>CREATED</th><th>LINES</th><th>FULFILLMENT</th><th>SUBTOTAL</th><th>TOTAL</th><th>STATUS</th></tr></thead><tbody>
          {sortedOrders.map((order) => <tr key={order.id}><td className="order-link">{order.order_number}</td><td className="muted-cell">{order.customer_id.slice(0, 8)}…</td><td>{formatDate(order.created_at)}</td><td>{order.items.length}</td><td>{[...new Set(order.items.map((item) => item.warehouse_code).filter((code): code is string => code !== null))].join(', ') || '—'}</td><td>{formatCurrency(order.subtotal, order.currency)}</td><td className="amount">{formatCurrency(order.total_amount, order.currency)}</td><td><StatusBadge status={order.status} /></td></tr>)}
        </tbody></table></div>}
      </section>
    </>
  )
}
