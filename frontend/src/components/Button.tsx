import React from 'react';
import {
  SparklesIcon,
  ArrowRightIcon,
  PlayIcon,
  PauseIcon,
  CheckIcon,
  XMarkIcon,
  PlusIcon,
  MinusIcon,
  HeartIcon,
  StarIcon,
  TrophyIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';
import {
  HeartIcon as HeartSolid,
  StarIcon as StarSolid,
  TrophyIcon as TrophySolid
} from '@heroicons/react/24/solid';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'gold' | 'outline' | 'ghost' | 'gradient' | 'glass' | 'premium';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  rounded?: boolean;
  glow?: boolean;
  pulse?: boolean;
  bounce?: boolean;
  className?: string;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  icon?: React.ComponentType<any>;
  iconPosition?: 'left' | 'right';
  badge?: string | number;
  tooltip?: string;
  href?: string;
  target?: string;
  animate?: boolean;
  xpReward?: number;
  coinsReward?: number;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  rounded = false,
  glow = false,
  pulse = false,
  bounce = false,
  className = '',
  onClick,
  type = 'button',
  icon: Icon,
  iconPosition = 'left',
  badge,
  tooltip,
  href,
  target,
  animate = false,
  xpReward,
  coinsReward
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white focus:ring-primary-300 shadow-glow border-transparent';
      case 'secondary':
        return 'bg-gradient-to-r from-navy-600 to-navy-700 hover:from-navy-700 hover:to-navy-800 text-white focus:ring-navy-300 border-transparent';
      case 'success':
        return 'bg-gradient-to-r from-success-600 to-success-700 hover:from-success-700 hover:to-success-800 text-white focus:ring-success-300 border-transparent';
      case 'warning':
        return 'bg-gradient-to-r from-warning-600 to-warning-700 hover:from-warning-700 hover:to-warning-800 text-white focus:ring-warning-300 border-transparent';
      case 'danger':
        return 'bg-gradient-to-r from-danger-600 to-danger-700 hover:from-danger-700 hover:to-danger-800 text-white focus:ring-danger-300 border-transparent';
      case 'gold':
        return 'bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-600 hover:to-gold-700 text-white focus:ring-gold-300 shadow-glow-gold border-transparent';
      case 'outline':
        return 'bg-transparent border-2 border-primary-600 text-primary-600 hover:bg-primary-600 hover:text-white focus:ring-primary-300';
      case 'ghost':
        return 'bg-transparent text-navy-600 hover:bg-navy-100 focus:ring-navy-300 shadow-none border-transparent';
      case 'gradient':
        return 'bg-gradient-to-r from-primary-500 via-primary-600 to-navy-700 hover:from-primary-600 hover:via-primary-700 hover:to-navy-800 text-white focus:ring-primary-300 shadow-glow border-transparent';
      case 'glass':
        return 'bg-white/20 backdrop-blur-lg border border-white/30 text-navy-800 hover:bg-white/30 focus:ring-primary-300 shadow-medium';
      case 'premium':
        return 'bg-gradient-to-r from-gold-500 via-gold-600 to-gold-500 hover:from-gold-600 hover:via-gold-700 hover:to-gold-600 text-white focus:ring-gold-300 shadow-glow-gold border-transparent relative overflow-hidden';
      default:
        return 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white focus:ring-primary-300 shadow-glow border-transparent';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'xs':
        return 'px-3 py-1.5 text-xs';
      case 'sm':
        return 'px-4 py-2 text-sm';
      case 'md':
        return 'px-6 py-3 text-sm';
      case 'lg':
        return 'px-8 py-4 text-base';
      case 'xl':
        return 'px-10 py-5 text-lg';
      default:
        return 'px-6 py-3 text-sm';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'xs':
        return 'h-3 w-3';
      case 'sm':
        return 'h-4 w-4';
      case 'md':
        return 'h-5 w-5';
      case 'lg':
        return 'h-6 w-6';
      case 'xl':
        return 'h-7 w-7';
      default:
        return 'h-5 w-5';
    }
  };

  const getAnimationClasses = () => {
    const animations = [];
    if (pulse) animations.push('animate-pulse');
    if (bounce) animations.push('animate-bounce');
    if (animate) animations.push('hover:scale-105 active:scale-95');
    return animations.join(' ');
  };

  const baseClasses = `
    inline-flex items-center justify-center font-semibold
    transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-opacity-50
    transform relative
    ${rounded ? 'rounded-full' : 'rounded-xl'}
    ${fullWidth ? 'w-full' : ''}
    ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    ${glow ? 'shadow-glow' : ''}
  `.trim();

  const buttonClasses = `
    ${baseClasses}
    ${getSizeClasses()}
    ${getVariantClasses()}
    ${getAnimationClasses()}
    ${className}
  `.trim();

  const renderIcon = (position: 'left' | 'right') => {
    if (!Icon || iconPosition !== position) return null;
    
    return (
      <Icon 
        className={`${getIconSize()} ${
          position === 'left' ? 'mr-2' : 'ml-2'
        } ${animate ? 'group-hover:animate-pulse' : ''}`} 
      />
    );
  };

  const renderLoadingSpinner = () => (
    <div className={`${getIconSize()} border-2 border-current border-t-transparent rounded-full animate-spin mr-2`}></div>
  );

  const renderBadge = () => {
    if (!badge) return null;
    
    return (
      <span className="absolute -top-2 -right-2 bg-danger-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center animate-pulse">
        {badge}
      </span>
    );
  };

  const renderRewards = () => {
    if (!xpReward && !coinsReward) return null;
    
    return (
      <div className="flex items-center space-x-2 ml-3">
        {xpReward && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-white/20 rounded-full">
            <TrophySolid className="h-3 w-3" />
            <span className="text-xs font-bold">+{xpReward}</span>
          </div>
        )}
        {coinsReward && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-white/20 rounded-full">
            <SparklesIcon className="h-3 w-3" />
            <span className="text-xs font-bold">{coinsReward}</span>
          </div>
        )}
      </div>
    );
  };

  const renderPremiumEffect = () => {
    if (variant !== 'premium') return null;
    
    return (
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
    );
  };

  const buttonContent = (
    <>
      {renderPremiumEffect()}
      {loading && renderLoadingSpinner()}
      {renderIcon('left')}
      <span className="relative z-10">{children}</span>
      {renderIcon('right')}
      {renderRewards()}
      {renderBadge()}
    </>
  );

  const handleClick = () => {
    if (!disabled && !loading && onClick) {
      onClick();
    }
  };

  if (href) {
    return (
      <a
        href={href}
        target={target}
        className={`${buttonClasses} no-underline`}
        title={tooltip}
      >
        {buttonContent}
      </a>
    );
  }

  return (
    <button
      type={type}
      className={`${buttonClasses} group`}
      onClick={handleClick}
      disabled={disabled || loading}
      title={tooltip}
    >
      {buttonContent}
    </button>
  );
};

