export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="text-center space-y-6 p-8">
        <h1 className="text-6xl font-bold text-white mb-4">SYNCAR</h1>
        <p className="text-2xl text-gray-300 mb-8">
          Plataforma de Importación de Datos
        </p>
        <div className="space-y-4">
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded border border-gray-700">
            <h2 className="text-xl font-semibold text-teal-400 mb-2 flex items-center justify-center space-x-2">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span>Backend Configurado</span>
            </h2>
            <p className="text-gray-400">FastAPI + SQLAlchemy + Celery</p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded border border-gray-700">
            <h2 className="text-xl font-semibold text-violet-400 mb-2 flex items-center justify-center space-x-2">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              <span>Frontend Listo</span>
            </h2>
            <p className="text-gray-400">Next.js 14 + Tailwind CSS</p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur p-6 rounded border border-gray-700">
            <h2 className="text-xl font-semibold text-emerald-400 mb-2 flex items-center justify-center space-x-2">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                />
              </svg>
              <span>Docker Configurado</span>
            </h2>
            <p className="text-gray-400">Dev y Prod ready</p>
          </div>
        </div>
        <div className="mt-8">
          <a
            href="/importers"
            className="inline-flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded font-bold text-lg transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            <span>Ir a Importadores</span>
          </a>
        </div>
        <div className="mt-8 text-gray-500 text-sm">
          <p className="flex items-center justify-center space-x-2">
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <span>Revisa el README.md para instrucciones de uso</span>
          </p>
          <p className="mt-2">
            API Docs (dev):{" "}
            <code className="text-teal-400">http://localhost:8000/docs</code>
          </p>
        </div>
      </div>
    </div>
  );
}
