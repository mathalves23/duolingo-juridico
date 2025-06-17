import React, { useState, useEffect } from 'react';
import {
  TrophyIcon,
  StarIcon,
  FireIcon,
  BoltIcon,
  AcademicCapIcon,
  ShieldCheckIcon,
  GiftIcon,
  SparklesIcon,
  ChartBarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import {
  TrophyIcon as TrophyIconSolid,
  StarIcon as StarIconSolid,
  FireIcon as FireIconSolid,
} from '@heroicons/react/24/solid';
import Card from './Card';
import { useAuth } from '../contexts/AuthContext';

// Interfaces
interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  category: 'study' | 'streak' | 'score' | 'social' | 'special';
  xpReward: number;
  coinReward: number;
  isUnlocked: boolean;
  unlockedAt?: Date;
  progress: number;
  maxProgress: number;
}

interface Level {
  level: number;
  title: string;
  minXP: number;
  maxXP: number;
  benefits: string[];
  color: string;
}

interface DailyQuest {
  id: string;
  title: string;
  description: string;
  type: 'questions' | 'time' | 'streak' | 'accuracy';
  target: number;
  progress: number;
  xpReward: number;
  coinReward: number;
  isCompleted: boolean;
  icon: React.ComponentType<any>;
}

interface Streak {
  current: number;
  best: number;
  freezeCount: number;
  lastActivityDate: Date;
}

