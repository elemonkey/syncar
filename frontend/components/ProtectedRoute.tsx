"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission: string;
  fallbackPath?: string;
}

export function ProtectedRoute({
  children,
  requiredPermission,
  fallbackPath = "/access-denied",
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading, hasPermission } = useAuth();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (isLoading) {
      return;
    }

    // Si no está autenticado, redirigir al login
    if (!isAuthenticated) {
      router.push("/");
      return;
    }

    // Si no tiene el permiso requerido, redirigir al fallback
    if (!hasPermission(requiredPermission)) {
      console.warn(
        `⚠️ Acceso denegado: Usuario "${user?.username}" no tiene permiso "${requiredPermission}"`
      );
      router.push(fallbackPath);
      return;
    }

    // Si tiene permiso, permitir acceso
    setIsChecking(false);
  }, [
    isAuthenticated,
    isLoading,
    user,
    requiredPermission,
    hasPermission,
    router,
    fallbackPath,
  ]);

  // Mostrar loading mientras verifica
  if (isLoading || isChecking) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
          <p className="mt-4 text-gray-400">Verificando permisos...</p>
        </div>
      </div>
    );
  }

  // Si tiene permiso, mostrar el contenido
  return <>{children}</>;
}
