export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="text-center space-y-6 p-8">
        <h1 className="text-6xl font-bold text-white mb-4">🚀 SYNCAR</h1>
        <p className="text-2xl text-gray-300 mb-8">
          Plataforma de Importación de Datos
        </p>
        <div className="space-y-4">
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-teal-400 mb-2">
              ✅ Backend Configurado
            </h2>
            <p className="text-gray-400">FastAPI + SQLAlchemy + Celery</p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-violet-400 mb-2">
              ⚡ Frontend Listo
            </h2>
            <p className="text-gray-400">Next.js 14 + Tailwind CSS</p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-semibold text-emerald-400 mb-2">
              🐳 Docker Configurado
            </h2>
            <p className="text-gray-400">Dev y Prod ready</p>
          </div>
        </div>
        <div className="mt-8">
          <a
            href="/importers"
            className="inline-block bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors shadow-lg hover:shadow-blue-500/50"
          >
            🚀 Ir a Importadores
          </a>
        </div>
        <div className="mt-8 text-gray-500 text-sm">
          <p>📖 Revisa el README.md para instrucciones de uso</p>
          <p className="mt-2">
            API Docs (dev):{" "}
            <code className="text-teal-400">http://localhost:8000/docs</code>
          </p>
        </div>
      </div>
    </div>
  );
}
