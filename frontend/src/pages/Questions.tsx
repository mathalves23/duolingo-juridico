import React, { useState, useEffect, useRef } from 'react';
import AIChat from '../components/AIChat';
import Button from '../components/Button';
import Card from '../components/Card';
import Loading from '../components/Loading';
import {
  ClockIcon,
  PlayIcon,
  PauseIcon,
  ForwardIcon,
  BackwardIcon,
  BookmarkIcon,
  HeartIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  ChartBarIcon,
  FireIcon,
  TrophyIcon,
  SparklesIcon,
  AcademicCapIcon,
  BoltIcon,
  StarIcon,
  EyeIcon,
  ChatBubbleLeftRightIcon,
  ArrowPathIcon,
  FlagIcon
} from '@heroicons/react/24/outline';
import {
  HeartIcon as HeartSolid,
  BookmarkIcon as BookmarkSolid,
  CheckCircleIcon as CheckCircleSolid,
  XCircleIcon as XCircleSolid,
  StarIcon as StarSolid,
  TrophyIcon as TrophySolid
} from '@heroicons/react/24/solid';

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

interface Alternative {
  id: number;
  text: string;
  is_correct: boolean;
}

interface Question {
  id: number;
  title: string;
  text: string;
  subject: number;
  difficulty_level: number;
  exam_board: string;
  exam_year: number;
  exam_name: string;
  explanation: string;
  source?: string;
  alternatives: Alternative[];
  created_at: string;
  updated_at: string;
}

interface Subject {
  id: number;
  name: string;
  color: string;
  icon: string;
}

interface SessionStats {
  questionsAnswered: number;
  correctAnswers: number;
  currentStreak: number;
  timeSpent: number;
  accuracy: number;
  xpEarned: number;
  coinsEarned: number;
}

