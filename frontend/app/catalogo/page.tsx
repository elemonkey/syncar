'use client'

import { useState, useEffect } from 'react'

interface Product {
  id: number
  sku: string
  name: string
  price: number
  stock: number
  category: string
  importer: string
  description?: string
  image_url?: string
  updated_at: string
}

interface Category {
  id: number
  name: string
  slug: string
  importer: string
}

export default function CatalogoPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedImporter, setSelectedImporter] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const importers = [
    { id: 'all', name: 'Todos', color: 'gray' },
    { id: 'noriega', name: 'Noriega', color: 'blue' },
    { id: 'alsacia', name: 'Alsacia', color: 'green' },
    { id: 'refax', name: 'Refax', color: 'purple' },
    { id: 'emasa', name: 'Emasa', color: 'orange' },
  ]

  useEffect(() => {
    loadData()
  }, [selectedImporter, selectedCategory])

  const loadData = async () => {
    setLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      
      // Cargar productos
      const productsParams = new URLSearchParams()
      if (selectedImporter !== 'all') productsParams.append('importer', selectedImporter)
      if (selectedCategory !== 'all') productsParams.append('category', selectedCategory)
      
      const productsResponse = await fetch(`${apiUrl}/products?${productsParams}`)
      if (productsResponse.ok) {
        const data = await productsResponse.json()
        setProducts(data.products || [])
      }

      // Cargar categorías
      const categoriesResponse = await fetch(`${apiUrl}/categories`)
      if (categoriesResponse.ok) {
        const data = await categoriesResponse.json()
        setCategories(data.categories || [])
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
    }).format(price)
  }

  const getImporterColor = (importer: string) => {
    const colors: Record<string, string> = {
      noriega: 'bg-blue-500',
      alsacia: 'bg-green-500',
      refax: 'bg-purple-500',
      emasa: 'bg-orange-500',
    }
    return colors[importer] || 'bg-gray-500'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 pt-8">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            📦 Catálogo de Productos
          </h1>
          <p className="text-gray-400">
            Explora y gestiona todos los productos importados
          </p>
        </div>

        {/* Filters */}
        <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🔍 Buscar
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por nombre o SKU..."
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Importer Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🏢 Importador
              </label>
              <select
                value={selectedImporter}
                onChange={(e) => setSelectedImporter(e.target.value)}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                {importers.map(imp => (
                  <option key={imp.id} value={imp.id}>{imp.name}</option>
                ))}
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                📂 Categoría
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="all">Todas</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.slug}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* View Mode & Stats */}
          <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-700">
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <span>Total: <span className="text-white font-bold">{filteredProducts.length}</span> productos</span>
              <span>•</span>
              <span>Categorías: <span className="text-white font-bold">{categories.length}</span></span>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                ⊞ Grid
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  viewMode === 'list'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                ☰ Lista
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mb-4"></div>
            <p className="text-gray-400">Cargando productos...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredProducts.length === 0 && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📦</div>
            <h3 className="text-2xl font-bold text-white mb-2">No hay productos</h3>
            <p className="text-gray-400 mb-6">
              {searchTerm
                ? 'No se encontraron productos que coincidan con tu búsqueda'
                : 'Aún no has importado productos. Ve a la sección de Importadores para comenzar.'}
            </p>
            {!searchTerm && (
              <a
                href="/importers"
                className="inline-block bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Ir a Importadores
              </a>
            )}
          </div>
        )}

        {/* Products Grid */}
        {!loading && filteredProducts.length > 0 && viewMode === 'grid' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 overflow-hidden hover:border-blue-500 transition-all group"
              >
                {/* Image */}
                <div className="aspect-square bg-gray-900 flex items-center justify-center overflow-hidden">
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                    />
                  ) : (
                    <span className="text-6xl">📦</span>
                  )}
                </div>

                {/* Content */}
                <div className="p-4">
                  {/* Importer Badge */}
                  <div className="flex items-center justify-between mb-2">
                    <span className={`${getImporterColor(product.importer)} text-white text-xs px-2 py-1 rounded-full font-medium`}>
                      {product.importer}
                    </span>
                    <span className="text-gray-500 text-xs">SKU: {product.sku}</span>
                  </div>

                  {/* Name */}
                  <h3 className="text-white font-medium mb-2 line-clamp-2 min-h-[3rem]">
                    {product.name}
                  </h3>

                  {/* Category */}
                  <p className="text-gray-400 text-sm mb-3">{product.category}</p>

                  {/* Price & Stock */}
                  <div className="flex items-center justify-between">
                    <span className="text-xl font-bold text-blue-400">
                      {formatPrice(product.price)}
                    </span>
                    <span className={`text-sm px-2 py-1 rounded ${
                      product.stock > 0
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {product.stock > 0 ? `Stock: ${product.stock}` : 'Sin stock'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Products List */}
        {!loading && filteredProducts.length > 0 && viewMode === 'list' && (
          <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-900/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Producto
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    SKU
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Categoría
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Importador
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Precio
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Stock
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredProducts.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-700/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gray-900 rounded-lg flex items-center justify-center">
                          {product.image_url ? (
                            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover rounded-lg" />
                          ) : (
                            <span>📦</span>
                          )}
                        </div>
                        <div className="text-white font-medium max-w-xs truncate">
                          {product.name}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-400 text-sm">{product.sku}</td>
                    <td className="px-6 py-4 text-gray-400 text-sm">{product.category}</td>
                    <td className="px-6 py-4">
                      <span className={`${getImporterColor(product.importer)} text-white text-xs px-2 py-1 rounded-full font-medium`}>
                        {product.importer}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-blue-400 font-bold">{formatPrice(product.price)}</td>
                    <td className="px-6 py-4">
                      <span className={`text-sm px-2 py-1 rounded ${
                        product.stock > 0
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {product.stock > 0 ? product.stock : 'Sin stock'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
