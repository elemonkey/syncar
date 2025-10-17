"use client";

import { useState } from "react";
import { ImporterTabs } from "@/components/importers/ImporterTabs";
import { ImporterPanel } from "@/components/importers/ImporterPanel";

export default function ImportersPage() {
  const [activeImporter, setActiveImporter] = useState("noriega");

  const importers = [
    { id: "noriega", name: "Noriega", color: "blue" },
    { id: "alsacia", name: "Alsacia", color: "green" },
    { id: "refax", name: "Refax", color: "purple" },
    { id: "emasa", name: "Emasa", color: "orange" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header - Sin emoji, con icono outline */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <svg
              className="w-10 h-10 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            <h1 className="text-4xl font-bold text-white">Importadores</h1>
          </div>
          <p className="text-gray-400">
            Gestiona la importación de datos de tus proveedores
          </p>
        </div>

        {/* Tabs */}
        <ImporterTabs
          importers={importers}
          activeImporter={activeImporter}
          onTabChange={setActiveImporter}
        />

        {/* Content Panel */}
        <div className="mt-6">
          <ImporterPanel importerId={activeImporter} />
        </div>
      </div>
    </div>
  );
}
