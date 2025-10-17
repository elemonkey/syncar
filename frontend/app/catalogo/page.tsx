"use client";

import { useState, useEffect } from "react";

interface Application {
  car_brand: string;
  car_model: string;
  secondary_name?: string;
  year_start?: number;
  year_end?: number;
}

interface Product {
  id: number;
  sku: string;
  name: string;
  price: number;
  stock: number;
  category: string;
  importer: string;
  description?: string;
  brand?: string;
  image_url?: string;
  images?: string[];
  extra_data?: {
    origin?: string;
    oem?: string[];
    applications?: Application[];
  };
  updated_at: string;
}

interface Category {
  id: number;
  name: string;
  slug: string;
  importer: string;
}

export default function CatalogoPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImporter, setSelectedImporter] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProducts, setSelectedProducts] = useState<Set<number>>(
    new Set()
  );
  const [showApplicationsModal, setShowApplicationsModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const importers = [
    { id: "all", name: "Todos", abbr: "ALL", color: "gray" },
    { id: "noriega", name: "Noriega", abbr: "NV", color: "blue" },
    { id: "alsacia", name: "Alsacia", abbr: "AL", color: "green" },
    { id: "refax", name: "Refax", abbr: "RX", color: "purple" },
    { id: "emasa", name: "Emasa", abbr: "EM", color: "orange" },
  ];

  useEffect(() => {
    loadData();
  }, [selectedImporter, selectedCategory]);

  const loadData = async () => {
    setLoading(true);
    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

      // Cargar productos
      const productsParams = new URLSearchParams();
      if (selectedImporter !== "all")
        productsParams.append("importer", selectedImporter);
      if (selectedCategory !== "all")
        productsParams.append("category", selectedCategory);

      const productsResponse = await fetch(
        `${apiUrl}/products?${productsParams}`
      );
      if (productsResponse.ok) {
        const data = await productsResponse.json();
        setProducts(data.products || []);
      }

      // Cargar categorías
      const categoriesResponse = await fetch(`${apiUrl}/categories`);
      if (categoriesResponse.ok) {
        const data = await categoriesResponse.json();
        setCategories(data.categories || []);
      }
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(
    (product) =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
    }).format(price);
  };

  const getImporterColor = (importer: string) => {
    const colors: Record<string, string> = {
      noriega: "bg-blue-500",
      alsacia: "bg-green-500",
      refax: "bg-purple-500",
      emasa: "bg-orange-500",
    };
    return colors[importer] || "bg-gray-500";
  };

  const getImporterAbbr = (importer: string) => {
    const abbr: Record<string, string> = {
      noriega: "NV",
      alsacia: "AL",
      refax: "RX",
      emasa: "EM",
    };
    return abbr[importer] || importer.substring(0, 2).toUpperCase();
  };

  const toggleProductSelection = (productId: number) => {
    const newSelection = new Set(selectedProducts);
    if (newSelection.has(productId)) {
      newSelection.delete(productId);
    } else {
      newSelection.add(productId);
    }
    setSelectedProducts(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedProducts.size === filteredProducts.length) {
      setSelectedProducts(new Set());
    } else {
      setSelectedProducts(new Set(filteredProducts.map((p) => p.id)));
    }
  };

  const deleteSelectedProducts = async () => {
    if (selectedProducts.size === 0) return;

    const confirmed = confirm(
      `¿Estás seguro de que deseas eliminar ${selectedProducts.size} producto(s)?`
    );
    if (!confirmed) return;

    // TODO: Implementar eliminación en el backend
    console.log("Eliminar productos:", Array.from(selectedProducts));
    alert(`Función de eliminación pendiente de implementación en el backend`);
  };

  const openApplicationsModal = (product: Product) => {
    setCurrentProduct(product);
    setShowApplicationsModal(true);
  };

  const openDetailModal = (product: Product) => {
    setCurrentProduct(product);
    setSelectedImageIndex(0); // Reset to first image
    setShowDetailModal(true);
  };

  const closeModals = () => {
    setShowApplicationsModal(false);
    setShowDetailModal(false);
    setCurrentProduct(null);
    setSelectedImageIndex(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 pt-8">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            📦 Catálogo de Productos
          </h1>
          <p className="text-gray-400">
            Explora y gestiona todos los productos importados
          </p>
        </div>

        {/* Filters */}
        <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🔍 Buscar
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por nombre o SKU..."
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Importer Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                🏢 Importador
              </label>
              <select
                value={selectedImporter}
                onChange={(e) => setSelectedImporter(e.target.value)}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                {importers.map((imp) => (
                  <option key={imp.id} value={imp.id}>
                    {imp.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                📂 Categoría
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="all">Todas</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.slug}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* View Mode & Stats */}
          <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-700">
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <span>
                Total:{" "}
                <span className="text-white font-bold">
                  {filteredProducts.length}
                </span>{" "}
                productos
              </span>
              <span>•</span>
              <span>
                Categorías:{" "}
                <span className="text-white font-bold">
                  {categories.length}
                </span>
              </span>
              {selectedProducts.size > 0 && (
                <>
                  <span>•</span>
                  <span>
                    Seleccionados:{" "}
                    <span className="text-blue-400 font-bold">
                      {selectedProducts.size}
                    </span>
                  </span>
                </>
              )}
            </div>

            {selectedProducts.size > 0 && (
              <button
                onClick={deleteSelectedProducts}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex items-center space-x-2"
              >
                <span>🗑️</span>
                <span>Eliminar ({selectedProducts.size})</span>
              </button>
            )}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent mb-4"></div>
            <p className="text-gray-400">Cargando productos...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredProducts.length === 0 && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📦</div>
            <h3 className="text-2xl font-bold text-white mb-2">
              No hay productos
            </h3>
            <p className="text-gray-400 mb-6">
              {searchTerm
                ? "No se encontraron productos que coincidan con tu búsqueda"
                : "Aún no has importado productos. Ve a la sección de Importadores para comenzar."}
            </p>
            {!searchTerm && (
              <a
                href="/importers"
                className="inline-block bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Ir a Importadores
              </a>
            )}
          </div>
        )}

        {/* Products List */}
        {!loading && filteredProducts.length > 0 && (
          <div className="bg-gray-800/50 backdrop-blur rounded-lg border border-gray-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-900/50">
                <tr>
                  <th className="px-4 py-2 text-left">
                    <input
                      type="checkbox"
                      checked={
                        selectedProducts.size === filteredProducts.length &&
                        filteredProducts.length > 0
                      }
                      onChange={toggleSelectAll}
                      className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
                    />
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Importador
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Producto
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    SKU
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Marca
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Categoría
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Compatibilidad
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Precio
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Stock
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredProducts.map((product) => {
                  const applicationsCount =
                    product.extra_data?.applications?.length || 0;

                  return (
                    <tr
                      key={product.id}
                      className="hover:bg-gray-700/30 transition-colors"
                    >
                      <td className="px-4 py-2">
                        <input
                          type="checkbox"
                          checked={selectedProducts.has(product.id)}
                          onChange={() => toggleProductSelection(product.id)}
                          className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`${getImporterColor(
                            product.importer
                          )} text-white text-xs px-2 py-1 rounded font-bold`}
                        >
                          {getImporterAbbr(product.importer)}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <div
                          className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity"
                          onClick={() => openDetailModal(product)}
                        >
                          <div className="w-10 h-10 bg-gray-900 rounded flex items-center justify-center flex-shrink-0">
                            {product.image_url ? (
                              <img
                                src={product.image_url}
                                alt={product.name}
                                className="w-full h-full object-cover rounded"
                              />
                            ) : (
                              <span className="text-sm">📦</span>
                            )}
                          </div>
                          <div className="text-white text-sm font-medium max-w-xs truncate hover:text-blue-400">
                            {product.name}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-2 text-gray-400 text-xs">
                        {product.sku}
                      </td>
                      <td className="px-4 py-2 text-gray-400 text-xs">
                        {product.brand || "-"}
                      </td>
                      <td className="px-4 py-2 text-gray-400 text-xs">
                        {product.category}
                      </td>
                      <td className="px-4 py-2">
                        {applicationsCount > 0 ? (
                          <button
                            onClick={() => openApplicationsModal(product)}
                            className="text-blue-400 hover:text-blue-300 text-xs underline cursor-pointer"
                          >
                            {applicationsCount}{" "}
                            {applicationsCount === 1
                              ? "aplicación"
                              : "aplicaciones"}
                          </button>
                        ) : (
                          <span className="text-gray-500 text-xs">-</span>
                        )}
                      </td>
                      <td className="px-4 py-2 text-blue-400 font-bold text-sm">
                        {formatPrice(product.price)}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            product.stock > 0
                              ? "bg-green-500/20 text-green-400"
                              : "bg-red-500/20 text-red-400"
                          }`}
                        >
                          {product.stock > 0 ? product.stock : "Sin stock"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Applications Modal */}
        {showApplicationsModal && currentProduct && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={closeModals}
          >
            <div
              className="bg-gray-800 rounded-lg border border-gray-700 max-w-4xl w-full max-h-[80vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-white">
                    🚗 Compatibilidad - {currentProduct.name}
                  </h2>
                  <button
                    onClick={closeModals}
                    className="text-gray-400 hover:text-white text-2xl"
                  >
                    ×
                  </button>
                </div>
                <p className="text-gray-400 text-sm mt-1">
                  SKU: {currentProduct.sku}
                </p>
              </div>
              <div className="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
                {currentProduct.extra_data?.applications &&
                currentProduct.extra_data.applications.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-900/50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">
                            #
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">
                            Marca
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">
                            Modelo
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">
                            Nombre Secundario
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">
                            Año Inicio
                          </th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase">
                            Año Término
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-700">
                        {currentProduct.extra_data.applications.map(
                          (app, index) => (
                            <tr key={index} className="hover:bg-gray-700/30">
                              <td className="px-4 py-2 text-gray-400 text-sm">
                                {index + 1}
                              </td>
                              <td className="px-4 py-2 text-white text-sm">
                                {app.car_brand}
                              </td>
                              <td className="px-4 py-2 text-white text-sm">
                                {app.car_model}
                              </td>
                              <td className="px-4 py-2 text-gray-300 text-sm italic">
                                {app.secondary_name || "-"}
                              </td>
                              <td className="px-4 py-2 text-gray-400 text-sm">
                                {app.year_start || "-"}
                              </td>
                              <td className="px-4 py-2 text-gray-400 text-sm">
                                {app.year_end || "--"}
                              </td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400">
                    No hay información de compatibilidad disponible
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Product Detail Modal */}
        {showDetailModal && currentProduct && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={closeModals}
          >
            <div
              className="bg-gray-800 rounded-lg border border-gray-700 max-w-5xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-white">
                      {currentProduct.name}
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">
                      SKU: {currentProduct.sku}
                    </p>
                  </div>
                  <button
                    onClick={closeModals}
                    className="text-gray-400 hover:text-white text-3xl"
                  >
                    ×
                  </button>
                </div>
              </div>
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left Column - Images Gallery */}
                  <div>
                    <h3 className="text-lg font-bold text-white mb-4">
                      📷 Galería de Imágenes
                    </h3>
                    <div className="space-y-3">
                      {/* Main Image */}
                      {currentProduct.images &&
                      currentProduct.images.length > 0 ? (
                        <>
                          <div className="w-full aspect-square bg-gray-900 rounded-lg border-2 border-gray-700 overflow-hidden">
                            <img
                              src={currentProduct.images[selectedImageIndex]}
                              alt={`${currentProduct.name} - Principal`}
                              className="w-full h-full object-contain"
                            />
                          </div>

                          {/* Thumbnails */}
                          {currentProduct.images.length > 1 && (
                            <div className="grid grid-cols-4 gap-2">
                              {currentProduct.images.map((img, index) => (
                                <button
                                  key={index}
                                  onClick={() => setSelectedImageIndex(index)}
                                  className={`aspect-square bg-gray-900 rounded-lg border-2 overflow-hidden transition-all hover:scale-105 ${
                                    selectedImageIndex === index
                                      ? "border-blue-500 ring-2 ring-blue-500/50"
                                      : "border-gray-700 hover:border-gray-600"
                                  }`}
                                >
                                  <img
                                    src={img}
                                    alt={`${currentProduct.name} - ${
                                      index + 1
                                    }`}
                                    className="w-full h-full object-cover"
                                  />
                                </button>
                              ))}
                            </div>
                          )}
                        </>
                      ) : currentProduct.image_url ? (
                        <div className="w-full aspect-square bg-gray-900 rounded-lg border-2 border-gray-700 overflow-hidden">
                          <img
                            src={currentProduct.image_url}
                            alt={currentProduct.name}
                            className="w-full h-full object-contain"
                          />
                        </div>
                      ) : (
                        <div className="w-full aspect-square bg-gray-900 rounded-lg flex items-center justify-center border-2 border-gray-700">
                          <span className="text-6xl">📦</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Column - Details */}
                  <div className="space-y-6">
                    {/* Basic Info */}
                    <div>
                      <h3 className="text-lg font-bold text-white mb-3">
                        📋 Información Básica
                      </h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Importador:</span>
                          <span
                            className={`${getImporterColor(
                              currentProduct.importer
                            )} text-white px-2 py-1 rounded text-xs font-bold`}
                          >
                            {getImporterAbbr(currentProduct.importer)} -{" "}
                            {currentProduct.importer}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Categoría:</span>
                          <span className="text-white">
                            {currentProduct.category}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Marca:</span>
                          <span className="text-white">
                            {currentProduct.brand || "-"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Origen:</span>
                          <span className="text-white">
                            {currentProduct.extra_data?.origin || "-"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Precio:</span>
                          <span className="text-blue-400 font-bold text-lg">
                            {formatPrice(currentProduct.price)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Stock:</span>
                          <span
                            className={`px-3 py-1 rounded ${
                              currentProduct.stock > 0
                                ? "bg-green-500/20 text-green-400"
                                : "bg-red-500/20 text-red-400"
                            }`}
                          >
                            {currentProduct.stock > 0
                              ? currentProduct.stock
                              : "Sin stock"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    {currentProduct.description && (
                      <div>
                        <h3 className="text-lg font-bold text-white mb-3">
                          📝 Descripción
                        </h3>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {currentProduct.description}
                        </p>
                      </div>
                    )}

                    {/* OEM Codes */}
                    {currentProduct.extra_data?.oem &&
                      currentProduct.extra_data.oem.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-white mb-3">
                            🔢 Códigos OEM
                          </h3>
                          <div className="flex flex-wrap gap-2">
                            {currentProduct.extra_data.oem.map(
                              (code, index) => (
                                <span
                                  key={index}
                                  className="bg-gray-900 text-gray-300 px-3 py-1 rounded text-sm font-mono"
                                >
                                  {code}
                                </span>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {/* Applications Summary */}
                    {currentProduct.extra_data?.applications &&
                      currentProduct.extra_data.applications.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-white mb-3">
                            🚗 Compatibilidad
                          </h3>
                          <button
                            onClick={() => {
                              setShowDetailModal(false);
                              setShowApplicationsModal(true);
                            }}
                            className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                          >
                            Ver {currentProduct.extra_data.applications.length}{" "}
                            {currentProduct.extra_data.applications.length === 1
                              ? "aplicación"
                              : "aplicaciones"}
                          </button>
                        </div>
                      )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
