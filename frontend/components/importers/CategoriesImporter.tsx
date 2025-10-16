"use client";

import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import { Toast } from "@/components/Toast";

interface CategoriesImporterProps {
  importerId: string;
  onCategoriesImported: (categoryIds: string[]) => void;
}

export interface CategoriesImporterRef {
  startImport: () => void;
}

interface Category {
  id: string;
  name: string;
  external_id: string;
  url?: string;
  product_count?: number;
}

export const CategoriesImporter = forwardRef<
  CategoriesImporterRef,
  CategoriesImporterProps
>(({ importerId, onCategoriesImported }, ref) => {
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [loadingFromDB, setLoadingFromDB] = useState(true);
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error" | "info";
  } | null>(null);

  // Cargar categorías desde la BD al montar el componente
  const loadCategoriesFromDB = async () => {
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(
        `${apiUrl}/importers/categories?importer=${importerId}`
      );

      if (response.ok) {
        const data = await response.json();
        if (data.categories && data.categories.length > 0) {
          setCategories(data.categories);
          console.log(
            `✅ Cargadas ${data.categories.length} categorías desde la BD`
          );
        }
      }
    } catch (err) {
      console.error("Error cargando categorías desde BD:", err);
    } finally {
      setLoadingFromDB(false);
    }
  };

  // Cargar categorías al montar el componente
  useEffect(() => {
    loadCategoriesFromDB();
  }, [importerId]);

  // Exponer función para ser llamada desde el componente padre
  useImperativeHandle(ref, () => ({
    startImport: () => {
      handleImportCategories();
    },
  }));

  const handleImportCategories = async () => {
    setLoading(true);
    setError(null);

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      // 🔧 MODO DESARROLLO: Usar endpoint /dev/ para navegador visible
      const isDev = process.env.NODE_ENV === "development";
      const endpoint = isDev
        ? `${apiUrl}/dev/${importerId}/import-categories` // Navegador visible
        : `${apiUrl}/importers/${importerId}/import-categories`; // Celery background

      console.log(
        `🔧 Modo: ${
          isDev ? "DESARROLLO (navegador visible)" : "PRODUCCIÓN (background)"
        }`
      );
      console.log(`📡 Endpoint: ${endpoint}`);

      const response = await fetch(endpoint, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || "Error al iniciar importación de categorías"
        );
      }

      const data = await response.json();
      console.log("✅ Respuesta:", data);

      if (data.success) {
        // Recargar categorías desde la BD
        await loadCategoriesFromDB();

        const count = data.saved || data.total || 0;
        setToast({
          type: "success",
          message: `Importación completada!\n\nSe guardaron ${count} categorías en la base de datos\n\n${
            data.message || ""
          }`,
        });
      } else if (data.job_id) {
        // Modo producción: job en background
        setToast({
          type: "info",
          message: `Importación iniciada en background\n\nJob ID: ${data.job_id}\n\n🔍 El proceso se ejecuta en segundo plano.`,
        });
        // TODO: Implementar polling del job status
      } else {
        throw new Error("Respuesta inesperada del servidor");
      }
    } catch (err) {
      console.error("❌ Error:", err);
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const selectAll = () => {
    if (selectedIds.size === categories.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(categories.map((c) => c.id)));
    }
  };

  const handleContinue = () => {
    onCategoriesImported(Array.from(selectedIds));
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
          duration={5000}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Importar Categorías</h2>
          <p className="text-gray-400 mt-1">
            Importa las categorías de{" "}
            <span className="text-blue-400 font-medium">{importerId}</span>
          </p>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mb-4"></div>
          <p className="text-gray-400">
            Importando categorías de {importerId}...
          </p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">❌ {error}</p>
        </div>
      )}

      {/* Categories List */}
      {!loading && categories.length > 0 && (
        <div className="space-y-4">
          {/* Actions */}
          <div className="flex items-center justify-between bg-gray-700/50 p-4 rounded-lg">
            <div className="text-white">
              <span className="font-medium">{selectedIds.size}</span> de{" "}
              <span className="font-medium">{categories.length}</span>{" "}
              categorías seleccionadas
            </div>
            <div className="flex space-x-2">
              <button
                onClick={selectAll}
                className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg transition-colors"
              >
                {selectedIds.size === categories.length
                  ? "Deseleccionar todas"
                  : "Seleccionar todas"}
              </button>
              <button
                onClick={handleContinue}
                disabled={selectedIds.size === 0}
                className={`
                  px-6 py-2 rounded-lg font-medium transition-colors
                  ${
                    selectedIds.size > 0
                      ? "bg-blue-500 hover:bg-blue-600 text-white"
                      : "bg-gray-600 text-gray-400 cursor-not-allowed"
                  }
                `}
              >
                Continuar →
              </button>
            </div>
          </div>

          {/* Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => (
              <div
                key={category.id}
                onClick={() => toggleCategory(category.id)}
                className={`
                  p-4 rounded-lg border-2 cursor-pointer transition-all
                  ${
                    selectedIds.has(category.id)
                      ? "border-blue-500 bg-blue-500/10"
                      : "border-gray-700 bg-gray-800/50 hover:border-gray-600"
                  }
                `}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-white font-medium flex-1">
                    {category.name}
                  </h3>
                  <div
                    className={`
                    w-6 h-6 rounded border-2 flex items-center justify-center
                    ${
                      selectedIds.has(category.id)
                        ? "border-blue-500 bg-blue-500"
                        : "border-gray-600"
                    }
                  `}
                  >
                    {selectedIds.has(category.id) && (
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    )}
                  </div>
                </div>
                <p className="text-gray-400 text-sm">
                  ID: {category.external_id}
                </p>
                {category.product_count !== undefined && (
                  <p className="text-gray-500 text-sm mt-1">
                    📦 {category.product_count} productos
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && categories.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📋</div>
          <p className="text-gray-400 text-lg">
            Haz clic en "Importar Categorías" para comenzar
          </p>
        </div>
      )}
    </div>
  );
});

CategoriesImporter.displayName = "CategoriesImporter";
