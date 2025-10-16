interface Importer {
  id: string
  name: string
  color: string
}

interface ImporterTabsProps {
  importers: Importer[]
  activeImporter: string
  onTabChange: (id: string) => void
}

const colorClasses = {
  blue: 'border-blue-500 text-blue-400 bg-blue-500/10',
  green: 'border-green-500 text-green-400 bg-green-500/10',
  purple: 'border-purple-500 text-purple-400 bg-purple-500/10',
  orange: 'border-orange-500 text-orange-400 bg-orange-500/10',
}

export function ImporterTabs({ importers, activeImporter, onTabChange }: ImporterTabsProps) {
  return (
    <div className="flex space-x-2 border-b border-gray-700">
      {importers.map((importer) => {
        const isActive = activeImporter === importer.id
        const colorClass = colorClasses[importer.color as keyof typeof colorClasses]

        return (
          <button
            key={importer.id}
            onClick={() => onTabChange(importer.id)}
            className={`
              px-6 py-3 font-medium rounded-t-lg transition-all
              ${isActive
                ? `${colorClass} border-b-2`
                : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800/50'
              }
            `}
          >
            {importer.name}
          </button>
        )
      })}
    </div>
  )
}
