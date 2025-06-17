import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  TrophyIcon,
  FireIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  BookOpenIcon,
  QuestionMarkCircleIcon,
  ClockIcon,
  SparklesIcon,
  StarIcon,
  CalendarDaysIcon,
  AcademicCapIcon,
  ArrowTrendingUpIcon,
  BoltIcon,
  PlayIcon,
  EyeIcon,
  RocketLaunchIcon,
  LightBulbIcon,
  ShieldCheckIcon,
  GiftIcon,
  BeakerIcon,
  UserGroupIcon,
  DocumentTextIcon,
  ChevronRightIcon,
  PlusIcon,
  ArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import {
  TrophyIcon as TrophySolid,
  FireIcon as FireSolid,
  StarIcon as StarSolid,
  HeartIcon as HeartSolid,
  BoltIcon as BoltSolid,
  CheckCircleIcon as CheckSolid
} from '@heroicons/react/24/solid';

interface DashboardStats {
  xp_points: number;
  coins: number;
  current_streak: number;
  best_streak: number;
  total_study_time: number;
  questions_answered: number;
  correct_answers: number;
  subjects_studied: number;
  achievements_earned: number;
  level: number;
  hearts: number;
}

interface RecentActivity {
  id: number;
  type: 'question' | 'lesson' | 'achievement' | 'quiz' | 'streak';
  title: string;
  description: string;
  timestamp: string;
  xp_earned?: number;
  icon: React.ComponentType<any>;
  color: string;
  isSolid?: boolean;
}

interface DailyGoal {
  id: string;
  type: string;
  current: number;
  target: number;
  icon: React.ComponentType<any>;
  color: string;
  unit: string;
}

interface StudyStreak {
  day: string;
  completed: boolean;
  xp: number;
  date: string;
}

