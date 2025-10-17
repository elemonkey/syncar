"use client";

import { useToast } from "@/contexts/ToastContext";
import { Toast } from "./Toast";

/**
 * Contenedor global de toasts que se muestra en posición fija
 * en la esquina superior derecha de toda la página
 */
export function GlobalToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed top-20 right-6 z-[100] space-y-3 pointer-events-none">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
    </div>
  );
}
