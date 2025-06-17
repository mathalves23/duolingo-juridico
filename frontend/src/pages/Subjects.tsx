import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpenIcon,
  AcademicCapIcon,
  ClockIcon,
  TrophyIcon,
  CheckCircleIcon,
  StarIcon,
  FireIcon,
  ChartBarIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import { 
  subjectsData, 
  Subject,
  getDifficultyColor, 
  getCategoryColor, 
  getCategoryName 
} from '../data/subjects';

interface SubjectProgress {
  completed: number;
  total: number;
  xp_earned: number;
  time_spent: number; // em minutos
  last_study: Date;
  accuracy: number;
}

const Subjects: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [subjects] = useState<Subject[]>(subjectsData);
  const [filteredSubjects, setFilteredSubjects] = useState<Subject[]>(subjectsData);
  const [progress, setProgress] = useState<Record<string, SubjectProgress>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    generateMockProgress();
    setLoading(false);
  }, []);

  useEffect(() => {
    filterSubjects();
  }, [searchTerm, selectedCategory, selectedDifficulty, subjects]);

  const generateMockProgress = () => {
    const mockProgress: Record<string, SubjectProgress> = {};
    
    subjects.forEach(subject => {
      const completed = Math.floor(Math.random() * (subject.lessons + 1));
      mockProgress[subject.id] = {
        completed,
        total: subject.lessons,
        xp_earned: completed * (10 + Math.floor(Math.random() * 15)),
        time_spent: completed * (15 + Math.floor(Math.random() * 30)), // 15-45 min por lição
        last_study: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000), // últimos 30 dias
        accuracy: 65 + Math.floor(Math.random() * 30) // 65-95%
      };
    });
    
    setProgress(mockProgress);
  };

  const filterSubjects = () => {
    let filtered = subjects;

    // Filtrar por termo de busca
    if (searchTerm) {
      filtered = filtered.filter(subject =>
        subject.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        subject.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        subject.topics.some(topic => topic.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filtrar por categoria
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(subject => subject.category === selectedCategory);
    }

    // Filtrar por dificuldade
    if (selectedDifficulty !== 'all') {
      filtered = filtered.filter(subject => subject.difficulty === selectedDifficulty);
    }

    setFilteredSubjects(filtered);
  };

  const getProgressPercentage = (subjectId: string) => {
    const prog = progress[subjectId];
    if (!prog) return 0;
    return Math.round((prog.completed / prog.total) * 100);
  };

  const formatTimeSpent = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getLastStudyText = (lastStudy: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - lastStudy.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Há poucos minutos';
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    const days = Math.floor(diffInHours / 24);
    if (days === 1) return 'Ontem';
    return `${days} dias atrás`;
  };

  const handleSubjectClick = (subject: Subject) => {
    navigate(`/subjects/${subject.id}/lessons`);
  };

  const handleStartQuestions = (subjectId: string) => {
    navigate(`/questions?subject=${subjectId}`);
  };

  const handleStartQuiz = (subjectId: string) => {
    navigate(`/quizzes/create?subject=${subjectId}`);
  };

  const totalStats = {
    totalLessons: Object.values(progress).reduce((sum, p) => sum + p.total, 0),
    completedLessons: Object.values(progress).reduce((sum, p) => sum + p.completed, 0),
    totalXP: Object.values(progress).reduce((sum, p) => sum + p.xp_earned, 0),
    totalTime: Object.values(progress).reduce((sum, p) => sum + p.time_spent, 0),
    avgAccuracy: Object.values(progress).length > 0 
      ? Math.round(Object.values(progress).reduce((sum, p) => sum + p.accuracy, 0) / Object.values(progress).length)
      : 0
  };

  const categories = Array.from(new Set(subjects.map(s => s.category)));
  const difficulties = ['beginner', 'intermediate', 'advanced'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold">📚 Disciplinas Jurídicas</h1>
        <p className="text-primary-100 mt-2">
          Domine o direito brasileiro com {subjects.length} disciplinas completas e mais de {totalStats.totalLessons} lições
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-xl">
              <BookOpenIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Disciplinas</p>
              <p className="text-2xl font-bold text-gray-900">{subjects.length}</p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-xl">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Lições Completas</p>
              <p className="text-2xl font-bold text-gray-900">
                {totalStats.completedLessons}/{totalStats.totalLessons}
              </p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-yellow-100 p-3 rounded-xl">
              <TrophyIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">XP Total</p>
              <p className="text-2xl font-bold text-gray-900">{totalStats.totalXP.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-xl">
              <ClockIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Tempo de Estudo</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatTimeSpent(totalStats.totalTime)}
              </p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-emerald-100 p-3 rounded-xl">
              <ChartBarIcon className="h-6 w-6 text-emerald-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Precisão Média</p>
              <p className="text-2xl font-bold text-gray-900">{totalStats.avgAccuracy}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Buscar disciplinas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">Todas as áreas</option>
            {categories.map(category => (
              <option key={category} value={category}>
                {getCategoryName(category)}
              </option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">Todas as dificuldades</option>
            <option value="beginner">Iniciante</option>
            <option value="intermediate">Intermediário</option>
            <option value="advanced">Avançado</option>
          </select>
        </div>
      </div>

      {/* Subjects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredSubjects.map((subject) => {
          const progressPercentage = getProgressPercentage(subject.id);
          const subjectProgress = progress[subject.id];

          return (
            <div key={subject.id} className="card card-hover group">
              {/* Subject Header */}
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{subject.icon}</span>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                          {subject.name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(subject.category)}`}>
                            {getCategoryName(subject.category)}
                          </span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(subject.difficulty)}`}>
                            {subject.difficulty === 'beginner' ? 'Iniciante' : 
                             subject.difficulty === 'intermediate' ? 'Intermediário' : 'Avançado'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {subject.description}
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progresso</span>
                    <span>{progressPercentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progressPercentage}%` }}
                    ></div>
                  </div>
                </div>

                {/* Stats */}
                {subjectProgress && (
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div>
                      <p className="text-gray-600">📖 Lições</p>
                      <p className="font-semibold">
                        {subjectProgress.completed}/{subjectProgress.total}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">🎯 Precisão</p>
                      <p className="font-semibold text-green-600">{subjectProgress.accuracy}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">⭐ XP Ganho</p>
                      <p className="font-semibold text-yellow-600">{subjectProgress.xp_earned}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">🕒 Último Estudo</p>
                      <p className="font-semibold">{getLastStudyText(subjectProgress.last_study)}</p>
                    </div>
                  </div>
                )}

                {/* Topics Preview */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Principais tópicos:</p>
                  <div className="flex flex-wrap gap-1">
                    {subject.topics.slice(0, 3).map((topic, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                      >
                        {topic}
                      </span>
                    ))}
                    {subject.topics.length > 3 && (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                        +{subject.topics.length - 3} mais
                      </span>
                    )}
                  </div>
                </div>

                {/* Estimated Time */}
                <div className="mb-4 text-sm">
                  <span className="text-gray-600">⏱️ Duração estimada: </span>
                  <span className="font-semibold">{subject.estimatedHours}h</span>
                </div>

                {/* Action Buttons */}
                <div className="space-y-2">
                  <button
                    onClick={() => handleSubjectClick(subject)}
                    className="w-full btn btn-primary flex items-center justify-center"
                  >
                    <AcademicCapIcon className="h-4 w-4 mr-2" />
                    {progressPercentage > 0 ? 'Continuar Estudos' : 'Começar Estudos'}
                  </button>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleStartQuestions(subject.id)}
                      className="btn btn-outline text-sm"
                    >
                      💭 Questões
                    </button>
                    <button
                      onClick={() => handleStartQuiz(subject.id)}
                      className="btn btn-outline text-sm"
                    >
                      🧠 Simulado
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredSubjects.length === 0 && (
        <div className="text-center py-12">
          <MagnifyingGlassIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Nenhuma disciplina encontrada
          </h3>
          <p className="text-gray-600">
            Tente ajustar os filtros ou termo de busca para encontrar as disciplinas desejadas.
          </p>
        </div>
      )}
    </div>
  );
};

export default Subjects; 