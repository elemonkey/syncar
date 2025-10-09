
'use client'

import { useState, useEffect, useCallback } from 'react';
import PageHeader from '@/components/layout/PageHeader';

interface Product {
  id: number;
  sku: string;
  name: string;
  price: number;
  importer_name: string;
  category: string;
  created_at: string;
}

const PAGE_SIZE = 15;

export default function CatalogoPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [hasNextPage, setHasNextPage] = useState(true);

  const fetchProducts = useCallback(async (currentPage: number, currentSearch: string) => {
    setIsLoading(true);
    try {
      const skip = (currentPage - 1) * PAGE_SIZE;
      const url = new URL(`/api/v1/products`, window.location.origin);
      url.searchParams.append('skip', skip.toString());
      url.searchParams.append('limit', PAGE_SIZE.toString());
      if (currentSearch) {
        url.searchParams.append('search', currentSearch);
      }

      const response = await fetch(url.toString());
      if (!response.ok) throw new Error('Error al cargar los productos');
      
      const data: Product[] = await response.json();
      setProducts(data);
      setHasNextPage(data.length === PAGE_SIZE);

    } catch (error) {
      console.error(error);
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const handler = setTimeout(() => {
      setPage(1); // Reset page to 1 on new search
      fetchProducts(1, searchTerm);
    }, 500); // Debounce de 500ms

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, fetchProducts]);

  useEffect(() => {
    fetchProducts(page, searchTerm);
  }, [page, fetchProducts]);

  const headerActions = (
    <input 
      type="text"
      placeholder="Buscar por SKU o nombre..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      className="w-80 bg-gray-700 border border-gray-600 rounded-md py-2 px-4 focus:ring-blue-500 focus:border-blue-500 text-white placeholder-gray-400"
    />
  );

  return (
    <div>
      <PageHeader
        title="Catálogo de Productos"
        actions={headerActions}
      />

      <div className="p-8">
        <div className="bg-gray-800/50 border border-gray-700 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-800">
            <tr>
              <th scope="col" className="py-3.5 px-4 text-left text-sm font-semibold">SKU</th>
              <th scope="col" className="py-3.5 px-4 text-left text-sm font-semibold">Nombre</th>
              <th scope="col" className="py-3.5 px-4 text-left text-sm font-semibold">Precio</th>
              <th scope="col" className="py-3.5 px-4 text-left text-sm font-semibold">Importador</th>
              <th scope="col" className="py-3.5 px-4 text-left text-sm font-semibold">Categoría</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {isLoading ? (
              <tr><td colSpan={5} className="text-center py-8 text-gray-400">Cargando...</td></tr>
            ) : products.length > 0 ? (
              products.map(product => (
                <tr key={product.id} className="hover:bg-gray-700/50">
                  <td className="whitespace-nowrap py-4 px-4 text-sm font-medium">{product.sku}</td>
                  <td className="whitespace-nowrap py-4 px-4 text-sm">{product.name}</td>
                  <td className="whitespace-nowrap py-4 px-4 text-sm">${product.price.toFixed(2)}</td>
                  <td className="whitespace-nowrap py-4 px-4 text-sm">{product.importer_name}</td>
                  <td className="whitespace-nowrap py-4 px-4 text-sm">{product.category}</td>
                </tr>
              ))
            ) : (
              <tr><td colSpan={5} className="text-center py-8 text-gray-400">No se encontraron productos.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      <div className="flex items-center justify-end gap-4 mt-6">
        <button 
          onClick={() => setPage(p => p - 1)}
          disabled={page <= 1 || isLoading}
          className="bg-gray-700 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          Anterior
        </button>
        <span className="text-gray-400">Página {page}</span>
        <button 
          onClick={() => setPage(p => p + 1)}
          disabled={!hasNextPage || isLoading}
          className="bg-gray-700 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          Siguiente
        </button>
        </div>
      </div>
    </div>
  )
}
