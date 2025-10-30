/**
 * PageHeader Component
 * Header estandarizado para todas las páginas de la aplicación
 */

interface PageHeaderProps {
  title: string;
  description?: React.ReactNode;
  icon: React.ReactNode;
}

export function PageHeader({ title, description, icon }: PageHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center space-x-3 mb-2">
        {icon}
        <h1 className="text-3xl font-bold text-white">{title}</h1>
      </div>
      {description && (
        <div className="text-gray-400">
          {typeof description === "string" ? <p>{description}</p> : description}
        </div>
      )}
    </div>
  );
}
