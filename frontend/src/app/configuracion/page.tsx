'use client'

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import PageHeader from '@/components/layout/PageHeader';

interface ImporterConfig {
  importer_name: string;
  display_name: string;
  is_active: boolean;
  config_fields: Record<string, string>;
  created_at?: string;
  updated_at?: string;
}

type TabType = 'importadores' | 'usuarios' | 'sistema';

export default function ConfiguracionPage() {
  const [activeTab, setActiveTab] = useState<TabType>('importadores');
  const [configs, setConfigs] = useState<ImporterConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [formData, setFormData] = useState<Record<string, Record<string, string>>>({});
  const [testingConnections, setTestingConnections] = useState<Record<string, boolean>>({});

  // Cargar configuraciones al montar el componente
  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/importer-configs');
      if (!response.ok) throw new Error('Error al cargar configuraciones');
      
      const data = await response.json();
      setConfigs(data);
    } catch (error) {
      toast.error('Error al cargar las configuraciones');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async (config: ImporterConfig) => {
    const toastId = toast.loading('Guardando configuración...');
    
    try {
      const response = await fetch(`/api/v1/importer-configs/${config.importer_name}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          config_fields: formData[config.importer_name] || config.config_fields,
          is_active: config.is_active
        }),
      });

      if (!response.ok) throw new Error('Error al guardar configuración');

      toast.success('Configuración guardada exitosamente', { id: toastId });
      fetchConfigs(); // Recargar datos
    } catch (error) {
      toast.error('Error al guardar la configuración', { id: toastId });
      console.error(error);
    }
  };

  const handleTestConnection = async (config: ImporterConfig) => {
    const toastId = toast.loading('Iniciando prueba de conexión...');
    
    // Activar estado de loading para este importador
    setTestingConnections(prev => ({ ...prev, [config.importer_name]: true }));
    
    try {
      const currentData = formData[config.importer_name] || config.config_fields;
      
      if (!currentData || Object.values(currentData).some(value => !value)) {
        toast.error('Por favor completa todas las credenciales antes de probar', { id: toastId });
        return;
      }

      // Llamar al endpoint de prueba de conexión
      toast.loading('🚀 Conectando y haciendo login automático...', { id: toastId });
      
      // Preparar datos según el importador
      const testData = config.importer_name.toLowerCase() === 'noriega' ? {
        rut_empresa: currentData.rut || '',
        usuario: currentData.username || '',
        password: currentData.password || '',
        url_base: 'https://proveedores.noriegaonline.cl/'
      } : {
        config_fields: currentData
      };
      
      const response = await fetch(`/api/v1/importer-configs/${config.importer_name}/test-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error en la prueba de conexión');
      }

      const result = await response.json();
      
      if (result.success) {
        toast.success(`✅ ${result.message || 'Login exitoso'}`, { 
          id: toastId,
          duration: 6000
        });
      } else {
        toast.error(`❌ ${result.message || 'Error en login'}`, { 
          id: toastId,
          duration: 8000
        });
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      toast.error(`Error al probar conexión: ${errorMessage}`, { id: toastId });
      console.error(error);
    } finally {
      // Desactivar estado de loading
      setTestingConnections(prev => ({ ...prev, [config.importer_name]: false }));
    }
  };

  const handleReset = (config: ImporterConfig) => {
    // Resetear los campos del formulario para este importador específico
    const defaultFields = {...config.config_fields};
    Object.keys(defaultFields).forEach(key => {
      defaultFields[key] = '';
    });
    
    setFormData({
      ...formData,
      [config.importer_name]: defaultFields
    });
    
    toast(`Campos de ${config.display_name} limpiados`, { icon: 'ℹ️' });
  };

  const handleToggleActive = async (config: ImporterConfig) => {
    const toastId = toast.loading(`${config.is_active ? 'Desactivando' : 'Activando'} ${config.display_name}...`);
    
    try {
      const response = await fetch(`/api/v1/importer-configs/${config.importer_name}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_active: !config.is_active
        }),
      });

      if (!response.ok) throw new Error('Error al actualizar estado');

      toast.success(`${config.display_name} ${!config.is_active ? 'activado' : 'desactivado'}`, { id: toastId });
      fetchConfigs();
    } catch (error) {
      toast.error('Error al actualizar el estado', { id: toastId });
      console.error(error);
    }
  };

  const renderConfigFields = (config: ImporterConfig) => {
    const fields = config.config_fields || {};
    const currentData = formData[config.importer_name] || config.config_fields || {};
    
    return Object.keys(fields).map((fieldKey) => (
      <div key={fieldKey} className="mb-4">
        <label className="block text-sm font-medium text-gray-300 mb-2 capitalize">
          {fieldKey === 'rut' ? 'RUT' : fieldKey}
        </label>
        <input
          type={fieldKey.includes('password') ? 'password' : 'text'}
          value={currentData[fieldKey] || ''}
          onChange={(e) => setFormData({ 
            ...formData, 
            [config.importer_name]: {
              ...currentData,
              [fieldKey]: e.target.value
            }
          })}
          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
          placeholder={`Ingresa ${fieldKey === 'rut' ? 'RUT' : fieldKey}`}
        />
      </div>
    ));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-400">Cargando configuraciones...</div>
      </div>
    );
  }

  const tabs = [
    { id: 'importadores', name: '⚙️ Ajustes de Importadores', available: true },
    { id: 'usuarios', name: '👥 Gestión de Usuarios', available: false },
    { id: 'sistema', name: '🔧 Configuración del Sistema', available: false }
  ];

  const renderImportadoresContent = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {configs.map((config) => (
          <div key={config.importer_name} className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">{config.display_name}</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => handleToggleActive(config)}
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    config.is_active 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                      : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                  }`}
                >
                  {config.is_active ? 'Activo' : 'Inactivo'}
                </button>
              </div>
            </div>

            {/* Siempre mostrar inputs editables */}
            <div>
              {renderConfigFields(config)}
              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => handleSave(config)}
                  className="flex-1 px-4 py-2 bg-teal-500 text-white rounded-md hover:bg-teal-600 transition-colors"
                >
                  Guardar
                </button>
                <button
                  onClick={() => handleTestConnection(config)}
                  disabled={testingConnections[config.importer_name]}
                  className={`flex-1 px-4 py-2 text-white rounded-md transition-colors ${
                    testingConnections[config.importer_name]
                      ? 'bg-blue-400 cursor-not-allowed'
                      : 'bg-blue-500 hover:bg-blue-600'
                  }`}
                >
                  {testingConnections[config.importer_name] ? '🔄 Probando...' : '🚀 Probar'}
                </button>
                <button
                  onClick={() => handleReset(config)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">ℹ️ Información</h3>
        <ul className="text-sm text-gray-400 space-y-1">
          <li>• Las credenciales se almacenan de forma segura en la base de datos</li>
          <li>• Solo los importadores activos aparecerán en la página de importación</li>
          <li>• Noriega requiere RUT, usuario y contraseña</li>
          <li>• Los demás importadores solo requieren usuario y contraseña</li>
          <li>• El botón "Probar" usa Selenium para hacer login automático</li>
          <li>• ⚠️ Verificar URLs correctas de cada importador antes de probar</li>
        </ul>
      </div>
    </div>
  );

  const renderUsuariosContent = () => (
    <div className="space-y-6">
      <div className="text-center py-12">
        <div className="text-6xl mb-4">👥</div>
        <h3 className="text-xl font-semibold mb-2">Gestión de Usuarios</h3>
        <p className="text-gray-400 mb-6">Próximamente podrás gestionar usuarios y permisos del sistema</p>
        <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-6 max-w-md mx-auto">
          <h4 className="font-semibold mb-3">Funcionalidades planeadas:</h4>
          <ul className="text-sm text-gray-400 space-y-2 text-left">
            <li>• Crear y gestionar cuentas de usuario</li>
            <li>• Asignar roles y permisos</li>
            <li>• Control de acceso por módulos</li>
            <li>• Historial de actividad de usuarios</li>
            <li>• Configuración de autenticación JWT</li>
          </ul>
        </div>
      </div>
    </div>
  );

  const renderSistemaContent = () => (
    <div className="space-y-6">
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🔧</div>
        <h3 className="text-xl font-semibold mb-2">Configuración del Sistema</h3>
        <p className="text-gray-400 mb-6">Ajustes generales y configuración avanzada del sistema</p>
        <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-6 max-w-md mx-auto">
          <h4 className="font-semibold mb-3">Configuraciones disponibles:</h4>
          <ul className="text-sm text-gray-400 space-y-2 text-left">
            <li>• Configuración de base de datos</li>
            <li>• Configuración de Redis y Celery</li>
            <li>• Configuración de logging</li>
            <li>• Configuración de notificaciones</li>
            <li>• Configuración de backups automáticos</li>
          </ul>
        </div>
      </div>
    </div>
  );

  return (
    <div>
      <PageHeader
        title="Configuración del Sistema"
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={(tabId: string) => setActiveTab(tabId as TabType)}
      />
      
      <div className="p-8">
        {/* Tab Content */}
        <div className="min-h-[400px]">
          {activeTab === 'importadores' && renderImportadoresContent()}
          {activeTab === 'usuarios' && renderUsuariosContent()}
          {activeTab === 'sistema' && renderSistemaContent()}
        </div>
      </div>
    </div>
  );
}