interface Subject {
  id: string;
  name: string;
  progress: number;
  totalLessons: number;
  completedLessons: number;
  color: string;
  icon: React.ComponentType<any>;
  nextLesson: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [dailyGoals, setDailyGoals] = useState<DailyGoal[]>([]);
  const [studyStreak, setStudyStreak] = useState<StudyStreak[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [motivationalQuote, setMotivationalQuote] = useState('');

  // Mock data - em produção, viria da API
  useEffect(() => {
    const mockStats: DashboardStats = {
      xp_points: user?.profile?.xp_points || 2850,
      coins: user?.profile?.coins || 540,
      current_streak: user?.profile?.current_streak || 12,
      best_streak: user?.profile?.best_streak || 28,
      total_study_time: user?.profile?.total_study_time || 4320, // em minutos
      questions_answered: 287,
      correct_answers: 231,
      subjects_studied: 7,
      achievements_earned: 15,
      level: Math.floor((user?.profile?.xp_points || 2850) / 1000) + 1,
      hearts: 5
    };

    const mockActivities: RecentActivity[] = [
      {
        id: 1,
        type: 'achievement',
        title: 'Mestre da Consistência! 🏆',
        description: 'Manteve uma sequência de 12 dias consecutivos',
        timestamp: '2024-01-15T10:30:00Z',
        xp_earned: 150,
        icon: TrophySolid,
        color: 'from-gold-500 to-gold-600',
        isSolid: true
      },
      {
        id: 2,
        type: 'quiz',
        title: 'Simulado Direito Constitucional 📚',
        description: 'Pontuou 92% no simulado de 30 questões',
        timestamp: '2024-01-15T09:15:00Z',
        xp_earned: 120,
        icon: AcademicCapIcon,
        color: 'from-primary-500 to-navy-600'
      },
      {
        id: 3,
        type: 'lesson',
        title: 'Direitos Fundamentais Avançado 🎯',
        description: 'Completou módulo sobre garantias constitucionais',
        timestamp: '2024-01-14T16:45:00Z',
        xp_earned: 85,
        icon: BookOpenIcon,
        color: 'from-legal-500 to-legal-600'
      },
      {
        id: 4,
        type: 'streak',
        title: 'Sequência Perfeita! ⚡',
        description: 'Acertou 15 questões consecutivas',
        timestamp: '2024-01-14T14:20:00Z',
        xp_earned: 75,
        icon: BoltSolid,
        color: 'from-warning-500 to-warning-600',
        isSolid: true
      },
      {
        id: 5,
        type: 'question',
        title: 'Especialista em Processo Civil 📖',
        description: 'Respondeu 50 questões de processo civil',
        timestamp: '2024-01-13T11:30:00Z',
        xp_earned: 100,
        icon: CheckSolid,
        color: 'from-success-500 to-success-600',
        isSolid: true
      }
    ];

    const mockDailyGoals: DailyGoal[] = [
      {
        id: 'questions',
        type: 'Questões Respondidas',
        current: 18,
        target: 25,
        icon: QuestionMarkCircleIcon,
        color: 'from-primary-500 to-primary-600',
        unit: 'questões'
      },
      {
        id: 'time',
        type: 'Tempo de Estudo',
        current: 75,
        target: 90,
        icon: ClockIcon,
        color: 'from-success-500 to-success-600',
        unit: 'minutos'
      },
      {
        id: 'xp',
        type: 'XP Conquistado',
        current: 280,
        target: 350,
        icon: TrophyIcon,
        color: 'from-gold-500 to-gold-600',
        unit: 'XP'
      },
      {
        id: 'lessons',
        type: 'Lições Concluídas',
        current: 3,
        target: 5,
        icon: BookOpenIcon,
        color: 'from-purple-500 to-purple-600',
        unit: 'lições'
      }
    ];

    const mockStudyStreak: StudyStreak[] = [
      { day: 'Seg', completed: true, xp: 250, date: '2024-01-08' },
      { day: 'Ter', completed: true, xp: 180, date: '2024-01-09' },
      { day: 'Qua', completed: true, xp: 320, date: '2024-01-10' },
      { day: 'Qui', completed: true, xp: 290, date: '2024-01-11' },
      { day: 'Sex', completed: true, xp: 410, date: '2024-01-12' },
      { day: 'Sáb', completed: true, xp: 380, date: '2024-01-13' },
      { day: 'Dom', completed: false, xp: 0, date: '2024-01-14' }
    ];

    const mockSubjects: Subject[] = [
      {
        id: 'constitutional',
        name: 'Direito Constitucional',
        progress: 75,
        totalLessons: 20,
        completedLessons: 15,
        color: 'from-primary-500 to-primary-600',
        icon: ShieldCheckIcon,
        nextLesson: 'Controle de Constitucionalidade'
      },
      {
        id: 'administrative',
        name: 'Direito Administrativo',
        progress: 60,
        totalLessons: 18,
        completedLessons: 11,
        color: 'from-legal-500 to-legal-600',
        icon: DocumentTextIcon,
        nextLesson: 'Licitações e Contratos'
      },
      {
        id: 'civil',
        name: 'Direito Civil',
        progress: 45,
        totalLessons: 25,
        completedLessons: 11,
        color: 'from-purple-500 to-purple-600',
        icon: UserGroupIcon,
        nextLesson: 'Direitos Reais'
      },
      {
        id: 'portuguese',
        name: 'Língua Portuguesa',
        progress: 80,
        totalLessons: 15,
        completedLessons: 12,
        color: 'from-cyan-500 to-cyan-600',
        icon: BookOpenIcon,
        nextLesson: 'Concordância Verbal'
      }
    ];

    const quotes = [
      'A persistência é o caminho do êxito. 💪',
      'Cada questão respondida é um passo mais próximo da aprovação! 🎯',
      'O sucesso é a soma de pequenos esforços repetidos dia após dia. ⭐',
      'Você está mais forte do que ontem! 🚀',
      'A disciplina é a ponte entre objetivos e conquistas. 🌟'
    ];

    setStats(mockStats);
    setRecentActivities(mockActivities);
    setDailyGoals(mockDailyGoals);
    setStudyStreak(mockStudyStreak);
    setSubjects(mockSubjects);
    setMotivationalQuote(quotes[Math.floor(Math.random() * quotes.length)]);
    setLoading(false);
  }, [user]);

  // Atualizar horário em tempo real
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const getAccuracyPercentage = () => {
    if (!stats || stats.questions_answered === 0) return 0;
    return Math.round((stats.correct_answers / stats.questions_answered) * 100);
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Agora há pouco';
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    return `${Math.floor(diffInHours / 24)}d atrás`;
  };

  const getProgressPercentage = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const getNextLevelXP = () => {
    if (!stats) return 1000;
    return (stats.level * 1000) - (stats.xp_points % 1000);
  };

  const getLevelProgress = () => {
    if (!stats) return 0;
    return (stats.xp_points % 1000) / 10;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative">
          <div className="loading-spinner w-12 h-12"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-gold-500 rounded-full animate-ping opacity-20"></div>
        </div>
        <p className="ml-6 text-navy-600 font-medium text-lg">Carregando seu universo jurídico...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* Hero Section Ultra Moderno */}
      <div className="relative overflow-hidden card-gradient rounded-3xl p-8 shadow-glass-xl border border-white/20">
        {/* Background Decorations Avançadas */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-primary-400/20 via-purple-400/20 to-transparent rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-gradient-to-tr from-gold-500/20 to-transparent rounded-full blur-2xl animate-blob"></div>
        <div className="absolute top-1/2 left-1/3 w-32 h-32 bg-gradient-to-r from-legal-500/10 to-transparent rounded-full blur-xl animate-pulse"></div>
        
        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between space-y-6 lg:space-y-0">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className="flex items-center space-x-2">
                  <SparklesIcon className="h-6 w-6 text-gold-500 animate-pulse" />
                  <span className="text-gold-600 font-semibold text-sm">
                    {getGreeting()}, futuro(a) aprovado(a)!
                  </span>
                </div>
                <div className="px-3 py-1 glass rounded-full">
                  <span className="text-xs font-bold text-navy-700">
                    {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
              
              <h1 className="text-4xl lg:text-5xl font-bold mb-3 title-gradient">
                Olá, {user?.first_name}! 👋
              </h1>
              
              <p className="text-navy-600 text-lg lg:text-xl font-medium mb-4">
                {motivationalQuote}
              </p>

              {/* Level Progress */}
              <div className="glass rounded-2xl p-4 mb-6 max-w-md">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-navy-700">Nível {stats?.level}</span>
                  <span className="text-xs text-navy-500">{getNextLevelXP()} XP para o próximo nível</span>
                </div>
                <div className="progress mb-2">
                  <div 
                    className="progress-bar transition-all duration-1000 ease-out"
                    style={{ width: `${getLevelProgress()}%` }}
                  ></div>
                </div>
                <div className="flex items-center justify-between text-xs text-navy-500">
                  <span>{stats?.xp_points.toLocaleString()} XP</span>
                  <span>{((stats?.level || 1) * 1000).toLocaleString()} XP</span>
                </div>
              </div>

              {/* Quick Stats Inline */}
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center space-x-2 glass px-4 py-2 rounded-2xl hover-lift">
                  <FireSolid className="h-5 w-5 text-orange-500 animate-pulse" />
                  <span className="font-bold text-navy-800">{stats?.current_streak} dias</span>
                  <span className="text-sm text-navy-500">sequência</span>
                </div>
                <div className="flex items-center space-x-2 glass px-4 py-2 rounded-2xl hover-lift">
                  <TrophySolid className="h-5 w-5 text-gold-500" />
                  <span className="font-bold text-navy-800">{stats?.xp_points.toLocaleString()}</span>
                  <span className="text-sm text-navy-500">XP</span>
                </div>
                <div className="flex items-center space-x-2 glass px-4 py-2 rounded-2xl hover-lift">
                  <ChartBarIcon className="h-5 w-5 text-legal-500" />
                  <span className="font-bold text-navy-800">{getAccuracyPercentage()}%</span>
                  <span className="text-sm text-navy-500">precisão</span>
                </div>
                <div className="flex items-center space-x-2 glass px-4 py-2 rounded-2xl hover-lift">
                  <HeartSolid className="h-5 w-5 text-rose-500" />
                  <span className="font-bold text-navy-800">{stats?.hearts}</span>
                  <span className="text-sm text-navy-500">vidas</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col space-y-3">
              <button className="btn btn-legal btn-lg group">
                <PlayIcon className="h-5 w-5 mr-2 group-hover:animate-pulse" />
                Continuar Estudando
                <RocketLaunchIcon className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="btn btn-outline">
                <BeakerIcon className="h-5 w-5 mr-2" />
                Laboratório IA
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-navy-800 mb-4">
          Bem-vindo ao Duolingo Jurídico! 🎓
        </h2>
        <p className="text-navy-600">
          Sua jornada de aprendizado jurídico começa aqui.
        </p>
      </div>
    </div>
  );
};

export default Dashboard; 