import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Alert,
  RefreshControl,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import { showMessage } from 'react-native-flash-message';

// Components
import StatsCard from '../components/StatsCard';
import ProgressCircle from '../components/ProgressCircle';
import QuickActionButton from '../components/QuickActionButton';
import StudyStreakCard from '../components/StudyStreakCard';
import RecentActivityCard from '../components/RecentActivityCard';

// Hooks & Services
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';

// Types
interface DashboardStats {
  totalQuestions: number;
  correctAnswers: number;
  currentStreak: number;
  xpPoints: number;
  studyTime: number;
  weeklyGoal: number;
  weeklyProgress: number;
}

interface RecentActivity {
  id: number;
  type: 'question' | 'quiz' | 'achievement';
  title: string;
  description: string;
  timestamp: string;
  points?: number;
}

const { width } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalQuestions: 0,
    correctAnswers: 0,
    currentStreak: 0,
    xpPoints: 0,
    studyTime: 0,
    weeklyGoal: 5,
    weeklyProgress: 0,
  });
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Simular carregamento de dados
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      const mockStats: DashboardStats = {
        totalQuestions: 247,
        correctAnswers: 189,
        currentStreak: 5,
        xpPoints: 2450,
        studyTime: 180, // em minutos
        weeklyGoal: 5,
        weeklyProgress: 3,
      };

      const mockActivities: RecentActivity[] = [
        {
          id: 1,
          type: 'quiz',
          title: 'Simulado CESPE concluído',
          description: '8/10 questões corretas',
          timestamp: '2024-01-10T10:30:00Z',
          points: 80,
        },
        {
          id: 2,
          type: 'achievement',
          title: 'Conquista desbloqueada!',
          description: 'Sequência de Fogo - 5 dias seguidos',
          timestamp: '2024-01-10T09:15:00Z',
          points: 100,
        },
        {
          id: 3,
          type: 'question',
          title: 'Questão de Direito Constitucional',
          description: 'Resposta correta! +10 XP',
          timestamp: '2024-01-10T08:45:00Z',
          points: 10,
        },
      ];

      setStats(mockStats);
      setRecentActivities(mockActivities);
      
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
      showMessage({
        message: 'Erro ao carregar dados',
        description: 'Tente novamente mais tarde',
        type: 'danger',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'questions':
        showMessage({
          message: 'Navegando para Questões',
          type: 'info',
        });
        break;
      case 'quiz':
        showMessage({
          message: 'Iniciando Simulado',
          type: 'info',
        });
        break;
      case 'achievements':
        showMessage({
          message: 'Visualizando Conquistas',
          type: 'info',
        });
        break;
      case 'analytics':
        showMessage({
          message: 'Abrindo Estatísticas',
          type: 'info',
        });
        break;
    }
  };

  const accuracyPercentage = stats.totalQuestions > 0 
    ? (stats.correctAnswers / stats.totalQuestions) * 100 
    : 0;

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header com saudação */}
      <LinearGradient
        colors={['#2563eb', '#3b82f6']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>Olá, {user?.first_name || 'Estudante'}! 👋</Text>
            <Text style={styles.motivationalText}>
              Continue estudando para alcançar seus objetivos!
            </Text>
          </View>
          <View style={styles.xpContainer}>
            <Icon name="stars" size={20} color="#fbbf24" />
            <Text style={styles.xpText}>{stats.xpPoints} XP</Text>
          </View>
        </View>
      </LinearGradient>

      {/* Progresso semanal */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Meta Semanal</Text>
        <StudyStreakCard
          currentStreak={stats.currentStreak}
          weeklyGoal={stats.weeklyGoal}
          weeklyProgress={stats.weeklyProgress}
        />
      </View>

      {/* Cards de estatísticas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Seu Progresso</Text>
        <View style={styles.statsGrid}>
          <StatsCard
            title="Questões"
            value={stats.totalQuestions.toString()}
            subtitle="resolvidas"
            icon="quiz"
            color="#10b981"
          />
          <StatsCard
            title="Precisão"
            value={`${accuracyPercentage.toFixed(1)}%`}
            subtitle="de acerto"
            icon="target"
            color="#f59e0b"
          />
          <StatsCard
            title="Sequência"
            value={stats.currentStreak.toString()}
            subtitle="dias seguidos"
            icon="local-fire-department"
            color="#ef4444"
          />
          <StatsCard
            title="Tempo"
            value={`${Math.floor(stats.studyTime / 60)}h`}
            subtitle="de estudo"
            icon="schedule"
            color="#8b5cf6"
          />
        </View>
      </View>

      {/* Progresso circular */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Desempenho Geral</Text>
        <View style={styles.progressContainer}>
          <ProgressCircle
            percentage={accuracyPercentage}
            size={120}
            strokeWidth={12}
            color="#10b981"
          />
          <View style={styles.progressText}>
            <Text style={styles.progressLabel}>Taxa de Acerto</Text>
            <Text style={styles.progressValue}>{accuracyPercentage.toFixed(1)}%</Text>
          </View>
        </View>
      </View>

      {/* Ações rápidas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ações Rápidas</Text>
        <View style={styles.quickActions}>
          <QuickActionButton
            title="Resolver Questões"
            icon="quiz"
            color="#2563eb"
            onPress={() => handleQuickAction('questions')}
          />
          <QuickActionButton
            title="Simulado"
            icon="assignment"
            color="#7c3aed"
            onPress={() => handleQuickAction('quiz')}
          />
          <QuickActionButton
            title="Conquistas"
            icon="emoji-events"
            color="#f59e0b"
            onPress={() => handleQuickAction('achievements')}
          />
          <QuickActionButton
            title="Estatísticas"
            icon="analytics"
            color="#10b981"
            onPress={() => handleQuickAction('analytics')}
          />
        </View>
      </View>

      {/* Atividade recente */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Atividade Recente</Text>
        {recentActivities.map((activity) => (
          <RecentActivityCard
            key={activity.id}
            activity={activity}
          />
        ))}
      </View>

      {/* Dica do dia */}
      <View style={styles.section}>
        <View style={styles.tipCard}>
          <Icon name="lightbulb" size={24} color="#f59e0b" />
          <View style={styles.tipContent}>
            <Text style={styles.tipTitle}>💡 Dica do Dia</Text>
            <Text style={styles.tipText}>
              Resolva pelo menos 10 questões por dia para manter um bom ritmo de estudos!
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 24,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  motivationalText: {
    fontSize: 14,
    color: '#dbeafe',
  },
  xpContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  xpText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginLeft: 4,
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressText: {
    marginLeft: 20,
  },
  progressLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  progressValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#10b981',
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  tipCard: {
    flexDirection: 'row',
    backgroundColor: '#fef3c7',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b',
  },
  tipContent: {
    flex: 1,
    marginLeft: 12,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#92400e',
    marginBottom: 4,
  },
  tipText: {
    fontSize: 14,
    color: '#a16207',
    lineHeight: 20,
  },
});

export default DashboardScreen; 