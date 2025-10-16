'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function Navigation() {
  const pathname = usePathname()

  const navItems = [
    { href: '/', label: 'Inicio', icon: '🏠' },
    { href: '/importers', label: 'Importadores', icon: '🔄' },
    { href: '/catalogo', label: 'Catálogo', icon: '📦' },
    { href: '/configuracion', label: 'Configuración', icon: '⚙️' },
  ]

  // No mostrar navegación en la página de inicio
  if (pathname === '/') {
    return null
  }

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
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`
                    px-4 py-2 rounded-lg font-medium transition-all flex items-center space-x-2
                    ${isActive
                      ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/50'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                    }
                  `}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>

          {/* User Section */}
          <div className="flex items-center space-x-4">
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
  )
}
