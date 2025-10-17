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
  selected?: boolean;
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

  // Cargar categorías y selección desde la BD al montar el componente
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

          // Cargar categorías seleccionadas previamente
          const selectedCategoryIds = data.categories
            .filter((cat: Category) => cat.selected)
            .map((cat: Category) => cat.id);

          setSelectedIds(new Set(selectedCategoryIds));

          console.log(
            `✅ Cargadas ${data.categories.length} categorías desde la BD (${selectedCategoryIds.length} seleccionadas)`
          );
        }
      }
    } catch (err) {
      console.error("Error cargando categorías desde BD:", err);
    } finally {
      setLoadingFromDB(false);
    }
  };

  // Cargar categorías al montar el componente o cuando cambia el importador
  useEffect(() => {
    setLoadingFromDB(true);
    setCategories([]);
    setSelectedIds(new Set());
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

  const handleSaveSelection = async () => {
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      const response = await fetch(
        `${apiUrl}/importers/${importerId}/categories/selection`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            category_ids: Array.from(selectedIds),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Error al guardar selección");
      }

      setToast({
        type: "success",
        message: `Selección guardada!\n\n${selectedIds.size} categorías seleccionadas para ${importerId}`,
      });
    } catch (err) {
      setToast({
        type: "error",
        message: "Error al guardar la selección de categorías",
      });
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) {
      setToast({
        type: "error",
        message: "No hay categorías seleccionadas para eliminar",
      });
      return;
    }

    // Confirmar eliminación
    if (!confirm(`¿Estás seguro de eliminar ${selectedIds.size} categorías?\n\nEsta acción no se puede deshacer.`)) {
      return;
    }

    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      // Obtener importer_id actual
      const importerResponse = await fetch(`${apiUrl}/importers`);
      const importersData = await importerResponse.json();
      
      // El endpoint retorna directamente un array de importers
      const currentImporter = importersData.find(
        (imp: any) => imp.name.toLowerCase() === importerId.toLowerCase()
      );

      if (!currentImporter) {
        throw new Error("Importador no encontrado");
      }

      const response = await fetch(`${apiUrl}/categories/delete-multiple`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          category_ids: Array.from(selectedIds).map(Number),
          importer_id: currentImporter.id,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al eliminar categorías");
      }

      const data = await response.json();

      // Recargar categorías
      await loadCategoriesFromDB();
      setSelectedIds(new Set());

      setToast({
        type: "success",
        message: `${data.deleted_count} categorías eliminadas correctamente`,
      });
    } catch (err) {
      console.error("❌ Error:", err);
      setToast({
        type: "error",
        message: err instanceof Error ? err.message : "Error al eliminar categorías",
      });
    } finally {
      setLoading(false);
    }
  };

  // Notificar al padre cada vez que cambia la selección (sin guardar en BD)
  useEffect(() => {
    onCategoriesImported(Array.from(selectedIds));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedIds]); // Solo depende de selectedIds, no de la función

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
                className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded transition-colors"
              >
                {selectedIds.size === categories.length
                  ? "Deseleccionar todas"
                  : "Seleccionar todas"}
              </button>
              <button
                onClick={handleDeleteSelected}
                disabled={selectedIds.size === 0}
                className="bg-red-500 hover:bg-red-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded transition-colors flex items-center space-x-2"
                title={selectedIds.size === 0 ? "Selecciona categorías para eliminar" : "Eliminar categorías seleccionadas"}
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                <span>Eliminar</span>
              </button>
              <button
                onClick={handleSaveSelection}
                className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded font-medium transition-colors flex items-center space-x-2"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                  />
                </svg>
                <span>Guardar Selección</span>
              </button>
            </div>
          </div>

          {/* Categories Grid - Layout compacto sin contadores */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
            {categories.map((category) => (
              <div
                key={category.id}
                onClick={() => toggleCategory(category.id)}
                className={`
                  p-3 rounded border cursor-pointer transition-colors
                  ${
                    selectedIds.has(category.id)
                      ? "border-blue-500 bg-blue-500/10"
                      : "border-gray-700 bg-gray-800/50 hover:border-gray-600"
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-white text-sm font-medium flex-1">
                    {category.name}
                  </h3>
                  <div
                    className={`
                    w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ml-2
                    ${
                      selectedIds.has(category.id)
                        ? "border-blue-500 bg-blue-500"
                        : "border-gray-600"
                    }
                  `}
                  >
                    {selectedIds.has(category.id) && (
                      <svg
                        className="w-3 h-3 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={3}
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    )}
                  </div>
                </div>
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
