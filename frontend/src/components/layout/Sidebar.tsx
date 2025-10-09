
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navLinks = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/catalogo', label: 'Catálogo' },
  { href: '/importadores', label: 'Importadores' },
  { href: '/informes', label: 'Informes' },
  { href: '/configuracion', label: 'Configuración' },
];

const Sidebar = () => {
  const appVersion = process.env.NEXT_PUBLIC_APP_VERSION || 'local-dev';
  const pathname = usePathname();

  return (
    <aside className="w-64 h-full bg-gray-800 p-5 flex flex-col flex-shrink-0 fixed left-0 top-0 z-10">
      <div className="text-2xl font-bold mb-10">SYNCAR</div>
      <nav className="flex flex-col space-y-4 flex-grow">
        {navLinks.map(link => {
          const isActive = pathname.startsWith(link.href);
          return (
            <Link 
              key={link.href} 
              href={link.href} 
              className={`transition-colors ${
                isActive ? 'text-teal-500 font-bold' : 'text-gray-400 hover:text-white'
              }`}>
              {link.label}
            </Link>
          )
        })}
      </nav>
      <div className="text-xs text-gray-400 mt-auto">
        Versión: {appVersion}
      </div>
    </aside>
  )
}

export default Sidebar;
