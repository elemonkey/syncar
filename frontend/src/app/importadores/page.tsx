'use client'

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Category, CategoryStats, CategoryImportResult } from '@/types/categories';
import PageHeader from '@/components/layout/PageHeader';

const IMPORTERS = [
  { id: 'alsacia', name: 'Alsacia', available: false },
  { id: 'refax', name: 'Refax', available: false },
  { id: 'noriega', name: 'Noriega', available: true },
  { id: 'emasa', name: 'Emasa', available: false }
];

export default function ImportadoresPage() {
  const [activeTab, setActiveTab] = useState('noriega');
  const [categories, setCategories] = useState<Category[]>([]);
  const [stats, setStats] = useState<CategoryStats | null>(null);
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'medida' | 'fabricante'>('all');

  const activeImporter = IMPORTERS.find(imp => imp.id === activeTab);

  // Filtrar categorías según el filtro seleccionado
  const filteredCategories = categories.filter(category => 
    categoryFilter === 'all' || category.category_type === categoryFilter
  );

  // Cargar categorías cuando cambia el tab
  const loadCategories = async (importerId: string) => {
    if (!IMPORTERS.find(imp => imp.id === importerId)?.available) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/categories/${importerId}`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Cargar estadísticas
  const loadStats = async (importerId: string) => {
    if (!IMPORTERS.find(imp => imp.id === importerId)?.available) return;
    
    try {
      const response = await fetch(`/api/v1/categories/${importerId}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  // Scraping de categorías
  const handleImportCategories = async () => {
    if (!activeImporter?.available) {
      toast.error(`Importación no disponible para ${activeImporter?.name}`);
      return;
    }

    const toastId = toast.loading('Importando categorías...');
    setIsImporting(true);

    try {
      const response = await fetch(`/api/v1/categories/${activeTab}/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Error en la importación');
      }

      const result: CategoryImportResult = await response.json();
      
      if (result.success) {
        toast.success(
          `✅ Importación exitosa!\n📊 ${result.total_imported} categorías importadas\n💾 ${result.total_saved_db} guardadas en BD\n⏱️ ${result.execution_time}`,
          { id: toastId, duration: 6000 }
        );
        
        // Recargar datos
        await loadCategories(activeTab);
        await loadStats(activeTab);
        setSelectedCategories(new Set());
      } else {
        toast.error(`Error: ${result.message}`, { id: toastId });
      }
    } catch (error) {
      console.error('Error importing categories:', error);
      toast.error('Error durante la importación', { id: toastId });
    } finally {
      setIsImporting(false);
    }
  };

  // Cambiar tab
  const handleTabChange = (importerId: string) => {
    setActiveTab(importerId);
    setCategories([]);
    setStats(null);
    setSelectedCategories(new Set());
    
    if (IMPORTERS.find(imp => imp.id === importerId)?.available) {
      loadCategories(importerId);
      loadStats(importerId);
    }
  };

  // Seleccionar/deseleccionar categoría
  const toggleCategorySelection = (categoryId: string) => {
    const newSelection = new Set(selectedCategories);
    if (newSelection.has(categoryId)) {
      newSelection.delete(categoryId);
    } else {
      newSelection.add(categoryId);
    }
    setSelectedCategories(newSelection);
  };

  // Seleccionar todas las categorías
  const selectAllCategories = () => {
    const allIds = categories.map(cat => cat.id.toString());
    setSelectedCategories(new Set(allIds));
  };

  // Deseleccionar todas las categorías
  const clearSelection = () => {
    setSelectedCategories(new Set());
  };

  useEffect(() => {
    // Cargar datos del tab inicial
    if (activeImporter?.available) {
      loadCategories(activeTab);
      loadStats(activeTab);
    }
  }, []);

  // Crear elementos para el header
  const headerStats = stats ? (
    <>
      <span className="bg-blue-900/50 px-2 py-1 rounded text-blue-300">
        📋 {stats.medida_count} medida
      </span>
      <span className="bg-green-900/50 px-2 py-1 rounded text-green-300">
        🏭 {stats.fabricante_count} fabricante  
      </span>
      <span className="bg-purple-900/50 px-2 py-1 rounded text-purple-300">
        📈 {stats.total_count} total
      </span>
    </>
  ) : null;

  const headerActions = activeImporter?.available ? (
    <>
      <button
        onClick={handleImportCategories}
        disabled={isImporting}
        className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-md transition-colors"
      >
        {isImporting ? '🔄 Importando...' : '🔄 Importar Categorías'}
      </button>
      
      {selectedCategories.size > 0 && (
        <button
          onClick={() => {
            toast.success(`Importando productos de ${selectedCategories.size} categorías seleccionadas...`);
            // TODO: Implementar importación de productos
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          📦 Importar Productos ({selectedCategories.size})
        </button>
      )}
    </>
  ) : null;

  return (
    <div>
      <PageHeader
        title="Importar Categorías"
        tabs={IMPORTERS}
        activeTab={activeTab}
        onTabChange={handleTabChange}
        stats={headerStats}
        actions={headerActions}
      />

      
      {/* Contenido del tab activo */}
      <div className="p-8">
        {activeImporter?.available ? (
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            {/* Contenido de categorías */}

            {/* Filtros y acciones de selección */}
            {categories.length > 0 && (
              <div className="flex justify-between items-center mb-4 p-3 bg-gray-700/30 rounded-md">
                <div className="flex gap-3 items-center">
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCategoryFilter('all')}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        categoryFilter === 'all'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                      }`}
                    >
                      Todas ({categories.length})
                    </button>
                    <button
                      onClick={() => setCategoryFilter('medida')}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        categoryFilter === 'medida'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                      }`}
                    >
                      📋 Medida ({categories.filter(c => c.category_type === 'medida').length})
                    </button>
                    <button
                      onClick={() => setCategoryFilter('fabricante')}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        categoryFilter === 'fabricante'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                      }`}
                    >
                      🏭 Fabricante ({categories.filter(c => c.category_type === 'fabricante').length})
                    </button>
                  </div>
                  
                  <div className="h-4 w-px bg-gray-600"></div>
                  
                  <button
                    onClick={selectAllCategories}
                    className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    Seleccionar Todo
                  </button>
                  <button
                    onClick={clearSelection}
                    className="text-sm text-gray-400 hover:text-gray-300 transition-colors"
                  >
                    Limpiar Selección
                  </button>
                </div>
                <div className="text-sm text-gray-400">
                  {selectedCategories.size} de {filteredCategories.length} seleccionadas
                </div>
              </div>
            )}

            {/* Tabla de categorías */}
            <div>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  <span className="ml-3 text-gray-400">Cargando categorías...</span>
                </div>
              ) : categories.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  <p>No hay categorías disponibles.</p>
                  <p className="text-sm mt-2">Haz clic en "Importar Categorías" para obtenerlas.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-separate border-spacing-0 rounded-lg overflow-hidden">
                    <thead>
                      <tr className="bg-gray-700">
                        <th className="border-b border-gray-600 px-4 py-3 text-left text-sm font-medium text-gray-300 w-12">
                          <input
                            type="checkbox"
                            checked={filteredCategories.length > 0 && filteredCategories.every(cat => selectedCategories.has(cat.id.toString()))}
                            onChange={() => {
                              const allFilteredSelected = filteredCategories.every(cat => selectedCategories.has(cat.id.toString()));
                              if (allFilteredSelected) {
                                // Deseleccionar todas las filtradas
                                const newSelection = new Set(selectedCategories);
                                filteredCategories.forEach(cat => newSelection.delete(cat.id.toString()));
                                setSelectedCategories(newSelection);
                              } else {
                                // Seleccionar todas las filtradas
                                const newSelection = new Set(selectedCategories);
                                filteredCategories.forEach(cat => newSelection.add(cat.id.toString()));
                                setSelectedCategories(newSelection);
                              }
                            }}
                            className="rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
                          />
                        </th>
                        <th className="border-b border-gray-600 px-4 py-3 text-left text-sm font-medium text-gray-300">
                          Tipo
                        </th>
                        <th className="border-b border-gray-600 px-4 py-3 text-left text-sm font-medium text-gray-300">
                          Nombre de Categoría
                        </th>
                        <th className="border-b border-gray-600 px-4 py-3 text-left text-sm font-medium text-gray-300">
                          Parámetro URL
                        </th>
                        <th className="border-b border-gray-600 px-4 py-3 text-left text-sm font-medium text-gray-300">
                          Última Actualización
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-gray-800/50">
                      {filteredCategories.map((category, index) => (
                        <tr 
                          key={category.id}
                          className={`transition-colors hover:bg-gray-700/50 ${
                            selectedCategories.has(category.id.toString()) ? 'bg-blue-900/20' : ''
                          }`}
                        >
                          <td className={`px-4 py-3 ${index !== categories.length - 1 ? 'border-b border-gray-700' : ''}`}>
                            <input
                              type="checkbox"
                              checked={selectedCategories.has(category.id.toString())}
                              onChange={() => toggleCategorySelection(category.id.toString())}
                              className="rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
                            />
                          </td>
                          <td className={`px-4 py-3 ${index !== filteredCategories.length - 1 ? 'border-b border-gray-700' : ''}`}>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              category.category_type === 'medida' 
                                ? 'bg-blue-900/50 text-blue-300' 
                                : 'bg-green-900/50 text-green-300'
                            }`}>
                              {category.category_type === 'medida' ? '📋' : '🏭'} {category.category_type}
                            </span>
                          </td>
                          <td className={`px-4 py-3 text-gray-300 font-medium ${index !== filteredCategories.length - 1 ? 'border-b border-gray-700' : ''}`}>
                            {category.name}
                          </td>
                          <td className={`px-4 py-3 text-gray-400 text-sm font-mono ${index !== filteredCategories.length - 1 ? 'border-b border-gray-700' : ''}`}>
                            {category.url_param}
                          </td>
                          <td className={`px-4 py-3 text-gray-400 text-sm ${index !== filteredCategories.length - 1 ? 'border-b border-gray-700' : ''}`}>
                            {category.created_at ? new Date(category.created_at).toLocaleString('es-ES', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit'
                            }) : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <div className="text-center text-gray-400 py-12">
              <h3 className="text-xl font-medium mb-2">{activeImporter?.name}</h3>
              <p>Este importador no está disponible aún.</p>
              <p className="text-sm mt-2">Será implementado en futuras versiones.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}