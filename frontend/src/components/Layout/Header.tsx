import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  UserIcon, 
  TrophyIcon, 
  CurrencyDollarIcon,
  FireIcon,
  Bars3Icon,
  BellIcon,
  ChevronDownIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  UserCircleIcon,
  SparklesIcon,
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon,
  CommandLineIcon,
  HeartIcon,
  StarIcon,
  BoltIcon,
  GiftIcon
} from '@heroicons/react/24/outline';
import {
  FireIcon as FireSolid,
  TrophyIcon as TrophySolid,
  HeartIcon as HeartSolid,
  StarIcon as StarSolid
} from '@heroicons/react/24/solid';

interface HeaderProps {
  onMenuToggle: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  const { user, logout } = useAuth();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Atualizar horário em tempo real
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const notifications = [
    { 
      id: 1, 
      title: 'Nova conquista desbloqueada! 🏆', 
      description: 'Mestre da Consistência - 12 dias seguidos',
      time: '2 min', 
      type: 'achievement',
      icon: TrophySolid,
      color: 'from-gold-500 to-gold-600'
    },
    { 
      id: 2, 
      title: 'Desafio diário disponível 🎯', 
      description: 'Complete 25 questões hoje e ganhe 150 XP',
      time: '1 hora', 
      type: 'challenge',
      icon: BoltIcon,
      color: 'from-primary-500 to-purple-500'
    },
    { 
      id: 3, 
      title: 'Você subiu no ranking! 📈', 
      description: 'Agora você está em 3º lugar na liga',
      time: '3 horas', 
      type: 'ranking',
      icon: StarSolid,
      color: 'from-legal-500 to-legal-600'
    },
    { 
      id: 4, 
      title: 'Oferta especial! 🎁', 
      description: '50% de desconto no plano premium',
      time: '1 dia', 
      type: 'offer',
      icon: GiftIcon,
      color: 'from-rose-500 to-rose-600'
    },
  ];

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const userStats = {
    xp: user?.profile?.xp_points || 2850,
    coins: user?.profile?.coins || 540,
    streak: user?.profile?.current_streak || 12,
    hearts: 5,
    level: Math.floor((user?.profile?.xp_points || 2850) / 1000) + 1
  };

  return (
    <header className="header-glass sticky top-0 z-40 transition-all duration-300">
      <div className="px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Left Section */}
          <div className="flex items-center space-x-4">
            {/* Menu Toggle (Mobile) */}
            <button
              onClick={onMenuToggle}
              className="lg:hidden p-2 rounded-2xl glass hover:bg-white/40 transition-all duration-200 hover:scale-105 focus-glass"
            >
              <Bars3Icon className="h-6 w-6 text-navy-700" />
            </button>

            {/* Logo & Brand */}
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-legal-500 to-legal-600 rounded-2xl flex items-center justify-center shadow-colored-legal">
                  <CommandLineIcon className="h-6 w-6 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-gold-500 to-gold-600 rounded-full flex items-center justify-center">
                  <SparklesIcon className="h-2.5 w-2.5 text-white" />
                </div>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-bold gradient-text">Duolingo Jurídico</h1>
                <p className="text-xs text-muted">{getGreeting()}, {user?.first_name}!</p>
              </div>
            </div>

            {/* Search Bar (Desktop) */}
            <div className="hidden md:block relative">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Buscar questões, leis, jurisprudência..."
                  className="input-glass w-80 pl-10 pr-4 py-2 text-sm"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              </div>
            </div>
          </div>

          {/* Center Section - User Stats */}
          <div className="hidden lg:flex items-center space-x-6">
            {/* XP */}
            <div className="flex items-center space-x-2 glass px-3 py-2 rounded-2xl">
              <TrophySolid className="h-5 w-5 text-gold-500" />
              <span className="font-bold text-navy-800">{userStats.xp.toLocaleString()}</span>
              <span className="text-xs text-muted">XP</span>
            </div>

            {/* Streak */}
            <div className="flex items-center space-x-2 glass px-3 py-2 rounded-2xl">
              <FireSolid className="h-5 w-5 text-orange-500 animate-pulse" />
              <span className="font-bold text-navy-800">{userStats.streak}</span>
              <span className="text-xs text-muted">dias</span>
            </div>

            {/* Coins */}
            <div className="flex items-center space-x-2 glass px-3 py-2 rounded-2xl">
              <CurrencyDollarIcon className="h-5 w-5 text-gold-500" />
              <span className="font-bold text-navy-800">{userStats.coins}</span>
            </div>

            {/* Hearts */}
            <div className="flex items-center space-x-2 glass px-3 py-2 rounded-2xl">
              <HeartSolid className="h-5 w-5 text-rose-500" />
              <span className="font-bold text-navy-800">{userStats.hearts}</span>
            </div>

            {/* Level */}
            <div className="level-badge">
              <StarSolid className="h-4 w-4 mr-1" />
              Nível {userStats.level}
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-3">
            {/* Search (Mobile) */}
            <button
              onClick={() => setSearchOpen(!searchOpen)}
              className="md:hidden p-2 rounded-2xl glass hover:bg-white/40 transition-all duration-200 hover:scale-105 focus-glass"
            >
              <MagnifyingGlassIcon className="h-5 w-5 text-navy-700" />
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-2xl glass hover:bg-white/40 transition-all duration-200 hover:scale-105 focus-glass"
            >
              {darkMode ? (
                <SunIcon className="h-5 w-5 text-yellow-500" />
              ) : (
                <MoonIcon className="h-5 w-5 text-navy-700" />
              )}
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setNotificationsOpen(!notificationsOpen)}
                className="p-2 rounded-2xl glass hover:bg-white/40 transition-all duration-200 hover:scale-105 focus-glass relative"
              >
                <BellIcon className="h-5 w-5 text-navy-700" />
                {notifications.length > 0 && (
                  <div className="notification-dot"></div>
                )}
              </button>

