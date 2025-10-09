'use client'

import { ReactNode } from 'react';

interface Tab {
  id: string;
  name: string;
  available: boolean;
}

interface PageHeaderProps {
  title: string;
  tabs?: Tab[];
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
  actions?: ReactNode;
  stats?: ReactNode;
}

const PageHeader = ({ 
  title, 
  tabs, 
  activeTab, 
  onTabChange, 
  actions,
  stats 
}: PageHeaderProps) => {
  return (
    <header className="bg-gray-800/95 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-20">
      <div className="px-8 py-4">
        {/* Título y acciones principales */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-white">{title}</h1>
            {stats && (
              <div className="flex gap-2 text-xs">
                {stats}
              </div>
            )}
          </div>
          
          {actions && (
            <div className="flex gap-3">
              {actions}
            </div>
          )}
        </div>

        {/* Tabs si existen */}
        {tabs && tabs.length > 0 && (
          <div className="border-b border-gray-600">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => tab.available && onTabChange?.(tab.id)}
                  className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                  } ${!tab.available ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                  disabled={!tab.available}
                >
                  {tab.name}
                  {!tab.available && (
                    <span className="ml-2 text-xs text-gray-500">(Próximamente)</span>
                  )}
                </button>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default PageHeader;