const Questions: React.FC = () => {
  const { user } = useAuth();
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Estados principais
  const [questions, setQuestions] = useState<Question[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [isAnswerCorrect, setIsAnswerCorrect] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Estados do timer
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  
  // Estados de filtros
  const [selectedSubject, setSelectedSubject] = useState<number | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<number | null>(null);
  const [selectedExamBoard, setSelectedExamBoard] = useState<string>('');
  
  // Estados de UI
  const [markedForReview, setMarkedForReview] = useState<number[]>([]);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [showStats, setShowStats] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);
  
  // Estados de sessão
  const [sessionStats, setSessionStats] = useState<SessionStats>({
    questionsAnswered: 0,
    correctAnswers: 0,
    currentStreak: 0,
    timeSpent: 0,
    accuracy: 0,
    xpEarned: 0,
    coinsEarned: 0
  });

  useEffect(() => {
    loadSubjects();
    loadQuestions();
    startTimer();
    
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [selectedSubject, selectedDifficulty, selectedExamBoard]);

  useEffect(() => {
    if (isTimerRunning && timerRef.current === null) {
      timerRef.current = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
        setSessionStats(prev => ({ ...prev, timeSpent: prev.timeSpent + 1 }));
      }, 1000);
    } else if (!isTimerRunning && timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [isTimerRunning]);

  const loadSubjects = async () => {
    try {
      setSubjects([
        { id: 1, name: 'Direito Constitucional', color: 'from-blue-500 to-blue-600', icon: '⚖️' },
        { id: 2, name: 'Direito Administrativo', color: 'from-green-500 to-green-600', icon: '🏛️' },
        { id: 3, name: 'Direito Civil', color: 'from-red-500 to-red-600', icon: '📋' },
        { id: 4, name: 'Direito Penal', color: 'from-purple-500 to-purple-600', icon: '🔒' },
        { id: 5, name: 'Direito Processual', color: 'from-yellow-500 to-yellow-600', icon: '⚡' }
      ]);
    } catch (error) {
      console.error('Erro ao carregar disciplinas:', error);
    }
  };

  const loadQuestions = async () => {
    try {
      setLoading(true);
      // Simular delay de carregamento
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setQuestions([
        {
          id: 1,
          title: 'Questão sobre Princípios Constitucionais',
          text: 'Considerando os princípios fundamentais da Constituição Federal de 1988, assinale a alternativa correta sobre o princípio da dignidade da pessoa humana.',
          subject: 1,
          difficulty_level: 2,
          exam_year: 2024,
          exam_board: 'CESPE',
          exam_name: 'Concurso Público Federal',
          explanation: 'A dignidade da pessoa humana é um dos fundamentos da República Federativa do Brasil, conforme o art. 1º, III, da CF/88. Este princípio serve como base para todos os direitos fundamentais e orienta a interpretação de todo o ordenamento jurídico.',
          source: 'CF/88, art. 1º, III',
          alternatives: [
            { id: 1, text: 'É um direito fundamental de segunda geração.', is_correct: false },
            { id: 2, text: 'É um princípio implícito na Constituição.', is_correct: false },
            { id: 3, text: 'É um dos fundamentos da República Federativa do Brasil.', is_correct: true },
            { id: 4, text: 'Aplica-se apenas nas relações entre Estado e particulares.', is_correct: false }
          ],
          created_at: '2024-01-01',
          updated_at: '2024-01-01'
        },
        {
          id: 2,
          title: 'Questão sobre Licitações',
          text: 'De acordo com a Lei nº 14.133/2021, que institui a nova Lei de Licitações e Contratos Administrativos, assinale a modalidade de licitação adequada para a contratação de serviços técnicos especializados.',
          subject: 2,
          difficulty_level: 3,
          exam_year: 2024,
          exam_board: 'FCC',
          exam_name: 'Tribunal Regional Federal',
          explanation: 'A modalidade adequada para serviços técnicos especializados é o concurso, conforme previsto no art. 28, IV, da Lei 14.133/2021. Esta modalidade é específica para trabalhos técnicos, científicos ou artísticos.',
          alternatives: [
            { id: 1, text: 'Pregão eletrônico', is_correct: false },
            { id: 2, text: 'Concorrência', is_correct: false },
            { id: 3, text: 'Concurso', is_correct: true },
            { id: 4, text: 'Leilão', is_correct: false }
          ],
          created_at: '2024-01-01',
          updated_at: '2024-01-01'
        },
        {
          id: 3,
          title: 'Questão sobre Contratos',
          text: 'No direito civil brasileiro, qual das seguintes características NÃO é essencial para a validade de um contrato?',
          subject: 3,
          difficulty_level: 1,
          exam_year: 2024,
          exam_board: 'VUNESP',
          exam_name: 'Defensoria Pública',
          explanation: 'Para a validade do contrato são essenciais: agente capaz, objeto lícito e forma prescrita ou não defesa em lei (art. 104, CC). A onerosidade não é requisito essencial.',
          alternatives: [
            { id: 1, text: 'Agente capaz', is_correct: false },
            { id: 2, text: 'Objeto lícito', is_correct: false },
            { id: 3, text: 'Forma prescrita em lei', is_correct: false },
            { id: 4, text: 'Onerosidade', is_correct: true }
          ],
          created_at: '2024-01-01',
          updated_at: '2024-01-01'
        }
      ]);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar questões:', error);
      setLoading(false);
    }
  };

  const startTimer = () => {
    setIsTimerRunning(true);
  };

  const pauseTimer = () => {
    setIsTimerRunning(false);
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (alternativeId: number) => {
    if (showExplanation) return;
    
    setSelectedAnswer(alternativeId);
    const currentQuestion = questions[currentQuestionIndex];
    const selectedAlternative = currentQuestion.alternatives.find(alt => alt.id === alternativeId);
    const isCorrect = selectedAlternative?.is_correct || false;
    
    setIsAnswerCorrect(isCorrect);
    setShowExplanation(true);
    
    // Atualizar estatísticas
    setSessionStats(prev => {
      const newStats = {
        ...prev,
        questionsAnswered: prev.questionsAnswered + 1,
        correctAnswers: isCorrect ? prev.correctAnswers + 1 : prev.correctAnswers,
        currentStreak: isCorrect ? prev.currentStreak + 1 : 0,
        xpEarned: prev.xpEarned + (isCorrect ? 10 : 5),
        coinsEarned: prev.coinsEarned + (isCorrect ? 5 : 2)
      };
      newStats.accuracy = newStats.questionsAnswered > 0 ? (newStats.correctAnswers / newStats.questionsAnswered) * 100 : 0;
      return newStats;
    });

    // Mostrar celebração se acertou
    if (isCorrect) {
      setShowCelebration(true);
      setTimeout(() => setShowCelebration(false), 2000);
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
      resetQuestionState();
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
      resetQuestionState();
    }
  };

  const resetQuestionState = () => {
    setSelectedAnswer(null);
    setShowExplanation(false);
    setIsAnswerCorrect(null);
  };

  const toggleReviewMark = () => {
    const questionId = questions[currentQuestionIndex]?.id;
    if (questionId) {
      setMarkedForReview(prev => 
        prev.includes(questionId) 
          ? prev.filter(id => id !== questionId)
          : [...prev, questionId]
      );
    }
  };

  const toggleFavorite = () => {
    const questionId = questions[currentQuestionIndex]?.id;
    if (questionId) {
      setFavorites(prev => 
        prev.includes(questionId) 
          ? prev.filter(id => id !== questionId)
          : [...prev, questionId]
      );
    }
  };

  const getDifficultyColor = (level: number) => {
    switch (level) {
      case 1: return 'from-green-500 to-green-600';
      case 2: return 'from-yellow-500 to-yellow-600';
      case 3: return 'from-orange-500 to-orange-600';
      case 4: return 'from-red-500 to-red-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getDifficultyLabel = (level: number) => {
    switch (level) {
      case 1: return 'Fácil';
      case 2: return 'Médio';
      case 3: return 'Difícil';
      case 4: return 'Expert';
      default: return 'Indefinido';
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const currentSubject = subjects.find(s => s.id === currentQuestion?.subject);
  const isMarkedForReview = currentQuestion && markedForReview.includes(currentQuestion.id);
  const isFavorite = currentQuestion && favorites.includes(currentQuestion.id);

  if (loading) {
    return <Loading type="questions" />;
  }

  if (questions.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Card variant="glass" className="text-center p-8">
          <AcademicCapIcon className="h-16 w-16 text-navy-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-navy-800 mb-2">Nenhuma questão encontrada</h3>
          <p className="text-navy-600 mb-6">Ajuste os filtros ou tente novamente mais tarde.</p>
          <Button variant="primary" onClick={loadQuestions} icon={ArrowPathIcon}>
            Recarregar
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 relative">
      {/* Celebration Animation */}
      {showCelebration && (
        <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
          <div className="animate-bounce">
            <div className="bg-gradient-to-r from-success-500 to-success-600 text-white p-8 rounded-3xl shadow-glow text-center">
              <TrophySolid className="h-16 w-16 mx-auto mb-4 animate-pulse" />
              <h2 className="text-2xl font-bold mb-2">Parabéns! 🎉</h2>
              <p className="text-lg">Resposta correta!</p>
              <div className="flex items-center justify-center space-x-4 mt-4">
                <div className="flex items-center space-x-1">
                  <SparklesIcon className="h-5 w-5" />
                  <span className="font-bold">+10 XP</span>
                </div>
                <div className="flex items-center space-x-1">
                  <StarSolid className="h-5 w-5 text-gold-300" />
                  <span className="font-bold">+5 moedas</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header com Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Timer Card */}
        <Card variant="gradient" className="text-center">
          <div className="flex items-center justify-center mb-3">
            <ClockIcon className="h-6 w-6 text-white mr-2" />
            <span className="text-white font-semibold">Tempo</span>
          </div>
          <div className="text-2xl font-bold text-white mb-3">{formatTime(timeElapsed)}</div>
          <div className="flex justify-center space-x-2">
            <Button
              size="sm"
              variant="glass"
              icon={isTimerRunning ? PauseIcon : PlayIcon}
              onClick={isTimerRunning ? pauseTimer : startTimer}
            >
              {isTimerRunning ? 'Pausar' : 'Iniciar'}
            </Button>
          </div>
        </Card>

        {/* Progress Card */}
        <Card variant="success" className="text-center">
          <div className="flex items-center justify-center mb-3">
            <ChartBarIcon className="h-6 w-6 text-white mr-2" />
            <span className="text-white font-semibold">Progresso</span>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {currentQuestionIndex + 1}/{questions.length}
          </div>
          <div className="w-full bg-white/20 rounded-full h-2">
            <div 
              className="bg-white h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
            ></div>
          </div>
        </Card>

        {/* Accuracy Card */}
        <Card variant="warning" className="text-center">
          <div className="flex items-center justify-center mb-3">
            <TrophyIcon className="h-6 w-6 text-white mr-2" />
            <span className="text-white font-semibold">Precisão</span>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {sessionStats.accuracy.toFixed(1)}%
          </div>
          <div className="text-sm text-white/80">
            {sessionStats.correctAnswers}/{sessionStats.questionsAnswered} acertos
          </div>
        </Card>

        {/* Streak Card */}
        <Card variant="danger" className="text-center">
          <div className="flex items-center justify-center mb-3">
            <FireIcon className="h-6 w-6 text-white mr-2" />
            <span className="text-white font-semibold">Sequência</span>
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {sessionStats.currentStreak}
          </div>
          <div className="text-sm text-white/80">acertos seguidos</div>
        </Card>
      </div>

      {/* Question Card */}
      <Card variant="glass" className="p-8">
        {/* Question Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-4">
              {/* Subject Badge */}
              {currentSubject && (
                <div className={`bg-gradient-to-r ${currentSubject.color} text-white px-4 py-2 rounded-xl font-semibold text-sm flex items-center space-x-2 shadow-glow`}>
                  <span>{currentSubject.icon}</span>
                  <span>{currentSubject.name}</span>
                </div>
              )}
              
              {/* Difficulty Badge */}
              <div className={`bg-gradient-to-r ${getDifficultyColor(currentQuestion.difficulty_level)} text-white px-3 py-1 rounded-lg font-medium text-sm`}>
                {getDifficultyLabel(currentQuestion.difficulty_level)}
              </div>
              
              {/* Exam Info */}
              <div className="bg-navy-100 text-navy-700 px-3 py-1 rounded-lg font-medium text-sm">
                {currentQuestion.exam_board} - {currentQuestion.exam_year}
              </div>
            </div>
            
            <h2 className="text-xl font-bold text-navy-800 mb-3">
              {currentQuestion.title}
            </h2>
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-2 ml-4">
            <Button
              size="sm"
              variant={isMarkedForReview ? "warning" : "ghost"}
              icon={isMarkedForReview ? FlagIcon : FlagIcon}
              onClick={toggleReviewMark}
              tooltip="Marcar para revisão"
            >
              {isMarkedForReview ? 'Marcado' : 'Marcar'}
            </Button>
            <Button
              size="sm"
              variant={isFavorite ? "danger" : "ghost"}
              icon={isFavorite ? HeartSolid : HeartIcon}
              onClick={toggleFavorite}
              tooltip="Favoritar questão"
            >
              {isFavorite ? 'Favoritado' : 'Favoritar'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              icon={ChatBubbleLeftRightIcon}
              onClick={() => setShowChat(!showChat)}
              tooltip="Chat com IA"
            >
              Chat IA
            </Button>
          </div>
        </div>

        {/* Question Text */}
        <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 mb-6 border border-white/30">
          <p className="text-navy-800 text-lg leading-relaxed font-medium">
            {currentQuestion.text}
          </p>
        </div>

        {/* Alternatives */}
        <div className="space-y-4 mb-6">
          {currentQuestion.alternatives.map((alternative, index) => {
            const isSelected = selectedAnswer === alternative.id;
            const isCorrect = alternative.is_correct;
            const showResult = showExplanation;
            
            let variantClass = 'bg-white/60 hover:bg-white/80 border-white/30 text-navy-800';
            
            if (showResult) {
              if (isCorrect) {
                variantClass = 'bg-gradient-to-r from-success-500 to-success-600 text-white border-success-400 shadow-glow';
              } else if (isSelected && !isCorrect) {
                variantClass = 'bg-gradient-to-r from-danger-500 to-danger-600 text-white border-danger-400 shadow-glow';
              } else {
                variantClass = 'bg-white/40 border-white/20 text-navy-600';
              }
            } else if (isSelected) {
              variantClass = 'bg-gradient-to-r from-primary-500 to-primary-600 text-white border-primary-400 shadow-glow';
            }

            return (
              <button
                key={alternative.id}
                onClick={() => handleAnswerSelect(alternative.id)}
                disabled={showExplanation}
                className={`w-full p-4 rounded-2xl border-2 transition-all duration-300 text-left font-medium hover:scale-[1.02] ${variantClass} ${
                  !showExplanation ? 'cursor-pointer' : 'cursor-default'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    showResult && isCorrect ? 'bg-white/20' :
                    showResult && isSelected && !isCorrect ? 'bg-white/20' :
                    isSelected ? 'bg-white/20' : 'bg-navy-100 text-navy-600'
                  }`}>
                    {showResult && isCorrect ? (
                      <CheckCircleSolid className="h-5 w-5" />
                    ) : showResult && isSelected && !isCorrect ? (
                      <XCircleSolid className="h-5 w-5" />
                    ) : (
                      String.fromCharCode(65 + index)
                    )}
                  </div>
                  <span className="flex-1">{alternative.text}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Explanation */}
        {showExplanation && (
          <div className="animate-slideInUp">
            <Card variant={isAnswerCorrect ? "success" : "warning"} className="mb-6">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {isAnswerCorrect ? (
                    <CheckCircleSolid className="h-8 w-8 text-white" />
                  ) : (
                    <LightBulbIcon className="h-8 w-8 text-white" />
                  )}
                </div>
                <div className="flex-1">
                  <h4 className="text-lg font-bold text-white mb-2">
                    {isAnswerCorrect ? 'Parabéns! Resposta correta!' : 'Resposta incorreta'}
                  </h4>
                  <p className="text-white/90 leading-relaxed mb-3">
                    {currentQuestion.explanation}
                  </p>
                  {currentQuestion.source && (
                    <div className="bg-white/20 rounded-lg p-3">
                      <p className="text-sm text-white/80">
                        <strong>Fonte:</strong> {currentQuestion.source}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            icon={BackwardIcon}
            onClick={previousQuestion}
            disabled={currentQuestionIndex === 0}
          >
            Anterior
          </Button>
          
          <div className="flex items-center space-x-4">
            <span className="text-navy-600 font-medium">
              Questão {currentQuestionIndex + 1} de {questions.length}
            </span>
          </div>
          
          <Button
            variant="primary"
            icon={ForwardIcon}
            iconPosition="right"
            onClick={nextQuestion}
            disabled={currentQuestionIndex === questions.length - 1}
          >
            Próxima
          </Button>
        </div>
      </Card>

      {/* AI Chat */}
      {showChat && (
        <div className="fixed bottom-4 right-4 w-96 h-96 z-40 animate-slideInUp">
          <AIChat />
        </div>
      )}

      {/* Session Summary */}
      {sessionStats.questionsAnswered > 0 && (
        <Card variant="glass" className="p-6">
          <h3 className="text-lg font-bold text-navy-800 mb-4 flex items-center">
            <TrophyIcon className="h-6 w-6 mr-2 text-gold-500" />
            Resumo da Sessão
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-navy-800">{sessionStats.questionsAnswered}</div>
              <div className="text-sm text-navy-600">Questões</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-600">{sessionStats.correctAnswers}</div>
              <div className="text-sm text-navy-600">Acertos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">{sessionStats.xpEarned}</div>
              <div className="text-sm text-navy-600">XP Ganho</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gold-600">{sessionStats.coinsEarned}</div>
              <div className="text-sm text-navy-600">Moedas</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Questions;