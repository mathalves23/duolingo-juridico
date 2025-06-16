import React, { useState, useEffect, useCallback } from 'react';
import { 
  TrophyIcon,
  StarIcon,
  FireIcon,
  BookOpenIcon,
  CheckCircleIcon,
  ClockIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';
import { 
  TrophyIcon as TrophySolid,
  StarIcon as StarSolid,
  FireIcon as FireSolid
} from '@heroicons/react/24/solid';
import { Achievement, UserAchievement } from '../types';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface AchievementProgress {
  achievement_id: number;
  current_progress: number;
  total_required: number;
  percentage: number;
}

const Achievements: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [userAchievements, setUserAchievements] = useState<UserAchievement[]>([]);
  const [achievementProgress, setAchievementProgress] = useState<Record<number, AchievementProgress>>({});
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedRarity, setSelectedRarity] = useState<string>('all');

  const categories = [
    { id: 'all', name: 'Todas', icon: SparklesIcon },
    { id: 'study', name: 'Estudos', icon: BookOpenIcon },
    { id: 'questions', name: 'Questões', icon: CheckCircleIcon },
    { id: 'streak', name: 'Sequência', icon: FireIcon },
    { id: 'progress', name: 'Progresso', icon: ChartBarIcon },
    { id: 'social', name: 'Social', icon: TrophyIcon },
    { id: 'special', name: 'Especiais', icon: StarIcon }
  ];

  const rarities = [
    { id: 'all', name: 'Todas', color: 'text-gray-600' },
    { id: 'common', name: 'Comum', color: 'text-gray-600' },
    { id: 'rare', name: 'Raro', color: 'text-blue-600' },
    { id: 'epic', name: 'Épico', color: 'text-purple-600' },
    { id: 'legendary', name: 'Lendário', color: 'text-yellow-600' }
  ];

  const loadAchievements = useCallback(async () => {
    try {
      const [achievementsData, userAchievementsData] = await Promise.all([
        apiService.getAchievements(),
        apiService.getUserAchievements()
      ]);

      setAchievements(achievementsData);
      setUserAchievements(userAchievementsData);

      // Mock progress data
      const progressData: Record<number, AchievementProgress> = {};
      achievementsData.forEach(achievement => {
        const userAchievement = userAchievementsData.find(ua => ua.achievement.id === achievement.id);
        
        if (!userAchievement) {
          // Create mock progress for unearned achievements
          const required = getRequirementValue(achievement.requirements);
          const current = Math.floor(Math.random() * required);
          
          progressData[achievement.id] = {
            achievement_id: achievement.id,
            current_progress: current,
            total_required: required,
            percentage: Math.round((current / required) * 100)
          };
        }
      });

      setAchievementProgress(progressData);
    } catch (error) {
      console.error('Erro ao carregar conquistas:', error);

      // Mock data for development
      const mockAchievements: Achievement[] = [
        {
          id: 1,
          title: 'Primeiro Passo',
          description: 'Complete sua primeira lição',
          icon: 'trophy',
          rarity: 'common',
          achievement_type: 'study',
          xp_reward: 50,
          coin_reward: 10,
          requirements: JSON.stringify({ lessons_completed: 1 }),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          title: 'Sequência de Fogo',
          description: 'Mantenha uma sequência de 7 dias consecutivos',
          icon: 'fire',
          rarity: 'rare',
          achievement_type: 'streak',
          xp_reward: 100,
          coin_reward: 25,
          requirements: JSON.stringify({ streak_days: 7 }),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 3,
          title: 'Mestre das Questões',
          description: 'Responda 100 questões corretamente',
          icon: 'star',
          rarity: 'epic',
          achievement_type: 'questions',
          xp_reward: 200,
          coin_reward: 50,
          requirements: JSON.stringify({ correct_answers: 100 }),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 4,
          title: 'Lenda Jurídica',
          description: 'Alcance 10.000 pontos de XP',
          icon: 'crown',
          rarity: 'legendary',
          achievement_type: 'progress',
          xp_reward: 500,
          coin_reward: 100,
          requirements: JSON.stringify({ total_xp: 10000 }),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ];

      const mockUserAchievements: UserAchievement[] = [
        {
          id: 1,
          user: 1,
          achievement: mockAchievements[0],
          earned_at: new Date(Date.now() - 86400000).toISOString(),
          progress: 1
        }
      ];

      setAchievements(mockAchievements);
      setUserAchievements(mockUserAchievements);

      // Mock progress
      const progressData: Record<number, AchievementProgress> = {
        2: { achievement_id: 2, current_progress: 4, total_required: 7, percentage: 57 },
        3: { achievement_id: 3, current_progress: 45, total_required: 100, percentage: 45 },
        4: { achievement_id: 4, current_progress: 2500, total_required: 10000, percentage: 25 }
      };
      setAchievementProgress(progressData);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAchievements();
  }, [loadAchievements]);

  const getRequirementValue = (requirements: string): number => {
    try {
      const req = JSON.parse(requirements);
      return Object.values(req)[0] as number;
    } catch {
      return 1;
    }
  };

  const getAchievementIcon = (iconName: string, isEarned: boolean) => {
    const iconClass = `h-8 w-8 ${isEarned ? 'text-yellow-500' : 'text-gray-400'}`;
    
    switch (iconName) {
      case 'trophy':
        return isEarned ? <TrophySolid className={iconClass} /> : <TrophyIcon className={iconClass} />;
      case 'fire':
        return isEarned ? <FireSolid className={iconClass} /> : <FireIcon className={iconClass} />;
      case 'star':
        return isEarned ? <StarSolid className={iconClass} /> : <StarIcon className={iconClass} />;
      default:
        return isEarned ? <TrophySolid className={iconClass} /> : <TrophyIcon className={iconClass} />;
    }
  };

  const getRarityColor = (rarity: string) => {
    const colors = {
      common: 'border-gray-300 bg-gray-50',
      rare: 'border-blue-300 bg-blue-50',
      epic: 'border-purple-300 bg-purple-50',
      legendary: 'border-yellow-300 bg-yellow-50'
    };
    return colors[rarity as keyof typeof colors] || colors.common;
  };

  const getRarityBadgeColor = (rarity: string) => {
    const colors = {
      common: 'bg-gray-100 text-gray-800',
      rare: 'bg-blue-100 text-blue-800',
      epic: 'bg-purple-100 text-purple-800',
      legendary: 'bg-yellow-100 text-yellow-800'
    };
    return colors[rarity as keyof typeof colors] || colors.common;
  };

  const isAchievementEarned = (achievementId: number): boolean => {
    return userAchievements.some(ua => ua.achievement.id === achievementId);
  };

  const getAchievementProgress = (achievement: Achievement): AchievementProgress | null => {
    return achievementProgress[achievement.id] || null;
  };

  const formatTimeAgo = (dateString: string): string => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 24) return `${diffInHours}h atrás`;
    const days = Math.floor(diffInHours / 24);
    return `${days}d atrás`;
  };

  const filteredAchievements = achievements.filter(achievement => {
    const categoryMatch = selectedCategory === 'all' || achievement.achievement_type === selectedCategory;
    const rarityMatch = selectedRarity === 'all' || achievement.rarity === selectedRarity;
    return categoryMatch && rarityMatch;
  });

  const earnedCount = userAchievements.length;
  const totalXPFromAchievements = userAchievements.reduce((sum, ua) => sum + ua.achievement.xp_reward, 0);
  const totalCoinsFromAchievements = userAchievements.reduce((sum, ua) => sum + ua.achievement.coin_reward, 0);

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
      <div className="bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold">Conquistas</h1>
        <p className="text-yellow-100 mt-2">
          Desbloqueie conquistas e ganhe recompensas por seus estudos
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-yellow-100 p-3 rounded-xl">
              <TrophyIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Conquistas</p>
              <p className="text-2xl font-bold text-gray-900">
                {earnedCount} / {achievements.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-xl">
              <StarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">XP das Conquistas</p>
              <p className="text-2xl font-bold text-gray-900">{totalXPFromAchievements}</p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-xl">
              <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Moedas das Conquistas</p>
              <p className="text-2xl font-bold text-gray-900">{totalCoinsFromAchievements}</p>
            </div>
          </div>
        </div>

        <div className="card card-hover">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-xl">
              <ChartBarIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Progresso</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round((earnedCount / achievements.length) * 100)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Category Filter */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Categoria
              </label>
              <div className="flex flex-wrap gap-2">
                {categories.map(category => {
                  const IconComponent = category.icon;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedCategory === category.id
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <IconComponent className="h-4 w-4 mr-2" />
                      {category.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Rarity Filter */}
            <div className="lg:w-48">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Raridade
              </label>
              <select
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={selectedRarity}
                onChange={(e) => setSelectedRarity(e.target.value)}
              >
                {rarities.map(rarity => (
                  <option key={rarity.id} value={rarity.id}>
                    {rarity.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Achievements Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAchievements.map(achievement => {
          const isEarned = isAchievementEarned(achievement.id);
          const progress = getAchievementProgress(achievement);
          const earnedData = userAchievements.find(ua => ua.achievement.id === achievement.id);

          return (
            <div
              key={achievement.id}
              className={`card relative overflow-hidden ${
                isEarned ? getRarityColor(achievement.rarity) : 'border-gray-200 bg-gray-50'
              } ${isEarned ? 'shadow-lg' : ''}`}
            >
              {/* Rarity Badge */}
              <div className="absolute top-4 right-4">
                <span className={`px-2 py-1 rounded-md text-xs font-medium ${getRarityBadgeColor(achievement.rarity)}`}>
                  {rarities.find(r => r.id === achievement.rarity)?.name || 'Comum'}
                </span>
              </div>

              {/* Lock/Earned Badge */}
              {!isEarned && (
                <div className="absolute top-4 left-4">
                  <LockClosedIcon className="h-5 w-5 text-gray-400" />
                </div>
              )}

              <div className="p-6">
                {/* Achievement Icon and Title */}
                <div className="text-center mb-4">
                  <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-3 ${
                    isEarned ? 'bg-yellow-100' : 'bg-gray-200'
                  }`}>
                    {getAchievementIcon(achievement.icon, isEarned)}
                  </div>
                  <h3 className={`text-lg font-bold ${isEarned ? 'text-gray-900' : 'text-gray-600'}`}>
                    {achievement.title}
                  </h3>
                  <p className={`text-sm mt-1 ${isEarned ? 'text-gray-700' : 'text-gray-500'}`}>
                    {achievement.description}
                  </p>
                </div>

                {/* Progress Bar (for unearned achievements) */}
                {!isEarned && progress && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Progresso</span>
                      <span>{progress.current_progress} / {progress.total_required}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress.percentage}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 text-center">
                      {progress.percentage}% completo
                    </p>
                  </div>
                )}

                {/* Earned Date */}
                {isEarned && earnedData && (
                  <div className="mb-4 text-center">
                    <div className="flex items-center justify-center text-sm text-green-600">
                      <CheckCircleIcon className="h-4 w-4 mr-1" />
                      <span>Conquistado {formatTimeAgo(earnedData.earned_at)}</span>
                    </div>
                  </div>
                )}

                {/* Rewards */}
                <div className="flex items-center justify-center space-x-4 text-sm">
                  <div className="flex items-center">
                    <StarIcon className="h-4 w-4 text-yellow-500 mr-1" />
                    <span className={isEarned ? 'text-gray-700' : 'text-gray-500'}>
                      {achievement.xp_reward} XP
                    </span>
                  </div>
                  <div className="flex items-center">
                    <CurrencyDollarIcon className="h-4 w-4 text-green-500 mr-1" />
                    <span className={isEarned ? 'text-gray-700' : 'text-gray-500'}>
                      {achievement.coin_reward} moedas
                    </span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredAchievements.length === 0 && (
        <div className="text-center py-12">
          <TrophyIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Nenhuma conquista encontrada
          </h3>
          <p className="text-gray-600">
            Tente ajustar os filtros para ver diferentes conquistas.
          </p>
        </div>
      )}

      {/* Recent Achievements */}
      {userAchievements.length > 0 && (
        <div className="card">
          <div className="p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Conquistas Recentes</h2>
            <div className="space-y-4">
              {userAchievements.slice(0, 3).map(userAchievement => (
                <div key={userAchievement.id} className="flex items-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex-shrink-0">
                    {getAchievementIcon(userAchievement.achievement.icon, true)}
                  </div>
                  <div className="ml-4 flex-1">
                    <h4 className="font-semibold text-gray-900">
                      {userAchievement.achievement.title}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {userAchievement.achievement.description}
                    </p>
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {formatTimeAgo(userAchievement.earned_at)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Achievements; 