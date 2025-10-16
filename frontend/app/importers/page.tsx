'use client'

import { useState } from 'react'
import { ImporterTabs } from '@/components/importers/ImporterTabs'
import { ImporterPanel } from '@/components/importers/ImporterPanel'

export default function ImportersPage() {
  const [activeImporter, setActiveImporter] = useState('noriega')

  const importers = [
    { id: 'noriega', name: 'Noriega', color: 'blue' },
    { id: 'alsacia', name: 'Alsacia', color: 'green' },
    { id: 'refax', name: 'Refax', color: 'purple' },
    { id: 'emasa', name: 'Emasa', color: 'orange' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🔄 Importadores
          </h1>
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
  )
}
