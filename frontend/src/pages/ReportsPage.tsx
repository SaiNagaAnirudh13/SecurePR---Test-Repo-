import { ArrowDownRight, ArrowUpRight } from 'lucide-react'
import { DataState } from '../components/DataState'
import { PageHeader } from '../components/PageHeader'
import { StatusBadge } from '../components/StatusBadge'
import { useResource } from '../hooks/useResource'
import { api } from '../services/api'
import { formatCurrency } from '../utils/format'

export function ReportsPage() {
  const report = useResource(api.salesSummary)
  const statuses = Object.entries(report.data?.status_counts ?? {})
  return <><PageHeader title="Reports" description="Sales performance, order mix and stock health." />
    <DataState loading={report.loading} error={report.error} empty={!report.data} />
    {report.data && <><section className="report-highlight"><div><span className="eyebrow">GROSS ORDER VALUE</span><h2>{formatCurrency(report.data.gross_sales)}</h2><p>Across {report.data.order_count} active orders</p></div><div className="report-decoration"><ArrowUpRight size={34} /></div></section>
      <section className="metric-grid report-metrics"><article className="metric-card"><span className="metric-label">Average order value</span><strong>{formatCurrency(report.data.average_order_value)}</strong><span className="metric-caption">Per active order</span></article><article className="metric-card"><span className="metric-label">Low stock records</span><strong>{report.data.low_stock_items}</strong><span className="metric-caption">{report.data.low_stock_items ? 'Review replenishment needs' : 'All stock above thresholds'}</span></article></section>
      <section className="panel"><div className="panel-heading"><div><h2>Order status distribution</h2><p>Current lifecycle counts</p></div></div><div className="status-list">{statuses.map(([status, count]) => <div className="status-row" key={status}><StatusBadge status={status} /><div className="status-bar"><span style={{ width: `${Math.min(100, (count / Math.max(report.data!.order_count, 1)) * 100)}%` }} /></div><strong>{count}</strong>{status === 'cancelled' ? <ArrowDownRight className="status-trend down" size={16} /> : <ArrowUpRight className="status-trend" size={16} />}</div>)}</div></section>
    </>}
  </>
}
