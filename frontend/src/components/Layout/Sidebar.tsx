import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  HomeIcon,
  BookOpenIcon,
  QuestionMarkCircleIcon,
  TrophyIcon,
  ChartBarIcon,
  ShoppingBagIcon,
  DocumentTextIcon,
  CogIcon,
  SparklesIcon,
  AcademicCapIcon,
  UserGroupIcon,
  BeakerIcon,
  RocketLaunchIcon,
  LightBulbIcon,
  FireIcon,
  StarIcon,
  GiftIcon,
  BoltIcon,
  HeartIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeSolid,
  BookOpenIcon as BookSolid,
  QuestionMarkCircleIcon as QuestionSolid,
  TrophyIcon as TrophySolid,
  ChartBarIcon as ChartSolid,
  ShoppingBagIcon as ShoppingSolid,
  DocumentTextIcon as DocumentSolid,
  CogIcon as CogSolid,
  FireIcon as FireSolid,
  StarIcon as StarSolid
} from '@heroicons/react/24/solid';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: React.ComponentType<any>;
  iconSolid: React.ComponentType<any>;
  badge?: string | number;
  color: string;
  description: string;
  isNew?: boolean;
  isPremium?: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const mainNavItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/',
      icon: HomeIcon,
      iconSolid: HomeSolid,
      color: 'from-primary-500 to-primary-600',
      description: 'Visão geral do seu progresso'
    },
    {
      id: 'subjects',
      label: 'Disciplinas',
      path: '/subjects',
      icon: BookOpenIcon,
      iconSolid: BookSolid,
      color: 'from-legal-500 to-legal-600',
      description: 'Explore todas as matérias'
    },
    {
      id: 'questions',
      label: 'Questões',
      path: '/questions',
      icon: QuestionMarkCircleIcon,
      iconSolid: QuestionSolid,
      badge: '2.5k',
      color: 'from-purple-500 to-purple-600',
      description: 'Pratique com questões reais'
    },
    {
      id: 'quizzes',
      label: 'Simulados',
      path: '/quizzes',
      icon: DocumentTextIcon,
      iconSolid: DocumentSolid,
      color: 'from-cyan-500 to-cyan-600',
      description: 'Teste seus conhecimentos'
    }
  ];

  const progressNavItems: NavItem[] = [
    {
      id: 'achievements',
      label: 'Conquistas',
      path: '/achievements',
      icon: TrophyIcon,
      iconSolid: TrophySolid,
      badge: 15,
      color: 'from-gold-500 to-gold-600',
      description: 'Suas medalhas e troféus'
    },
    {
      id: 'leaderboard',
      label: 'Ranking',
      path: '/leaderboard',
      icon: ChartBarIcon,
      iconSolid: ChartSolid,
      color: 'from-rose-500 to-rose-600',
      description: 'Compare-se com outros usuários'
    },
    {
      id: 'analytics',
      label: 'Estatísticas',
      path: '/analytics',
      icon: ChartBarIcon,
      iconSolid: ChartSolid,
      color: 'from-indigo-500 to-indigo-600',
      description: 'Análise detalhada do desempenho'
    }
  ];

  const premiumNavItems: NavItem[] = [
    {
      id: 'store',
      label: 'Loja',
      path: '/store',
      icon: ShoppingBagIcon,
      iconSolid: ShoppingSolid,
      color: 'from-emerald-500 to-emerald-600',
      description: 'Itens e upgrades especiais'
    },
    {
      id: 'ai-assistant',
      label: 'IA Assistente',
      path: '/ai-assistant',
      icon: SparklesIcon,
      iconSolid: SparklesIcon,
      color: 'from-violet-500 to-violet-600',
      description: 'Seu tutor pessoal inteligente',
      isNew: true,
      isPremium: true
    }
  ];

  const settingsNavItems: NavItem[] = [
    {
      id: 'settings',
      label: 'Configurações',
      path: '/settings',
      icon: CogIcon,
      iconSolid: CogSolid,
      color: 'from-slate-500 to-slate-600',
      description: 'Personalize sua experiência'
    }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    if (window.innerWidth < 1024) {
      onClose();
    }
  };

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const renderNavItem = (item: NavItem) => {
    const active = isActive(item.path);
    const IconComponent = active ? item.iconSolid : item.icon;
    const isHovered = hoveredItem === item.id;

    return (
      <div key={item.id} className="relative">
        <button
          onClick={() => handleNavigation(item.path)}
          onMouseEnter={() => setHoveredItem(item.id)}
          onMouseLeave={() => setHoveredItem(null)}
          className={`
            w-full flex items-center space-x-3 px-4 py-3 rounded-2xl transition-all duration-300 group relative overflow-hidden
            ${active 
              ? 'bg-gradient-to-r ' + item.color + ' text-white shadow-colored-primary transform scale-105' 
              : 'text-slate-200 hover:bg-white/20 hover:text-white'
            }
          `}
        >
          {/* Background Gradient on Hover */}
          {!active && (
            <div className={`absolute inset-0 bg-gradient-to-r ${item.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300 rounded-2xl`} />
          )}

          {/* Icon Container */}
          <div className={`
            relative p-2 rounded-xl transition-all duration-300
            ${active 
              ? 'bg-white/20 shadow-soft' 
              : 'bg-transparent group-hover:bg-white/10'
            }
          `}>
            <IconComponent className={`h-5 w-5 transition-all duration-300 ${active ? 'text-white' : 'text-slate-300 group-hover:text-white'}`} />
            
            {/* Badges */}
            {item.badge && (
              <div className="absolute -top-1 -right-1 min-w-[18px] h-[18px] bg-gradient-to-r from-danger-500 to-rose-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold px-1">
                  {typeof item.badge === 'number' && item.badge > 99 ? '99+' : item.badge}
                </span>
              </div>
            )}
          </div>

          {/* Label and Description */}
          <div className="flex-1 text-left">
            <div className="flex items-center space-x-2">
              <span className={`font-semibold transition-colors duration-300 ${active ? 'text-white' : 'text-slate-200'}`}>
                {item.label}
              </span>
              
              {/* New Badge */}
              {item.isNew && (
                <span className="badge badge-gold text-xs animate-pulse">
                  NOVO
                </span>
              )}
              
              {/* Premium Badge */}
              {item.isPremium && (
                <div className="flex items-center space-x-1">
                  <StarSolid className="h-3 w-3 text-gold-400" />
                  <span className="text-xs font-bold text-gold-400">PRO</span>
                </div>
              )}
            </div>
            
            {/* Description (visible on hover) */}
            <p className={`text-xs transition-all duration-300 ${
              active ? 'text-white/80' : 'text-slate-300'
            } ${isHovered ? 'opacity-100 max-h-10' : 'opacity-0 max-h-0'} overflow-hidden`}>
              {item.description}
            </p>
          </div>

          {/* Active Indicator */}
          {active && (
            <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-white rounded-l-full" />
          )}
        </button>
      </div>
    );
  };

  const renderSection = (title: string, items: NavItem[], icon?: React.ComponentType<any>) => {
    const IconComponent = icon;
    
    return (
      <div className="space-y-2">
        <div className="flex items-center space-x-2 px-4 py-2">
          {IconComponent && <IconComponent className="h-4 w-4 text-slate-400" />}
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            {title}
          </h3>
        </div>
        <div className="space-y-1">
          {items.map(renderNavItem)}
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-navy-900/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-80 sidebar-glass border-r border-white/10 z-50 transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-auto
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-legal-500 to-legal-600 rounded-3xl flex items-center justify-center shadow-colored-legal">
                  <AcademicCapIcon className="h-7 w-7 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-r from-gold-500 to-gold-600 rounded-full flex items-center justify-center animate-pulse">
                  <SparklesIcon className="h-3 w-3 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">Duolingo Jurídico</h1>
                <p className="text-sm text-white/70">Rumo à aprovação! 🚀</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 overflow-y-auto py-6 space-y-8">
            {/* Main Navigation */}
            {renderSection('Principal', mainNavItems, HomeIcon)}

            {/* Progress & Stats */}
            {renderSection('Progresso', progressNavItems, TrophyIcon)}

            {/* Premium Features */}
            {renderSection('Premium', premiumNavItems, StarIcon)}

            {/* Settings */}
            {renderSection('Configurações', settingsNavItems, CogIcon)}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-white/10">
            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="glass rounded-2xl p-3 text-center">
                <FireSolid className="h-5 w-5 text-orange-500 mx-auto mb-1" />
                <p className="text-xs text-white/70">Sequência</p>
                <p className="font-bold text-white">12 dias</p>
              </div>
              <div className="glass rounded-2xl p-3 text-center">
                <TrophySolid className="h-5 w-5 text-gold-500 mx-auto mb-1" />
                <p className="text-xs text-white/70">Nível</p>
                <p className="font-bold text-white">3</p>
              </div>
            </div>

            {/* Upgrade Button */}
            <button className="w-full btn btn-gold btn-sm group">
              <RocketLaunchIcon className="h-4 w-4 mr-2 group-hover:animate-bounce" />
              Upgrade para Pro
              <SparklesIcon className="h-4 w-4 ml-2" />
            </button>

            {/* Version */}
            <p className="text-xs text-white/50 text-center mt-3">
              v2.0.0 • Beta
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;

