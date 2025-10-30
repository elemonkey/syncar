"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function AccessDeniedPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Ícono de prohibición */}
        <div className="inline-flex items-center justify-center w-24 h-24 bg-red-500/10 rounded-full mb-6">
          <svg
            className="w-12 h-12 text-red-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
            />
          </svg>
        </div>

        {/* Título */}
        <h1 className="text-4xl font-bold text-white mb-4">
          Acceso Denegado
        </h1>

        {/* Descripción */}
        <p className="text-gray-400 mb-8">
          {user ? (
            <>
              <span className="text-blue-400 font-semibold">{user.username}</span>
              , no tienes permisos para acceder a esta página.
              <br />
              <span className="text-sm text-gray-500 mt-2 block">
                Rol actual: <span className="text-gray-300">{user.role?.name || "Sin rol"}</span>
              </span>
            </>
          ) : (
            "No tienes permisos para acceder a esta página."
          )}
        </p>

        {/* Botones de acción */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
          >
            Volver al Dashboard
          </Link>
          
          <Link
            href="/configuracion"
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
          >
            Solicitar Permisos
          </Link>
        </div>

        {/* Información adicional */}
        <div className="mt-8 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <p className="text-sm text-gray-400">
            💡 <strong className="text-white">¿Necesitas acceso?</strong>
            <br />
            Contacta con un administrador para solicitar los permisos necesarios.
          </p>
        </div>
      </div>
    </div>
  );
}
