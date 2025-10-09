import PageHeader from '@/components/layout/PageHeader';

export default function DashboardPage() {
  return (
    <div>
      <PageHeader title="Dashboard" />
      
      <div className="p-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Importadores</h3>
            <p className="text-gray-400">Gestiona tus importadores de productos</p>
          </div>
          
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Catálogo</h3>
            <p className="text-gray-400">Explora el catálogo de productos</p>
          </div>
          
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Informes</h3>
            <p className="text-gray-400">Genera informes y estadísticas</p>
          </div>
        </div>
      </div>
    </div>
  )
}