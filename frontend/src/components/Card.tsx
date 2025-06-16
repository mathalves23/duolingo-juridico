import React from 'react';
import {
  SparklesIcon,
  StarIcon,
  TrophyIcon,
  FireIcon,
  LockClosedIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  ArrowTopRightOnSquareIcon,
  HeartIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import {
  StarIcon as StarSolid,
  TrophyIcon as TrophySolid,
  FireIcon as FireSolid,
  HeartIcon as HeartSolid,
  CheckCircleIcon as CheckCircleSolid
} from '@heroicons/react/24/solid';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'premium' | 'success' | 'warning' | 'danger' | 'info' | 'dark' | 'gradient' | 'glass' | 'achievement' | 'locked';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  hover?: boolean;
  glow?: boolean;
  interactive?: boolean;
  onClick?: () => void;
  icon?: React.ComponentType<any>;
  title?: string;
  subtitle?: string;
  badge?: string;
  badgeColor?: string;
  progress?: number;
  showProgress?: boolean;
  isNew?: boolean;
  isCompleted?: boolean;
  isLocked?: boolean;
  xpReward?: number;
  coinsReward?: number;
  difficulty?: 'easy' | 'medium' | 'hard' | 'expert';
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  size = 'md',
  hover = false,
  glow = false,
  interactive = false,
  onClick,
  icon: Icon,
  title,
  subtitle,
  badge,
  badgeColor = 'primary',
  progress = 0,
  showProgress = false,
  isNew = false,
  isCompleted = false,
  isLocked = false,
  xpReward,
  coinsReward,
  difficulty
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'premium':
        return 'bg-gradient-to-br from-gold-50 via-gold-100 to-gold-50 border-gold-300 shadow-glow-gold relative overflow-hidden';
      case 'success':
        return 'bg-gradient-to-br from-success-50 to-success-100 border-success-300 shadow-glow';
      case 'warning':
        return 'bg-gradient-to-br from-warning-50 to-warning-100 border-warning-300 shadow-glow';
      case 'danger':
        return 'bg-gradient-to-br from-danger-50 to-danger-100 border-danger-300 shadow-glow';
      case 'info':
        return 'bg-gradient-to-br from-primary-50 to-primary-100 border-primary-300 shadow-glow';
      case 'dark':
        return 'bg-gradient-to-br from-navy-800 to-navy-900 border-navy-700 text-white shadow-strong';
      case 'gradient':
        return 'bg-gradient-to-br from-primary-500 via-primary-600 to-navy-700 text-white shadow-strong border-transparent';
      case 'glass':
        return 'bg-white/20 backdrop-blur-lg border-white/30 shadow-strong';
      case 'achievement':
        return 'bg-gradient-to-br from-gold-100 via-gold-50 to-warning-50 border-gold-400 shadow-glow-gold relative overflow-hidden';
      case 'locked':
        return 'bg-gradient-to-br from-navy-100 to-navy-200 border-navy-300 opacity-60';
      default:
        return 'bg-white/80 backdrop-blur-sm border-white/20 shadow-soft hover:bg-white/90';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'p-4 rounded-xl';
      case 'md':
        return 'p-6 rounded-2xl';
      case 'lg':
        return 'p-8 rounded-3xl';
      case 'xl':
        return 'p-10 rounded-3xl';
      default:
        return 'p-6 rounded-2xl';
    }
  };

  const getHoverClasses = () => {
    if (!hover && !interactive) return '';
    return 'hover:shadow-medium hover:border-primary-200 hover:-translate-y-1 transition-all duration-300 cursor-pointer';
  };

  const getGlowClasses = () => {
    if (!glow) return '';
    switch (variant) {
      case 'premium':
      case 'achievement':
        return 'shadow-glow-gold';
      case 'success':
        return 'shadow-glow';
      case 'gradient':
        return 'shadow-glow';
      default:
        return 'shadow-glow';
    }
  };

  const getDifficultyColor = () => {
    switch (difficulty) {
      case 'easy':
        return 'from-success-500 to-success-600';
      case 'medium':
        return 'from-warning-500 to-warning-600';
      case 'hard':
        return 'from-danger-500 to-danger-600';
      case 'expert':
        return 'from-purple-500 to-purple-600';
      default:
        return 'from-primary-500 to-primary-600';
    }
  };

  const getBadgeColorClasses = () => {
    switch (badgeColor) {
      case 'success':
        return 'bg-success-100 text-success-800 border-success-200';
      case 'warning':
        return 'bg-warning-100 text-warning-800 border-warning-200';
      case 'danger':
        return 'bg-danger-100 text-danger-800 border-danger-200';
      case 'gold':
        return 'bg-gold-100 text-gold-800 border-gold-200';
      case 'navy':
        return 'bg-navy-100 text-navy-800 border-navy-200';
      default:
        return 'bg-primary-100 text-primary-800 border-primary-200';
    }
  };

  const cardClasses = `
    ${getSizeClasses()}
    ${getVariantClasses()}
    ${getHoverClasses()}
    ${getGlowClasses()}
    border transition-all duration-300
    ${interactive || onClick ? 'cursor-pointer' : ''}
    ${isLocked ? 'pointer-events-none' : ''}
    ${className}
  `.trim();

  const handleClick = () => {
    if (onClick && !isLocked) {
      onClick();
    }
  };

  return (
    <div className={cardClasses} onClick={handleClick}>
      {/* Premium/Achievement Background Pattern */}
      {(variant === 'premium' || variant === 'achievement') && (
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-gold-400 to-transparent rounded-full blur-2xl"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-gold-300 to-transparent rounded-full blur-xl"></div>
        </div>
      )}

      {/* New Badge */}
      {isNew && (
        <div className="absolute -top-2 -right-2 z-10">
          <div className="bg-gradient-to-r from-danger-500 to-warning-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-medium animate-pulse">
            NOVO!
          </div>
        </div>
      )}

      {/* Completed Badge */}
      {isCompleted && (
        <div className="absolute -top-2 -right-2 z-10">
          <div className="bg-gradient-to-r from-success-500 to-success-600 p-2 rounded-full shadow-medium">
            <CheckCircleSolid className="h-4 w-4 text-white" />
          </div>
        </div>
      )}

      {/* Locked Overlay */}
      {isLocked && (
        <div className="absolute inset-0 flex items-center justify-center bg-navy-900/20 backdrop-blur-sm rounded-2xl z-10">
          <div className="text-center">
            <LockClosedIcon className="h-12 w-12 text-navy-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-navy-600">Bloqueado</p>
          </div>
        </div>
      )}

      <div className="relative z-10">
        {/* Header Section */}
        {(Icon || title || badge || xpReward || coinsReward) && (
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              {Icon && (
                <div className={`p-3 rounded-2xl ${
                  variant === 'dark' || variant === 'gradient' 
                    ? 'bg-white/20' 
                    : variant === 'premium' || variant === 'achievement'
                    ? 'bg-gradient-to-br from-gold-500 to-gold-600 shadow-glow-gold'
                    : 'bg-gradient-to-br from-primary-500 to-primary-600 shadow-glow'
                } transition-transform duration-300 hover:scale-110`}>
                  <Icon className={`h-6 w-6 ${
                    variant === 'dark' || variant === 'gradient' || variant === 'premium' || variant === 'achievement'
                      ? 'text-white' 
                      : 'text-white'
                  }`} />
                </div>
              )}
              
              {title && (
                <div>
                  <h3 className={`font-bold text-lg ${
                    variant === 'dark' || variant === 'gradient' ? 'text-white' : 'text-navy-800'
                  }`}>
                    {title}
                  </h3>
                  {subtitle && (
                    <p className={`text-sm ${
                      variant === 'dark' || variant === 'gradient' ? 'text-white/70' : 'text-navy-500'
                    }`}>
                      {subtitle}
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {/* Difficulty Badge */}
              {difficulty && (
                <div className={`px-2 py-1 bg-gradient-to-r ${getDifficultyColor()} text-white text-xs font-bold rounded-full`}>
                  {difficulty.toUpperCase()}
                </div>
              )}

              {/* Custom Badge */}
              {badge && (
                <div className={`badge ${getBadgeColorClasses()}`}>
                  {badge}
                </div>
              )}

              {/* Rewards */}
              {xpReward && (
                <div className="flex items-center space-x-1 px-2 py-1 bg-gold-100 rounded-full">
                  <TrophySolid className="h-3 w-3 text-gold-600" />
                  <span className="text-xs font-bold text-gold-800">+{xpReward}</span>
                </div>
              )}

              {coinsReward && (
                <div className="flex items-center space-x-1 px-2 py-1 bg-warning-100 rounded-full">
                  <SparklesIcon className="h-3 w-3 text-warning-600" />
                  <span className="text-xs font-bold text-warning-800">{coinsReward}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Content */}
        <div className={variant === 'dark' || variant === 'gradient' ? 'text-white' : ''}>
          {children}
        </div>

        {/* Progress Bar */}
        {showProgress && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className={`text-sm font-medium ${
                variant === 'dark' || variant === 'gradient' ? 'text-white/70' : 'text-navy-600'
              }`}>
                Progresso
              </span>
              <span className={`text-sm font-bold ${
                variant === 'dark' || variant === 'gradient' ? 'text-white' : 'text-primary-600'
              }`}>
                {Math.round(progress)}%
              </span>
            </div>
            <div className={`w-full rounded-full h-2 ${
              variant === 'dark' || variant === 'gradient' ? 'bg-white/20' : 'bg-navy-100'
            }`}>
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  variant === 'premium' || variant === 'achievement'
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600'
                    : 'bg-gradient-to-r from-primary-500 to-primary-600'
                }`}
                style={{ width: `${progress}%` }}
              >
                <div className="h-full bg-white/30 rounded-full animate-shimmer"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Specialized Card Components
export const StatsCard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ComponentType<any>;
  color?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}> = ({ title, value, subtitle, icon: Icon, color = 'primary', trend, trendValue }) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <ArrowTopRightOnSquareIcon className="h-4 w-4 text-success-600" />;
      case 'down':
        return <ArrowTopRightOnSquareIcon className="h-4 w-4 text-danger-600 rotate-180" />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-success-600';
      case 'down':
        return 'text-danger-600';
      default:
        return 'text-navy-500';
    }
  };

  return (
    <Card hover glow className="group">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 bg-gradient-to-br from-${color}-500 to-${color}-600 rounded-2xl shadow-glow group-hover:scale-110 transition-transform duration-300`}>
          <Icon className="h-8 w-8 text-white" />
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-navy-800">{value}</p>
          <p className="text-sm text-navy-500 font-medium">{title}</p>
        </div>
      </div>
      {(subtitle || trend) && (
        <div className="flex items-center justify-between">
          {subtitle && <span className="text-xs text-navy-400">{subtitle}</span>}
          {trend && trendValue && (
            <div className="flex items-center space-x-1">
              {getTrendIcon()}
              <span className={`text-xs font-bold ${getTrendColor()}`}>{trendValue}</span>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export const AchievementCard: React.FC<{
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  isUnlocked?: boolean;
  xpReward?: number;
  rarity?: 'common' | 'rare' | 'epic' | 'legendary';
}> = ({ title, description, icon: Icon, isUnlocked = false, xpReward, rarity = 'common' }) => {
  const getRarityColor = () => {
    switch (rarity) {
      case 'rare':
        return 'from-primary-500 to-primary-600';
      case 'epic':
        return 'from-purple-500 to-purple-600';
      case 'legendary':
        return 'from-gold-500 to-gold-600';
      default:
        return 'from-navy-500 to-navy-600';
    }
  };

  const getRarityBg = () => {
    switch (rarity) {
      case 'rare':
        return 'from-primary-50 to-primary-100 border-primary-300';
      case 'epic':
        return 'from-purple-50 to-purple-100 border-purple-300';
      case 'legendary':
        return 'from-gold-50 to-gold-100 border-gold-300';
      default:
        return 'from-navy-50 to-navy-100 border-navy-300';
    }
  };

  return (
    <Card 
      variant={isUnlocked ? 'achievement' : 'locked'}
      hover={isUnlocked}
      glow={isUnlocked}
      isLocked={!isUnlocked}
      className={`relative overflow-hidden ${isUnlocked ? getRarityBg() : ''}`}
    >
      {isUnlocked && (
        <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-gold-400/20 to-transparent rounded-full blur-xl"></div>
      )}
      
      <div className="relative z-10">
        <div className="flex items-center space-x-4 mb-4">
          <div className={`p-4 rounded-2xl ${
            isUnlocked 
              ? `bg-gradient-to-br ${getRarityColor()} shadow-glow`
              : 'bg-navy-200'
          } transition-transform duration-300 hover:scale-110`}>
            <Icon className={`h-8 w-8 ${isUnlocked ? 'text-white' : 'text-navy-400'}`} />
          </div>
          <div className="flex-1">
            <h3 className={`font-bold text-lg ${isUnlocked ? 'text-navy-800' : 'text-navy-500'}`}>
              {title}
            </h3>
            <p className={`text-sm ${isUnlocked ? 'text-navy-600' : 'text-navy-400'}`}>
              {description}
            </p>
          </div>
        </div>

        {isUnlocked && xpReward && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1 px-3 py-1 bg-gold-100 rounded-full">
              <TrophySolid className="h-4 w-4 text-gold-600" />
              <span className="text-sm font-bold text-gold-800">+{xpReward} XP</span>
            </div>
            <div className={`px-2 py-1 bg-gradient-to-r ${getRarityColor()} text-white text-xs font-bold rounded-full`}>
              {rarity.toUpperCase()}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export const NotificationCard: React.FC<{
  type: 'success' | 'warning' | 'danger' | 'info';
  title: string;
  message: string;
  onClose?: () => void;
  action?: {
    label: string;
    onClick: () => void;
  };
}> = ({ type, title, message, onClose, action }) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircleSolid className="h-6 w-6 text-success-600" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-6 w-6 text-warning-600" />;
      case 'danger':
        return <XCircleIcon className="h-6 w-6 text-danger-600" />;
      default:
        return <InformationCircleIcon className="h-6 w-6 text-primary-600" />;
    }
  };

  return (
    <Card variant={type} className="animate-slideInRight">
      <div className="flex items-start space-x-3">
        {getIcon()}
        <div className="flex-1">
          <h4 className="font-semibold text-navy-800 mb-1">{title}</h4>
          <p className="text-sm text-navy-600">{message}</p>
          {action && (
            <button 
              onClick={action.onClick}
              className="mt-2 text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors"
            >
              {action.label}
            </button>
          )}
        </div>
        {onClose && (
          <button 
            onClick={onClose}
            className="text-navy-400 hover:text-navy-600 transition-colors"
          >
            <XCircleIcon className="h-5 w-5" />
          </button>
        )}
      </div>
    </Card>
  );
};

export default Card; 