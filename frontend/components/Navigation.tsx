"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

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

  const navItems = [
    { href: "/", label: "Inicio", Icon: HomeIcon },
    { href: "/catalogo", label: "Catálogo", Icon: CatalogIcon },
    { href: "/importers", label: "Importadores", Icon: ImportersIcon },
  ];

  // No mostrar navegación en la página de inicio
  if (pathname === "/") {
    return null;
  }

  const isConfigActive = pathname === "/configuracion" || pathname.startsWith("/configuracion/");

  return (
    <nav className="bg-gray-900/95 backdrop-blur border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-blue-400">SYNCAR</span>
            <span className="text-sm text-gray-400">v2.0</span>
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
            {/* Ícono de Configuración */}
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

            {/* Usuario */}
            <div className="text-right">
              <p className="text-sm text-gray-400">Usuario</p>
              <p className="text-sm font-medium text-white">Admin</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
              A
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
