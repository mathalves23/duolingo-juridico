import React, { useState, useEffect } from 'react';
import {
  CalendarIcon,
  ClockIcon,
  BookOpenIcon,
  AcademicCapIcon,
  ChartBarIcon,
  LightBulbIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  ArrowRightIcon,
  PlayIcon,
  PauseIcon,
  AdjustmentsHorizontalIcon,
  DocumentTextIcon,
  FlagIcon
} from '@heroicons/react/24/outline';
import {
  CheckCircleIcon as CheckCircleSolid,
  StarIcon as StarSolid
} from '@heroicons/react/24/solid';
import Card from '../components/Card';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

// Interfaces
interface StudyGoal {
  id: string;
  title: string;
  description: string;
  targetDate: Date;
  progress: number;
  priority: 'high' | 'medium' | 'low';
  category: 'exam' | 'subject' | 'skill' | 'certification';
  estimatedHours: number;
  completedHours: number;
}

interface StudySession {
  id: string;
  subject: string;
  topic: string;
  duration: number;
  scheduledTime: Date;
  status: 'scheduled' | 'in-progress' | 'completed' | 'missed';
  type: 'reading' | 'practice' | 'review' | 'simulation';
  difficulty: number;
  xpReward: number;
}

interface WeeklyPlan {
  week: string;
  totalHours: number;
  completedHours: number;
  sessions: StudySession[];
  goals: string[];
}

interface StudyAnalytics {
  totalStudyTime: number;
  averageSessionDuration: number;
  completionRate: number;
  strongestSubjects: string[];
  weakestSubjects: string[];
  recommendedFocus: string[];
  productivityTrends: { day: string; hours: number; efficiency: number }[];
}

