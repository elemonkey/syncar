"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Logo } from "./Logo";
import { useState } from "react";

// Iconos como componentes funcionales
const HomeIcon = () => (
  <svg
    className="w-5 h-5 pointer-events-none"
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
);

const CatalogIcon = () => (
  <svg
    className="w-5 h-5 pointer-events-none"
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
);

const ImportersIcon = () => (
  <svg
    className="w-5 h-5 pointer-events-none"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
    />
  </svg>
);

const SettingsIcon = () => (
  <svg
    className="w-5 h-5 pointer-events-none"
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
);

export function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout, isAuthenticated, hasPermission } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  // Filtrar items según permisos del usuario
  const allNavItems = [
    { href: "/dashboard", label: "Inicio", Icon: HomeIcon, permission: "dashboard" },
    { href: "/catalogo", label: "Catálogo", Icon: CatalogIcon, permission: "catalogo" },
    { href: "/importers", label: "Importadores", Icon: ImportersIcon, permission: "importers" },
  ];

  // Mostrar solo los items que el usuario tiene permiso para ver
  const navItems = allNavItems.filter(item => hasPermission(item.permission));

  // No mostrar navegación en la página de login
  if (pathname === "/" || !isAuthenticated) {
    return null;
  }

  const isConfigActive =
    pathname === "/configuracion" || pathname.startsWith("/configuracion/");

  return (
    <nav className="bg-gray-900/95 backdrop-blur border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            href="/dashboard"
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
          >
            <Logo variant="full" height={32} width={160} />
            <span className="text-sm text-gray-400 font-medium">v2.0</span>
          </Link>

          {/* Navigation Items */}
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const isActive =
                pathname === item.href || pathname.startsWith(item.href + "/");
              const Icon = item.Icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`
                    px-4 py-2 rounded font-medium transition-all flex items-center space-x-2 cursor-pointer
                    ${
                      isActive
                        ? "bg-blue-500 text-white"
                        : "text-gray-400 hover:text-white hover:bg-gray-800"
                    }
                  `}
                >
                  <Icon />
                  <span className="pointer-events-none">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* User Section con ícono de configuración */}
          <div className="flex items-center space-x-3">
            {/* Ícono de Configuración - Solo si tiene permiso */}
            {hasPermission("configuracion") && (
              <Link
                href="/configuracion"
                className={`
                  p-2 rounded transition-all cursor-pointer
                  ${
                    isConfigActive
                      ? "bg-blue-500 text-white"
                      : "text-gray-400 hover:text-white hover:bg-gray-800"
                  }
                `}
                title="Configuración"
              >
                <SettingsIcon />
              </Link>
            )}

            {/* Usuario con menú desplegable */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-3 hover:bg-gray-800 rounded px-3 py-2 transition-colors"
              >
                <div className="text-right">
                  <p className="text-sm text-gray-400">Usuario</p>
                  <p className="text-sm font-medium text-white">
                    {user?.username || "Admin"}
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </div>
              </button>

              {/* Menú desplegable */}
              {showUserMenu && (
                <>
                  {/* Overlay para cerrar el menú */}
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />

                  <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-20">
                    <div className="p-3 border-b border-gray-700">
                      <p className="text-sm text-gray-400">
                        Sesión iniciada como
                      </p>
                      <p className="text-sm font-medium text-white truncate">
                        {user?.email || "admin@syncar.cl"}
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        logout(() => router.push("/"));
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-700 transition-colors flex items-center space-x-2"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={2}
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                        />
                      </svg>
                      <span>Cerrar Sesión</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
