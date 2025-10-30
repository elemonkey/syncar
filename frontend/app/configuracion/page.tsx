"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { PageHeader } from "@/components/PageHeader";
import { ProtectedRoute } from "@/components/ProtectedRoute";

interface Permission {
  id: number;
  role_id: number;
  page_name: string;
  can_access: boolean;
  created_at: string;
}

interface Role {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  permissions?: Permission[];
}

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

interface UserFormData {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role_id: number | null;
  is_active: boolean;
  is_superuser: boolean;
}

interface ImporterConfig {
  id: string;
  name: string;
  rut: string;
  username: string;
  password: string;
  color: string;
  enabled: boolean;
  categoryLimit: number;
  productsPerMinute: number;
}

export default function ConfiguracionPage() {
  return (
    <ProtectedRoute requiredPermission="configuracion">
      <ConfiguracionContent />
    </ProtectedRoute>
  );
}

function ConfiguracionContent() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, token } = useAuth();

  const [activeTab, setActiveTab] = useState<
    "usuarios" | "roles" | "importadores"
  >("usuarios");

  // Estados para usuarios
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    username: "",
    email: "",
    password: "",
    full_name: "",
    role_id: null,
    is_active: true,
    is_superuser: false,
  });
  const [userError, setUserError] = useState("");
  const [userSuccess, setUserSuccess] = useState("");

  // Estados para roles y permisos
  const [loadingRoles, setLoadingRoles] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [roleError, setRoleError] = useState("");
  const [roleSuccess, setRoleSuccess] = useState("");

  // Estados para importadores
  const [configs, setConfigs] = useState<ImporterConfig[]>([
    {
      id: "noriega",
      name: "Noriega",
      rut: "",
      username: "",
      password: "",
      color: "blue",
      enabled: true,
      categoryLimit: 100,
      productsPerMinute: 60,
    },
    {
      id: "alsacia",
      name: "Alsacia",
      rut: "",
      username: "",
      password: "",
      color: "green",
      enabled: true,
      categoryLimit: 100,
      productsPerMinute: 60,
    },
    {
      id: "refax",
      name: "Refax",
      rut: "",
      username: "",
      password: "",
      color: "purple",
      enabled: true,
      categoryLimit: 100,
      productsPerMinute: 60,
    },
    {
      id: "emasa",
      name: "Emasa",
      rut: "",
      username: "",
      password: "",
      color: "orange",
      enabled: true,
      categoryLimit: 100,
      productsPerMinute: 60,
    },
  ]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, isLoading, router]);

  // Páginas disponibles en la aplicación
  const availablePages = [
    {
      name: "dashboard",
      label: "Dashboard",
      description: "Página principal con estadísticas",
    },
    {
      name: "catalogo",
      label: "Catálogo",
      description: "Ver y gestionar productos",
    },
    {
      name: "importers",
      label: "Importadores",
      description: "Gestionar importaciones",
    },
    {
      name: "configuracion",
      label: "Configuración",
      description: "Configuración del sistema",
    },
  ];

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (activeTab === "usuarios" && token) {
      fetchUsers();
      fetchRoles();
    } else if (activeTab === "roles" && token) {
      fetchRolesWithPermissions();
    } else if (activeTab === "importadores") {
      loadConfigs();
    } else if (!token && !isLoading) {
      // Si no hay token, redirigir al login
      setUserError("Sesión expirada. Por favor, inicia sesión nuevamente.");
      setTimeout(() => {
        router.push("/");
      }, 2000);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, token, isLoading]);

  // Funciones para usuarios
  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${API_URL}/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        // Token expirado o inválido, hacer logout y redirigir
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        router.push("/");
        return;
      }

      if (!response.ok) throw new Error("Error al cargar usuarios");

      const data = await response.json();
      setUsers(data);
    } catch (err: any) {
      setUserError(err.message);
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${API_URL}/roles`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        // Token expirado o inválido, hacer logout y redirigir
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        router.push("/");
        return;
      }

      if (!response.ok) throw new Error("Error al cargar roles");

      const data = await response.json();
      setRoles(data);
    } catch (err: any) {
      console.error("Error cargando roles:", err);
    }
  };

  // Funciones para roles y permisos
  const fetchRolesWithPermissions = async () => {
    setLoadingRoles(true);
    setRoleError("");
    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${API_URL}/roles`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        // Token expirado o inválido, hacer logout y redirigir
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        router.push("/");
        return;
      }

      if (!response.ok) throw new Error("Error al cargar roles");

      const data = await response.json();
      setRoles(data);
    } catch (err: any) {
      setRoleError(err.message);
    } finally {
      setLoadingRoles(false);
    }
  };

  const updatePermission = async (
    roleId: number,
    pageName: string,
    canAccess: boolean
  ) => {
    setRoleError("");
    setRoleSuccess("");

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      // Buscar si ya existe el permiso
      const role = roles.find((r) => r.id === roleId);
      const existingPermission = role?.permissions?.find(
        (p) => p.page_name === pageName
      );

      let response;
      if (existingPermission) {
        // Actualizar permiso existente
        response = await fetch(
          `${API_URL}/roles/${roleId}/permissions/${existingPermission.id}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              page_name: pageName,
              can_access: canAccess,
            }),
          }
        );
      } else {
        // Crear nuevo permiso
        response = await fetch(`${API_URL}/roles/${roleId}/permissions`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ page_name: pageName, can_access: canAccess }),
        });
      }

      if (!response.ok) throw new Error("Error al actualizar permiso");

      setRoleSuccess("Permiso actualizado correctamente");
      await fetchRolesWithPermissions();

      setTimeout(() => setRoleSuccess(""), 3000);
    } catch (err: any) {
      setRoleError(err.message);
    }
  };

  const handleOpenModal = (userToEdit?: User) => {
    if (userToEdit) {
      setEditingUser(userToEdit);
      setFormData({
        username: userToEdit.username,
        email: userToEdit.email,
        password: "",
        full_name: userToEdit.full_name || "",
        role_id: userToEdit.role_id,
        is_active: userToEdit.is_active,
        is_superuser: userToEdit.is_superuser,
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: "",
        email: "",
        password: "",
        full_name: "",
        role_id: null,
        is_active: true,
        is_superuser: false,
      });
    }
    setShowModal(true);
    setUserError("");
    setUserSuccess("");
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingUser(null);
    setUserError("");
    setUserSuccess("");
  };

  const handleSubmitUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setUserError("");
    setUserSuccess("");

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const url = editingUser
        ? `${API_URL}/users/${editingUser.id}`
        : `${API_URL}/users`;

      const method = editingUser ? "PUT" : "POST";

      const payload =
        editingUser && !formData.password
          ? {
              username: formData.username,
              email: formData.email,
              full_name: formData.full_name,
              role_id: formData.role_id,
              is_active: formData.is_active,
              is_superuser: formData.is_superuser,
            }
          : formData;

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al guardar usuario");
      }

      setUserSuccess(editingUser ? "Usuario actualizado" : "Usuario creado");
      await fetchUsers();
      setTimeout(() => {
        handleCloseModal();
      }, 1500);
    } catch (err: any) {
      setUserError(err.message);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm("¿Estás seguro de eliminar este usuario?")) return;

    try {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${API_URL}/users/${userId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al eliminar usuario");
      }

      setUserSuccess("Usuario eliminado");
      await fetchUsers();
      setTimeout(() => setUserSuccess(""), 3000);
    } catch (err: any) {
      setUserError(err.message);
      setTimeout(() => setUserError(""), 3000);
    }
  };

  // Funciones para importadores

  const loadConfigs = async () => {
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${apiUrl}/importers/configs`);
      if (response.ok) {
        const data = await response.json();
        if (data.configs && data.configs.length > 0) {
          setConfigs(data.configs);
        }
      }
    } catch (error) {
      console.error("Error loading configs:", error);
    }
  };

  const handleInputChange = (
    id: string,
    field: keyof ImporterConfig,
    value: string | boolean | number
  ) => {
    setConfigs(
      configs.map((config) =>
        config.id === id ? { ...config, [field]: value } : config
      )
    );
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${apiUrl}/importers/configs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ configs }),
      });

      if (response.ok) {
        setMessage({
          type: "success",
          text: "✅ Configuración guardada exitosamente",
        });
      } else {
        throw new Error("Error al guardar");
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: "❌ Error al guardar la configuración",
      });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const colorClasses: Record<string, string> = {
    blue: "border-blue-500 bg-blue-500/10",
    green: "border-green-500 bg-green-500/10",
    purple: "border-purple-500 bg-purple-500/10",
    orange: "border-orange-500 bg-orange-500/10",
  };

  // Mostrar loading mientras se verifica autenticación
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400 mx-auto"></div>
          <p className="text-gray-400 mt-4">Cargando...</p>
        </div>
      </div>
    );
  }

  // Si no está autenticado, no renderizar nada (el useEffect redirigirá)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Mensaje flotante */}
      {message && (
        <div className="fixed top-24 right-6 z-50 animate-in slide-in-from-right duration-300">
          <div
            className={`
            p-4 rounded-lg border-2 shadow-2xl backdrop-blur-sm min-w-[300px]
            ${
              message.type === "success"
                ? "bg-green-500/20 border-green-500 text-green-400"
                : "bg-red-500/20 border-red-500 text-red-400"
            }
          `}
          >
            {message.text}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <PageHeader
          title="Configuración"
          description="Administra la configuración general del sistema"
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
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          }
        />

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-700">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab("usuarios")}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${
                  activeTab === "usuarios"
                    ? "border-teal-500 text-teal-400"
                    : "border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300"
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                </svg>
                <span>Usuarios</span>
              </div>
            </button>

            <button
              onClick={() => setActiveTab("roles")}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${
                  activeTab === "roles"
                    ? "border-purple-500 text-purple-400"
                    : "border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300"
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
                <span>Roles y Permisos</span>
              </div>
            </button>

            <button
              onClick={() => setActiveTab("importadores")}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${
                  activeTab === "importadores"
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300"
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <svg
                  className="w-5 h-5"
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
                <span>Importadores</span>
              </div>
            </button>
          </nav>
        </div>

        {/* Contenido según tab activo */}
        {activeTab === "usuarios" ? (
          // Tab de Usuarios - Gestión completa
          <div>
            {/* Header de usuarios */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">
                  Gestión de Usuarios
                </h2>
                <p className="text-gray-400 mt-1">
                  Administra los usuarios del sistema
                </p>
              </div>
              <button
                onClick={() => handleOpenModal()}
                className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                <span>Nuevo Usuario</span>
              </button>
            </div>

            {/* Mensajes */}
            {userError && (
              <div className="mb-4 bg-red-500/10 border border-red-500/50 rounded-lg p-4">
                <p className="text-red-400">{userError}</p>
              </div>
            )}

            {userSuccess && (
              <div className="mb-4 bg-green-500/10 border border-green-500/50 rounded-lg p-4">
                <p className="text-green-400">{userSuccess}</p>
              </div>
            )}

            {/* Tabla de Usuarios */}
            {loadingUsers ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-400 mx-auto"></div>
                  <p className="text-gray-400 mt-4">Cargando usuarios...</p>
                </div>
              </div>
            ) : (
              <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-900/50 border-b border-gray-700">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Usuario
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Email
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Rol
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Estado
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                          Acciones
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {users.map((userItem) => (
                        <tr
                          key={userItem.id}
                          className="hover:bg-gray-700/30 transition-colors"
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="h-10 w-10 rounded-full bg-teal-500 flex items-center justify-center mr-3">
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
                              <div>
                                <div className="text-sm font-medium text-white flex items-center space-x-2">
                                  <span>{userItem.username}</span>
                                  {userItem.is_superuser && (
                                    <span className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs rounded">
                                      Superuser
                                    </span>
                                  )}
                                </div>
                                <div className="text-sm text-gray-400">
                                  {userItem.full_name}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                            {userItem.email}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {userItem.role ? (
                              <span
                                className={`px-3 py-1 text-xs rounded-full ${
                                  userItem.role.name === "Super Admin"
                                    ? "bg-purple-500/10 border border-purple-500/30 text-purple-400"
                                    : userItem.role.name === "Admin"
                                    ? "bg-blue-500/10 border border-blue-500/30 text-blue-400"
                                    : userItem.role.name === "Viewer"
                                    ? "bg-green-500/10 border border-green-500/30 text-green-400"
                                    : "bg-gray-500/10 border border-gray-500/30 text-gray-400"
                                }`}
                              >
                                {userItem.role.name}
                              </span>
                            ) : (
                              <span className="text-gray-500 text-sm">
                                Sin rol
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {userItem.is_active ? (
                              <span className="px-3 py-1 bg-green-500/10 border border-green-500/30 text-green-400 text-xs rounded-full">
                                Activo
                              </span>
                            ) : (
                              <span className="px-3 py-1 bg-red-500/10 border border-red-500/30 text-red-400 text-xs rounded-full">
                                Inactivo
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex items-center space-x-3">
                              <button
                                onClick={() => handleOpenModal(userItem)}
                                className="text-blue-400 hover:text-blue-300 transition-colors"
                                title="Editar"
                              >
                                <svg
                                  className="w-5 h-5"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                  strokeWidth={2}
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                  />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleDeleteUser(userItem.id)}
                                className="text-red-400 hover:text-red-300 transition-colors"
                                title="Eliminar"
                              >
                                <svg
                                  className="w-5 h-5"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                  strokeWidth={2}
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                  />
                                </svg>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : activeTab === "roles" ? (
          // Tab de Roles y Permisos
          <div>
            {/* Header de roles */}
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white">
                Gestión de Roles y Permisos
              </h2>
              <p className="text-gray-400 mt-1">
                Configura los permisos de acceso para cada rol del sistema
              </p>
            </div>

            {/* Mensajes de éxito/error */}
            {roleSuccess && (
              <div className="mb-4 bg-green-500/10 border border-green-500/50 rounded p-3">
                <p className="text-green-400 text-sm">{roleSuccess}</p>
              </div>
            )}

            {roleError && (
              <div className="mb-4 bg-red-500/10 border border-red-500/50 rounded p-3">
                <p className="text-red-400 text-sm">{roleError}</p>
              </div>
            )}

            {/* Contenido de roles */}
            {loadingRoles ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {roles.map((role) => (
                  <div
                    key={role.id}
                    className="bg-gray-800/50 backdrop-blur border border-gray-700 rounded-lg p-6"
                  >
                    {/* Header del rol */}
                    <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-700">
                      <div>
                        <h3 className="text-xl font-bold text-white flex items-center space-x-2">
                          <span>{role.name}</span>
                          {role.name === "Super Admin" && (
                            <span className="px-2 py-1 bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs rounded-full">
                              Acceso Total
                            </span>
                          )}
                        </h3>
                        {role.description && (
                          <p className="text-gray-400 text-sm mt-1">
                            {role.description}
                          </p>
                        )}
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          role.is_active
                            ? "bg-green-500/10 border border-green-500/30 text-green-400"
                            : "bg-gray-500/10 border border-gray-500/30 text-gray-400"
                        }`}
                      >
                        {role.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </div>

                    {/* Grid de permisos */}
                    {role.name === "Super Admin" ? (
                      <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                        <p className="text-purple-400 text-sm flex items-center space-x-2">
                          <svg
                            className="w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={2}
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                            />
                          </svg>
                          <span>
                            Este rol tiene acceso completo a todas las funciones
                            del sistema
                          </span>
                        </p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {availablePages.map((page) => {
                          const permission = role.permissions?.find(
                            (p) => p.page_name === page.name
                          );
                          const hasAccess = permission?.can_access ?? false;

                          return (
                            <div
                              key={page.name}
                              className="bg-gray-900/50 border border-gray-600 rounded-lg p-4 hover:border-gray-500 transition-colors"
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <h4 className="text-white font-medium flex items-center space-x-2">
                                    <svg
                                      className="w-5 h-5 text-gray-400"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="currentColor"
                                      strokeWidth={2}
                                    >
                                      <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                      />
                                    </svg>
                                    <span>{page.label}</span>
                                  </h4>
                                  <p className="text-gray-400 text-xs mt-1">
                                    {page.description}
                                  </p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer ml-4">
                                  <input
                                    type="checkbox"
                                    checked={hasAccess}
                                    onChange={(e) =>
                                      updatePermission(
                                        role.id,
                                        page.name,
                                        e.target.checked
                                      )
                                    }
                                    className="sr-only peer"
                                    disabled={role.name === "Super Admin"}
                                  />
                                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                                </label>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          // Tab de Importadores
          <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {configs.map((config) => (
                <div
                  key={config.id}
                  className={`
                    relative p-4 rounded-lg border-2 backdrop-blur-sm
                    ${
                      colorClasses[config.color as keyof typeof colorClasses] ||
                      colorClasses.blue
                    }
                    transition-all
                  `}
                >
                  {/* Header del importador */}
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-white">
                      {config.name}
                    </h3>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={config.enabled}
                        onChange={(e) =>
                          handleInputChange(
                            config.id,
                            "enabled",
                            e.target.checked
                          )
                        }
                        className="sr-only peer"
                      />
                      <div className="w-10 h-5 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-600"></div>
                    </label>
                  </div>

                  <div className="space-y-2">
                    {/* RUT */}
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        RUT
                      </label>
                      <input
                        type="text"
                        value={config.rut}
                        onChange={(e) =>
                          handleInputChange(config.id, "rut", e.target.value)
                        }
                        className="w-full bg-gray-800/50 border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-400"
                        placeholder="12345678-9"
                      />
                    </div>

                    {/* Username */}
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        Usuario
                      </label>
                      <input
                        type="text"
                        value={config.username}
                        onChange={(e) =>
                          handleInputChange(
                            config.id,
                            "username",
                            e.target.value
                          )
                        }
                        className="w-full bg-gray-800/50 border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-400"
                        placeholder="usuario"
                      />
                    </div>

                    {/* Password */}
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        Contraseña
                      </label>
                      <input
                        type="password"
                        value={config.password}
                        onChange={(e) =>
                          handleInputChange(
                            config.id,
                            "password",
                            e.target.value
                          )
                        }
                        className="w-full bg-gray-800/50 border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-400"
                        placeholder="••••••••"
                      />
                    </div>

                    {/* Límite de categorías */}
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        Límite por Categoría
                      </label>
                      <input
                        type="number"
                        value={config.categoryLimit}
                        onChange={(e) =>
                          handleInputChange(
                            config.id,
                            "categoryLimit",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full bg-gray-800/50 border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-400"
                        min="1"
                      />
                      <p className="text-xs text-gray-400 mt-0.5">
                        Productos máximos por categoría
                      </p>
                    </div>

                    {/* Velocidad */}
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        Velocidad (prod/min)
                      </label>
                      <input
                        type="number"
                        value={config.productsPerMinute}
                        onChange={(e) =>
                          handleInputChange(
                            config.id,
                            "productsPerMinute",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full bg-gray-800/50 border border-gray-600 rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-blue-400"
                        min="1"
                        max="120"
                      />
                      <p className="text-xs text-gray-400 mt-0.5">
                        Productos por minuto (1-120)
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Botón de guardar */}
            <div className="flex justify-end">
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Guardando...</span>
                  </>
                ) : (
                  <>
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                      />
                    </svg>
                    <span>Guardar Configuración</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Usuario */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg border border-gray-700 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">
                {editingUser ? "Editar Usuario" : "Nuevo Usuario"}
              </h2>

              {userError && (
                <div className="mb-4 bg-red-500/10 border border-red-500/50 rounded p-3">
                  <p className="text-red-400 text-sm">{userError}</p>
                </div>
              )}

              {userSuccess && (
                <div className="mb-4 bg-green-500/10 border border-green-500/50 rounded p-3">
                  <p className="text-green-400 text-sm">{userSuccess}</p>
                </div>
              )}

              <form onSubmit={handleSubmitUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Nombre de Usuario *
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                    className="w-full bg-gray-900/50 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-teal-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    className="w-full bg-gray-900/50 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-teal-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Contraseña {editingUser ? "" : "*"}
                  </label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="w-full bg-gray-900/50 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-teal-500"
                    required={!editingUser}
                    placeholder={
                      editingUser ? "Dejar en blanco para mantener" : ""
                    }
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Nombre Completo
                  </label>
                  <input
                    type="text"
                    value={formData.full_name}
                    onChange={(e) =>
                      setFormData({ ...formData, full_name: e.target.value })
                    }
                    className="w-full bg-gray-900/50 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Rol
                  </label>
                  <select
                    value={formData.role_id || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        role_id: e.target.value
                          ? parseInt(e.target.value)
                          : null,
                      })
                    }
                    className="w-full bg-gray-900/50 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-teal-500"
                  >
                    <option value="">Sin rol</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          is_active: e.target.checked,
                        })
                      }
                      className="w-4 h-4 text-teal-600 bg-gray-900 border-gray-600 rounded focus:ring-teal-500"
                    />
                    <span className="text-sm text-gray-300">
                      Usuario activo
                    </span>
                  </label>

                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_superuser}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          is_superuser: e.target.checked,
                        })
                      }
                      className="w-4 h-4 text-purple-600 bg-gray-900 border-gray-600 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm text-gray-300">Superusuario</span>
                  </label>
                </div>

                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-teal-600 hover:bg-teal-700 text-white py-2 rounded transition-colors"
                  >
                    {editingUser ? "Actualizar" : "Crear"}
                  </button>
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
