import React from 'react';
import { FiSun } from 'react-icons/fi';

export const Header: React.FC = () => {
  return (
    <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-green-100 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FiSun className="w-8 h-8 text-green-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">AgroPlantas Colombia</h1>
              <p className="text-xs text-gray-500">IA para el sector agrícola</p>
            </div>
          </div>
          <nav className="hidden md:flex space-x-6 text-sm">
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              Inicio
            </a>
            <a href="#metodologia" className="text-gray-600 hover:text-green-600 transition-colors">
              Metodología
            </a>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-gray-600 hover:text-green-600 transition-colors"
            >
              API Docs
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};
