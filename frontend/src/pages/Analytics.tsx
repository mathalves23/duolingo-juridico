import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  TrophyIcon,
  FireIcon,
  ClockIcon,
  AcademicCapIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';

interface PerformanceData {
  totalQuestions: number;
  correctAnswers: number;
  averageTime: number;
  currentStreak: number;
  longestStreak: number;
  weeklyProgress: Array<{day: string, questions: number, accuracy: number}>;
  subjectPerformance: Array<{subject: string, accuracy: number, questions: number}>;
  difficultyBreakdown: Array<{level: string, accuracy: number, count: number}>;
  recentActivity: Array<{date: string, activity: string, score: number}>;
}

const Analytics: React.FC = () => {
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [selectedView, setSelectedView] = useState('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      // Simular dados da API (em produção viria do backend)
      const mockData: PerformanceData = {
        totalQuestions: 247,
        correctAnswers: 189,
        averageTime: 42,
        currentStreak: 5,
        longestStreak: 12,
        weeklyProgress: [
          {day: 'Seg', questions: 8, accuracy: 87.5},
          {day: 'Ter', questions: 12, accuracy: 83.3},
          {day: 'Qua', questions: 15, accuracy: 93.3},
          {day: 'Qui', questions: 10, accuracy: 80.0},
          {day: 'Sex', questions: 18, accuracy: 88.9},
          {day: 'Sáb', questions: 5, accuracy: 100.0},
          {day: 'Dom', questions: 3, accuracy: 66.7}
        ],
        subjectPerformance: [
          {subject: 'Direito Constitucional', accuracy: 92.1, questions: 76},
          {subject: 'Direito Administrativo', accuracy: 87.3, questions: 63},
          {subject: 'Direito Penal', accuracy: 79.4, questions: 51},
          {subject: 'Direito Civil', accuracy: 84.6, questions: 39},
          {subject: 'Direito Processual', accuracy: 75.8, questions: 18}
        ],
        difficultyBreakdown: [
          {level: 'Fácil', accuracy: 94.2, count: 85},
          {level: 'Médio', accuracy: 82.7, count: 108},
          {level: 'Difícil', accuracy: 67.9, count: 54}
        ],
        recentActivity: [
          {date: '2024-01-10', activity: 'Quiz Constitucional', score: 9},
          {date: '2024-01-09', activity: 'Simulado CESPE', score: 7},
          {date: '2024-01-08', activity: 'Prática Diária', score: 8}
        ]
      };
      
      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 90) return 'text-green-600 bg-green-100';
    if (accuracy >= 75) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getAccuracyChange = (current: number, previous: number) => {
    const change = current - previous;
    return {
      value: Math.abs(change),
      direction: change >= 0 ? 'up' : 'down',
      color: change >= 0 ? 'text-green-600' : 'text-red-600'
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando estatísticas...</p>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Dados não disponíveis</h2>
          <p className="text-gray-600">Responda algumas questões para ver suas estatísticas.</p>
        </div>
      </div>
    );
  }

  const accuracyRate = (analyticsData.correctAnswers / analyticsData.totalQuestions) * 100;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-purple-100 mt-2">
              Acompanhe seu progresso e evolução nos estudos
            </p>
          </div>
          <div className="text-right">
            <div className="text-purple-100 text-sm">Taxa de Acerto Geral</div>
            <div className="text-3xl font-bold">{accuracyRate.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Filtros de período */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex space-x-1">
            {['week', 'month', 'year'].map(period => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedPeriod === period
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {period === 'week' ? 'Semana' : period === 'month' ? 'Mês' : 'Ano'}
              </button>
            ))}
          </div>
          
          <div className="flex space-x-1">
            {['overview', 'detailed'].map(view => (
              <button
                key={view}
                onClick={() => setSelectedView(view)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedView === view
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {view === 'overview' ? 'Visão Geral' : 'Detalhado'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Cards de estatísticas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Questões Respondidas</p>
              <p className="text-2xl font-bold text-gray-900">{analyticsData.totalQuestions}</p>
              <p className="text-xs text-green-600 mt-1">+12 esta semana</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Taxa de Acerto</p>
              <p className="text-2xl font-bold text-gray-900">{accuracyRate.toFixed(1)}%</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-600 mr-1" />
                <p className="text-xs text-green-600">+2.3% vs semana passada</p>
              </div>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <TrophyIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Streak Atual</p>
              <p className="text-2xl font-bold text-gray-900">{analyticsData.currentStreak}</p>
              <p className="text-xs text-gray-600 mt-1">Máximo: {analyticsData.longestStreak} dias</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-lg">
              <FireIcon className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tempo Médio</p>
              <p className="text-2xl font-bold text-gray-900">{analyticsData.averageTime}s</p>
              <div className="flex items-center mt-1">
                <ArrowTrendingDownIcon className="h-4 w-4 text-green-600 mr-1" />
                <p className="text-xs text-green-600">-5s vs média</p>
              </div>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <ClockIcon className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos e análises */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progresso Semanal */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Progresso Semanal</h3>
          <div className="space-y-4">
            {analyticsData.weeklyProgress.map((day, index) => (
              <div key={day.day} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                    <span className="text-sm font-semibold text-primary-700">{day.day}</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{day.questions} questões</p>
                    <p className="text-xs text-gray-600">{day.accuracy}% acerto</p>
                  </div>
                </div>
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full" 
                    style={{width: `${day.accuracy}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance por Disciplina */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance por Disciplina</h3>
          <div className="space-y-4">
            {analyticsData.subjectPerformance.map((subject, index) => (
              <div key={subject.subject} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{subject.subject}</p>
                    <p className="text-xs text-gray-600">{subject.questions} questões</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-md text-xs font-semibold ${getAccuracyColor(subject.accuracy)}`}>
                      {subject.accuracy}%
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      subject.accuracy >= 90 ? 'bg-green-500' :
                      subject.accuracy >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{width: `${subject.accuracy}%`}}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Análise por Dificuldade e Atividade Recente */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Breakdown por Dificuldade */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Análise por Dificuldade</h3>
          <div className="space-y-4">
            {analyticsData.difficultyBreakdown.map((level, index) => (
              <div key={level.level} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    level.level === 'Fácil' ? 'bg-green-500' :
                    level.level === 'Médio' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{level.level}</p>
                    <p className="text-xs text-gray-600">{level.count} questões</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-gray-900">{level.accuracy}%</p>
                  <div className="w-16 bg-gray-200 rounded-full h-1 mt-1">
                    <div 
                      className={`h-1 rounded-full ${
                        level.level === 'Fácil' ? 'bg-green-500' :
                        level.level === 'Médio' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{width: `${level.accuracy}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Atividade Recente */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Atividade Recente</h3>
          <div className="space-y-4">
            {analyticsData.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <AcademicCapIcon className="h-5 w-5 text-primary-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{activity.activity}</p>
                    <p className="text-xs text-gray-600">{activity.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-semibold text-gray-900">{activity.score}/10</span>
                  <div className="w-12 bg-gray-200 rounded-full h-1 mt-1">
                    <div 
                      className="bg-primary-600 h-1 rounded-full" 
                      style={{width: `${activity.score * 10}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recomendações */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recomendações Personalizadas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <ArrowTrendingUpIcon className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-semibold text-blue-900">Foco em Direito Penal</span>
            </div>
            <p className="text-xs text-blue-800">
              Sua performance em Direito Penal (79.4%) está abaixo da média. 
              Pratique mais questões desta disciplina.
            </p>
          </div>

          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <FireIcon className="h-5 w-5 text-green-600" />
              <span className="text-sm font-semibold text-green-900">Mantenha o Streak</span>
            </div>
            <p className="text-xs text-green-800">
              Você está em uma sequência de 5 dias! Continue estudando para 
              bater seu recorde de 12 dias.
            </p>
          </div>

          <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <ClockIcon className="h-5 w-5 text-orange-600" />
              <span className="text-sm font-semibold text-orange-900">Otimize o Tempo</span>
            </div>
            <p className="text-xs text-orange-800">
              Seu tempo médio por questão melhorou! Continue praticando 
              questões de nível difícil para ganhar agilidade.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 