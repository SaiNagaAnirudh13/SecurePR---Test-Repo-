import { DataState } from '../components/DataState'
import { PageHeader } from '../components/PageHeader'
import { useResource } from '../hooks/useResource'
import { api } from '../services/api'

export function CustomersPage() {
  const customers = useResource(api.customers)
  return <><PageHeader title="Customers" description="Manage business accounts and fulfillment contacts." />
    <section className="panel"><div className="panel-heading"><div><h2>Customer accounts</h2><p>{customers.data?.length ?? 0} accounts</p></div></div>
      <DataState loading={customers.loading} error={customers.error} empty={!customers.data?.length} />
      {!!customers.data?.length && <div className="table-wrap"><table><thead><tr><th>COMPANY</th><th>ACCOUNT</th><th>CONTACT</th><th>EMAIL</th><th>PHONE</th><th>STATUS</th></tr></thead><tbody>
        {customers.data.map((customer) => <tr key={customer.id}><td><strong>{customer.company_name}</strong></td><td className="muted-cell">{customer.account_number}</td><td>{customer.contact_name}</td><td><a href={`mailto:${customer.email}`} className="text-link">{customer.email}</a></td><td>{customer.phone || '—'}</td><td><span className={`status-badge ${customer.is_active ? 'status-delivered' : 'status-cancelled'}`}>{customer.is_active ? 'active' : 'inactive'}</span></td></tr>)}
      </tbody></table></div>}
    </section>
  </>
}
