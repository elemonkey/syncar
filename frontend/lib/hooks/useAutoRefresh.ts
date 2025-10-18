"use client";

import { useEffect, useRef } from "react";

interface UseAutoRefreshOptions {
  onRefresh: () => void | Promise<void>;
  enabled?: boolean;
  interval?: number;
}

/**
 * Hook para refrescar automáticamente datos
 * Se activa cuando hay cambios en otras partes de la aplicación
 */
export function useAutoRefresh({
  onRefresh,
  enabled = true,
  interval = 5000,
}: UseAutoRefreshOptions) {
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastRefreshRef = useRef<number>(Date.now());

  // Escuchar evento personalizado de refresh
  useEffect(() => {
    if (!enabled) return;

    const handleRefreshEvent = () => {
      // Solo refrescar si han pasado al menos 2 segundos desde el último refresh
      const now = Date.now();
      if (now - lastRefreshRef.current > 2000) {
        lastRefreshRef.current = now;
        onRefresh();
      }
    };

    // Escuchar eventos de refresh globales
    window.addEventListener("app:data-changed", handleRefreshEvent);

    return () => {
      window.removeEventListener("app:data-changed", handleRefreshEvent);
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [enabled, onRefresh]);

  // Polling mientras hay procesos activos
  useEffect(() => {
    if (!enabled) return;

    const checkForActiveJobs = async () => {
      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
        const response = await fetch(`${apiUrl}/import-jobs?limit=1`);

        if (response.ok) {
          const data = await response.json();
          const hasActiveJobs = data.jobs?.some(
            (job: any) => job.status === "RUNNING" || job.status === "PENDING"
          );

          if (hasActiveJobs) {
            // Si hay jobs activos, refrescar más frecuentemente
            onRefresh();
            refreshTimeoutRef.current = setTimeout(
              checkForActiveJobs,
              interval
            );
          } else {
            // Si no hay jobs activos, verificar de nuevo en el doble de tiempo
            refreshTimeoutRef.current = setTimeout(
              checkForActiveJobs,
              interval * 2
            );
          }
        }
      } catch (error) {
        // En caso de error, reintentar después del intervalo normal
        refreshTimeoutRef.current = setTimeout(checkForActiveJobs, interval);
      }
    };

    // Iniciar verificación
    const initialTimeout = setTimeout(checkForActiveJobs, interval);

    return () => {
      clearTimeout(initialTimeout);
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, [enabled, interval, onRefresh]);
}

/**
 * Emitir evento de cambio de datos para notificar a otros componentes
 */
export function emitDataChanged() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("app:data-changed"));
  }
}
