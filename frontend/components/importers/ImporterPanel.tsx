"use client";

import { useState, useRef } from "react";
import {
  CategoriesImporter,
  CategoriesImporterRef,
} from "./CategoriesImporter";
import { ProductsImporter } from "./ProductsImporter";

interface ImporterPanelProps {
  importerId: string;
}

type Phase = "categories" | "products";

export function ImporterPanel({ importerId }: ImporterPanelProps) {
  const [phase, setPhase] = useState<Phase>("categories");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const categoriesImporterRef = useRef<CategoriesImporterRef>(null);

  const handleCategoriesImported = (categoryIds: string[]) => {
    setSelectedCategories(categoryIds);
    if (categoryIds.length > 0) {
      setPhase("products");
    }
  };

  const handleImportCategoriesClick = () => {
    if (categoriesImporterRef.current) {
      categoriesImporterRef.current.startImport();
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 p-6">
      {/* Phase Selector */}
      <div className="flex space-x-4 mb-6 border-b border-gray-700 pb-4">
        <button
          onClick={() => {
            setPhase("categories");
            handleImportCategoriesClick();
          }}
          className={`
            px-4 py-2 rounded-lg font-medium transition-colors
            ${
              phase === "categories"
                ? "bg-blue-500 text-white"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }
          `}
        >
          📋 Importar Categorías
        </button>
        <button
          onClick={() => setPhase("products")}
          disabled={selectedCategories.length === 0}
          className={`
            px-4 py-2 rounded-lg font-medium transition-colors
            ${
              phase === "products"
                ? "bg-blue-500 text-white"
                : selectedCategories.length === 0
                ? "bg-gray-800 text-gray-600 cursor-not-allowed"
                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
            }
          `}
        >
          📦 Importar Productos{" "}
          {selectedCategories.length > 0 && `(${selectedCategories.length})`}
        </button>
      </div>

      {/* Content */}
      {phase === "categories" ? (
        <CategoriesImporter
          ref={categoriesImporterRef}
          importerId={importerId}
          onCategoriesImported={handleCategoriesImported}
        />
      ) : (
        <ProductsImporter
          importerId={importerId}
          categoryIds={selectedCategories}
        />
      )}
    </div>
  );
}