// Specialized Button Components
export const PlayButton: React.FC<{
  isPlaying?: boolean;
  onPlay?: () => void;
  onPause?: () => void;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'success' | 'gold';
}> = ({ isPlaying = false, onPlay, onPause, size = 'md', variant = 'primary' }) => {
  return (
    <Button
      variant={variant}
      size={size}
      rounded
      glow
      animate
      icon={isPlaying ? PauseIcon : PlayIcon}
      onClick={isPlaying ? onPause : onPlay}
    >
      {isPlaying ? 'Pausar' : 'Jogar'}
    </Button>
  );
};

export const LikeButton: React.FC<{
  isLiked?: boolean;
  onToggle?: () => void;
  count?: number;
}> = ({ isLiked = false, onToggle, count }) => {
  return (
    <Button
      variant={isLiked ? 'danger' : 'ghost'}
      size="sm"
      icon={isLiked ? HeartSolid : HeartIcon}
      onClick={onToggle}
      animate
      pulse={isLiked}
      badge={count}
    >
      {isLiked ? 'Curtido' : 'Curtir'}
    </Button>
  );
};

export const StarButton: React.FC<{
  isStarred?: boolean;
  onToggle?: () => void;
  rating?: number;
}> = ({ isStarred = false, onToggle, rating }) => {
  return (
    <Button
      variant={isStarred ? 'gold' : 'ghost'}
      size="sm"
      icon={isStarred ? StarSolid : StarIcon}
      onClick={onToggle}
      animate
      glow={isStarred}
    >
      {rating ? `${rating}/5` : (isStarred ? 'Favoritado' : 'Favoritar')}
    </Button>
  );
};

export const ActionButton: React.FC<{
  action: 'add' | 'remove' | 'check' | 'close' | 'next' | 'previous';
  variant?: 'primary' | 'success' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  children?: React.ReactNode;
}> = ({ action, variant = 'primary', size = 'md', onClick, children }) => {
  const getActionIcon = () => {
    switch (action) {
      case 'add':
        return PlusIcon;
      case 'remove':
        return MinusIcon;
      case 'check':
        return CheckIcon;
      case 'close':
        return XMarkIcon;
      case 'next':
        return ArrowRightIcon;
      case 'previous':
        return ArrowRightIcon;
      default:
        return PlusIcon;
    }
  };

  const getActionVariant = () => {
    switch (action) {
      case 'add':
      case 'check':
        return 'success';
      case 'remove':
      case 'close':
        return 'danger';
      default:
        return variant;
    }
  };

  return (
    <Button
      variant={getActionVariant()}
      size={size}
      icon={getActionIcon()}
      iconPosition={action === 'previous' ? 'left' : action === 'next' ? 'right' : 'left'}
      onClick={onClick}
      animate
      className={action === 'previous' ? 'rotate-180' : ''}
    >
      {children || action.charAt(0).toUpperCase() + action.slice(1)}
    </Button>
  );
};

export default Button; 