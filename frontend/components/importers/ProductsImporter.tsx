'use client'

import { useState } from 'react'

interface ProductsImporterProps {
  importerId: string
  categoryIds: string[]
}

interface ImportJob {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  total_items: number
  processed_items: number
  message?: string
}

export function ProductsImporter({ importerId, categoryIds }: ProductsImporterProps) {
  const [loading, setLoading] = useState(false)
  const [job, setJob] = useState<ImportJob | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleImportProducts = async () => {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/importers/${importerId}/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category_ids: categoryIds,
        }),
      })

      if (!response.ok) {
        throw new Error('Error al importar productos')
      }

      const data = await response.json()
      setJob(data)

      // Start polling job status
      if (data.job_id) {
        pollJobStatus(data.job_id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      setLoading(false)
    }
  }

  const pollJobStatus = async (jobId: string) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${apiUrl}/jobs/${jobId}`)
        if (!response.ok) throw new Error('Error al obtener estado del job')

        const data = await response.json()
        setJob(data)

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval)
          setLoading(false)
        }
      } catch (err) {
        console.error('Error polling job:', err)
        clearInterval(interval)
        setLoading(false)
      }
    }, 2000) // Poll every 2 seconds
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Importar Productos</h2>
          <p className="text-gray-400 mt-1">
            Importando productos de <span className="text-blue-400 font-medium">{categoryIds.length}</span> categorías seleccionadas
          </p>
        </div>
        {!loading && !job && (
          <button
            onClick={handleImportProducts}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <span>🚀</span>
            <span>Iniciar Importación</span>
          </button>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">❌ {error}</p>
        </div>
      )}

      {/* Job Status */}
      {job && (
        <div className="space-y-4">
          {/* Status Card */}
          <div className="bg-gray-700/50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-white">Estado del Job</h3>
                <p className="text-gray-400">ID: {job.job_id}</p>
              </div>
              <div className={`
                px-4 py-2 rounded-lg font-medium
                ${job.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' : ''}
                ${job.status === 'processing' ? 'bg-blue-500/20 text-blue-400' : ''}
                ${job.status === 'completed' ? 'bg-green-500/20 text-green-400' : ''}
                ${job.status === 'failed' ? 'bg-red-500/20 text-red-400' : ''}
              `}>
                {job.status === 'pending' && '⏳ Pendiente'}
                {job.status === 'processing' && '⚙️ Procesando'}
                {job.status === 'completed' && '✅ Completado'}
                {job.status === 'failed' && '❌ Fallido'}
              </div>
            </div>

            {/* Progress Bar */}
            {(job.status === 'processing' || job.status === 'completed') && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Progreso</span>
                  <span className="text-white font-medium">{job.progress}%</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-3">
                  <div
                    className="bg-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
                <div className="flex justify-between text-sm text-gray-400">
                  <span>{job.processed_items} procesados</span>
                  <span>{job.total_items} total</span>
                </div>
              </div>
            )}

            {/* Message */}
            {job.message && (
              <div className="mt-4 p-3 bg-gray-800 rounded-lg">
                <p className="text-gray-300 text-sm">{job.message}</p>
              </div>
            )}
          </div>

          {/* Loading Animation */}
          {loading && job.status === 'processing' && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            </div>
          )}

          {/* Success State */}
          {job.status === 'completed' && (
            <div className="bg-green-500/10 border border-green-500 rounded-lg p-6 text-center">
              <div className="text-5xl mb-3">🎉</div>
              <h3 className="text-xl font-bold text-green-400 mb-2">
                ¡Importación Completada!
              </h3>
              <p className="text-gray-300">
                Se importaron <span className="text-green-400 font-bold">{job.processed_items}</span> productos exitosamente
              </p>
            </div>
          )}

          {/* Failed State */}
          {job.status === 'failed' && (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-center">
              <div className="text-5xl mb-3">😞</div>
              <h3 className="text-xl font-bold text-red-400 mb-2">
                Error en la Importación
              </h3>
              <p className="text-gray-300">{job.message || 'Ocurrió un error inesperado'}</p>
              <button
                onClick={handleImportProducts}
                className="mt-4 bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Reintentar
              </button>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && !job && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-gray-400 text-lg mb-2">
            Listo para importar productos
          </p>
          <p className="text-gray-500">
            Se importarán productos de {categoryIds.length} categorías
          </p>
        </div>
      )}
    </div>
  )
}
