import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";
import { ImportJobProvider } from "@/contexts/ImportJobContext";
import { ToastProvider } from "@/contexts/ToastContext";
import { AuthProvider } from "@/contexts/AuthContext";
import PersistentImportModal from "@/components/PersistentImportModal";
import { GlobalToastContainer } from "@/components/GlobalToastContainer";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "SYNCAR - Plataforma de Gestión de Repuestos",
  description: "Sistema de importación y gestión de repuestos automotrices",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <head>
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
      </head>
      <body className={montserrat.className}>
        <AuthProvider>
          <ToastProvider>
            <ImportJobProvider>
              <Navigation />
              <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
                {children}
              </div>
              <PersistentImportModal />
              <GlobalToastContainer />
            </ImportJobProvider>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
