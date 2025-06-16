import React, { useState, useEffect } from 'react';
import {
  ClockIcon,
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
  TrophyIcon,
  CalendarIcon,
  UserGroupIcon,
  ChartBarIcon,
  AcademicCapIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';
import { Question, Subject } from '../types';

interface SimuladoConfig {
  id: string;
  name: string;
  description: string;
  examBoard: string;
  totalQuestions: number;
  timeLimit: number; // em minutos
  subjects: string[];
  difficulty: 'mixed' | 'easy' | 'medium' | 'hard';
  year?: number;
}

interface SimuladoAtivo {
  config: SimuladoConfig;
  questions: Question[];
  currentQuestionIndex: number;
  answers: Record<number, string>;
  timeRemaining: number;
  startedAt: Date;
  isRunning: boolean;
}

interface SimuladoResult {
  score: number;
  totalQuestions: number;
  timeSpent: number;
  accuracy: number;
  subjectBreakdown: Array<{subject: string, correct: number, total: number}>;
  correctAnswers: number[];
  wrongAnswers: number[];
}

const Quizzes: React.FC = () => {
  const { user } = useAuth();
  const [simulados, setSimulados] = useState<SimuladoConfig[]>([]);
  const [simuladoAtivo, setSimuladoAtivo] = useState<SimuladoAtivo | null>(null);
  const [resultado, setResultado] = useState<SimuladoResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    carregarSimulados();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (simuladoAtivo?.isRunning) {
      interval = setInterval(() => {
        setSimuladoAtivo(prev => {
          if (!prev) return null;
          
          const newTimeRemaining = prev.timeRemaining - 1;
          if (newTimeRemaining <= 0) {
            finalizarSimulado(prev);
            return null;
          }
          
          return { ...prev, timeRemaining: newTimeRemaining };
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [simuladoAtivo?.isRunning]);

  const carregarSimulados = async () => {
    setLoading(true);
    try {
      // Mock data para simulados predefinidos
      const mockSimulados: SimuladoConfig[] = [
        {
          id: 'cespe-constitucional-2024',
          name: 'CESPE - Direito Constitucional 2024',
          description: 'Simulado baseado nas provas mais recentes do CESPE',
          examBoard: 'CESPE',
          totalQuestions: 20,
          timeLimit: 40,
          subjects: ['Direito Constitucional'],
          difficulty: 'mixed',
          year: 2024
        },
        {
          id: 'fcc-administrativo-mix',
          name: 'FCC - Direito Administrativo Mix',
          description: 'Questões variadas de Direito Administrativo da FCC',
          examBoard: 'FCC',
          totalQuestions: 15,
          timeLimit: 30,
          subjects: ['Direito Administrativo'],
          difficulty: 'medium'
        },
        {
          id: 'vunesp-simulado-geral',
          name: 'VUNESP - Simulado Geral',
          description: 'Simulado completo com todas as disciplinas básicas',
          examBoard: 'VUNESP',
          totalQuestions: 30,
          timeLimit: 60,
          subjects: ['Direito Constitucional', 'Direito Administrativo', 'Direito Penal'],
          difficulty: 'mixed'
        },
        {
          id: 'fgv-penal-avancado',
          name: 'FGV - Direito Penal Avançado',
          description: 'Questões de nível avançado em Direito Penal',
          examBoard: 'FGV',
          totalQuestions: 25,
          timeLimit: 50,
          subjects: ['Direito Penal'],
          difficulty: 'hard'
        }
      ];
      
      setSimulados(mockSimulados);
    } catch (error) {
      console.error('Erro ao carregar simulados:', error);
    } finally {
      setLoading(false);
    }
  };

  const iniciarSimulado = async (config: SimuladoConfig) => {
    setLoading(true);
    try {
      // Carregar questões para o simulado
      // Em produção, viria da API filtrada por banca e disciplinas
      const questoesMock: Question[] = Array.from({ length: config.totalQuestions }, (_, index) => ({
        id: index + 1,
        title: `Questão ${index + 1} - ${config.examBoard}`,
        question_text: `Esta é uma questão de exemplo sobre ${config.subjects[index % config.subjects.length]}. Assinale a alternativa correta.`,
        question_type: 'multiple_choice',
        subject: 1,
        exam_board: 1,
        exam_name: config.examBoard,
        exam_year: config.year || 2024,
        difficulty_level: config.difficulty === 'easy' ? 1 : config.difficulty === 'medium' ? 3 : 5,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }));

      const novoSimulado: SimuladoAtivo = {
        config,
        questions: questoesMock,
        currentQuestionIndex: 0,
        answers: {},
        timeRemaining: config.timeLimit * 60, // converter para segundos
        startedAt: new Date(),
        isRunning: true
      };

      setSimuladoAtivo(novoSimulado);
      setResultado(null);
    } catch (error) {
      console.error('Erro ao iniciar simulado:', error);
    } finally {
      setLoading(false);
    }
  };

  const responderQuestao = (questionId: number, resposta: string) => {
    if (!simuladoAtivo) return;

    setSimuladoAtivo(prev => {
      if (!prev) return null;
      return {
        ...prev,
        answers: { ...prev.answers, [questionId]: resposta }
      };
    });
  };

  const proximaQuestao = () => {
    if (!simuladoAtivo) return;

    if (simuladoAtivo.currentQuestionIndex < simuladoAtivo.questions.length - 1) {
      setSimuladoAtivo(prev => {
        if (!prev) return null;
        return { ...prev, currentQuestionIndex: prev.currentQuestionIndex + 1 };
      });
    }
  };

  const questaoAnterior = () => {
    if (!simuladoAtivo) return;

    if (simuladoAtivo.currentQuestionIndex > 0) {
      setSimuladoAtivo(prev => {
        if (!prev) return null;
        return { ...prev, currentQuestionIndex: prev.currentQuestionIndex - 1 };
      });
    }
  };

  const pausarResumir = () => {
    if (!simuladoAtivo) return;

    setSimuladoAtivo(prev => {
      if (!prev) return null;
      return { ...prev, isRunning: !prev.isRunning };
    });
  };

  const finalizarSimulado = (simulado: SimuladoAtivo) => {
    const timeSpent = simulado.config.timeLimit * 60 - simulado.timeRemaining;
    const totalAnswered = Object.keys(simulado.answers).length;
    
    // Simular correção (em produção, viria da API)
    const correctAnswers = Object.values(simulado.answers).filter((_, index) => 
      Math.random() > 0.3 // 70% chance de acerto para demo
    ).length;

    const resultado: SimuladoResult = {
      score: correctAnswers,
      totalQuestions: simulado.config.totalQuestions,
      timeSpent,
      accuracy: (correctAnswers / totalAnswered) * 100,
      correctAnswers: Array.from({length: correctAnswers}, (_, i) => i + 1),
      wrongAnswers: Array.from({length: totalAnswered - correctAnswers}, (_, i) => correctAnswers + i + 1),
      subjectBreakdown: simulado.config.subjects.map(subject => ({
        subject,
        correct: Math.floor(Math.random() * 5) + 3,
        total: Math.floor(simulado.config.totalQuestions / simulado.config.subjects.length)
      }))
    };

    setResultado(resultado);
    setSimuladoAtivo(null);
  };

  const formatarTempo = (segundos: number) => {
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const secs = segundos % 60;
    
    if (horas > 0) {
      return `${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutos.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const filteredSimulados = simulados.filter(simulado => {
    if (selectedFilter === 'all') return true;
    return simulado.examBoard.toLowerCase() === selectedFilter.toLowerCase();
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ArrowPathIcon className="h-12 w-12 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Carregando simulados...</p>
        </div>
      </div>
    );
  }

  // Tela de resultado do simulado
  if (resultado) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Header do resultado */}
            <div className="bg-gradient-to-r from-green-500 to-green-600 px-8 py-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold">Simulado Concluído!</h1>
                  <p className="text-green-100 mt-1">Confira seu desempenho abaixo</p>
                </div>
                <div className="bg-white bg-opacity-20 p-4 rounded-lg">
                  <TrophyIcon className="h-10 w-10" />
                </div>
              </div>
            </div>

            {/* Estatísticas principais */}
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center p-6 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600">{resultado.score}/{resultado.totalQuestions}</div>
                  <div className="text-sm text-blue-800 mt-1">Questões Certas</div>
                </div>
                
                <div className="text-center p-6 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-600">{resultado.accuracy.toFixed(1)}%</div>
                  <div className="text-sm text-green-800 mt-1">Taxa de Acerto</div>
                </div>
                
                <div className="text-center p-6 bg-purple-50 rounded-lg">
                  <div className="text-3xl font-bold text-purple-600">{formatarTempo(resultado.timeSpent)}</div>
                  <div className="text-sm text-purple-800 mt-1">Tempo Gasto</div>
                </div>
                
                <div className="text-center p-6 bg-orange-50 rounded-lg">
                  <div className="text-3xl font-bold text-orange-600">
                    {Math.floor(resultado.timeSpent / Object.keys(simuladoAtivo?.answers || {}).length)}s
                  </div>
                  <div className="text-sm text-orange-800 mt-1">Por Questão</div>
                </div>
              </div>

              {/* Breakdown por disciplina */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance por Disciplina</h3>
                <div className="space-y-3">
                  {resultado.subjectBreakdown.map((subject, index) => (
                    <div key={subject.subject} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <AcademicCapIcon className="h-5 w-5 text-gray-600" />
                        <span className="font-medium text-gray-900">{subject.subject}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-600">
                          {subject.correct}/{subject.total}
                        </span>
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{width: `${(subject.correct / subject.total) * 100}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold text-gray-900 w-12">
                          {Math.round((subject.correct / subject.total) * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Botões de ação */}
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => setResultado(null)}
                  className="btn btn-secondary flex items-center space-x-2"
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  <span>Novo Simulado</span>
                </button>
                
                <button
                  onClick={() => {/* Implementar revisão */}}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <DocumentTextIcon className="h-4 w-4" />
                  <span>Revisar Questões</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Tela do simulado ativo
  if (simuladoAtivo) {
    const questaoAtual = simuladoAtivo.questions[simuladoAtivo.currentQuestionIndex];
    const respostaSelecionada = simuladoAtivo.answers[questaoAtual.id];
    const progressoPercentual = ((simuladoAtivo.currentQuestionIndex + 1) / simuladoAtivo.questions.length) * 100;

    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header do simulado */}
        <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    {simuladoAtivo.currentQuestionIndex + 1} de {simuladoAtivo.questions.length}
                  </span>
                </div>
                
                <div className="w-48 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                    style={{width: `${progressoPercentual}%`}}
                  ></div>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg ${
                  simuladoAtivo.timeRemaining < 300 ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                }`}>
                  <ClockIcon className="h-4 w-4" />
                  <span className="font-mono font-semibold">
                    {formatarTempo(simuladoAtivo.timeRemaining)}
                  </span>
                </div>
                
                <button
                  onClick={pausarResumir}
                  className="btn btn-secondary flex items-center space-x-2"
                >
                  {simuladoAtivo.isRunning ? (
                    <PauseIcon className="h-4 w-4" />
                  ) : (
                    <PlayIcon className="h-4 w-4" />
                  )}
                  <span>{simuladoAtivo.isRunning ? 'Pausar' : 'Continuar'}</span>
                </button>
                
                <button
                  onClick={() => finalizarSimulado(simuladoAtivo)}
                  className="btn btn-primary"
                >
                  Finalizar
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Questão atual */}
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* Header da questão */}
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">{questaoAtual.title}</h2>
                  <p className="text-sm text-gray-600">{questaoAtual.exam_name} • {questaoAtual.exam_year}</p>
                </div>
                <div className="flex">
                  {[1, 2, 3, 4, 5].map(level => (
                    <div
                      key={level}
                      className={`w-2 h-2 rounded-full mr-1 ${
                        level <= questaoAtual.difficulty_level ? 'bg-yellow-400' : 'bg-gray-300'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Enunciado */}
            <div className="p-6">
              <div className="prose max-w-none">
                <p className="text-gray-900 leading-relaxed text-lg">
                  {questaoAtual.question_text}
                </p>
              </div>
            </div>

            {/* Alternativas */}
            <div className="px-6 pb-6">
              <div className="space-y-3">
                {['A', 'B', 'C', 'D', 'E'].map((letra, index) => {
                  const alternativas = [
                    'Esta é a primeira alternativa da questão.',
                    'Esta é a segunda alternativa da questão.',
                    'Esta é a terceira alternativa da questão.',
                    'Esta é a quarta alternativa da questão.',
                    'Esta é a quinta alternativa da questão.'
                  ];
                  
                  const isSelected = respostaSelecionada === letra;
                  
                  return (
                    <button
                      key={letra}
                      onClick={() => responderQuestao(questaoAtual.id, letra)}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
                        isSelected
                          ? 'border-primary-300 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-semibold ${
                          isSelected
                            ? 'border-primary-500 bg-primary-500 text-white'
                            : 'border-gray-300 text-gray-700'
                        }`}>
                          {letra}
                        </div>
                        <div>
                          <p className="text-gray-900">{alternativas[index]}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Navegação */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <button
                  onClick={questaoAnterior}
                  disabled={simuladoAtivo.currentQuestionIndex === 0}
                  className="btn btn-secondary disabled:opacity-50"
                >
                  ← Anterior
                </button>
                
                <div className="text-sm text-gray-600">
                  {Object.keys(simuladoAtivo.answers).length} de {simuladoAtivo.questions.length} respondidas
                </div>
                
                <button
                  onClick={proximaQuestao}
                  disabled={simuladoAtivo.currentQuestionIndex === simuladoAtivo.questions.length - 1}
                  className="btn btn-primary disabled:opacity-50"
                >
                  Próxima →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Tela principal com lista de simulados
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Simulados</h1>
            <p className="text-indigo-100 mt-2">
              Pratique com simulados reais de concursos públicos
            </p>
          </div>
          <div className="bg-white bg-opacity-20 p-4 rounded-lg">
            <DocumentTextIcon className="h-10 w-10" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Filtrar por banca:</span>
          <div className="flex space-x-2">
            {['all', 'CESPE', 'FCC', 'FGV', 'VUNESP'].map(filter => (
              <button
                key={filter}
                onClick={() => setSelectedFilter(filter)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  selectedFilter === filter
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {filter === 'all' ? 'Todas' : filter}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Lista de simulados */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredSimulados.map(simulado => (
          <div key={simulado.id} className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
            {/* Header do card */}
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{simulado.name}</h3>
                  <p className="text-sm text-gray-600">{simulado.description}</p>
                </div>
                <span className="bg-primary-100 text-primary-800 px-2 py-1 rounded-md text-xs font-semibold">
                  {simulado.examBoard}
                </span>
              </div>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <DocumentTextIcon className="h-4 w-4" />
                  <span>{simulado.totalQuestions} questões</span>
                </div>
                <div className="flex items-center space-x-1">
                  <ClockIcon className="h-4 w-4" />
                  <span>{simulado.timeLimit} min</span>
                </div>
                {simulado.year && (
                  <div className="flex items-center space-x-1">
                    <CalendarIcon className="h-4 w-4" />
                    <span>{simulado.year}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Disciplinas */}
            <div className="p-4 bg-gray-50">
              <div className="flex flex-wrap gap-2 mb-4">
                {simulado.subjects.map(subject => (
                  <span key={subject} className="bg-white px-2 py-1 rounded-md text-xs text-gray-700 border">
                    {subject}
                  </span>
                ))}
              </div>
              
              <button
                onClick={() => iniciarSimulado(simulado)}
                className="w-full btn btn-primary flex items-center justify-center space-x-2"
              >
                <PlayIcon className="h-4 w-4" />
                <span>Iniciar Simulado</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredSimulados.length === 0 && (
        <div className="text-center py-12">
          <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhum simulado encontrado</h3>
          <p className="text-gray-600">Tente ajustar os filtros para encontrar simulados.</p>
        </div>
      )}
    </div>
  );
};

export default Quizzes; 