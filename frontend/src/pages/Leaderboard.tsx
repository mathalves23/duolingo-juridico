import React, { useState, useEffect } from 'react';
import { 
  TrophyIcon,
  ChartBarIcon,
  UserGroupIcon,
  CalendarIcon,
  FireIcon
} from '@heroicons/react/24/outline';
import { StarIcon as StarSolid, TrophyIcon as TrophySolid } from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import { LeaderboardEntry } from '../types';
import { Leaderboard as LeaderboardType, Subject, User } from '../types';
import { apiService } from '../services/api';

interface LeaderboardStats {
  total_users: number;
  user_rank: number;
  user_score: number;
  points_to_next: number;
  percentile: number;
}

// Interface local para dados mock do leaderboard
interface MockLeaderboardEntry {
  id: number;
  user: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    avatar: string;
  };
  rank: number;
  score: number;
  change: number;
  badge?: string;
  streak?: number;
  activity_level: 'baixa' | 'média' | 'alta';
}

const Leaderboard: React.FC = () => {
  const { user } = useAuth();
  const [leaderboards, setLeaderboards] = useState<LeaderboardType[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedLeaderboard, setSelectedLeaderboard] = useState<string>('global_xp');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('all_time');
  const [entries, setEntries] = useState<MockLeaderboardEntry[]>([]);
  const [stats, setStats] = useState<LeaderboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const leaderboardTypes = [
    { id: 'global_xp', name: 'XP Global', icon: TrophyIcon, color: 'text-yellow-600' },
    { id: 'streak', name: 'Sequência', icon: FireIcon, color: 'text-orange-600' },
    { id: 'questions', name: 'Questões', icon: ChartBarIcon, color: 'text-blue-600' },
    { id: 'weekly', name: 'Semanal', icon: CalendarIcon, color: 'text-green-600' }
  ];

  const periods = [
    { id: 'all_time', name: 'Todos os Tempos' },
    { id: 'monthly', name: 'Este Mês' },
    { id: 'weekly', name: 'Esta Semana' },
    { id: 'daily', name: 'Hoje' }
  ];

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadLeaderboardData();
  }, [selectedLeaderboard, selectedPeriod]);

  const loadInitialData = async () => {
    try {
      const [leaderboardsData, subjectsData] = await Promise.all([
        apiService.getLeaderboards(),
        apiService.getSubjects()
      ]);
      setLeaderboards(leaderboardsData);
      setSubjects(subjectsData);
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
    }
  };

  const loadLeaderboardData = async () => {
    setLoading(true);
    try {
      // In a real implementation, you would fetch from the API
      // const response = await apiService.getLeaderboard(selectedLeaderboard);
      
      // Mock data for development
      const mockEntries: MockLeaderboardEntry[] = generateMockLeaderboard();
      const mockStats: LeaderboardStats = {
        total_users: mockEntries.length,
        user_rank: mockEntries.findIndex(entry => entry.user.id === user?.id) + 1 || 15,
        user_score: mockEntries.find(entry => entry.user.id === user?.id)?.score || 1250,
        points_to_next: 150,
        percentile: 75
      };

      setEntries(mockEntries);
      setStats(mockStats);
    } catch (error) {
      console.error('Erro ao carregar leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockLeaderboard = (): MockLeaderboardEntry[] => {
    const mockNames = [
      'Ana Silva', 'Carlos Santos', 'Maria Oliveira', 'João Pereira', 'Luciana Costa',
      'Pedro Lima', 'Fernanda Souza', 'Ricardo Alves', 'Juliana Ferreira', 'Marcos Rodriguez',
      'Patrícia Martins', 'Rafael Barbosa', 'Camila Ribeiro', 'Diego Nascimento', user?.first_name + ' ' + (user?.last_name || ''),
      'Beatriz Cardoso', 'Thiago Araújo', 'Larissa Dias', 'Bruno Campos', 'Vanessa Rocha'
    ];

    return mockNames.map((name, index) => {
      const isCurrentUser = name === user?.first_name + ' ' + (user?.last_name || '');
      const baseScore = 5000 - (index * 200) + Math.floor(Math.random() * 150);
      
      return {
        id: index + 1,
        user: {
          id: isCurrentUser ? user?.id || 0 : index + 1,
          username: name.toLowerCase().replace(' ', '.'),
          first_name: name.split(' ')[0],
          last_name: name.split(' ')[1] || '',
          avatar: `https://ui-avatars.com/api/?name=${name}&background=random`
        },
        rank: index + 1,
        score: baseScore,
        change: Math.floor(Math.random() * 21) - 10, // -10 to +10
        badge: index < 3 ? ['👑', '🥈', '🥉'][index] : undefined,
        streak: Math.floor(Math.random() * 30) + 1,
        activity_level: (index < 5 ? 'alta' : index < 15 ? 'média' : 'baixa') as 'baixa' | 'média' | 'alta'
      };
    }).sort((a, b) => b.score - a.score);
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <TrophySolid className="h-6 w-6 text-yellow-500" />;
      case 2:
        return <TrophySolid className="h-6 w-6 text-gray-400" />;
      case 3:
        return <TrophySolid className="h-6 w-6 text-yellow-600" />;
      default:
        return <span className="text-lg font-bold text-gray-600">#{rank}</span>;
    }
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) {
      return <span className="text-green-600 text-sm">↗ +{change}</span>;
    } else if (change < 0) {
      return <span className="text-red-600 text-sm">↘ {change}</span>;
    }
    return <span className="text-gray-500 text-sm">—</span>;
  };

  const getActivityColor = (level: string) => {
    switch (level) {
      case 'alta':
        return 'bg-green-100 text-green-800';
      case 'média':
        return 'bg-yellow-100 text-yellow-800';
      case 'baixa':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCurrentUserEntry = () => {
    return entries.find(entry => entry.user.id === user?.id);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const currentUserEntry = getCurrentUserEntry();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold">Ranking</h1>
        <p className="text-purple-100 mt-2">
          Compare seu progresso com outros estudantes e compita pelos primeiros lugares
        </p>
      </div>

      {/* User Stats */}
      {stats && (
        <div className="card">
          <div className="p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Sua Posição</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="bg-purple-100 p-4 rounded-xl inline-flex items-center justify-center mb-2">
                  <TrophyIcon className="h-8 w-8 text-purple-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">#{stats.user_rank}</p>
                <p className="text-sm text-gray-600">Posição Global</p>
              </div>

              <div className="text-center">
                <div className="bg-yellow-100 p-4 rounded-xl inline-flex items-center justify-center mb-2">
                  <TrophyIcon className="h-8 w-8 text-yellow-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{stats.user_score.toLocaleString()}</p>
                <p className="text-sm text-gray-600">Pontos XP</p>
              </div>

              <div className="text-center">
                <div className="bg-green-100 p-4 rounded-xl inline-flex items-center justify-center mb-2">
                  <ChartBarIcon className="h-8 w-8 text-green-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">Top {100 - stats.percentile}%</p>
                <p className="text-sm text-gray-600">Percentil</p>
              </div>

              <div className="text-center">
                <div className="bg-blue-100 p-4 rounded-xl inline-flex items-center justify-center mb-2">
                  <UserGroupIcon className="h-8 w-8 text-blue-600" />
                </div>
                <p className="text-2xl font-bold text-gray-900">{stats.points_to_next}</p>
                <p className="text-sm text-gray-600">Para próxima posição</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Leaderboard Type */}
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Ranking
              </label>
              <div className="flex flex-wrap gap-2">
                {leaderboardTypes.map(type => {
                  const IconComponent = type.icon;
                  return (
                    <button
                      key={type.id}
                      onClick={() => setSelectedLeaderboard(type.id)}
                      className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedLeaderboard === type.id
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <IconComponent className="h-4 w-4 mr-2" />
                      {type.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Period Filter */}
            <div className="lg:w-48">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Período
              </label>
              <select
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
              >
                {periods.map(period => (
                  <option key={period.id} value={period.id}>
                    {period.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Top 3 Podium */}
      <div className="card">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 text-center">Top 3</h2>
          <div className="flex items-end justify-center space-x-8">
            {/* 2nd Place */}
            {entries[1] && (
              <div className="text-center">
                <div className="bg-gray-100 rounded-lg p-4 w-24 h-20 flex items-center justify-center mb-2">
                  <img
                    src={entries[1].user.avatar}
                    alt={entries[1].user.first_name}
                    className="w-12 h-12 rounded-full"
                  />
                </div>
                <div className="bg-gray-300 text-gray-800 text-xs px-2 py-1 rounded-full mb-2">
                  2º Lugar
                </div>
                <p className="font-semibold text-sm">{entries[1].user.first_name}</p>
                <p className="text-xs text-gray-600">{entries[1].score.toLocaleString()} XP</p>
              </div>
            )}

            {/* 1st Place */}
            {entries[0] && (
              <div className="text-center">
                <div className="bg-yellow-100 rounded-lg p-4 w-28 h-24 flex items-center justify-center mb-2 relative">
                  <img
                    src={entries[0].user.avatar}
                    alt={entries[0].user.first_name}
                    className="w-16 h-16 rounded-full border-4 border-yellow-400"
                  />
                  <div className="absolute -top-2 -right-2">
                    <TrophyIcon className="h-6 w-6 text-yellow-500" />
                  </div>
                </div>
                <div className="bg-yellow-400 text-yellow-900 text-xs px-2 py-1 rounded-full mb-2">
                  1º Lugar
                </div>
                <p className="font-bold text-sm">{entries[0].user.first_name}</p>
                <p className="text-xs text-gray-600">{entries[0].score.toLocaleString()} XP</p>
              </div>
            )}

            {/* 3rd Place */}
            {entries[2] && (
              <div className="text-center">
                <div className="bg-yellow-50 rounded-lg p-4 w-24 h-20 flex items-center justify-center mb-2">
                  <img
                    src={entries[2].user.avatar}
                    alt={entries[2].user.first_name}
                    className="w-12 h-12 rounded-full"
                  />
                </div>
                <div className="bg-yellow-600 text-white text-xs px-2 py-1 rounded-full mb-2">
                  3º Lugar
                </div>
                <p className="font-semibold text-sm">{entries[2].user.first_name}</p>
                <p className="text-xs text-gray-600">{entries[2].score.toLocaleString()} XP</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Full Leaderboard */}
      <div className="card">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Ranking Completo</h2>
          <div className="space-y-2">
            {entries.map((entry, index) => (
              <div
                key={entry.id}
                className={`p-4 rounded-lg border transition-all ${
                  entry.user.id === user?.id
                    ? 'bg-primary-50 border-primary-200 shadow-md'
                    : 'bg-white border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {/* Rank */}
                    <div className="flex items-center justify-center w-12">
                      {getRankIcon(entry.rank)}
                    </div>

                    {/* User Info */}
                    <div className="flex items-center space-x-3">
                      <img
                        src={entry.user.avatar}
                        alt={entry.user.first_name}
                        className="w-10 h-10 rounded-full"
                      />
                      <div>
                        <p className="font-semibold text-gray-900">
                          {entry.user.first_name} {entry.user.last_name}
                          {entry.user.id === user?.id && (
                            <span className="ml-2 text-primary-600 text-sm">(Você)</span>
                          )}
                        </p>
                        <p className="text-sm text-gray-600">@{entry.user.username}</p>
                      </div>
                    </div>

                    {/* Activity Level */}
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActivityColor(entry.activity_level)}`}>
                      Atividade {entry.activity_level}
                    </span>
                  </div>

                  <div className="flex items-center space-x-6">
                    {/* Streak */}
                    {entry.streak && (
                      <div className="flex items-center text-orange-600">
                        <FireIcon className="h-4 w-4 mr-1" />
                        <span className="text-sm font-medium">{entry.streak}</span>
                      </div>
                    )}

                    {/* Score */}
                    <div className="text-right">
                      <p className="font-bold text-gray-900">
                        {entry.score.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-600">XP</p>
                    </div>

                    {/* Change */}
                    <div className="w-16 text-right">
                      {getChangeIcon(entry.change)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Subject Leaderboards */}
      <div className="card">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Rankings por Disciplina</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {subjects.slice(0, 6).map(subject => (
              <div key={subject.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center mb-3">
                  <div 
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: subject.color_hex }}
                  ></div>
                  <h3 className="font-semibold text-gray-900">{subject.name}</h3>
                </div>
                <div className="space-y-2">
                  {entries.slice(0, 3).map((entry, index) => (
                    <div key={entry.id} className="flex items-center justify-between text-sm">
                      <div className="flex items-center">
                        <span className="text-gray-500 mr-2">#{index + 1}</span>
                        <span className="font-medium">{entry.user.first_name}</span>
                      </div>
                      <span className="text-gray-600">
                        {Math.floor(entry.score * 0.8).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
                <button className="w-full mt-3 text-primary-600 text-sm font-medium hover:text-primary-700">
                  Ver ranking completo →
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard; 