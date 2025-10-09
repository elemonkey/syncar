'use client'

import { useState, useEffect } from 'react';
import { Category, CategoryStats, CategoryImportResult } from '@/types/categories';
import toast from 'react-hot-toast';

interface CategoriesSectionProps {
  importerName: string;
}

const CategoriesSection = ({ importerName }: CategoriesSectionProps) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [stats, setStats] = useState<CategoryStats | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [selectedType, setSelectedType] = useState<'all' | 'medida' | 'fabricante'>('all');

  const loadCategories = async () => {
    if (categories.length > 0) return; // Solo cargar si no hay datos
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/categories/${importerName.toLowerCase()}`);
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

  const loadStats = async () => {
    try {
      const response = await fetch(`/api/v1/categories/${importerName.toLowerCase()}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleImportCategories = async () => {
    if (importerName.toLowerCase() !== 'noriega') {
      toast.error(`Importación no disponible para ${importerName}`);
      return;
    }

    const toastId = toast.loading('Importando categorías...');
    setIsImporting(true);

    try {
      const response = await fetch(`/api/v1/categories/${importerName.toLowerCase()}/import`, {
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
        setCategories([]);
        await loadCategories();
        await loadStats();
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

  const handleToggleExpand = () => {
    if (!isExpanded) {
      loadCategories();
      loadStats();
    }
    setIsExpanded(!isExpanded);
  };

  const filteredCategories = categories.filter(cat => 
    selectedType === 'all' || cat.category_type === selectedType
  );

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="mt-4 border-t border-gray-600 pt-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={handleToggleExpand}
            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors"
          >
            <span className={`transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
              ▶
            </span>
            <span className="font-medium">Categorías</span>
          </button>
          
          {stats && (
            <div className="flex gap-2 text-sm text-gray-400">
              <span className="bg-blue-900/50 px-2 py-1 rounded">
                📋 {stats.medida_count} medida
              </span>
              <span className="bg-green-900/50 px-2 py-1 rounded">
                🏭 {stats.fabricante_count} fabricante
              </span>
              <span className="bg-purple-900/50 px-2 py-1 rounded">
                📈 {stats.total_count} total
              </span>
            </div>
          )}
        </div>

        {importerName.toLowerCase() === 'noriega' && (
          <button
            onClick={handleImportCategories}
            disabled={isImporting}
            className="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white px-3 py-1 rounded text-sm transition-colors"
          >
            {isImporting ? '🔄 Importando...' : '🔄 Importar'}
          </button>
        )}
      </div>

      {isExpanded && (
        <div className="mt-3 space-y-3">
          {stats && (
            <div className="text-xs text-gray-500">
              Última actualización: {formatDate(stats.last_updated)}
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                selectedType === 'all' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Todas ({categories.length})
            </button>
            <button
              onClick={() => setSelectedType('medida')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                selectedType === 'medida' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              📋 Medida ({categories.filter(c => c.category_type === 'medida').length})
            </button>
            <button
              onClick={() => setSelectedType('fabricante')}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                selectedType === 'fabricante' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              🏭 Fabricante ({categories.filter(c => c.category_type === 'fabricante').length})
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-4 text-gray-400">
              <div className="animate-spin inline-block w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              <p className="mt-2">Cargando categorías...</p>
            </div>
          ) : filteredCategories.length > 0 ? (
            <div className="max-h-60 overflow-y-auto space-y-1">
              {filteredCategories.map((category) => (
                <div
                  key={category.id}
                  className="flex items-center justify-between p-2 bg-gray-700/50 rounded hover:bg-gray-700/70 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">
                      {category.category_type === 'medida' ? '📋' : '🏭'}
                    </span>
                    <span className="text-sm text-gray-200">{category.name}</span>
                  </div>
                  <span className="text-xs text-gray-500 font-mono">
                    {category.url_param.substring(0, 20)}
                    {category.url_param.length > 20 ? '...' : ''}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              {importerName.toLowerCase() === 'noriega' 
                ? 'No hay categorías. Haz clic en "Importar" para obtenerlas.'
                : 'Categorías no disponibles para este importador.'
              }
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CategoriesSection;