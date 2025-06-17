import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon, 
  XCircleIcon,
  XMarkIcon,
  BellIcon,
  CogIcon
} from '@heroicons/react/24/outline';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  autoClose?: boolean;
  duration?: number;
  actions?: NotificationAction[];
  timestamp: Date;
}

interface NotificationAction {
  label: string;
  action: () => void;
  style?: 'primary' | 'secondary';
}

interface NotificationSystemProps {
  notifications: Notification[];
  onRemove: (id: string) => void;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center';
  maxVisible?: number;
}

const NotificationItem: React.FC<{
  notification: Notification;
  onRemove: (id: string) => void;
}> = ({ notification, onRemove }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Animação de entrada
    setTimeout(() => setIsVisible(true), 100);

    // Auto-close
    if (notification.autoClose !== false) {
      const duration = notification.duration || 5000;
      const timer = setTimeout(() => {
        handleRemove();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, []);

  const handleRemove = () => {
    setIsExiting(true);
    setTimeout(() => {
      onRemove(notification.id);
    }, 300);
  };

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'info':
        return <InformationCircleIcon className="w-5 h-5 text-blue-500" />;
      default:
        return <InformationCircleIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getBackgroundColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Agora';
    if (diffInMinutes < 60) return `${diffInMinutes}min atrás`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d atrás`;
  };

  return (
    <div className={`
      transform transition-all duration-300 ease-in-out mb-4
      ${isVisible && !isExiting ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
      ${isExiting ? 'translate-x-full opacity-0' : ''}
    `}>
      <div className={`
        max-w-sm w-full shadow-lg rounded-lg border pointer-events-auto
        ${getBackgroundColor()}
      `}>
        <div className="p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getIcon()}
            </div>
            <div className="ml-3 w-0 flex-1">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">
                  {notification.title}
                </p>
                <div className="flex items-center ml-4">
                  <span className="text-xs text-gray-500">
                    {formatTime(notification.timestamp)}
                  </span>
                  <button
                    onClick={handleRemove}
                    className="ml-2 bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="mt-1 text-sm text-gray-600">
                {notification.message}
              </p>
              
              {/* Actions */}
              {notification.actions && notification.actions.length > 0 && (
                <div className="mt-3 flex gap-2">
                  {notification.actions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        action.action();
                        handleRemove();
                      }}
                      className={`
                        text-xs font-medium px-2 py-1 rounded transition-colors
                        ${action.style === 'primary' 
                          ? 'bg-blue-600 text-white hover:bg-blue-700' 
                          : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                        }
                      `}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const NotificationSystem: React.FC<NotificationSystemProps> = ({
  notifications,
  onRemove,
  position = 'top-right',
  maxVisible = 5
}) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const getPositionClasses = () => {
    switch (position) {
      case 'top-right':
        return 'top-4 right-4';
      case 'top-left':
        return 'top-4 left-4';
      case 'bottom-right':
        return 'bottom-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2';
      default:
        return 'top-4 right-4';
    }
  };

  // Limitar o número de notificações visíveis
  const visibleNotifications = notifications.slice(0, maxVisible);
  const hiddenCount = notifications.length - maxVisible;

  if (notifications.length === 0) return null;

  return (
    <div className={`fixed z-50 ${getPositionClasses()}`}>
      {/* Notification Header (quando há muitas notificações) */}
      {notifications.length > 1 && (
        <div className="mb-2 flex items-center justify-between max-w-sm">
          <div className="bg-white rounded-lg shadow-md px-3 py-2 flex items-center gap-2">
            <BellIcon className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-700 font-medium">
              {notifications.length} notificação{notifications.length > 1 ? 'ões' : ''}
            </span>
            {hiddenCount > 0 && (
              <span className="text-xs text-gray-500">
                (+{hiddenCount} oculta{hiddenCount > 1 ? 's' : ''})
              </span>
            )}
            <div className="flex items-center gap-1 ml-auto">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="text-gray-400 hover:text-gray-600 p-1"
                title={isMinimized ? 'Expandir' : 'Minimizar'}
              >
                {isMinimized ? '▲' : '▼'}
              </button>
              <button
                onClick={() => notifications.forEach(n => onRemove(n.id))}
                className="text-gray-400 hover:text-gray-600 p-1"
                title="Limpar todas"
              >
                <XMarkIcon className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notifications List */}
      {!isMinimized && (
        <div className="space-y-2">
          {visibleNotifications.map((notification) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onRemove={onRemove}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Hook para gerenciar notificações
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (
    notification: Omit<Notification, 'id' | 'timestamp'>
  ) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };

    setNotifications(prev => [newNotification, ...prev]);
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  // Funções utilitárias
  const success = (title: string, message: string, actions?: NotificationAction[]) => {
    addNotification({ type: 'success', title, message, actions });
  };

  const error = (title: string, message: string, actions?: NotificationAction[]) => {
    addNotification({ type: 'error', title, message, actions, autoClose: false });
  };

  const warning = (title: string, message: string, actions?: NotificationAction[]) => {
    addNotification({ type: 'warning', title, message, actions });
  };

  const info = (title: string, message: string, actions?: NotificationAction[]) => {
    addNotification({ type: 'info', title, message, actions });
  };

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info,
  };
};

export default NotificationSystem; 