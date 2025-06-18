import React, { useState, useEffect } from 'react';
import {
  ClockIcon,
  ChartBarIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlayIcon,
  PauseIcon,
  ArrowRightIcon,
  LightBulbIcon,
  SparklesIcon,
  TrophyIcon,
  FireIcon,
  BookOpenIcon,
  EyeIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import {
  CheckCircleIcon as CheckCircleSolid,
  XCircleIcon as XCircleSolid,
  StarIcon as StarSolid
} from '@heroicons/react/24/solid';
import Card from '../components/Card';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

interface Question {
  id: string;
  subject: string;
  topic: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  source: string;
  year?: number;
}

interface SimulationResult {
  id: string;
  name: string;
  date: Date;
  totalQuestions: number;
  correctAnswers: number;
  timeSpent: number;
  score: number;
  subjects: { [key: string]: { correct: number; total: number } };
  difficulty: string;
  type: 'oab' | 'concurso' | 'custom';
}

interface ExamTemplate {
  id: string;
  name: string;
  description: string;
  totalQuestions: number;
  timeLimit: number;
  subjects: { [key: string]: number };
  difficulty: string;
  type: 'oab' | 'concurso' | 'custom';
  icon: string;
}

const ExamSimulator: React.FC = () => {
  const { user } = useAuth();
  const { success, info, error } = useNotification();
  const [activeTab, setActiveTab] = useState<'templates' | 'simulation' | 'results' | 'analytics'>('templates');
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: number }>({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<ExamTemplate | null>(null);
  const [simulationQuestions, setSimulationQuestions] = useState<Question[]>([]);

  const examTemplates: ExamTemplate[] = [
    {
      id: 'oab-1',
      name: 'Simulado OAB Completo',
      description: 'Simulado completo baseado no padrão do exame da OAB com 80 questões',
      totalQuestions: 80,
      timeLimit: 300, // 5 horas em minutos
      subjects: {
        'Direito Constitucional': 15,
        'Direito Civil': 20,
        'Direito Penal': 15,
        'Direito Processual Civil': 15,
        'Direito Processual Penal': 10,
        'Direito Empresarial': 5
      },
      difficulty: 'medium',
      type: 'oab',
      icon: '⚖️'
    },
    {
      id: 'oab-2',
      name: 'OAB - Direito Constitucional',
      description: 'Foco específico em Direito Constitucional com questões de concursos anteriores',
      totalQuestions: 30,
      timeLimit: 90,
      subjects: {
        'Direito Constitucional': 30
      },
      difficulty: 'hard',
      type: 'oab',
      icon: '📜'
    },
    {
      id: 'concurso-1',
      name: 'Concurso Público - Nível Superior',
      description: 'Simulado para concursos públicos da área jurídica',
      totalQuestions: 50,
      timeLimit: 180,
      subjects: {
        'Direito Administrativo': 20,
        'Direito Constitucional': 15,
        'Direito Civil': 10,
        'Direito Penal': 5
      },
      difficulty: 'medium',
      type: 'concurso',
      icon: '🏛️'
    },
    {
      id: 'custom-1',
      name: 'Revisão Rápida',
      description: 'Simulado rápido para revisão com questões variadas',
      totalQuestions: 20,
      timeLimit: 45,
      subjects: {
        'Direito Civil': 8,
        'Direito Penal': 6,
        'Direito Constitucional': 6
      },
      difficulty: 'easy',
      type: 'custom',
      icon: '⚡'
    }
  ];

  const mockQuestions: Question[] = [
    {
      id: '1',
      subject: 'Direito Constitucional',
      topic: 'Princípios Fundamentais',
      question: 'Segundo a Constituição Federal de 1988, são fundamentos da República Federativa do Brasil, EXCETO:',
      options: [
        'A soberania',
        'A cidadania',
        'A dignidade da pessoa humana',
        'O desenvolvimento econômico',
        'O pluralismo político'
      ],
      correctAnswer: 3,
      explanation: 'O desenvolvimento econômico não está listado entre os fundamentos da República no art. 1º da CF/88. Os fundamentos são: soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e da livre iniciativa, e pluralismo político.',
      difficulty: 'medium',
      source: 'OAB 2023',
      year: 2023
    },
    {
      id: '2',
      subject: 'Direito Civil',
      topic: 'Personalidade Jurídica',
      question: 'A personalidade civil da pessoa natural termina com:',
      options: [
        'A maioridade',
        'O casamento',
        'A morte',
        'A emancipação',
        'A interdição'
      ],
      correctAnswer: 2,
      explanation: 'Segundo o art. 6º do Código Civil, a existência da pessoa natural termina com a morte. A morte é o marco final da personalidade jurídica da pessoa natural.',
      difficulty: 'easy',
      source: 'Código Civil',
      year: 2024
    },
    {
      id: '3',
      subject: 'Direito Penal',
      topic: 'Teoria Geral do Crime',
      question: 'São elementos do crime:',
      options: [
        'Tipicidade, ilicitude e culpabilidade',
        'Dolo, culpa e preterdolo',
        'Ação, resultado e nexo causal',
        'Imputabilidade, potencial consciência da ilicitude e exigibilidade de conduta diversa',
        'Consumação, tentativa e crime impossível'
      ],
      correctAnswer: 0,
      explanation: 'Os elementos do crime são: tipicidade (adequação do fato ao tipo penal), ilicitude (contrariedade ao direito) e culpabilidade (reprovabilidade da conduta). Esta é a teoria tripartite adotada pelo direito penal brasileiro.',
      difficulty: 'medium',
      source: 'Doutrina',
      year: 2024
    }
  ];

  const [results] = useState<SimulationResult[]>([
    {
      id: '1',
      name: 'Simulado OAB Completo',
      date: new Date('2024-01-20'),
      totalQuestions: 80,
      correctAnswers: 68,
      timeSpent: 285,
      score: 85,
      subjects: {
        'Direito Constitucional': { correct: 13, total: 15 },
        'Direito Civil': { correct: 18, total: 20 },
        'Direito Penal': { correct: 12, total: 15 },
        'Direito Processual Civil': { correct: 13, total: 15 },
        'Direito Processual Penal': { correct: 8, total: 10 },
        'Direito Empresarial': { correct: 4, total: 5 }
      },
      difficulty: 'medium',
      type: 'oab'
    },
    {
      id: '2',
      name: 'OAB - Direito Constitucional',
      date: new Date('2024-01-18'),
      totalQuestions: 30,
      correctAnswers: 24,
      timeSpent: 75,
      score: 80,
      subjects: {
        'Direito Constitucional': { correct: 24, total: 30 }
      },
      difficulty: 'hard',
      type: 'oab'
    }
  ]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSimulating && timeRemaining > 0 && !isPaused) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            finishSimulation();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isSimulating, timeRemaining, isPaused]);

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  };

  const startSimulation = (template: ExamTemplate) => {
    setSelectedTemplate(template);
    setSimulationQuestions(mockQuestions.slice(0, template.totalQuestions));
    setIsSimulating(true);
    setCurrentQuestion(0);
    setAnswers({});
    setTimeRemaining(template.timeLimit);
    setIsPaused(false);
    setShowExplanation(false);
    setActiveTab('simulation');
    
    success(
      'Simulação Iniciada! 🎯',
      `${template.name} - ${template.totalQuestions} questões em ${formatTime(template.timeLimit)}`
    );
  };

  const selectAnswer = (questionIndex: number, answerIndex: number) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answerIndex
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < simulationQuestions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
      setShowExplanation(false);
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
      setShowExplanation(false);
    }
  };

  const finishSimulation = () => {
    if (!selectedTemplate) return;
    
    const correctAnswers = simulationQuestions.reduce((count, question, index) => {
      return answers[index] === question.correctAnswer ? count + 1 : count;
    }, 0);
    
    const score = Math.round((correctAnswers / simulationQuestions.length) * 100);
    const timeSpent = selectedTemplate.timeLimit - timeRemaining;
    
    setIsSimulating(false);
    setActiveTab('results');
    
    success(
      'Simulação Concluída! 🎉',
      `Você acertou ${correctAnswers} de ${simulationQuestions.length} questões (${score}%)`,
      [
        {
          label: 'Ver Resultados',
          action: () => setActiveTab('results'),
          style: 'primary'
        }
      ]
    );
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'oab': return '⚖️';
      case 'concurso': return '🏛️';
      case 'custom': return '⚡';
      default: return '📝';
    }
  };

  const renderTemplates = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Escolha seu Simulado</h2>
        <p className="text-gray-600">Selecione o tipo de simulado que melhor atende seus objetivos de estudo</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-6">
        {examTemplates.map((template) => (
          <Card key={template.id} className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-start gap-4">
              <div className="text-4xl">{template.icon}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor(template.difficulty)}`}>
                    {template.difficulty.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-4">{template.description}</p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <DocumentTextIcon className="w-4 h-4" />
                    <span>{template.totalQuestions} questões</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <ClockIcon className="w-4 h-4" />
                    <span>{formatTime(template.timeLimit)}</span>
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Matérias:</h4>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(template.subjects).map(([subject, count]) => (
                      <span key={subject} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {subject}: {count}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => startSimulation(template)}
                  className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
                >
                  <PlayIcon className="w-4 h-4" />
                  Iniciar Simulado
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Simulado Personalizado com IA</h3>
            <p className="text-sm text-gray-600">Crie um simulado baseado nas suas dificuldades e objetivos</p>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <LightBulbIcon className="w-4 h-4 text-yellow-500" />
              <span className="font-medium text-gray-900">Análise Inteligente</span>
            </div>
            <p className="text-sm text-gray-600">IA analisa seu histórico e cria questões focadas nas suas dificuldades</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <ChartBarIcon className="w-4 h-4 text-blue-500" />
              <span className="font-medium text-gray-900">Dificuldade Adaptativa</span>
            </div>
            <p className="text-sm text-gray-600">Nível de dificuldade se ajusta conforme seu desempenho</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <TrophyIcon className="w-4 h-4 text-green-500" />
              <span className="font-medium text-gray-900">Feedback Detalhado</span>
            </div>
            <p className="text-sm text-gray-600">Explicações personalizadas e dicas de estudo</p>
          </div>
        </div>

        <button className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 transition-colors flex items-center gap-2">
          <SparklesIcon className="w-4 h-4" />
          Criar Simulado com IA
        </button>
      </Card>
    </div>
  );

  const renderSimulation = () => {
    if (!isSimulating || !selectedTemplate || simulationQuestions.length === 0) {
      return renderTemplates();
    }

    const currentQ = simulationQuestions[currentQuestion];
    const progress = ((currentQuestion + 1) / simulationQuestions.length) * 100;

    return (
      <div className="space-y-6">
        {/* Header da Simulação */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{selectedTemplate.name}</h2>
              <p className="text-sm text-gray-600">
                Questão {currentQuestion + 1} de {simulationQuestions.length}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{formatTime(timeRemaining)}</div>
                <div className="text-xs text-gray-500">Tempo restante</div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setIsPaused(!isPaused)}
                  className={`p-2 rounded-lg transition-colors ${
                    isPaused ? 'bg-green-500 hover:bg-green-600' : 'bg-yellow-500 hover:bg-yellow-600'
                  } text-white`}
                >
                  {isPaused ? <PlayIcon className="w-4 h-4" /> : <PauseIcon className="w-4 h-4" />}
                </button>
                <button
                  onClick={finishSimulation}
                  className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
                >
                  Finalizar
                </button>
              </div>
            </div>
          </div>

          {/* Barra de Progresso */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </Card>

        {/* Questão */}
        <Card className="p-6">
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium text-blue-600">{currentQ.subject}</span>
              <span className="text-sm text-gray-500">•</span>
              <span className="text-sm text-gray-500">{currentQ.topic}</span>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor(currentQ.difficulty)}`}>
                {currentQ.difficulty}
              </span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 leading-relaxed">
              {currentQ.question}
            </h3>
          </div>

          <div className="space-y-3 mb-6">
            {currentQ.options.map((option, index) => (
              <button
                key={index}
                onClick={() => selectAnswer(currentQuestion, index)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  answers[currentQuestion] === index
                    ? 'border-blue-500 bg-blue-50 text-blue-900'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                    answers[currentQuestion] === index
                      ? 'border-blue-500 bg-blue-500 text-white'
                      : 'border-gray-300'
                  }`}>
                    {answers[currentQuestion] === index && (
                      <CheckCircleIcon className="w-4 h-4" />
                    )}
                  </div>
                  <span className="flex-1">{option}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Explicação (se habilitada) */}
          {showExplanation && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2 mb-2">
                <LightBulbIcon className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-blue-900">Explicação</span>
              </div>
              <p className="text-blue-800">{currentQ.explanation}</p>
              <div className="mt-2 text-sm text-blue-600">
                Fonte: {currentQ.source} {currentQ.year && `(${currentQ.year})`}
              </div>
            </div>
          )}

          {/* Controles de Navegação */}
          <div className="flex items-center justify-between">
            <button
              onClick={previousQuestion}
              disabled={currentQuestion === 0}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>

            <div className="flex gap-2">
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors"
              >
                <EyeIcon className="w-4 h-4" />
                {showExplanation ? 'Ocultar' : 'Ver'} Explicação
              </button>
            </div>

            <button
              onClick={nextQuestion}
              disabled={currentQuestion === simulationQuestions.length - 1}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Próxima
              <ArrowRightIcon className="w-4 h-4" />
            </button>
          </div>
        </Card>

        {/* Mapa de Questões */}
        <Card className="p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Mapa de Questões</h4>
          <div className="grid grid-cols-10 gap-2">
            {simulationQuestions.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentQuestion(index)}
                className={`w-8 h-8 rounded text-xs font-medium transition-colors ${
                  index === currentQuestion
                    ? 'bg-blue-500 text-white'
                    : answers[index] !== undefined
                    ? 'bg-green-100 text-green-800 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </Card>
      </div>
    );
  };

  const renderResults = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Histórico de Simulados</h2>
        <p className="text-gray-600">Acompanhe sua evolução e identifique pontos de melhoria</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-6">
        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <TrophyIcon className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{results.length}</div>
          <div className="text-sm text-gray-600">Simulados Realizados</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <ChartBarIcon className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {Math.round(results.reduce((acc, r) => acc + r.score, 0) / results.length)}%
          </div>
          <div className="text-sm text-gray-600">Média Geral</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <FireIcon className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {Math.max(...results.map(r => r.score))}%
          </div>
          <div className="text-sm text-gray-600">Melhor Score</div>
        </Card>
      </div>

      <div className="space-y-4">
        {results.map((result) => (
          <Card key={result.id} className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="text-2xl">{getTypeIcon(result.type)}</div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{result.name}</h3>
                  <p className="text-sm text-gray-600">
                    {result.date.toLocaleDateString('pt-BR')} • {formatTime(result.timeSpent)}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">{result.score}%</div>
                <div className="text-sm text-gray-600">
                  {result.correctAnswers}/{result.totalQuestions} acertos
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-6 gap-4">
              {Object.entries(result.subjects).map(([subject, stats]) => (
                <div key={subject} className="text-center">
                  <div className="text-sm font-medium text-gray-900 mb-1">
                    {subject.replace('Direito ', '')}
                  </div>
                  <div className="text-lg font-bold text-gray-700">
                    {stats.correct}/{stats.total}
                  </div>
                  <div className="text-xs text-gray-500">
                    {Math.round((stats.correct / stats.total) * 100)}%
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex gap-2">
              <button className="flex items-center gap-2 bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors">
                <EyeIcon className="w-4 h-4" />
                Ver Detalhes
              </button>
              <button className="flex items-center gap-2 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 transition-colors">
                <ArrowPathIcon className="w-4 h-4" />
                Refazer
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const tabs = [
    { id: 'templates', label: 'Simulados', icon: DocumentTextIcon },
    { id: 'simulation', label: 'Em Andamento', icon: PlayIcon },
    { id: 'results', label: 'Resultados', icon: ChartBarIcon },
    { id: 'analytics', label: 'Analytics', icon: TrophyIcon }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-700 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <AcademicCapIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Simulador de Exames</h1>
            <p className="text-green-100">
              Pratique com simulados realistas e acompanhe sua evolução
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
        {activeTab === 'templates' && renderTemplates()}
        {activeTab === 'simulation' && renderSimulation()}
        {activeTab === 'results' && renderResults()}
        {activeTab === 'analytics' && (
          <div className="text-center py-12">
            <ChartBarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Avançado</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExamSimulator; 