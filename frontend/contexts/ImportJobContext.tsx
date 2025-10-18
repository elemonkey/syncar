"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface ImportJob {
  jobId: string;
  jobType: "categories" | "products";
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  currentStep: string;
  detailedStatus: string;
  startedAt: Date;
  isMinimized: boolean;
}

interface ImportJobContextType {
  currentJob: ImportJob | null;
  startJob: (jobId: string, jobType: "categories" | "products") => void;
  updateJob: (updates: Partial<ImportJob>) => void;
  closeJob: () => void;
  toggleMinimize: () => void;
  cancelJob: () => Promise<void>;
}

const ImportJobContext = createContext<ImportJobContextType | undefined>(
  undefined
);

export function ImportJobProvider({ children }: { children: React.ReactNode }) {
  const [currentJob, setCurrentJob] = useState<ImportJob | null>(null);

  // Cargar job desde localStorage al montar
  useEffect(() => {
    const savedJob = localStorage.getItem("currentImportJob");
    if (savedJob) {
      const job = JSON.parse(savedJob);
      // Solo restaurar si no está completado o en error
      if (job.status === "running" || job.status === "pending") {
        setCurrentJob({
          ...job,
          startedAt: new Date(job.startedAt),
        });
      } else {
        localStorage.removeItem("currentImportJob");
      }
    }
  }, []);

  // Guardar job en localStorage cuando cambia
  useEffect(() => {
    if (currentJob) {
      localStorage.setItem("currentImportJob", JSON.stringify(currentJob));
    } else {
      localStorage.removeItem("currentImportJob");
    }
  }, [currentJob]);

  const startJob = (jobId: string, jobType: "categories" | "products") => {
    setCurrentJob({
      jobId,
      jobType,
      status: "pending",
      progress: 0,
      currentStep: "Iniciando...",
      detailedStatus: "Preparando importación",
      startedAt: new Date(),
      isMinimized: false,
    });
  };

  const updateJob = (updates: Partial<ImportJob>) => {
    setCurrentJob((prev) => {
      if (!prev) return null;
      return { ...prev, ...updates };
    });
  };

  const closeJob = () => {
    setCurrentJob(null);
    localStorage.removeItem("currentImportJob");
  };

  const toggleMinimize = () => {
    setCurrentJob((prev) => {
      if (!prev) return null;
      return { ...prev, isMinimized: !prev.isMinimized };
    });
  };

  const cancelJob = async () => {
    if (!currentJob) return;

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      // Llamar al endpoint de cancelación
      const response = await fetch(`${apiUrl}/dev/cancel/${currentJob.jobId}`, {
        method: "POST",
      });

      if (response.ok) {
        // Actualizar estado del job a cancelado
        updateJob({
          status: "cancelled",
          progress: 0,
          currentStep: "CANCELADO",
          detailedStatus: "Importación cancelada por el usuario",
        });
      } else {
        console.error("Error al cancelar el job");
      }
    } catch (error) {
      console.error("Error cancelando job:", error);
    }
  };

  return (
    <ImportJobContext.Provider
      value={{
        currentJob,
        startJob,
        updateJob,
        closeJob,
        toggleMinimize,
        cancelJob,
      }}
    >
      {children}
    </ImportJobContext.Provider>
  );
}

export function useImportJob() {
  const context = useContext(ImportJobContext);
  if (context === undefined) {
    throw new Error("useImportJob must be used within an ImportJobProvider");
  }
  return context;
}
