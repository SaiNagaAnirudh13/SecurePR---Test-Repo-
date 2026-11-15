import { useState } from 'react'
import { DataState } from '../components/DataState'
import { PageHeader } from '../components/PageHeader'
import { useResource } from '../hooks/useResource'
import { api } from '../services/api'

export function InventoryPage() {
  const [lowOnly, setLowOnly] = useState(false)
  const inventory = useResource(api.inventory)
  const rows = inventory.data?.filter((item) => !lowOnly || item.available_quantity <= item.reorder_point) ?? []
  return <><PageHeader title="Inventory" description="Monitor on-hand, reserved and available stock by warehouse." action={<label className="toggle-label"><input type="checkbox" checked={lowOnly} onChange={(event) => setLowOnly(event.target.checked)} />Low stock only</label>} />
    <section className="panel"><div className="panel-heading"><div><h2>Warehouse stock</h2><p>{rows.length} inventory records</p></div></div>
      <DataState loading={inventory.loading} error={inventory.error} empty={rows.length === 0} />
      {!inventory.loading && !inventory.error && rows.length > 0 && <div className="table-wrap"><table><thead><tr><th>PRODUCT</th><th>SKU</th><th>WAREHOUSE</th><th>ON HAND</th><th>RESERVED</th><th>AVAILABLE</th><th>REORDER AT</th></tr></thead><tbody>
        {rows.map((item) => <tr key={item.id}><td>{item.product_name}</td><td className="muted-cell">{item.sku}</td><td><span className="warehouse-code">{item.warehouse_code}</span></td><td>{item.quantity_on_hand}</td><td>{item.quantity_reserved}</td><td><strong className={item.available_quantity <= item.reorder_point ? 'stock-low' : 'stock-ok'}>{item.available_quantity}</strong></td><td>{item.reorder_point}</td></tr>)}
      </tbody></table></div>}
    </section>
  </>
}