const StudyPlan: React.FC = () => {
  const { user } = useAuth();
  const { success, info } = useNotification();
  const [activeTab, setActiveTab] = useState<'overview' | 'schedule' | 'goals' | 'analytics' | 'ai-tutor'>('overview');
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
  const [currentSession, setCurrentSession] = useState<StudySession | null>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionTimer, setSessionTimer] = useState(0);

  // Estados dos dados
  const [studyGoals, setStudyGoals] = useState<StudyGoal[]>([
    {
      id: '1',
      title: 'Aprovação na OAB',
      description: 'Conquistar aprovação no exame da Ordem dos Advogados do Brasil',
      targetDate: new Date('2024-06-15'),
      progress: 65,
      priority: 'high',
      category: 'exam',
      estimatedHours: 400,
      completedHours: 260
    },
    {
      id: '2',
      title: 'Dominar Direito Constitucional',
      description: 'Alcançar 90% de acertos em questões de direito constitucional',
      targetDate: new Date('2024-03-30'),
      progress: 78,
      priority: 'high',
      category: 'subject',
      estimatedHours: 120,
      completedHours: 94
    },
    {
      id: '3',
      title: 'Especialização em Direito Digital',
      description: 'Completar curso de pós-graduação em direito digital',
      targetDate: new Date('2024-12-20'),
      progress: 25,
      priority: 'medium',
      category: 'certification',
      estimatedHours: 600,
      completedHours: 150
    }
  ]);

  const [weeklyPlan, setWeeklyPlan] = useState<WeeklyPlan>({
    week: 'Semana de 22-28 Jan 2024',
    totalHours: 25,
    completedHours: 18,
    sessions: [
      {
        id: 's1',
        subject: 'Direito Constitucional',
        topic: 'Princípios Fundamentais',
        duration: 120,
        scheduledTime: new Date('2024-01-22T09:00:00'),
        status: 'completed',
        type: 'reading',
        difficulty: 3,
        xpReward: 150
      },
      {
        id: 's2',
        subject: 'Direito Civil',
        topic: 'Contratos - Teoria Geral',
        duration: 90,
        scheduledTime: new Date('2024-01-22T14:00:00'),
        status: 'scheduled',
        type: 'practice',
        difficulty: 4,
        xpReward: 200
      },
      {
        id: 's3',
        subject: 'Direito Penal',
        topic: 'Crimes contra a Pessoa',
        duration: 60,
        scheduledTime: new Date('2024-01-23T10:00:00'),
        status: 'in-progress',
        type: 'review',
        difficulty: 3,
        xpReward: 120
      },
      {
        id: 's4',
        subject: 'Simulado OAB',
        topic: 'Simulado Completo #15',
        duration: 180,
        scheduledTime: new Date('2024-01-24T09:00:00'),
        status: 'scheduled',
        type: 'simulation',
        difficulty: 5,
        xpReward: 300
      }
    ],
    goals: [
      'Completar 3 capítulos de Direito Constitucional',
      'Resolver 50 questões de Direito Civil',
      'Fazer 1 simulado completo',
      'Revisar anotações da semana anterior'
    ]
  });

  const [analytics, setAnalytics] = useState<StudyAnalytics>({
    totalStudyTime: 1440, // em minutos
    averageSessionDuration: 85,
    completionRate: 87,
    strongestSubjects: ['Direito Constitucional', 'Direito Administrativo'],
    weakestSubjects: ['Direito Tributário', 'Direito Empresarial'],
    recommendedFocus: ['Direito Tributário', 'Simulados', 'Revisão Geral'],
    productivityTrends: [
      { day: 'Seg', hours: 3.5, efficiency: 92 },
      { day: 'Ter', hours: 4.2, efficiency: 88 },
      { day: 'Qua', hours: 2.8, efficiency: 95 },
      { day: 'Qui', hours: 3.8, efficiency: 85 },
      { day: 'Sex', hours: 4.5, efficiency: 90 },
      { day: 'Sáb', hours: 2.0, efficiency: 78 },
      { day: 'Dom', hours: 1.5, efficiency: 82 }
    ]
  });

  // Timer para sessão de estudo
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSessionActive && currentSession) {
      interval = setInterval(() => {
        setSessionTimer(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isSessionActive, currentSession]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}min` : `${mins}min`;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in-progress': return 'text-blue-600 bg-blue-100';
      case 'scheduled': return 'text-gray-600 bg-gray-100';
      case 'missed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const generateAIPlan = async () => {
    setIsGeneratingPlan(true);
    
    // Simular geração de plano pela IA
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    info(
      'Plano Personalizado Gerado! 🤖',
      'Sua IA analisou seu histórico e criou um plano otimizado para seus objetivos.',
      [
        {
          label: 'Ver Plano',
          action: () => setActiveTab('schedule'),
          style: 'primary'
        }
      ]
    );
    
    setIsGeneratingPlan(false);
  };

  const startStudySession = (session: StudySession) => {
    setCurrentSession(session);
    setIsSessionActive(true);
    setSessionTimer(0);
    
    success(
      'Sessão Iniciada! 📚',
      `Estudando: ${session.topic}. Foco total por ${formatDuration(session.duration)}!`
    );
  };

  const pauseSession = () => {
    setIsSessionActive(false);
  };

  const resumeSession = () => {
    setIsSessionActive(true);
  };

  const completeSession = () => {
    if (currentSession) {
      const updatedSessions = weeklyPlan.sessions.map(s => 
        s.id === currentSession.id 
          ? { ...s, status: 'completed' as const }
          : s
      );
      
      setWeeklyPlan(prev => ({
        ...prev,
        sessions: updatedSessions,
        completedHours: prev.completedHours + (currentSession.duration / 60)
      }));
      
      success(
        'Sessão Concluída! 🎉',
        `Parabéns! Você ganhou ${currentSession.xpReward} XP estudando ${currentSession.topic}.`,
        [
          {
            label: 'Próxima Sessão',
            action: () => setActiveTab('schedule'),
            style: 'primary'
          }
        ]
      );
    }
    
    setCurrentSession(null);
    setIsSessionActive(false);
    setSessionTimer(0);
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Current Session */}
      {currentSession && (
        <Card className="p-6 border-l-4 border-l-blue-500 bg-blue-50">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Sessão Atual</h3>
              <p className="text-sm text-gray-600">{currentSession.subject} - {currentSession.topic}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">{formatTime(sessionTimer)}</div>
              <div className="text-sm text-gray-500">de {formatDuration(currentSession.duration)}</div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {isSessionActive ? (
              <button
                onClick={pauseSession}
                className="flex items-center gap-2 bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors"
              >
                <PauseIcon className="w-4 h-4" />
                Pausar
              </button>
            ) : (
              <button
                onClick={resumeSession}
                className="flex items-center gap-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
              >
                <PlayIcon className="w-4 h-4" />
                Continuar
              </button>
            )}
            
            <button
              onClick={completeSession}
              className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
            >
              <CheckCircleIcon className="w-4 h-4" />
              Concluir
            </button>
          </div>
          
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((sessionTimer / (currentSession.duration * 60)) * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </Card>
      )}

      {/* Study Goals */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Metas de Estudo</h3>
          <button
            onClick={generateAIPlan}
            disabled={isGeneratingPlan}
            className="flex items-center gap-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50"
          >
            <SparklesIcon className="w-4 h-4" />
            {isGeneratingPlan ? 'Gerando...' : 'IA Personalizada'}
          </button>
        </div>
        
        <div className="space-y-4">
          {studyGoals.map((goal) => (
            <div key={goal.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{goal.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{goal.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getPriorityColor(goal.priority)}`}>
                    {goal.priority.toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>{goal.completedHours}h de {goal.estimatedHours}h</span>
                <span>Meta: {goal.targetDate.toLocaleDateString('pt-BR')}</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${goal.progress}%` }}
                ></div>
              </div>
              
              <div className="text-right mt-2">
                <span className="text-sm font-medium text-gray-900">{goal.progress}%</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Weekly Progress */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Progresso Semanal</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Horas Completadas</span>
              <span className="font-semibold">{weeklyPlan.completedHours}h de {weeklyPlan.totalHours}h</span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-500"
                style={{ width: `${(weeklyPlan.completedHours / weeklyPlan.totalHours) * 100}%` }}
              ></div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{analytics.completionRate}%</div>
                <div className="text-sm text-gray-600">Taxa de Conclusão</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{formatDuration(analytics.averageSessionDuration)}</div>
                <div className="text-sm text-gray-600">Duração Média</div>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Próximas Sessões</h3>
          
          <div className="space-y-3">
            {weeklyPlan.sessions
              .filter(s => s.status === 'scheduled' || s.status === 'in-progress')
              .slice(0, 3)
              .map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">{session.topic}</h4>
                    <p className="text-xs text-gray-600">{session.subject}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <ClockIcon className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {session.scheduledTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => startStudySession(session)}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-xs hover:bg-blue-600 transition-colors"
                  >
                    Iniciar
                  </button>
                </div>
              ))}
          </div>
        </Card>
      </div>

      {/* AI Recommendations */}
      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Recomendações da IA</h3>
            <p className="text-sm text-gray-600">Baseado no seu histórico de estudos</p>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-4">
          {analytics.recommendedFocus.map((focus, index) => (
            <div key={index} className="bg-white p-4 rounded-lg border">
              <div className="flex items-center gap-2 mb-2">
                <LightBulbIcon className="w-4 h-4 text-yellow-500" />
                <span className="font-medium text-gray-900">{focus}</span>
              </div>
              <p className="text-sm text-gray-600">
                {focus === 'Direito Tributário' && 'Sua área com menor performance. Recomendamos 2h extras esta semana.'}
                {focus === 'Simulados' && 'Pratique mais simulados para melhorar seu tempo de resposta.'}
                {focus === 'Revisão Geral' && 'Hora de consolidar o conhecimento com revisões estratégicas.'}
              </p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderSchedule = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Cronograma de Estudos</h2>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
            <CalendarIcon className="w-4 h-4" />
            Adicionar Sessão
          </button>
          <button className="flex items-center gap-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-colors">
            <AdjustmentsHorizontalIcon className="w-4 h-4" />
            Personalizar
          </button>
        </div>
      </div>

      <Card className="p-6">
        <div className="space-y-4">
          {weeklyPlan.sessions.map((session) => (
            <div key={session.id} className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="w-2 h-12 rounded-full bg-gradient-to-b from-blue-500 to-purple-500"></div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-gray-900">{session.topic}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(session.status)}`}>
                    {session.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{session.subject}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <ClockIcon className="w-3 h-3" />
                    {session.scheduledTime.toLocaleString('pt-BR')}
                  </div>
                  <div className="flex items-center gap-1">
                    <BookOpenIcon className="w-3 h-3" />
                    {formatDuration(session.duration)}
                  </div>
                  <div className="flex items-center gap-1">
                    <StarSolid className="w-3 h-3 text-yellow-500" />
                    {session.xpReward} XP
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {session.status === 'scheduled' && (
                  <button
                    onClick={() => startStudySession(session)}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 transition-colors"
                  >
                    Iniciar
                  </button>
                )}
                {session.status === 'completed' && (
                  <CheckCircleSolid className="w-6 h-6 text-green-500" />
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Visão Geral', icon: ChartBarIcon },
    { id: 'schedule', label: 'Cronograma', icon: CalendarIcon },
    { id: 'goals', label: 'Metas', icon: FlagIcon },
    { id: 'analytics', label: 'Analytics', icon: DocumentTextIcon },
    { id: 'ai-tutor', label: 'IA Tutor', icon: SparklesIcon }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <AcademicCapIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Plano de Estudos Inteligente</h1>
            <p className="text-blue-100">
              Seu assistente pessoal para uma preparação eficiente e personalizada
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'schedule' && renderSchedule()}
        {activeTab === 'goals' && (
          <div className="text-center py-12">
            <FlagIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Gerenciamento de Metas</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
        {activeTab === 'analytics' && (
          <div className="text-center py-12">
            <ChartBarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Detalhado</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
        {activeTab === 'ai-tutor' && (
          <div className="text-center py-12">
            <SparklesIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">IA Tutor Personalizado</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StudyPlan; 