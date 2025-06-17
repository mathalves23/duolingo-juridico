import React from 'react';
import {
  TrophyIcon,
  ScaleIcon,
  BookOpenIcon,
  AcademicCapIcon,
  SparklesIcon,
  FireIcon,
  StarIcon
} from '@heroicons/react/24/outline';
import {
  TrophyIcon as TrophySolid,
  ScaleIcon as ScaleSolid,
  StarIcon as StarSolid
} from '@heroicons/react/24/solid';

interface LoadingProps {
  message?: string;
  type?: 'default' | 'questions' | 'lessons' | 'quiz' | 'achievements' | 'legal';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showProgress?: boolean;
  progress?: number;
}

const Loading: React.FC<LoadingProps> = ({ 
  message = 'Carregando...', 
  type = 'default',
  size = 'md',
  showProgress = false,
  progress = 0
}) => {
  const getLoadingIcon = () => {
    switch (type) {
      case 'questions':
        return <BookOpenIcon className="h-8 w-8 text-primary-600" />;
      case 'lessons':
        return <AcademicCapIcon className="h-8 w-8 text-success-600" />;
      case 'quiz':
        return <TrophySolid className="h-8 w-8 text-gold-600" />;
      case 'achievements':
        return <StarSolid className="h-8 w-8 text-warning-600" />;
      case 'legal':
        return <ScaleSolid className="h-8 w-8 text-navy-600" />;
      default:
        return <SparklesIcon className="h-8 w-8 text-primary-600" />;
    }
  };

  const getLoadingColor = () => {
    switch (type) {
      case 'questions':
        return 'from-primary-500 to-primary-600';
      case 'lessons':
        return 'from-success-500 to-success-600';
      case 'quiz':
        return 'from-gold-500 to-gold-600';
      case 'achievements':
        return 'from-warning-500 to-warning-600';
      case 'legal':
        return 'from-navy-500 to-navy-600';
      default:
        return 'from-primary-500 to-navy-600';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'w-6 h-6';
      case 'md':
        return 'w-8 h-8';
      case 'lg':
        return 'w-12 h-12';
      case 'xl':
        return 'w-16 h-16';
      default:
        return 'w-8 h-8';
    }
  };

  const getContainerSize = () => {
    switch (size) {
      case 'sm':
        return 'p-4';
      case 'md':
        return 'p-6';
      case 'lg':
        return 'p-8';
      case 'xl':
        return 'p-12';
      default:
        return 'p-6';
    }
  };

  const motivationalMessages = [
    "Preparando seu universo jurídico...",
    "Organizando conhecimentos para sua aprovação...",
    "Carregando sabedoria jurídica...",
    "Sincronizando com a justiça...",
    "Preparando questões desafiadoras...",
    "Ativando modo aprovação...",
    "Carregando conquistas incríveis...",
    "Preparando sua jornada de sucesso..."
  ];

  const getRandomMessage = () => {
    if (message !== 'Carregando...') return message;
    return motivationalMessages[Math.floor(Math.random() * motivationalMessages.length)];
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-6 animate-fadeInUp min-h-screen pt-20">
      {/* Main Loading Animation */}
      <div className="relative">
        {/* Outer Ring */}
        <div className={`${getSizeClasses()} border-4 border-navy-200 rounded-full animate-spin`}>
          <div className={`w-full h-full bg-gradient-to-r ${getLoadingColor()} rounded-full animate-pulse`}></div>
        </div>
        
        {/* Inner Ring */}
        <div className="absolute inset-2">
          <div className={`w-full h-full border-2 border-primary-300 rounded-full animate-spin`} style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}>
            <div className="w-full h-full bg-gradient-to-l from-gold-400 to-gold-500 rounded-full animate-pulse"></div>
          </div>
        </div>

        {/* Center Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-bounce">
            {getLoadingIcon()}
          </div>
        </div>

        {/* Floating Particles */}
        <div className="absolute -inset-4">
          <div className="absolute top-0 left-1/2 w-2 h-2 bg-primary-400 rounded-full animate-ping" style={{ animationDelay: '0s' }}></div>
          <div className="absolute top-1/2 right-0 w-1.5 h-1.5 bg-gold-400 rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
          <div className="absolute bottom-0 left-1/2 w-2 h-2 bg-success-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-0 w-1.5 h-1.5 bg-warning-400 rounded-full animate-ping" style={{ animationDelay: '1.5s' }}></div>
        </div>

        {/* Glow Effect */}
        <div className={`absolute inset-0 bg-gradient-to-r ${getLoadingColor()} rounded-full blur-xl opacity-20 animate-pulse`}></div>
      </div>

      {/* Legal Symbols Animation */}
      <div className="flex items-center space-x-4 animate-slideInUp">
        <div className="animate-bounce" style={{ animationDelay: '0s' }}>
          <ScaleIcon className="h-6 w-6 text-navy-400" />
        </div>
        <div className="animate-bounce" style={{ animationDelay: '0.2s' }}>
          <BookOpenIcon className="h-6 w-6 text-primary-400" />
        </div>
        <div className="animate-bounce" style={{ animationDelay: '0.4s' }}>
          <TrophyIcon className="h-6 w-6 text-gold-400" />
        </div>
        <div className="animate-bounce" style={{ animationDelay: '0.6s' }}>
          <AcademicCapIcon className="h-6 w-6 text-success-400" />
        </div>
        <div className="animate-bounce" style={{ animationDelay: '0.8s' }}>
          <FireIcon className="h-6 w-6 text-danger-400" />
        </div>
      </div>

      {/* Loading Message */}
      <div className="text-center space-y-2 animate-slideInUp" style={{ animationDelay: '0.3s' }}>
        <p className="text-lg font-semibold text-navy-700 animate-pulse">
          {getRandomMessage()}
        </p>
        <div className="flex items-center justify-center space-x-1">
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>

      {/* Progress Bar (if enabled) */}
      {showProgress && (
        <div className="w-64 animate-slideInUp" style={{ animationDelay: '0.5s' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-navy-600">Progresso</span>
            <span className="text-sm font-bold text-primary-600">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-navy-200 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-2 bg-gradient-to-r ${getLoadingColor()} rounded-full transition-all duration-500 ease-out relative`}
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white/30 animate-shimmer"></div>
            </div>
          </div>
        </div>
      )}

      {/* Motivational Quote */}
      <div className="max-w-md text-center animate-slideInUp" style={{ animationDelay: '0.7s' }}>
        <div className="bg-gradient-to-r from-primary-50 to-gold-50 rounded-2xl p-4 border border-primary-200">
          <div className="flex items-center justify-center mb-2">
            <SparklesIcon className="h-5 w-5 text-gold-500 mr-2" />
            <span className="text-sm font-semibold text-navy-700">Dica Motivacional</span>
            <SparklesIcon className="h-5 w-5 text-gold-500 ml-2" />
          </div>
          <p className="text-sm text-navy-600 italic font-medium">
            "Cada questão resolvida é um passo mais próximo da sua aprovação!"
          </p>
        </div>
      </div>

      {/* Loading Stats */}
      <div className="flex items-center space-x-6 text-center animate-slideInUp" style={{ animationDelay: '0.9s' }}>
        <div className="flex flex-col items-center">
          <div className="flex items-center space-x-1 mb-1">
            <TrophySolid className="h-4 w-4 text-gold-500" />
            <span className="text-xs font-bold text-gold-600">XP</span>
          </div>
          <span className="text-sm font-semibold text-navy-700">2.850</span>
        </div>
        <div className="w-px h-8 bg-navy-200"></div>
        <div className="flex flex-col items-center">
          <div className="flex items-center space-x-1 mb-1">
            <FireIcon className="h-4 w-4 text-danger-500" />
            <span className="text-xs font-bold text-danger-600">Sequência</span>
          </div>
          <span className="text-sm font-semibold text-navy-700">12 dias</span>
        </div>
        <div className="w-px h-8 bg-navy-200"></div>
        <div className="flex flex-col items-center">
          <div className="flex items-center space-x-1 mb-1">
            <StarSolid className="h-4 w-4 text-warning-500" />
            <span className="text-xs font-bold text-warning-600">Precisão</span>
          </div>
          <span className="text-sm font-semibold text-navy-700">89%</span>
        </div>
      </div>
    </div>
  );
};

// Loading Skeleton Components
export const CardSkeleton: React.FC = () => (
  <div className="card animate-pulse">
    <div className="flex items-center space-x-4 mb-4">
      <div className="w-12 h-12 bg-navy-200 rounded-2xl"></div>
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-navy-200 rounded w-3/4"></div>
        <div className="h-3 bg-navy-200 rounded w-1/2"></div>
      </div>
    </div>
    <div className="space-y-3">
      <div className="h-3 bg-navy-200 rounded"></div>
      <div className="h-3 bg-navy-200 rounded w-5/6"></div>
      <div className="h-3 bg-navy-200 rounded w-4/6"></div>
    </div>
  </div>
);

export const QuestionSkeleton: React.FC = () => (
  <div className="card animate-pulse">
    <div className="flex items-center justify-between mb-6">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-navy-200 rounded-xl"></div>
        <div className="h-4 bg-navy-200 rounded w-32"></div>
      </div>
      <div className="h-6 bg-navy-200 rounded w-16"></div>
    </div>
    
    <div className="space-y-4 mb-6">
      <div className="h-4 bg-navy-200 rounded"></div>
      <div className="h-4 bg-navy-200 rounded w-5/6"></div>
      <div className="h-4 bg-navy-200 rounded w-4/6"></div>
    </div>

    <div className="space-y-3">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="flex items-center space-x-3 p-4 border border-navy-200 rounded-xl">
          <div className="w-4 h-4 bg-navy-200 rounded-full"></div>
          <div className="h-3 bg-navy-200 rounded flex-1"></div>
        </div>
      ))}
    </div>
  </div>
);

export const StatsSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {[1, 2, 3, 4].map((i) => (
      <div key={i} className="card animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-navy-200 rounded-2xl"></div>
          <div className="text-right space-y-2">
            <div className="h-6 bg-navy-200 rounded w-16"></div>
            <div className="h-3 bg-navy-200 rounded w-12"></div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between">
            <div className="h-3 bg-navy-200 rounded w-16"></div>
            <div className="h-3 bg-navy-200 rounded w-12"></div>
          </div>
          <div className="w-full h-2 bg-navy-200 rounded-full"></div>
        </div>
      </div>
    ))}
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="card animate-pulse">
    <div className="space-y-4">
      {/* Header */}
      <div className="flex space-x-4 pb-4 border-b border-navy-200">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-4 bg-navy-200 rounded flex-1"></div>
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex space-x-4 py-3">
          {[1, 2, 3, 4].map((j) => (
            <div key={j} className="h-3 bg-navy-200 rounded flex-1"></div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

export default Loading; 