/**
 * Modal de progreso para mostrar el estado de importación
 * en tiempo real mientras el proceso corre en segundo plano
 */

import { useEffect, useState } from "react";

interface ImportProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: string;
  importerName: string;
  jobType: "categories" | "products";
  onComplete?: (result: any) => void; // Callback cuando se completa
}

interface JobStatus {
  job_id: string;
  status: "RUNNING" | "COMPLETED" | "FAILED" | "PENDING";
  progress: number;
  result?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export function ImportProgressModal({
  isOpen,
  onClose,
  jobId,
  importerName,
  jobType,
  onComplete,
}: ImportProgressModalProps) {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [isMinimized, setIsMinimized] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [hasNotified, setHasNotified] = useState(false);

  useEffect(() => {
    if (!isOpen || !jobId) return;

    // Polling cada 2 segundos para obtener el estado
    const interval = setInterval(async () => {
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
        const response = await fetch(`${apiUrl}/dev/status/${jobId}`);

        if (response.ok) {
          const data: JobStatus = await response.json();
          setJobStatus(data);

          // Agregar log si hay mensaje nuevo
          if (data.result?.message) {
            setLogs((prev) => {
              const newLog = `[${new Date().toLocaleTimeString()}] ${
                data.result.message
              }`;
              if (!prev.includes(newLog)) {
                return [...prev, newLog];
              }
              return prev;
            });
          }

          // Si completó o falló, detener polling
          if (data.status === "COMPLETED" || data.status === "FAILED") {
            clearInterval(interval);

            // Llamar callback onComplete solo una vez cuando se completa exitosamente
            if (data.status === "COMPLETED" && !hasNotified && onComplete) {
              setHasNotified(true);
              onComplete(data.result);
            }
          }
        }
      } catch (error) {
        console.error("Error obteniendo estado del job:", error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isOpen, jobId, hasNotified, onComplete]);

  if (!isOpen) return null;

  const getStatusColor = () => {
    switch (jobStatus?.status) {
      case "RUNNING":
        return "text-blue-400";
      case "COMPLETED":
        return "text-green-400";
      case "FAILED":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = () => {
    switch (jobStatus?.status) {
      case "RUNNING":
        return (
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        );
      case "COMPLETED":
        return (
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        );
      case "FAILED":
        return (
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div
        className={`bg-gray-900 border border-gray-700 rounded-lg shadow-2xl transition-all duration-300 ${
          isMinimized ? "w-96 h-16" : "w-full max-w-3xl max-h-[80vh]"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <div className={getStatusColor()}>{getStatusIcon()}</div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                Importación de{" "}
                {jobType === "categories" ? "Categorías" : "Productos"}
              </h3>
              <p className="text-sm text-gray-400">
                {importerName} • Job ID: {jobId.slice(0, 8)}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Minimize button */}
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
              title={isMinimized ? "Maximizar" : "Minimizar"}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMinimized ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20 12H4"
                  />
                )}
              </svg>
            </button>

            {/* Close button */}
            {(jobStatus?.status === "COMPLETED" ||
              jobStatus?.status === "FAILED") && (
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                title="Cerrar"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        {!isMinimized && (
          <div className="p-6 space-y-4 overflow-y-auto max-h-[60vh]">
            {/* Progress bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Progreso</span>
                <span className={`font-medium ${getStatusColor()}`}>
                  {jobStatus?.progress || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    jobStatus?.status === "COMPLETED"
                      ? "bg-green-500"
                      : jobStatus?.status === "FAILED"
                      ? "bg-red-500"
                      : "bg-blue-500"
                  }`}
                  style={{ width: `${jobStatus?.progress || 0}%` }}
                />
              </div>
            </div>

            {/* Status */}
            <div className="p-4 bg-gray-800 rounded border border-gray-700">
              <p className={`text-sm font-medium ${getStatusColor()}`}>
                Estado: {jobStatus?.status || "INICIANDO"}
              </p>
              {jobStatus?.result?.message && (
                <p className="text-sm text-gray-300 mt-2">
                  {jobStatus.result.message}
                </p>
              )}
              {jobStatus?.error && (
                <p className="text-sm text-red-400 mt-2">
                  Error: {jobStatus.error}
                </p>
              )}
            </div>

            {/* Logs */}
            {logs.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-400">Logs:</h4>
                <div className="bg-gray-950 rounded border border-gray-800 p-3 max-h-64 overflow-y-auto font-mono text-xs">
                  {logs.map((log, index) => (
                    <div key={index} className="text-gray-300 py-1">
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results */}
            {jobStatus?.status === "COMPLETED" && jobStatus.result && (
              <div className="p-4 bg-green-900/20 border border-green-700 rounded">
                <h4 className="text-green-400 font-medium mb-2">
                  ✅ Importación Completada
                </h4>
                {jobStatus.result.total !== undefined && (
                  <p className="text-sm text-gray-300">
                    Total procesado: {jobStatus.result.total}
                  </p>
                )}
                {jobStatus.result.categories_processed !== undefined && (
                  <p className="text-sm text-gray-300">
                    Categorías procesadas:{" "}
                    {jobStatus.result.categories_processed}
                  </p>
                )}
              </div>
            )}

            {/* Info box */}
            <div className="p-4 bg-blue-900/20 border border-blue-700 rounded">
              <p className="text-sm text-blue-300">
                💡 <strong>Modo Desarrollo:</strong> El navegador Safari
                permanecerá abierto para que puedas inspeccionar el proceso.
                Presiona Ctrl+C en la terminal del backend cuando termines.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
