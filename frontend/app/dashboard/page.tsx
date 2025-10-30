"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Redirigir si no está autenticado
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400 mx-auto"></div>
          <p className="text-gray-400 mt-4">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <PageHeader
          title={`Bienvenido, ${user.full_name || user.username}`}
          description={
            <>
              Rol:{" "}
              <span className="text-teal-400">
                {user.role?.name || "Sin rol"}
              </span>
            </>
          }
          icon={
            <svg
              className="w-8 h-8 text-teal-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
          }
        />

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Importadores</p>
                <p className="text-2xl font-bold text-white mt-1">4</p>
              </div>
              <div className="bg-teal-500/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-teal-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Categorías</p>
                <p className="text-2xl font-bold text-white mt-1">73</p>
              </div>
              <div className="bg-violet-500/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-violet-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Productos</p>
                <p className="text-2xl font-bold text-white mt-1">0</p>
              </div>
              <div className="bg-emerald-500/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-emerald-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Estado</p>
                <p className="text-2xl font-bold text-emerald-400 mt-1">
                  Activo
                </p>
              </div>
              <div className="bg-emerald-500/10 p-3 rounded-lg">
                <svg
                  className="w-8 h-8 text-emerald-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Accesos Rápidos
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              href="/catalogo"
              className="flex items-center p-4 bg-gray-900/50 rounded-lg border border-gray-700 hover:border-teal-500 transition-colors group"
            >
              <div className="bg-teal-500/10 p-3 rounded-lg mr-4">
                <svg
                  className="w-6 h-6 text-teal-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-white group-hover:text-teal-400 transition-colors">
                  Catálogo
                </h3>
                <p className="text-sm text-gray-400">
                  Ver productos y categorías
                </p>
              </div>
            </Link>

            <Link
              href="/importers"
              className="flex items-center p-4 bg-gray-900/50 rounded-lg border border-gray-700 hover:border-violet-500 transition-colors group"
            >
              <div className="bg-violet-500/10 p-3 rounded-lg mr-4">
                <svg
                  className="w-6 h-6 text-violet-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-white group-hover:text-violet-400 transition-colors">
                  Importadores
                </h3>
                <p className="text-sm text-gray-400">Gestionar importaciones</p>
              </div>
            </Link>

            <Link
              href="/configuracion"
              className="flex items-center p-4 bg-gray-900/50 rounded-lg border border-gray-700 hover:border-emerald-500 transition-colors group"
            >
              <div className="bg-emerald-500/10 p-3 rounded-lg mr-4">
                <svg
                  className="w-6 h-6 text-emerald-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-white group-hover:text-emerald-400 transition-colors">
                  Configuración
                </h3>
                <p className="text-sm text-gray-400">Usuarios y ajustes</p>
              </div>
            </Link>
          </div>
        </div>

        {/* User Info */}
        <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">
            Información de Usuario
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-gray-400 text-sm">Nombre de Usuario</p>
              <p className="text-white font-medium">{user.username}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Email</p>
              <p className="text-white font-medium">{user.email}</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Rol</p>
              <p className="text-white font-medium">
                {user.role?.name || "Sin rol"}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Permisos</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {user.role?.permissions
                  .filter((p) => p.can_access)
                  .map((p) => (
                    <span
                      key={p.id}
                      className="px-2 py-1 bg-teal-500/10 border border-teal-500/30 rounded text-teal-400 text-xs"
                    >
                      {p.page_name}
                    </span>
                  )) || (
                  <span className="text-gray-500 text-sm">Sin permisos</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
