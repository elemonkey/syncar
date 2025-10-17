"use client";

import { useImportJob } from "@/contexts/ImportJobContext";
import { useEffect, useState } from "react";
import { showToast } from "./Toast";

export default function PersistentImportModal() {
  const { currentJob, updateJob, closeJob, toggleMinimize, cancelJob } = useImportJob();
  const [elapsedTime, setElapsedTime] = useState("00:00");
  const [isCancelling, setIsCancelling] = useState(false);

  // Polling para actualizar el progreso
  useEffect(() => {
    if (
      !currentJob ||
      currentJob.status === "completed" ||
      currentJob.status === "failed" ||
      currentJob.status === "cancelled"
    ) {
      return;
    }

    console.log("🔄 Iniciando polling para job:", currentJob.jobId);

    const pollInterval = setInterval(async () => {
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

        // Usar endpoint de desarrollo solo en desarrollo, en producción usar el endpoint principal
        const isDev = process.env.NODE_ENV === "development";
        const endpoint = isDev ? "dev/status" : "importers/status";
        const url = `${apiUrl}/${endpoint}/${currentJob.jobId}`;

        console.log("📡 Polling status:", url);

        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          console.log("📊 Status data:", data);

          // Mapear el progreso a pasos detallados
          let currentStep = "";
          let detailedStatus = "";
          const progress = data.progress || 0;

          if (progress < 10) {
            currentStep = "PASO 1: AUTENTICACIÓN";
            detailedStatus = "Iniciando sesión en el importador...";
          } else if (progress < 20) {
            currentStep = "PASO 2: NAVEGACIÓN";
            detailedStatus = "Navegando hacia la categoría seleccionada...";
          } else if (progress < 90) {
            currentStep = "PASO 3: EXTRACCIÓN";
            // Usar datos reales del backend si están disponibles
            const totalProducts = data.total_items || 100;
            const currentItem = data.current_item || 0;
            const processedProducts = data.processed_items || 0;
            const currentSku = data.result?.current_sku || "";

            if (currentItem > 0) {
              // Usar datos reales del backend
              detailedStatus = `Importando producto ${currentItem}/${totalProducts}${
                currentSku ? ` (${currentSku})` : ""
              }`;
            } else {
              // Fallback: calcular aproximado
              const estimated = Math.floor(
                ((progress - 20) / 70) * totalProducts
              );
              detailedStatus = `Importando producto ${estimated}/${totalProducts}`;
            }
          } else if (progress < 100) {
            currentStep = "PASO 4: GUARDANDO";
            detailedStatus = "Guardando productos en la base de datos...";
          } else {
            currentStep = "PASO 5: COMPLETADO";
            detailedStatus = `Importación finalizada: ${
              data.processed_items || 0
            } productos`;
          }

          updateJob({
            status: data.status,
            progress: progress,
            currentStep,
            detailedStatus,
          });

          // Si está completado o en error, detener el polling
          // Backend usa: "completed", "failed", "cancelled"
          if (
            data.status === "completed" ||
            data.status === "failed" ||
            data.status === "cancelled"
          ) {
            console.log("✅ Job finalizado, deteniendo polling");
            clearInterval(pollInterval);
          }
        } else {
          console.error(
            "❌ Error response:",
            response.status,
            response.statusText
          );
        }
      } catch (error) {
        console.error("❌ Error polling job status:", error);
      }
    }, 2000);

    return () => {
      console.log("🛑 Limpiando polling interval");
      clearInterval(pollInterval);
    };
  }, [currentJob, updateJob]);

  // Actualizar tiempo transcurrido
  useEffect(() => {
    if (!currentJob) return;

    const interval = setInterval(() => {
      const elapsed = Math.floor(
        (new Date().getTime() - currentJob.startedAt.getTime()) / 1000
      );
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      setElapsedTime(
        `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
          2,
          "0"
        )}`
      );
    }, 1000);

    return () => clearInterval(interval);
  }, [currentJob]);

  if (!currentJob) return null;

  const isRunning =
    currentJob.status === "running" || currentJob.status === "pending";
  const isCompleted = currentJob.status === "completed";
  const isError =
    currentJob.status === "failed" || currentJob.status === "cancelled";

  const handleCancelJob = async () => {
    if (!confirm("¿Estás seguro de cancelar esta importación?\n\nEsto detendrá todos los procesos de scraping activos.")) {
      return;
    }

    setIsCancelling(true);
    try {
      await cancelJob();
      // Esperar un momento para que el backend procese la cancelación
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Cerrar el modal
      closeJob();
      
      // Mostrar toast de confirmación
      showToast("Tarea cancelada", "info");
    } catch (error) {
      console.error("Error al cancelar job:", error);
      showToast("Error al cancelar la tarea", "error");
    } finally {
      setIsCancelling(false);
    }
  };

  return (
    <>
      {/* Modal Minimizado */}
      {currentJob.isMinimized && (
        <div
          className="fixed bottom-4 right-4 bg-white rounded-lg shadow-2xl border-2 border-blue-500 z-50 cursor-pointer hover:shadow-3xl transition-shadow"
          onClick={toggleMinimize}
        >
          <div className="px-4 py-3 flex items-center gap-3">
            {/* Icono animado si está corriendo */}
            {isRunning && (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            )}
            {isCompleted && (
              <svg
                className="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
            {isError && (
              <svg
                className="w-5 h-5 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            )}

            <div className="flex-1 min-w-[200px]">
              <p className="text-sm font-semibold text-gray-900">
                {currentJob.jobType === "products"
                  ? "Importando Productos"
                  : "Importando Categorías"}
              </p>
              <p className="text-xs text-gray-600">
                {currentJob.progress}% • {elapsedTime}
              </p>
            </div>

            {/* Barra de progreso mini */}
            <div className="w-20 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  isCompleted
                    ? "bg-green-600"
                    : isError
                    ? "bg-red-600"
                    : "bg-blue-600"
                }`}
                style={{ width: `${currentJob.progress}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Modal Maximizado */}
      {!currentJob.isMinimized && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={`rounded-full p-2 ${
                    isCompleted
                      ? "bg-green-100"
                      : isError
                      ? "bg-red-100"
                      : "bg-blue-100"
                  }`}
                >
                  {isRunning && (
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  )}
                  {isCompleted && (
                    <svg
                      className="w-6 h-6 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                  {isError && (
                    <svg
                      className="w-6 h-6 text-red-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  )}
                </div>
                <div>
                  <h3 className="text-white font-bold text-lg">
                    {currentJob.jobType === "products"
                      ? "Importación de Productos"
                      : "Importación de Categorías"}
                  </h3>
                  <p className="text-blue-100 text-sm">Tiempo: {elapsedTime}</p>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={toggleMinimize}
                  className="text-white hover:bg-blue-500 rounded p-2 transition-colors"
                  title="Minimizar"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {(isCompleted || isError) && (
                  <button
                    onClick={closeJob}
                    className="text-white hover:bg-blue-500 rounded p-2 transition-colors"
                    title="Cerrar"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
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

            {/* Body */}
            <div className="p-6 space-y-6">
              {/* Paso Actual */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-900 font-semibold text-lg mb-1">
                  {currentJob.currentStep}
                </p>
                <p className="text-blue-700 text-sm">
                  {currentJob.detailedStatus}
                </p>
              </div>

              {/* Barra de Progreso */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Progreso General
                  </span>
                  <span className="text-sm font-bold text-blue-600">
                    {currentJob.progress}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className={`h-3 rounded-full transition-all duration-300 ${
                      isCompleted
                        ? "bg-green-600"
                        : isError
                        ? "bg-red-600"
                        : "bg-blue-600"
                    }`}
                    style={{ width: `${currentJob.progress}%` }}
                  />
                </div>
              </div>

              {/* Pasos del Proceso */}
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900 text-sm uppercase">
                  Pasos del Proceso
                </h4>

                {[
                  { step: 1, name: "AUTENTICACIÓN", range: [0, 10] },
                  { step: 2, name: "NAVEGACIÓN", range: [10, 20] },
                  { step: 3, name: "EXTRACCIÓN", range: [20, 90] },
                  { step: 4, name: "GUARDANDO", range: [90, 100] },
                  { step: 5, name: "COMPLETADO", range: [100, 100] },
                ].map(({ step, name, range }) => {
                  const [min, max] = range;
                  const isActive =
                    currentJob.progress >= min && currentJob.progress < max;
                  const isCompleted = currentJob.progress >= max;

                  return (
                    <div key={step} className="flex items-center gap-3">
                      <div
                        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                          isCompleted
                            ? "bg-green-600 text-white"
                            : isActive
                            ? "bg-blue-600 text-white"
                            : "bg-gray-300 text-gray-600"
                        }`}
                      >
                        {isCompleted ? "✓" : step}
                      </div>
                      <div className="flex-1">
                        <p
                          className={`text-sm font-medium ${
                            isActive
                              ? "text-blue-900"
                              : isCompleted
                              ? "text-green-900"
                              : "text-gray-500"
                          }`}
                        >
                          PASO {step}: {name}
                        </p>
                        {isActive && (
                          <div className="mt-1 w-full bg-gray-200 rounded-full h-1">
                            <div
                              className="bg-blue-600 h-1 rounded-full animate-pulse"
                              style={{ width: "60%" }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Mensaje de Estado Final */}
              {isCompleted && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                  <svg
                    className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <div>
                    <p className="font-semibold text-green-900">
                      ¡Importación Completada!
                    </p>
                    <p className="text-sm text-green-700 mt-1">
                      Todos los datos han sido importados exitosamente.
                    </p>
                  </div>
                </div>
              )}

              {isError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                  <svg
                    className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <div>
                    <p className="font-semibold text-red-900">
                      Error en la Importación
                    </p>
                    <p className="text-sm text-red-700 mt-1">
                      Ocurrió un problema durante la importación.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            {isRunning && (
              <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t">
                <button
                  onClick={handleCancelJob}
                  disabled={isCancelling}
                  className="px-4 py-2 bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg transition-colors font-medium flex items-center gap-2"
                >
                  {isCancelling ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>Cancelando...</span>
                    </>
                  ) : (
                    <>
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                      <span>Cancelar Importación</span>
                    </>
                  )}
                </button>
              </div>
            )}
            {(isCompleted || isError) && (
              <div className="bg-gray-50 px-6 py-4 flex justify-end gap-3 border-t">
                <button
                  onClick={toggleMinimize}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors font-medium"
                >
                  Minimizar
                </button>
                <button
                  onClick={closeJob}
                  className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors font-medium"
                >
                  Cerrar
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
