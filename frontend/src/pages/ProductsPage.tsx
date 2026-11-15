import { DataState } from '../components/DataState'
import { PageHeader } from '../components/PageHeader'
import { useResource } from '../hooks/useResource'
import { api } from '../services/api'
import { formatCurrency } from '../utils/format'

export function ProductsPage() {
  const products = useResource(api.products)
  return <><PageHeader title="Products" description="Browse your active catalog, pricing and product classifications." />
    <section className="panel"><div className="panel-heading"><div><h2>Product catalog</h2><p>{products.data?.length ?? 0} products</p></div></div>
      <DataState loading={products.loading} error={products.error} empty={!products.data?.length} />
      {!!products.data?.length && <div className="product-grid">{products.data.map((product) => <article className="product-card" key={product.id}><div className="product-art"><span>{product.category.slice(0, 1).toUpperCase()}</span></div><div className="product-details"><span className="eyebrow">{product.category}</span><h3>{product.name}</h3><p>{product.description || 'No description provided.'}</p><div className="product-meta"><span className="sku-tag">{product.sku}</span><strong>{formatCurrency(product.unit_price, product.currency)}</strong></div></div></article>)}</div>}
    </section>
  </>
}