const GamificationSystem: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'achievements' | 'quests' | 'leaderboard'>('overview');

  // Estados de gamificação
  const [userLevel, setUserLevel] = useState<Level>({
    level: 15,
    title: 'Bacharel Dedicado',
    minXP: 2500,
    maxXP: 3500,
    benefits: ['XP Bônus +10%', 'Questões Premium', 'Chat Prioritário'],
    color: 'blue'
  });

  const [streak, setStreak] = useState<Streak>({
    current: 12,
    best: 15,
    freezeCount: 3,
    lastActivityDate: new Date()
  });

  const [achievements, setAchievements] = useState<Achievement[]>([
    {
      id: 'first_steps',
      title: 'Primeiros Passos',
      description: 'Complete sua primeira questão',
      icon: StarIcon,
      rarity: 'common',
      category: 'study',
      xpReward: 50,
      coinReward: 10,
      isUnlocked: true,
      unlockedAt: new Date('2024-01-15'),
      progress: 1,
      maxProgress: 1
    },
    {
      id: 'streak_master',
      title: 'Mestre da Sequência',
      description: 'Mantenha uma sequência de 30 dias',
      icon: FireIcon,
      rarity: 'epic',
      category: 'streak',
      xpReward: 500,
      coinReward: 100,
      isUnlocked: false,
      progress: 12,
      maxProgress: 30
    },
    {
      id: 'perfect_score',
      title: 'Pontuação Perfeita',
      description: 'Acerte 100% das questões em um simulado',
      icon: TrophyIcon,
      rarity: 'legendary',
      category: 'score',
      xpReward: 1000,
      coinReward: 250,
      isUnlocked: false,
      progress: 0,
      maxProgress: 1
    },
    {
      id: 'knowledge_seeker',
      title: 'Buscador do Conhecimento',
      description: 'Responda 1000 questões',
      icon: AcademicCapIcon,
      rarity: 'rare',
      category: 'study',
      xpReward: 300,
      coinReward: 75,
      isUnlocked: false,
      progress: 234,
      maxProgress: 1000
    },
    {
      id: 'time_warrior',
      title: 'Guerreiro do Tempo',
      description: 'Estude por 100 horas',
      icon: ClockIcon,
      rarity: 'rare',
      category: 'study',
      xpReward: 350,
      coinReward: 80,
      isUnlocked: false,
      progress: 24,
      maxProgress: 100
    },
    {
      id: 'ai_friend',
      title: 'Amigo da IA',
      description: 'Tenha 50 conversas com o assistente',
      icon: SparklesIcon,
      rarity: 'common',
      category: 'social',
      xpReward: 100,
      coinReward: 25,
      isUnlocked: true,
      unlockedAt: new Date('2024-01-18'),
      progress: 50,
      maxProgress: 50
    }
  ]);

  const [dailyQuests, setDailyQuests] = useState<DailyQuest[]>([
    {
      id: 'daily_questions',
      title: 'Questões Diárias',
      description: 'Responda 20 questões hoje',
      type: 'questions',
      target: 20,
      progress: 12,
      xpReward: 100,
      coinReward: 20,
      isCompleted: false,
      icon: AcademicCapIcon
    },
    {
      id: 'study_time',
      title: 'Tempo de Estudo',
      description: 'Estude por 60 minutos',
      type: 'time',
      target: 60,
      progress: 45,
      xpReward: 150,
      coinReward: 30,
      isCompleted: false,
      icon: ClockIcon
    },
    {
      id: 'accuracy_challenge',
      title: 'Desafio de Precisão',
      description: 'Mantenha 80% de acertos',
      type: 'accuracy',
      target: 80,
      progress: 75,
      xpReward: 200,
      coinReward: 40,
      isCompleted: false,
      icon: BoltIcon
    }
  ]);

  const calculateXPProgress = () => {
    const currentXP = user?.profile?.xp_points || 0;
    const progress = ((currentXP - userLevel.minXP) / (userLevel.maxXP - userLevel.minXP)) * 100;
    return Math.min(Math.max(progress, 0), 100);
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common':
        return 'border-gray-300 bg-gray-50';
      case 'rare':
        return 'border-blue-300 bg-blue-50';
      case 'epic':
        return 'border-purple-300 bg-purple-50';
      case 'legendary':
        return 'border-yellow-400 bg-gradient-to-r from-yellow-50 to-orange-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  const getRarityTextColor = (rarity: string) => {
    switch (rarity) {
      case 'common':
        return 'text-gray-600';
      case 'rare':
        return 'text-blue-600';
      case 'epic':
        return 'text-purple-600';
      case 'legendary':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* User Level and XP */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
                         <div className={`w-12 h-12 bg-${userLevel.color}-100 rounded-full flex items-center justify-center`}>
               <TrophyIcon className={`w-6 h-6 text-${userLevel.color}-600`} />
             </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Nível {userLevel.level}</h3>
              <p className="text-sm text-gray-600">{userLevel.title}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">{user?.profile?.xp_points || 0} XP</p>
            <p className="text-sm text-gray-500">{userLevel.maxXP - (user?.profile?.xp_points || 0)} para próximo nível</p>
          </div>
        </div>
        
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progresso do Nível</span>
            <span>{calculateXPProgress().toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`bg-${userLevel.color}-500 h-3 rounded-full transition-all duration-500`}
              style={{ width: `${calculateXPProgress()}%` }}
            ></div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <FireIconSolid className="w-8 h-8 text-orange-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{streak.current}</p>
            <p className="text-sm text-gray-600">Sequência Atual</p>
          </div>
          <div className="text-center">
            <TrophyIconSolid className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{achievements.filter(a => a.isUnlocked).length}</p>
            <p className="text-sm text-gray-600">Conquistas</p>
          </div>
          <div className="text-center">
            <GiftIcon className="w-8 h-8 text-purple-500 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{user?.profile?.coins || 0}</p>
            <p className="text-sm text-gray-600">Moedas</p>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-2">Benefícios do Nível:</h4>
          <div className="flex flex-wrap gap-2">
            {userLevel.benefits.map((benefit, index) => (
              <span
                key={index}
                className={`text-xs px-2 py-1 bg-${userLevel.color}-100 text-${userLevel.color}-700 rounded-full`}
              >
                {benefit}
              </span>
            ))}
          </div>
        </div>
      </Card>

      {/* Daily Quests */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Missões Diárias</h3>
          <div className="text-sm text-gray-500">
            Renovam em: 14h 23min
          </div>
        </div>
        
        <div className="space-y-4">
          {dailyQuests.map((quest) => {
            const IconComponent = quest.icon;
            const progressPercentage = (quest.progress / quest.target) * 100;
            
            return (
              <div key={quest.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <IconComponent className="w-5 h-5 text-blue-600" />
                </div>
                
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{quest.title}</h4>
                  <p className="text-sm text-gray-600">{quest.description}</p>
                  
                  <div className="mt-2">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>{quest.progress} / {quest.target}</span>
                      <span>{progressPercentage.toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-blue-600 font-medium">+{quest.xpReward} XP</span>
                    <span className="text-yellow-600 font-medium">+{quest.coinReward} 🪙</span>
                  </div>
                  {quest.isCompleted && (
                    <div className="mt-1">
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                        Completa!
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Recent Achievements */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Últimas Conquistas</h3>
        <div className="space-y-3">
          {achievements.filter(a => a.isUnlocked).slice(0, 3).map((achievement) => {
            const IconComponent = achievement.icon;
            return (
              <div key={achievement.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getRarityColor(achievement.rarity)}`}>
                  <IconComponent className={`w-6 h-6 ${getRarityTextColor(achievement.rarity)}`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{achievement.title}</h4>
                  <p className="text-sm text-gray-600">{achievement.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">
                    {achievement.unlockedAt?.toLocaleDateString('pt-BR')}
                  </p>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-blue-600">+{achievement.xpReward} XP</span>
                    <span className="text-yellow-600">+{achievement.coinReward} 🪙</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );

  const renderAchievements = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {achievements.map((achievement) => {
          const IconComponent = achievement.icon;
          const progressPercentage = (achievement.progress / achievement.maxProgress) * 100;
          
          return (
            <Card key={achievement.id} className={`p-4 border-2 ${getRarityColor(achievement.rarity)} ${achievement.isUnlocked ? 'opacity-100' : 'opacity-75'}`}>
              <div className="text-center">
                <div className={`w-16 h-16 mx-auto mb-3 rounded-lg flex items-center justify-center ${getRarityColor(achievement.rarity)}`}>
                  <IconComponent className={`w-8 h-8 ${getRarityTextColor(achievement.rarity)}`} />
                </div>
                
                <h3 className="font-semibold text-gray-900 mb-1">{achievement.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{achievement.description}</p>
                
                <div className={`text-xs font-medium mb-3 px-2 py-1 rounded-full inline-block ${getRarityColor(achievement.rarity)} ${getRarityTextColor(achievement.rarity)}`}>
                  {achievement.rarity.toUpperCase()}
                </div>
                
                {!achievement.isUnlocked && (
                  <div className="mb-3">
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${progressPercentage}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500">
                      {achievement.progress} / {achievement.maxProgress}
                    </p>
                  </div>
                )}
                
                <div className="flex justify-center gap-3 text-sm">
                  <span className="text-blue-600 font-medium">+{achievement.xpReward} XP</span>
                  <span className="text-yellow-600 font-medium">+{achievement.coinReward} 🪙</span>
                </div>
                
                {achievement.isUnlocked && (
                  <div className="mt-2">
                    <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                      Desbloqueada!
                    </span>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Visão Geral', icon: ChartBarIcon },
    { id: 'achievements', label: 'Conquistas', icon: TrophyIcon },
    { id: 'quests', label: 'Missões', icon: BoltIcon },
    { id: 'leaderboard', label: 'Ranking', icon: TrophyIcon }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <TrophyIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Sistema de Gamificação</h1>
            <p className="text-purple-100">
              Acompanhe seu progresso e conquiste recompensas!
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
                    ? 'border-purple-500 text-purple-600'
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
        {activeTab === 'achievements' && renderAchievements()}
        {activeTab === 'quests' && (
          <div className="text-center py-12">
            <BoltIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Missões Especiais</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
        {activeTab === 'leaderboard' && (
          <div className="text-center py-12">
            <TrophyIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ranking Global</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GamificationSystem;