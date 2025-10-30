"use client";

import { createContext, useContext, useEffect, useState } from "react";

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  role_id: number | null;
  role: Role | null;
  created_at: string;
  updated_at: string;
}

interface Role {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  permissions: Permission[];
  created_at: string;
  updated_at: string;
}

interface Permission {
  id: number;
  role_id: number;
  page_name: string;
  can_access: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (
    username: string,
    password: string,
    onSuccess?: () => void
  ) => Promise<void>;
  logout: (onSuccess?: () => void) => void;
  isLoading: boolean;
  isAuthenticated: boolean;
  hasPermission: (pageName: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Cargar usuario desde localStorage al iniciar
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }

    setIsLoading(false);
  }, []);

  const login = async (
    username: string,
    password: string,
    onSuccess?: () => void
  ) => {
    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();

      // Guardar en localStorage
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // Actualizar estado
      setToken(data.access_token);
      setUser(data.user);

      // Ejecutar callback de éxito si existe
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };

  const logout = (onSuccess?: () => void) => {
    // Limpiar localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    // Limpiar estado
    setToken(null);
    setUser(null);

    // Ejecutar callback de éxito si existe
    if (onSuccess) {
      onSuccess();
    }
  };

  const hasPermission = (pageName: string): boolean => {
    // Superusuarios tienen todos los permisos
    if (user?.is_superuser) {
      return true;
    }

    // Verificar permisos del rol
    if (user?.role?.permissions) {
      return user.role.permissions.some(
        (perm) => perm.page_name === pageName && perm.can_access
      );
    }

    return false;
  };

  const isAuthenticated = !!token && !!user;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isLoading,
        isAuthenticated,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    // En lugar de lanzar error, retornar valores por defecto
    // Esto evita el crash durante el SSR
    return {
      user: null,
      token: null,
      login: async () => {},
      logout: () => {},
      isLoading: true,
      isAuthenticated: false,
      hasPermission: () => false,
    };
  }
  return context;
}
