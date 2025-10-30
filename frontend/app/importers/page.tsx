"use client";

import { useState } from "react";
import { ImporterTabs } from "@/components/importers/ImporterTabs";
import { ImporterPanel } from "@/components/importers/ImporterPanel";
import { PageHeader } from "@/components/PageHeader";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function ImportersPage() {
  return (
    <ProtectedRoute requiredPermission="importers">
      <ImportersContent />
    </ProtectedRoute>
  );
}

function ImportersContent() {
  const [activeImporter, setActiveImporter] = useState("noriega");

  const importers = [
    { id: "noriega", name: "Noriega", color: "blue" },
    { id: "alsacia", name: "Alsacia", color: "green" },
    { id: "refax", name: "Refax", color: "purple" },
    { id: "emasa", name: "Emasa", color: "orange" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <PageHeader
          title="Importadores"
          description="Gestiona la importación de datos de tus proveedores"
          icon={
            <svg
              className="w-8 h-8 text-blue-400"
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
          }
        />

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
