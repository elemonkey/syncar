
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'
import Sidebar from '@/components/layout/Sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Syncar',
  description: 'Plataforma centralizada para la importación de datos.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={`${inter.className} bg-gray-900 text-white h-screen overflow-hidden`}>
        <Toaster position="top-right" />
        <div className="h-full">
          <Sidebar />
          <main className="ml-64 h-full overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
