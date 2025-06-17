import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleMenuToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-primary-50/30 relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Animated Blobs */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-gradient-to-r from-primary-400/20 to-purple-400/20 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute top-40 right-20 w-96 h-96 bg-gradient-to-r from-cyan-400/20 to-legal-400/20 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-gradient-to-r from-rose-400/20 to-gold-400/20 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
        
        {/* Mesh Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-mesh opacity-30"></div>
        
        {/* Subtle Pattern */}
        <div className="absolute inset-0 bg-legal-pattern opacity-5"></div>
      </div>

      {/* Layout Structure - Flex row com altura total */}
      <div className="relative z-10 flex h-screen">
        {/* Sidebar - Altura total da tela */}
        <Sidebar isOpen={sidebarOpen} onClose={handleSidebarClose} />

        {/* Main Content Area - Flex column */}
        <div className="flex-1 flex flex-col min-w-0 lg:ml-0">
          {/* Header */}
          <Header onMenuToggle={handleMenuToggle} />

          {/* Main Content com Footer incorporado */}
          <main className="flex-1 overflow-y-auto min-h-0 flex flex-col">
            {/* Content Area */}
            <div className="flex-1">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
                {/* Content with Glass Effect */}
                <div className="relative min-h-full">
                  {children}
                </div>
              </div>
            </div>

            {/* Footer integrado ao conteúdo principal */}
            <footer className="glass border-t border-white/10 py-6 shrink-0 mt-auto">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
                  <div className="flex items-center space-x-4">
                    <p className="text-sm text-navy-600">
                      © 2024 Duolingo Jurídico. Todos os direitos reservados.
                    </p>
                  </div>
                  <div className="flex items-center space-x-6">
                    <button className="text-sm text-navy-600 hover:text-primary-600 transition-colors duration-200">
                      Política de Privacidade
                    </button>
                    <button className="text-sm text-navy-600 hover:text-primary-600 transition-colors duration-200">
                      Termos de Uso
                    </button>
                    <button className="text-sm text-navy-600 hover:text-primary-600 transition-colors duration-200">
                      Suporte
                    </button>
                  </div>
                </div>
              </div>
            </footer>
          </main>
        </div>
      </div>

      {/* Floating Action Button (Mobile) */}
      <div className="fixed bottom-6 right-6 lg:hidden z-50">
        <button className="w-14 h-14 bg-gradient-to-r from-primary-600 to-purple-600 rounded-full shadow-colored-primary flex items-center justify-center text-white hover:scale-110 transition-transform duration-300">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-navy-900/50 backdrop-blur-sm z-30 lg:hidden"
          onClick={handleSidebarClose}
        />
      )}
    </div>
  );
};

export default Layout;

