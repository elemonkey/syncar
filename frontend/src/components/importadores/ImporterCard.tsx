
'use client'

import { useState } from 'react';
import toast from 'react-hot-toast';
import CategoriesSection from './CategoriesSection';

interface ImporterCardProps {
  name: string;
  status: 'Inactive' | 'In Progress' | 'Error';
}

const statusColors = {
  Inactive: 'bg-green-500',
  'In Progress': 'bg-blue-500',
  Error: 'bg-red-500',
};

const ImporterCard = ({ name, status: initialStatus }: ImporterCardProps) => {
  const [status, setStatus] = useState(initialStatus);
  const [isTestingConnection, setIsTestingConnection] = useState(false);

  const handleImport = async () => {
    const toastId = toast.loading(`Iniciando importación para ${name}...`);
    setStatus('In Progress');

    try {
      const response = await fetch('/api/v1/import/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ importer_name: name.toLowerCase(), category: 'Frenos' }),
      });

      if (!response.ok) {
        throw new Error('Falló la comunicación con el servidor');
      }

      const data = await response.json();
      toast.success(`Tarea de importación iniciada. Job ID: ${data.job_id}`, { id: toastId });

    } catch (error) {
      console.error(error);
      toast.error(`Error al iniciar la importación para ${name}.`, { id: toastId });
      setStatus('Error');
    } finally {
      // En un caso real, el estado se actualizaría vía polling o websockets.
      // Por ahora, lo dejamos en 'In Progress' para ver el cambio visual.
    }
  };

  const handleTestConnection = async () => {
    if (name.toLowerCase() !== 'noriega') {
      toast.error(`Prueba de conexión no disponible para ${name}`);
      return;
    }

    const toastId = toast.loading(`Probando conexión con ${name}...`);
    setIsTestingConnection(true);

    try {
      const response = await fetch(`/api/v1/importer-configs/${name.toLowerCase()}/test-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error('Error en la prueba de conexión');
      }

      const result = await response.json();
      
      if (result.success) {
        toast.success(`✅ Conexión exitosa con ${name}`, { id: toastId });
        setStatus('Inactive'); // Estado activo
      } else {
        toast.error(`❌ Error: ${result.message}`, { id: toastId });
        setStatus('Error');
      }
    } catch (error) {
      console.error('Error testing connection:', error);
      toast.error(`Error probando conexión con ${name}`, { id: toastId });
      setStatus('Error');
    } finally {
      setIsTestingConnection(false);
    }
  };

  return (
    <div className="border border-gray-700 rounded-lg p-5 flex flex-col bg-gray-800/50 backdrop-blur-sm shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold">{name}</h3>
        <div className={`w-4 h-4 rounded-full ${statusColors[status]}`}></div>
      </div>
      <p className="text-sm text-gray-400 mb-6">Estado: {status}</p>
      
      {/* Sección de categorías */}
      <CategoriesSection importerName={name} />
      
      <div className="mt-4 space-y-2">
        {name.toLowerCase() === 'noriega' && (
          <button 
            onClick={handleTestConnection}
            disabled={isTestingConnection}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-2 rounded-md transition-colors">
            {isTestingConnection ? '🔄 Probando...' : '🧪 Probar Conexión'}
          </button>
        )}
        
        <button 
          onClick={handleImport}
          disabled={name !== 'Alsacia'} // Habilitado solo para Alsacia como pide el prompt
          className="w-full bg-teal-500 text-white py-2 rounded-md hover:bg-teal-600 transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed">
          Importar Productos
        </button>
      </div>
    </div>
  );
};

export default ImporterCard;
