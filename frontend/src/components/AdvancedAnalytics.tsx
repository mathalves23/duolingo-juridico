import React, { useState, useEffect } from 'react';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  EyeIcon,
  ClockIcon,
  CpuChipIcon,
  LightBulbIcon,
  TagIcon,
  CalendarDaysIcon,
  UsersIcon,
  AcademicCapIcon,
  SparklesIcon,
  ChartPieIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

// Mock useAuth para evitar erro de contexto
const useAuth = () => ({
  user: {
    id: 1,
    first_name: 'Usuário',
    last_name: 'Demo',
    email: 'demo@teste.com'
  },
  isAuthenticated: true
});

interface PredictiveInsight {
  id: string;
  type: 'success' | 'warning' | 'info' | 'danger';
  title: string;
  description: string;
  confidence: number;
  timeframe: string;
  action?: string;
}

interface PerformanceMetric {
  label: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change: number;
}

interface LearningPattern {
  pattern: string;
  frequency: number;
  impact: string;
  recommendation: string;
}

const AdvancedAnalytics: React.FC = () => {
  const { user } = useAuth();
  const [insights, setInsights] = useState<PredictiveInsight[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [patterns, setPatterns] = useState<LearningPattern[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState('7d');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [selectedTimeframe]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      // Simular dados analíticos avançados
      setTimeout(() => {
        setInsights([
          {
            id: '1',
            type: 'success',
            title: 'Melhoria Significativa Detectada',
            description: 'Seu desempenho em Direito Constitucional melhorou 23% nas últimas 2 semanas',
            confidence: 92,
            timeframe: 'Próximos 7 dias',
            action: 'Continue focando em jurisprudência do STF'
          },
          {
            id: '2',
            type: 'warning',
            title: 'Risco de Burnout Detectado',
            description: 'Padrão de estudo indica sobrecarga. Recomendamos pausas mais frequentes',
            confidence: 78,
            timeframe: 'Próximos 3 dias',
            action: 'Reduzir sessões para 45 minutos'
          },
          {
            id: '3',
            type: 'info',
            title: 'Momento Ideal para Novo Tópico',
            description: 'IA sugere iniciar Direito Administrativo baseado em seu progresso atual',
            confidence: 85,
            timeframe: 'Esta semana',
            action: 'Começar com princípios básicos'
          }
        ]);

        setMetrics([
          { label: 'Taxa de Retenção', value: 87, unit: '%', trend: 'up', change: 5.2 },
          { label: 'Velocidade de Aprendizado', value: 1.4, unit: 'x', trend: 'up', change: 12.3 },
          { label: 'Precisão de Predições', value: 91, unit: '%', trend: 'stable', change: 0.8 },
          { label: 'Engajamento Médio', value: 8.7, unit: '/10', trend: 'up', change: 3.1 }
        ]);

        setPatterns([
          {
            pattern: 'Estudo matinal intensivo',
            frequency: 85,
            impact: 'Alto desempenho em questões complexas',
            recommendation: 'Manter horário das 7h-9h'
          },
          {
            pattern: 'Revisão espaçada eficaz',
            frequency: 72,
            impact: 'Retenção 40% superior',
            recommendation: 'Aumentar intervalos gradualmente'
          }
        ]);

        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
      setIsLoading(false);
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'warning': return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'info': return <LightBulbIcon className="w-5 h-5 text-blue-500" />;
      default: return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />;
      case 'down': return <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />;
      default: return <div className="w-4 h-4 bg-gray-400 rounded-full"></div>;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <CpuChipIcon className="w-8 h-8" />
              Analytics Preditivos
            </h1>
            <p className="text-purple-100 mt-1">
              IA avançada analisando seus padrões de aprendizado em tempo real
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">91%</div>
            <div className="text-sm text-purple-100">Precisão das Predições</div>
          </div>
        </div>
      </div>

      {/* Filtros de Tempo */}
      <div className="flex gap-2">
        {[
          { key: '24h', label: '24 horas' },
          { key: '7d', label: '7 dias' },
          { key: '30d', label: '30 dias' },
          { key: '90d', label: '3 meses' }
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSelectedTimeframe(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedTimeframe === key
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Insights Preditivos */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <SparklesIcon className="w-6 h-6 text-purple-600" />
          Insights Preditivos da IA
        </h2>
        <div className="space-y-4">
          {insights.map((insight) => (
            <div
              key={insight.id}
              className="p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-3">
                {getInsightIcon(insight.type)}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {insight.confidence}% confiança
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{insight.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <ClockIcon className="w-3 h-3" />
                      {insight.timeframe}
                    </span>
                    {insight.action && (
                      <button className="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded-full hover:bg-blue-100">
                        {insight.action}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Métricas de Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-500">{metric.label}</h3>
              {getTrendIcon(metric.trend)}
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-gray-900">
                {metric.value}{metric.unit}
              </span>
              <span className={`text-xs px-1.5 py-0.5 rounded ${
                metric.trend === 'up' ? 'bg-green-100 text-green-600' :
                metric.trend === 'down' ? 'bg-red-100 text-red-600' :
                'bg-gray-100 text-gray-600'
              }`}>
                {metric.change > 0 ? '+' : ''}{metric.change}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Padrões de Aprendizado */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <ChartPieIcon className="w-6 h-6 text-green-600" />
          Padrões de Aprendizado Detectados
        </h2>
        <div className="space-y-4">
          {patterns.map((pattern, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900">{pattern.pattern}</h3>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${pattern.frequency}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-500">{pattern.frequency}%</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-2">{pattern.impact}</p>
              <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                💡 {pattern.recommendation}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Predições de Desempenho */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <ChartBarIcon className="w-6 h-6 text-orange-600" />
          Predições de Desempenho
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600 mb-1">+15%</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Próxima Semana</div>
            <div className="text-xs text-gray-600">Melhoria esperada em Constitucional</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 mb-1">78%</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Probabilidade</div>
            <div className="text-xs text-gray-600">De passar na próxima simulação</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 mb-1">12 dias</div>
            <div className="text-sm font-medium text-gray-900 mb-1">Tempo Estimado</div>
            <div className="text-xs text-gray-600">Para dominar próximo tópico</div>
          </div>
        </div>
      </div>

      {/* Recomendações da IA */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <CpuChipIcon className="w-6 h-6 text-blue-600" />
          Recomendações Personalizadas da IA
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">📚 Próximo Tópico Ideal</h3>
            <p className="text-sm text-gray-600 mb-3">
              Baseado em seu progresso, a IA recomenda iniciar "Processo Administrativo" 
              para maximizar seu aprendizado.
            </p>
            <button className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full hover:bg-blue-700">
              Começar Agora
            </button>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">⏰ Horário Otimizado</h3>
            <p className="text-sm text-gray-600 mb-3">
              Seus melhores resultados acontecem entre 7h-9h. Considere concentrar 
              estudos complexos neste período.
            </p>
            <button className="text-xs bg-green-600 text-white px-3 py-1 rounded-full hover:bg-green-700">
              Agendar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalytics; 