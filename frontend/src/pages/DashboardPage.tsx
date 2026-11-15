import { ArrowUpRight, CircleAlert, ClipboardList, DollarSign, PackageCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { DataState } from '../components/DataState'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'
import { useResource } from '../hooks/useResource'
import { api } from '../services/api'
import { formatCurrency, formatDate } from '../utils/format'

export function DashboardPage() {
  const orders = useResource(api.orders)
  const summary = useResource(api.salesSummary)
  const orderData = orders.data ?? []

  return (
    <>
      <PageHeader title="Good morning" description="Here is the latest operational overview for your business." action={<span className="date-label">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</span>} />
      {summary.error && <div className="inline-error">{summary.error}</div>}
      <section className="metric-grid">
        <article className="metric-card"><div className="metric-icon blue"><ClipboardList size={19} /></div><span className="metric-label">Active orders</span><strong>{summary.data?.order_count ?? '—'}</strong><span className="metric-caption">Excludes cancelled orders</span></article>
        <article className="metric-card"><div className="metric-icon green"><DollarSign size={19} /></div><span className="metric-label">Gross sales</span><strong>{summary.data ? formatCurrency(summary.data.gross_sales) : '—'}</strong><span className="metric-caption">All-time order value</span></article>
        <article className="metric-card"><div className="metric-icon amber"><CircleAlert size={19} /></div><span className="metric-label">Low stock items</span><strong>{summary.data?.low_stock_items ?? '—'}</strong><span className="metric-caption">At or below reorder point</span></article>
        <article className="metric-card"><div className="metric-icon violet"><PackageCheck size={19} /></div><span className="metric-label">Average order value</span><strong>{summary.data ? formatCurrency(summary.data.average_order_value) : '—'}</strong><span className="metric-caption">Across active orders</span></article>
      </section>
      <section className="panel">
        <div className="panel-heading"><div><h2>Recent orders</h2><p>Latest activity across your customer accounts</p></div><Link className="text-link" to="/orders">View all <ArrowUpRight size={15} /></Link></div>
        <DataState loading={orders.loading} error={orders.error} empty={orderData.length === 0} />
        {!orders.loading && !orders.error && orderData.length > 0 && <OrderTable orders={orderData.slice(0, 6)} />}
      </section>
    </>
  )
}

function OrderTable({ orders }: { orders: Awaited<ReturnType<typeof api.orders>> }) {
  return <div className="table-wrap"><table><thead><tr><th>ORDER</th><th>CUSTOMER</th><th>DATE</th><th>ITEMS</th><th>TOTAL</th><th>STATUS</th></tr></thead><tbody>
    {orders.map((order) => <tr key={order.id}><td><Link className="order-link" to={`/orders?id=${order.id}`}>{order.order_number}</Link></td><td>Customer {order.customer_id.slice(0, 8)}</td><td>{formatDate(order.created_at)}</td><td>{order.items.length} line{order.items.length === 1 ? '' : 's'}</td><td className="amount">{formatCurrency(order.total_amount, order.currency)}</td><td><StatusBadge status={order.status} /></td></tr>)}
  </tbody></table></div>
}
