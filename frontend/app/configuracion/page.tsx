'use client'

import { useState, useEffect } from 'react'

interface ImporterConfig {
  id: string
  name: string
  rut: string
  username: string
  password: string
  color: string
  enabled: boolean
}

export default function ConfiguracionPage() {
  const [configs, setConfigs] = useState<ImporterConfig[]>([
    { id: 'noriega', name: 'Noriega', rut: '', username: '', password: '', color: 'blue', enabled: true },
    { id: 'alsacia', name: 'Alsacia', rut: '', username: '', password: '', color: 'green', enabled: true },
    { id: 'refax', name: 'Refax', rut: '', username: '', password: '', color: 'purple', enabled: true },
    { id: 'emasa', name: 'Emasa', rut: '', username: '', password: '', color: 'orange', enabled: true },
  ])

  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // Cargar configuración al montar
  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/importers/configs`)
      if (response.ok) {
        const data = await response.json()
        if (data.configs && data.configs.length > 0) {
          setConfigs(data.configs)
        }
      }
    } catch (error) {
      console.error('Error loading configs:', error)
    }
  }

  const handleInputChange = (id: string, field: keyof ImporterConfig, value: string | boolean) => {
    setConfigs(configs.map(config => 
      config.id === id ? { ...config, [field]: value } : config
    ))
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${apiUrl}/importers/configs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ configs }),
      })

      if (response.ok) {
        setMessage({ type: 'success', text: '✅ Configuración guardada exitosamente' })
      } else {
        throw new Error('Error al guardar')
      }
    } catch (error) {
      setMessage({ type: 'error', text: '❌ Error al guardar la configuración' })
    } finally {
      setSaving(false)
      setTimeout(() => setMessage(null), 3000)
    }
  }

  const colorClasses = {
    blue: 'border-blue-500 bg-blue-500/10',
    green: 'border-green-500 bg-green-500/10',
    purple: 'border-purple-500 bg-purple-500/10',
    orange: 'border-orange-500 bg-orange-500/10',
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 pt-8">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            ⚙️ Configuración de Importadores
          </h1>
          <p className="text-gray-400">
            Configura las credenciales de acceso para cada importador
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className={`
            mb-6 p-4 rounded-lg border-2
            ${message.type === 'success' 
              ? 'bg-green-500/10 border-green-500 text-green-400' 
              : 'bg-red-500/10 border-red-500 text-red-400'
            }
          `}>
            {message.text}
          </div>
        )}

        {/* Configurations Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {configs.map((config) => (
            <div
              key={config.id}
              className={`
                rounded-lg border-2 p-6 transition-all
                ${colorClasses[config.color as keyof typeof colorClasses]}
                ${!config.enabled && 'opacity-50'}
              `}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">{config.name}</h2>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.enabled}
                    onChange={(e) => handleInputChange(config.id, 'enabled', e.target.checked)}
                    className="w-5 h-5 rounded"
                  />
                  <span className="text-sm text-gray-300">Habilitado</span>
                </label>
              </div>

              {/* Form Fields */}
              <div className="space-y-4">
                {/* RUT */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    RUT
                  </label>
                  <input
                    type="text"
                    value={config.rut}
                    onChange={(e) => handleInputChange(config.id, 'rut', e.target.value)}
                    placeholder="12.345.678-9"
                    disabled={!config.enabled}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Username */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Usuario
                  </label>
                  <input
                    type="text"
                    value={config.username}
                    onChange={(e) => handleInputChange(config.id, 'username', e.target.value)}
                    placeholder="usuario@ejemplo.com"
                    disabled={!config.enabled}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Password */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contraseña
                  </label>
                  <input
                    type="password"
                    value={config.password}
                    onChange={(e) => handleInputChange(config.id, 'password', e.target.value)}
                    placeholder="••••••••"
                    disabled={!config.enabled}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Status */}
                <div className="pt-2">
                  {config.rut && config.username && config.password ? (
                    <div className="flex items-center space-x-2 text-green-400 text-sm">
                      <span>✅</span>
                      <span>Configuración completa</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-yellow-400 text-sm">
                      <span>⚠️</span>
                      <span>Configuración incompleta</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className={`
              px-8 py-3 rounded-lg font-bold text-lg transition-all flex items-center space-x-2
              ${saving
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg hover:shadow-blue-500/50'
              }
            `}
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-transparent" />
                <span>Guardando...</span>
              </>
            ) : (
              <>
                <span>💾</span>
                <span>Guardar Configuración</span>
              </>
            )}
          </button>
        </div>

        {/* Info Card */}
        <div className="mt-8 bg-blue-500/10 border border-blue-500 rounded-lg p-6">
          <h3 className="text-xl font-bold text-blue-400 mb-3">ℹ️ Información Importante</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start space-x-2">
              <span className="text-blue-400">•</span>
              <span>Las credenciales se almacenan de forma segura en la base de datos.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-blue-400">•</span>
              <span>Desactiva un importador si no deseas utilizarlo temporalmente.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-blue-400">•</span>
              <span>Las credenciales son necesarias para realizar las importaciones.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-blue-400">•</span>
              <span>Verifica que los datos sean correctos antes de guardar.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
