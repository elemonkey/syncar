import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";
import { ImportJobProvider } from "@/contexts/ImportJobContext";
import PersistentImportModal from "@/components/PersistentImportModal";

const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "SYNCAR - Plataforma de Importación",
  description:
    "Plataforma centralizada para importación de datos de proveedores",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <body className={montserrat.className}>
        <ImportJobProvider>
          <Navigation />
          {children}
          <PersistentImportModal />
        </ImportJobProvider>
      </body>
    </html>
  );
}
