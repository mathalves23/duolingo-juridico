import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  TrophyIcon,
  BookOpenIcon,
  QuestionMarkCircleIcon,
  ClockIcon,
  SparklesIcon,
  AcademicCapIcon,
  PlayIcon,
  EyeIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import {
  TrophyIcon as TrophySolid,
  FireIcon as FireSolid,
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
      xp_points: user?.profile?.xp_points || 10000,
      coins: user?.profile?.coins || 9999,
      current_streak: user?.profile?.current_streak || 100,
      best_streak: user?.profile?.best_streak || 120,
      total_study_time: user?.profile?.total_study_time || 4320, // em minutos
      questions_answered: 287,
      correct_answers: 231,
      subjects_studied: 7,
      achievements_earned: 15,
      level: Math.floor((user?.profile?.xp_points || 10000) / 1000) + 1,
      hearts: 5
    };

    const mockActivities: RecentActivity[] = [
      {
        id: 1,
        type: 'achievement',
        title: 'Mestre da Consistência! 🏆',
        description: 'Manteve uma sequência de 100 dias consecutivos',
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
    <div className="space-y-8 animate-fade-in-up pb-8">
      {/* Hero Section Ultra Moderno */}
      <div className="relative overflow-hidden card-gradient rounded-3xl p-6 lg:p-8 shadow-glass-xl border border-white/20">
        {/* Background Decorations Avançadas */}
        <div className="absolute top-0 right-0 w-64 lg:w-96 h-64 lg:h-96 bg-gradient-to-br from-primary-400/20 via-purple-400/20 to-transparent rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-48 lg:w-64 h-48 lg:h-64 bg-gradient-to-tr from-gold-500/20 to-transparent rounded-full blur-2xl animate-blob"></div>
        <div className="absolute top-1/2 left-1/3 w-24 lg:w-32 h-24 lg:h-32 bg-gradient-to-r from-legal-500/10 to-transparent rounded-full blur-xl animate-pulse"></div>
        
        <div className="relative z-10">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between space-y-6 lg:space-y-0">
            <div className="flex-1 min-w-0">
              <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-3 mb-4">
                <div className="flex items-center space-x-2">
                  <SparklesIcon className="h-5 w-5 lg:h-6 lg:w-6 text-gold-500 animate-pulse" />
                  <span className="text-gold-600 font-semibold text-xs lg:text-sm">
                    {getGreeting()}, futuro(a) aprovado(a)!
                  </span>
                </div>
                <div className="px-3 py-1 glass rounded-full">
                  <span className="text-xs font-bold text-navy-700">
                    {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
              <h1 className="text-2xl lg:text-4xl font-bold text-navy-800 mb-2">
                Olá, {user?.first_name || 'Administrador'}!
              </h1>
              <p className="text-navy-600 text-sm lg:text-base max-w-lg">
                {motivationalQuote}
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 w-full lg:w-auto">
              <button className="btn-secondary-glass">
                <EyeIcon className="h-5 w-5 mr-2" />
                Revisar Questões
              </button>
              <button className="btn-primary-glow">
                <PlayIcon className="h-5 w-5 mr-2" />
                Continuar Estudos
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        {/* XP Card */}
        <div className="card card-hover group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs lg:text-sm font-medium text-navy-600 mb-1">Experiência Total</p>
              <p className="text-2xl lg:text-3xl font-bold text-navy-800">{stats?.xp_points.toLocaleString()}</p>
              <p className="text-xs text-gold-600 mt-1">Nível {stats?.level}</p>
            </div>
            <div className="p-3 bg-gradient-to-r from-gold-500 to-gold-600 rounded-2xl shadow-colored-gold group-hover:scale-110 transition-transform duration-300">
              <TrophySolid className="h-6 w-6 text-white" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-xs text-navy-600 mb-1">
              <span>Próximo nível</span>
              <span>{getNextLevelXP()} XP</span>
            </div>
            <div className="progress">
              <div 
                className="progress-bar progress-bar-gold" 
                style={{ width: `${getLevelProgress()}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Streak Card */}
        <div className="card card-hover group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs lg:text-sm font-medium text-navy-600 mb-1">Sequência</p>
              <p className="text-2xl lg:text-3xl font-bold text-navy-800">{stats?.current_streak}</p>
              <p className="text-xs text-orange-600 mt-1">dias consecutivos</p>
            </div>
            <div className="p-3 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl shadow-colored-orange group-hover:scale-110 transition-transform duration-300">
              <FireSolid className="h-6 w-6 text-white animate-pulse" />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-xs text-navy-600">Melhor sequência: <span className="font-semibold">{stats?.best_streak} dias</span></p>
          </div>
        </div>

        {/* Accuracy Card */}
        <div className="card card-hover group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs lg:text-sm font-medium text-navy-600 mb-1">Precisão</p>
              <p className="text-2xl lg:text-3xl font-bold text-navy-800">{getAccuracyPercentage()}%</p>
              <p className="text-xs text-success-600 mt-1">{stats?.correct_answers}/{stats?.questions_answered} questões</p>
            </div>
            <div className="p-3 bg-gradient-to-r from-success-500 to-success-600 rounded-2xl shadow-colored-success group-hover:scale-110 transition-transform duration-300">
              <CheckSolid className="h-6 w-6 text-white" />
            </div>
          </div>
        </div>

        {/* Study Time Card */}
        <div className="card card-hover group">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs lg:text-sm font-medium text-navy-600 mb-1">Tempo de Estudo</p>
              <p className="text-2xl lg:text-3xl font-bold text-navy-800">{formatTime(stats?.total_study_time || 0)}</p>
              <p className="text-xs text-primary-600 mt-1">tempo total</p>
            </div>
            <div className="p-3 bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl shadow-colored-primary group-hover:scale-110 transition-transform duration-300">
              <ClockIcon className="h-6 w-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6 lg:space-y-8">
          {/* Daily Goals */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg lg:text-xl font-bold text-navy-800">Metas Diárias</h2>
              <span className="badge badge-primary">{dailyGoals.filter(goal => getProgressPercentage(goal.current, goal.target) === 100).length}/{dailyGoals.length} completas</span>
            </div>
            <div className="space-y-4">
              {dailyGoals.map((goal) => {
                const IconComponent = goal.icon;
                const progress = getProgressPercentage(goal.current, goal.target);
                const isCompleted = progress === 100;
                
                return (
                  <div key={goal.id} className="flex items-center space-x-4">
                    <div className={`p-2 rounded-xl bg-gradient-to-r ${goal.color} shadow-soft flex-shrink-0`}>
                      <IconComponent className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-center mb-1">
                        <p className="font-medium text-navy-800 text-sm lg:text-base">{goal.type}</p>
                        <div className="flex items-center space-x-2">
                          {isCompleted && <CheckSolid className="h-4 w-4 text-success-500" />}
                          <span className="text-sm font-semibold text-navy-600">
                            {goal.current}/{goal.target} {goal.unit}
                          </span>
                        </div>
                      </div>
                      <div className="progress">
                        <div 
                          className={`progress-bar ${isCompleted ? 'progress-bar-legal' : 'progress-bar'} transition-all duration-500`}
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Activities */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg lg:text-xl font-bold text-navy-800">Atividades Recentes</h2>
              <button className="text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors">
                Ver todas
              </button>
            </div>
            <div className="space-y-4">
              {recentActivities.map((activity) => {
                const IconComponent = activity.icon;
                return (
                  <div key={activity.id} className="flex items-start space-x-4 p-3 rounded-2xl hover:bg-slate-50/50 transition-colors">
                    <div className={`p-2 rounded-xl bg-gradient-to-r ${activity.color} shadow-soft flex-shrink-0`}>
                      <IconComponent className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-navy-800 text-sm lg:text-base">{activity.title}</p>
                      <p className="text-xs lg:text-sm text-navy-600 mt-1">{activity.description}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-navy-500">{getTimeAgo(activity.timestamp)}</span>
                        {activity.xp_earned && (
                          <span className="text-xs font-semibold text-gold-600 bg-gold-50/80 px-2 py-1 rounded-full">
                            +{activity.xp_earned} XP
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6 lg:space-y-8">
          {/* Week Streak */}
          <div className="card">
            <h3 className="text-lg font-bold text-navy-800 mb-4">Sequência da Semana</h3>
            <div className="grid grid-cols-7 gap-2">
              {studyStreak.map((day, index) => (
                <div key={index} className="text-center">
                  <p className="text-xs font-medium text-navy-600 mb-2">{day.day}</p>
                  <div className={`w-8 h-8 mx-auto rounded-xl flex items-center justify-center ${
                    day.completed 
                      ? 'bg-gradient-to-r from-success-500 to-success-600 text-white' 
                      : 'bg-slate-100 text-slate-400'
                  }`}>
                    {day.completed ? (
                      <CheckSolid className="h-4 w-4" />
                    ) : (
                      <span className="text-xs">•</span>
                    )}
                  </div>
                  {day.completed && (
                    <p className="text-xs text-success-600 mt-1 font-medium">{day.xp}XP</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Subjects Progress */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-navy-800">Matérias</h3>
              <button className="text-primary-600 text-sm font-medium hover:text-primary-700 transition-colors">
                Ver todas
              </button>
            </div>
            <div className="space-y-4">
              {subjects.map((subject) => {
                const IconComponent = subject.icon;
                return (
                  <div key={subject.id} className="p-3 rounded-2xl border border-slate-100/50 hover:bg-slate-50/50 transition-colors">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`p-2 rounded-xl bg-gradient-to-r ${subject.color} shadow-soft`}>
                        <IconComponent className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-navy-800 text-sm">{subject.name}</p>
                        <p className="text-xs text-navy-600">{subject.completedLessons}/{subject.totalLessons} lições</p>
                      </div>
                      <span className="text-xs font-semibold text-navy-700">{subject.progress}%</span>
                    </div>
                    <div className="progress mb-2">
                      <div 
                        className="progress-bar transition-all duration-500"
                        style={{ width: `${subject.progress}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-navy-600">Próxima: {subject.nextLesson}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 