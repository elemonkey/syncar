"use client";

import { useState, useRef } from "react";
import {
  CategoriesImporter,
  CategoriesImporterRef,
} from "./CategoriesImporter";
import { useImportJob } from "@/contexts/ImportJobContext";
import { useToast } from "@/contexts/ToastContext";

interface ImporterPanelProps {
  importerId: string;
}

export function ImporterPanel({ importerId }: ImporterPanelProps) {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [importingProducts, setImportingProducts] = useState(false);
  const categoriesImporterRef = useRef<CategoriesImporterRef>(null);
  const { showToast } = useToast();

  // Usar el contexto del job
  const { startJob } = useImportJob();

  const handleCategoriesImported = (categoryIds: string[]) => {
    setSelectedCategories(categoryIds);
  };

  const handleImportCategoriesClick = () => {
    if (categoriesImporterRef.current) {
      categoriesImporterRef.current.startImport();
    }
  };

  const handleImportProductsClick = async () => {
    if (selectedCategories.length === 0) return;

    setImportingProducts(true);

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      // 🔧 MODO DESARROLLO: Usar endpoint /dev/ para navegador visible
      const isDev = process.env.NODE_ENV === "development";
      const endpoint = isDev
        ? `${apiUrl}/dev/${importerId}/import-products`
        : `${apiUrl}/importers/${importerId}/import-products`;

      console.log(`🔧 Iniciando importación de productos para ${importerId}`);
      console.log(`📋 Categorías seleccionadas: ${selectedCategories.length}`);

      // Iniciar el proceso (el backend lo ejecuta en background)
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selected_categories: selectedCategories,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || "Error al iniciar importación de productos"
        );
      }

      const data = await response.json();
      console.log("✅ Importación iniciada:", data);

      // Iniciar el job en el contexto global
      startJob(data.job_id, "products");

      showToast(
        `Importación iniciada\n\n🌐 Safari se abrirá automáticamente\n📊 Sigue el progreso en el modal`,
        "info"
      );

      setImportingProducts(false);
    } catch (err) {
      console.error("❌ Error:", err);
      showToast(
        err instanceof Error ? err.message : "Error al importar productos",
        "error"
      );
      setImportingProducts(false);
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 p-6">
      {/* Action Buttons - Sin glows/shadows, iconos outline */}
      <div className="flex space-x-4 mb-6 border-b border-gray-700 pb-4">
        <button
          onClick={handleImportCategoriesClick}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded font-medium transition-colors flex items-center space-x-2"
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <span>Importar Categorías</span>
        </button>
        <button
          onClick={handleImportProductsClick}
          disabled={selectedCategories.length === 0 || importingProducts}
          className={`
            px-6 py-3 rounded font-medium transition-colors flex items-center space-x-2
            ${
              selectedCategories.length > 0 && !importingProducts
                ? "bg-green-500 hover:bg-green-600 text-white"
                : "bg-gray-700 text-gray-500 cursor-not-allowed"
            }
          `}
        >
          {importingProducts ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              <span>Importando...</span>
            </>
          ) : (
            <>
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
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
              <span>
                Importar Productos{" "}
                {selectedCategories.length > 0 &&
                  `(${selectedCategories.length})`}
              </span>
            </>
          )}
        </button>
      </div>

      {/* Content */}
      <CategoriesImporter
        ref={categoriesImporterRef}
        importerId={importerId}
        onCategoriesImported={handleCategoriesImported}
      />
    </div>
  );
}
