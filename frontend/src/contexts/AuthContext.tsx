import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthResponse, LoginRequest, RegisterRequest, LoadingState } from '../types';
import apiService from '../services/api';

// Tipos para o contexto de autenticação
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: LoadingState;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
  checkAuth: () => Promise<void>;
}

// Ações do reducer
type AuthAction =
  | { type: 'SET_LOADING'; payload: { isLoading: boolean; error?: string | null } }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: Partial<User> }
  | { type: 'SET_ERROR'; payload: string };

// Estado inicial
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  loading: {
    isLoading: false,
    error: null,
  },
};

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          isLoading: action.payload.isLoading,
          error: action.payload.error || null,
        },
      };

    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        loading: {
          isLoading: false,
          error: null,
        },
      };

    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        loading: {
          isLoading: false,
          error: null,
        },
      };

    case 'UPDATE_USER':
      return {
        ...state,
        user: state.user ? { ...state.user, ...action.payload } : null,
      };

    case 'SET_ERROR':
      return {
        ...state,
        loading: {
          isLoading: false,
          error: action.payload,
        },
      };

    default:
      return state;
  }
};

// Contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Verificar autenticação no carregamento da aplicação
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      dispatch({ type: 'LOGOUT' });
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: { isLoading: true } });

    try {
      // Para modo demo/desenvolvimento, use dados mock
      const mockUser: User = {
        id: 1,
        username: 'demo',
        email: 'demo@duolingojuridico.com',
        first_name: 'Estudante',
        last_name: 'Demo',
        is_verified: true,
        created_at: new Date().toISOString(),
        profile: {
          id: 1,
          bio: 'Estudante de Direito determinado!',
          date_of_birth: null,
          phone_number: '',
          preferred_study_time: 'evening',
          target_exam: 'OAB',
          experience_level: 'intermediate',
          study_goals: 'Passar na OAB',
          xp_points: 2850,
          coins: 450,
          current_streak: 12,
          best_streak: 15,
          total_study_time: 1440,
          avatar: null,
        }
      };
      
      dispatch({ type: 'LOGIN_SUCCESS', payload: mockUser });
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
      dispatch({ type: 'LOGOUT' });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  };

  const login = async (credentials: LoginRequest) => {
    dispatch({ type: 'SET_LOADING', payload: { isLoading: true } });

    try {
      // Modo demo - aceita qualquer usuário/senha
      if (credentials.username && credentials.password) {
        // Simular dados de resposta
        const mockUser: User = {
          id: 1,
          username: credentials.username,
          email: 'demo@duolingojuridico.com',
          first_name: 'Estudante',
          last_name: 'Demo',
          is_verified: true,
          created_at: new Date().toISOString(),
          profile: {
            id: 1,
            bio: 'Estudante de Direito determinado!',
            date_of_birth: null,
            phone_number: '',
            preferred_study_time: 'evening',
            target_exam: 'OAB',
            experience_level: 'intermediate',
            study_goals: 'Passar na OAB',
            xp_points: 2850,
            coins: 450,
            current_streak: 12,
            best_streak: 15,
            total_study_time: 1440,
            avatar: null,
          }
        };
        
        // Salvar token demo no localStorage
        localStorage.setItem('access_token', 'demo_token_' + Date.now());
        localStorage.setItem('refresh_token', 'demo_refresh_' + Date.now());
        
        dispatch({ type: 'LOGIN_SUCCESS', payload: mockUser });
      } else {
        throw new Error('Usuário e senha são obrigatórios');
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Erro ao fazer login. Verifique suas credenciais.';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const register = async (userData: RegisterRequest) => {
    dispatch({ type: 'SET_LOADING', payload: { isLoading: true } });

    try {
      const response: AuthResponse = await apiService.register(userData);
      
      // Salvar tokens no localStorage
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
      
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.user });
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          error.response?.data?.non_field_errors?.[0] ||
                          'Erro ao criar conta. Tente novamente.';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const logout = async () => {
    dispatch({ type: 'SET_LOADING', payload: { isLoading: true } });

    try {
      await apiService.logout();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  };

  const updateUser = (userData: Partial<User>) => {
    dispatch({ type: 'UPDATE_USER', payload: userData });
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    updateUser,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizado para usar o contexto
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  
  return context;
};

export default AuthContext; 