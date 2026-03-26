// frontend/src/components/Header.tsx
import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-green-600">
            Plantas IA
          </h1>
          <nav className="hidden md:flex space-x-6">
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              Inicio
            </a>
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              Acerca de
            </a>
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              Contacto
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};