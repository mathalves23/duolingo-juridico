import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpenIcon,
  AcademicCapIcon,
  ClockIcon,
  TrophyIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import { Subject, UserLesson } from '../types';
import { apiService } from '../services/api';

interface SubjectProgress {
  subject_id: number;
  total_lessons: number;
  completed_lessons: number;
  total_questions: number;
  answered_questions: number;
  correct_answers: number;
  xp_earned: number;
  time_spent: number; // em minutos
  last_study: string;
}

const Subjects: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [progress, setProgress] = useState<Record<number, SubjectProgress>>({});
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSubjects: 0,
    completedSubjects: 0,
    totalXP: 0,
    currentStreak: 0
  });

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      const subjectsData = await apiService.getSubjects();
      setSubjects(subjectsData);

      // Carregar progresso para cada disciplina
      const progressData: Record<number, SubjectProgress> = {};
      for (const subject of subjectsData) {
        try {
          const subjectProgress = await apiService.getUserProgress(subject.id);
          progressData[subject.id] = subjectProgress;
        } catch (error) {
          // Mock progress if API call fails
          progressData[subject.id] = {
            subject_id: subject.id,
            total_lessons: 12,
            completed_lessons: Math.floor(Math.random() * 8),
            total_questions: 50,
            answered_questions: Math.floor(Math.random() * 30),
            correct_answers: Math.floor(Math.random() * 25),
            xp_earned: Math.floor(Math.random() * 500),
            time_spent: Math.floor(Math.random() * 180), // minutos
            last_study: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString()
          };
        }
      }
      setProgress(progressData);
    } catch (error) {
      console.error('Erro ao carregar disciplinas:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = (subjectId: number) => {
    const prog = progress[subjectId];
    if (!prog) return 0;
    return Math.round((prog.completed_lessons / prog.total_lessons) * 100);
  };

  const getAccuracyPercentage = (subjectId: number) => {
    const prog = progress[subjectId];
    if (!prog || prog.answered_questions === 0) return 0;
    return Math.round((prog.correct_answers / prog.answered_questions) * 100);
  };

  const formatTimeSpent = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getLastStudyText = (lastStudy: string) => {
    const now = new Date();
    const study = new Date(lastStudy);
    const diffInHours = Math.floor((now.getTime() - study.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Há poucos minutos';
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    const days = Math.floor(diffInHours / 24);
    return `${days}d atrás`;
  };

  const handleSubjectClick = (subject: Subject) => {
    navigate(`/subjects/${subject.id}/topics`);
  };

  const handleStartQuestions = (subjectId: number) => {
    navigate(`/questions?subject=${subjectId}`);
  };

  const handleStartQuiz = (subjectId: number) => {
    navigate(`/quizzes/create?subject=${subjectId}`);
  };

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
        <h1 className="text-3xl font-bold">Disciplinas Jurídicas</h1>
        <p className="text-primary-100 mt-2">
          Explore e domine cada área do direito com nosso sistema personalizado
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-xl">
              <BookOpenIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total de Disciplinas</p>
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
                {Object.values(progress).reduce((sum, p) => sum + p.completed_lessons, 0)}
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
              <p className="text-2xl font-bold text-gray-900">
                {Object.values(progress).reduce((sum, p) => sum + p.xp_earned, 0)}
              </p>
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
                {formatTimeSpent(Object.values(progress).reduce((sum, p) => sum + p.time_spent, 0))}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Subjects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {subjects.map((subject) => {
          const progressPercentage = getProgressPercentage(subject.id);
          const accuracyPercentage = getAccuracyPercentage(subject.id);
          const subjectProgress = progress[subject.id];

          return (
            <div key={subject.id} className="card card-hover group">
              {/* Header with color */}
              <div 
                className="h-2 rounded-t-xl"
                style={{ backgroundColor: subject.color_hex }}
              ></div>

              <div className="p-6">
                {/* Subject Info */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {subject.name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1 capitalize">
                      {subject.category}
                    </p>
                    {subject.description && (
                      <p className="text-sm text-gray-500 mt-2 line-clamp-2">
                        {subject.description}
                      </p>
                    )}
                  </div>
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${subject.color_hex}20` }}
                  >
                    <BookOpenIcon 
                      className="h-6 w-6"
                      style={{ color: subject.color_hex }}
                    />
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
                      className="h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${progressPercentage}%`,
                        backgroundColor: subject.color_hex 
                      }}
                    ></div>
                  </div>
                </div>

                {/* Stats */}
                {subjectProgress && (
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div>
                      <p className="text-gray-600">Lições</p>
                      <p className="font-semibold">
                        {subjectProgress.completed_lessons}/{subjectProgress.total_lessons}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Precisão</p>
                      <p className="font-semibold text-green-600">{accuracyPercentage}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">XP Ganho</p>
                      <p className="font-semibold text-yellow-600">{subjectProgress.xp_earned}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Último Estudo</p>
                      <p className="font-semibold">{getLastStudyText(subjectProgress.last_study)}</p>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="space-y-2">
                  <button
                    onClick={() => handleSubjectClick(subject)}
                    className="w-full btn btn-primary flex items-center justify-center"
                  >
                    <AcademicCapIcon className="h-4 w-4 mr-2" />
                    Continuar Estudos
                  </button>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleStartQuestions(subject.id)}
                      className="btn btn-outline text-sm"
                    >
                      Questões
                    </button>
                    <button
                      onClick={() => handleStartQuiz(subject.id)}
                      className="btn btn-outline text-sm"
                    >
                      Simulado
                    </button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {subjects.length === 0 && (
        <div className="text-center py-12">
          <BookOpenIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Nenhuma disciplina encontrada
          </h3>
          <p className="text-gray-600">
            As disciplinas aparecerão aqui quando estiverem disponíveis.
          </p>
        </div>
      )}
    </div>
  );
};

export default Subjects; 