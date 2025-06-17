import React, { createContext, useContext, ReactNode } from 'react';
import NotificationSystem, { useNotifications } from '../components/NotificationSystem';

interface NotificationContextType {
  success: (title: string, message: string, actions?: any[]) => void;
  error: (title: string, message: string, actions?: any[]) => void;
  warning: (title: string, message: string, actions?: any[]) => void;
  info: (title: string, message: string, actions?: any[]) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const { notifications, removeNotification, success, error, warning, info, clearAll } = useNotifications();

  return (
    <NotificationContext.Provider value={{ success, error, warning, info, clearAll }}>
      {children}
      <NotificationSystem
        notifications={notifications}
        onRemove={removeNotification}
        position="top-right"
        maxVisible={5}
      />
    </NotificationContext.Provider>
  );
};

export const useNotification = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification deve ser usado dentro de um NotificationProvider');
  }
  return context;
}; 