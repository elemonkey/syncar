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
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [showingProducts, setShowingProducts] = useState(false);
  const categoriesImporterRef = useRef<CategoriesImporterRef>(null);

  const handleCategoriesImported = (categoryIds: string[]) => {
    setSelectedCategories(categoryIds);
  };

  const handleImportCategoriesClick = () => {
    if (categoriesImporterRef.current) {
      categoriesImporterRef.current.startImport();
    }
  };

  const handleImportProductsClick = () => {
    if (selectedCategories.length > 0) {
      setShowingProducts(true);
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 p-6">
      {/* Action Buttons */}
      <div className="flex space-x-4 mb-6 border-b border-gray-700 pb-4">
        <button
          onClick={handleImportCategoriesClick}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          <span>📋</span>
          <span>Importar Categorías</span>
        </button>
        <button
          onClick={handleImportProductsClick}
          disabled={selectedCategories.length === 0}
          className={`
            px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2
            ${
              selectedCategories.length > 0
                ? "bg-green-500 hover:bg-green-600 text-white"
                : "bg-gray-700 text-gray-500 cursor-not-allowed"
            }
          `}
        >
          <span>📦</span>
          <span>
            Importar Productos{" "}
            {selectedCategories.length > 0 && `(${selectedCategories.length})`}
          </span>
        </button>
        {showingProducts && (
          <button
            onClick={() => setShowingProducts(false)}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg transition-colors"
          >
            ← Volver a Categorías
          </button>
        )}
      </div>

      {/* Content */}
      {!showingProducts ? (
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
