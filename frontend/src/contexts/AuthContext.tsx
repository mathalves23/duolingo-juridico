import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, LoginRequest, RegisterRequest, LoadingState } from '../types';

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
    isLoading: true,
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
      // Se não há token, finaliza o carregamento e desloga
      dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
      dispatch({ type: 'LOGOUT' });
      return;
    }

    // Se existe token, reconstroi o usuário com dados mock
    try {
      const storedUsername = localStorage.getItem('user_username') || 'demo';
      const storedFirstName = localStorage.getItem('user_first_name') || 'Estudante';
      const storedLastName = localStorage.getItem('user_last_name') || 'Demo';
      const storedEmail = localStorage.getItem('user_email') || 'demo@duolingojuridico.com';
      const isAdmin = localStorage.getItem('user_role') === 'admin';
      
      const mockUser: User = {
        id: 1,
        username: storedUsername,
        email: storedEmail,
        first_name: storedFirstName,
        last_name: storedLastName,
        is_verified: true,
        created_at: new Date().toISOString(),
        profile: {
          id: 1,
          bio: isAdmin ? 'Administrador do Sistema' : 'Estudante de Direito determinado!',
          date_of_birth: null,
          phone_number: '',
          preferred_study_time: 'evening',
          target_exam: 'OAB',
          experience_level: isAdmin ? 'advanced' : 'intermediate',
          study_goals: isAdmin ? 'Gerenciar a plataforma' : 'Passar na OAB',
          xp_points: isAdmin ? 10000 : 2850,
          coins: isAdmin ? 9999 : 450,
          current_streak: isAdmin ? 100 : 12,
          best_streak: isAdmin ? 150 : 15,
          total_study_time: isAdmin ? 10000 : 1440,
          avatar: null,
        }
      };
      
      dispatch({ type: 'LOGIN_SUCCESS', payload: mockUser });
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
      dispatch({ type: 'LOGOUT' });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_username');
      localStorage.removeItem('user_first_name');
      localStorage.removeItem('user_last_name');
      localStorage.removeItem('user_email');
      localStorage.removeItem('user_role');
    }
  };

  const login = async (credentials: LoginRequest) => {
    dispatch({ type: 'SET_LOADING', payload: { isLoading: true } });

    try {
      // Modo demo - aceita qualquer usuário/senha, com verificação especial para admin
      if (credentials.username && credentials.password) {
        // Verificar se são credenciais de admin
        const isAdmin = credentials.username === 'admin' && credentials.password === 'admin123';
        
        // Simular dados de resposta
        const mockUser: User = {
          id: isAdmin ? 999 : 1,
          username: credentials.username,
          email: isAdmin ? 'admin@duolingojuridico.com' : 'demo@duolingojuridico.com',
          first_name: isAdmin ? 'Administrador' : 'Estudante',
          last_name: isAdmin ? 'Sistema' : 'Demo',
          is_verified: true,
          created_at: new Date().toISOString(),
          profile: {
            id: 1,
            bio: isAdmin ? 'Administrador do Sistema' : 'Estudante de Direito determinado!',
            date_of_birth: null,
            phone_number: '',
            preferred_study_time: 'evening',
            target_exam: 'OAB',
            experience_level: isAdmin ? 'advanced' : 'intermediate',
            study_goals: isAdmin ? 'Gerenciar a plataforma' : 'Passar na OAB',
            xp_points: isAdmin ? 10000 : 2850,
            coins: isAdmin ? 9999 : 450,
            current_streak: isAdmin ? 100 : 12,
            best_streak: isAdmin ? 150 : 15,
            total_study_time: isAdmin ? 10000 : 1440,
            avatar: null,
          }
        };
        
        // Salvar dados no localStorage para persistência
        localStorage.setItem('access_token', 'demo_token_' + Date.now());
        localStorage.setItem('refresh_token', 'demo_refresh_' + Date.now());
        localStorage.setItem('user_username', mockUser.username);
        localStorage.setItem('user_first_name', mockUser.first_name);
        localStorage.setItem('user_last_name', mockUser.last_name);
        localStorage.setItem('user_email', mockUser.email);
        localStorage.setItem('user_role', isAdmin ? 'admin' : 'user');
        
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
      // Modo demo - criar conta com dados fornecidos
      if (userData.username && userData.email && userData.password && userData.first_name && userData.last_name) {
        // Simular dados de resposta
        const mockUser: User = {
          id: Math.floor(Math.random() * 1000) + 1,
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          is_verified: false,
          created_at: new Date().toISOString(),
          profile: {
            id: 1,
            bio: `Estudante de Direito - ${userData.first_name} ${userData.last_name}`,
            date_of_birth: null,
            phone_number: '',
            preferred_study_time: 'evening',
            target_exam: 'OAB',
            experience_level: 'beginner',
            study_goals: 'Passar na OAB',
            xp_points: 0,
            coins: 100,
            current_streak: 0,
            best_streak: 0,
            total_study_time: 0,
            avatar: null,
          }
        };
        
        // Salvar token demo no localStorage
        localStorage.setItem('access_token', 'demo_token_' + Date.now());
        localStorage.setItem('refresh_token', 'demo_refresh_' + Date.now());
        localStorage.setItem('user_username', mockUser.username);
        localStorage.setItem('user_first_name', mockUser.first_name);
        localStorage.setItem('user_last_name', mockUser.last_name);
        localStorage.setItem('user_email', mockUser.email);
        localStorage.setItem('user_role', 'user');
        
        dispatch({ type: 'LOGIN_SUCCESS', payload: mockUser });
      } else {
        throw new Error('Todos os campos são obrigatórios');
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Erro ao criar conta. Tente novamente.';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const logout = async () => {
    dispatch({ type: 'SET_LOADING', payload: { isLoading: true } });

    try {
      // Em produção, chamar a API de logout aqui
      // await apiService.logout();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_username');
      localStorage.removeItem('user_first_name');
      localStorage.removeItem('user_last_name');
      localStorage.removeItem('user_email');
      localStorage.removeItem('user_role');
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