              {/* Notifications Dropdown */}
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 glass rounded-3xl shadow-glass-xl border border-white/20 z-50 animate-scale-in">
                  <div className="p-4 border-b border-white/10">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-navy-800">Notificações</h3>
                      <span className="badge badge-primary">{notifications.length}</span>
                    </div>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.map((notification) => {
                      const IconComponent = notification.icon;
                      return (
                        <div
                          key={notification.id}
                          className="p-4 border-b border-white/5 last:border-b-0 hover:bg-white/20 transition-colors duration-200 cursor-pointer"
                        >
                          <div className="flex items-start space-x-3">
                            <div className={`p-2 rounded-xl bg-gradient-to-r ${notification.color} shadow-soft`}>
                              <IconComponent className="h-4 w-4 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-navy-800 text-sm">{notification.title}</p>
                              <p className="text-xs text-muted mt-1">{notification.description}</p>
                              <p className="text-xs text-primary-600 mt-1">{notification.time} atrás</p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="p-4 border-t border-white/10">
                    <button className="w-full btn btn-ghost text-sm">
                      Ver todas as notificações
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-2xl glass hover:bg-white/40 transition-all duration-200 hover:scale-105 focus-glass"
              >
                <div className="relative">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <span className="text-white font-bold text-sm">
                      {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="status-online absolute -bottom-0.5 -right-0.5"></div>
                </div>
                <ChevronDownIcon className={`h-4 w-4 text-navy-700 transition-transform duration-200 ${userMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* User Dropdown */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 glass rounded-3xl shadow-glass-xl border border-white/20 z-50 animate-scale-in">
                  <div className="p-4 border-b border-white/10">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl flex items-center justify-center">
                        <span className="text-white font-bold text-lg">
                          {user?.first_name?.charAt(0)?.toUpperCase() || 'U'}
                        </span>
                      </div>
                      <div>
                        <p className="font-semibold text-navy-800">{user?.first_name} {user?.last_name}</p>
                        <p className="text-sm text-muted">{user?.email}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <div className="level-badge text-xs">
                            Nível {userStats.level}
                          </div>
                          <span className="text-xs text-muted">•</span>
                          <span className="text-xs font-medium text-gold-600">{userStats.xp} XP</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-2">
                    <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-2xl hover:bg-white/20 transition-colors duration-200 text-left">
                      <UserCircleIcon className="h-5 w-5 text-navy-600" />
                      <span className="text-navy-800 font-medium">Meu Perfil</span>
                    </button>
                    <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-2xl hover:bg-white/20 transition-colors duration-200 text-left">
                      <TrophyIcon className="h-5 w-5 text-navy-600" />
                      <span className="text-navy-800 font-medium">Conquistas</span>
                    </button>
                    <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-2xl hover:bg-white/20 transition-colors duration-200 text-left">
                      <CogIcon className="h-5 w-5 text-navy-600" />
                      <span className="text-navy-800 font-medium">Configurações</span>
                    </button>
                  </div>

                  <div className="p-2 border-t border-white/10">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-3 px-3 py-2 rounded-2xl hover:bg-danger-50/50 transition-colors duration-200 text-left text-danger-600"
                    >
                      <ArrowRightOnRectangleIcon className="h-5 w-5" />
                      <span className="font-medium">Sair</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Search Bar */}
        {searchOpen && (
          <div className="mt-4 md:hidden animate-slide-down">
            <div className="relative">
              <input
                type="text"
                placeholder="Buscar questões, leis, jurisprudência..."
                className="input-glass w-full pl-10 pr-4 py-3"
                autoFocus
              />
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
            </div>
          </div>
        )}

        {/* Mobile Stats Bar */}
        <div className="lg:hidden mt-4 flex items-center justify-between space-x-2">
          <div className="flex items-center space-x-1 glass px-2 py-1 rounded-xl flex-1">
            <TrophySolid className="h-4 w-4 text-gold-500" />
            <span className="font-bold text-navy-800 text-sm">{userStats.xp.toLocaleString()}</span>
          </div>
          <div className="flex items-center space-x-1 glass px-2 py-1 rounded-xl flex-1">
            <FireSolid className="h-4 w-4 text-orange-500" />
            <span className="font-bold text-navy-800 text-sm">{userStats.streak}</span>
          </div>
          <div className="flex items-center space-x-1 glass px-2 py-1 rounded-xl flex-1">
            <CurrencyDollarIcon className="h-4 w-4 text-gold-500" />
            <span className="font-bold text-navy-800 text-sm">{userStats.coins}</span>
          </div>
          <div className="flex items-center space-x-1 glass px-2 py-1 rounded-xl flex-1">
            <HeartSolid className="h-4 w-4 text-rose-500" />
            <span className="font-bold text-navy-800 text-sm">{userStats.hearts}</span>
          </div>
        </div>
      </div>

      {/* Click outside handlers */}
      {(userMenuOpen || notificationsOpen) && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => {
            setUserMenuOpen(false);
            setNotificationsOpen(false);
          }}
        />
      )}
    </header>
  );
};

export default Header;

