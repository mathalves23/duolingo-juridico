// Tipos para Autenticação
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  created_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  id: number;
  bio: string;
  date_of_birth: string | null;
  phone_number: string;
  preferred_study_time: string;
  target_exam: string;
  experience_level: 'beginner' | 'intermediate' | 'advanced';
  study_goals: string;
  xp_points: number;
  coins: number;
  current_streak: number;
  best_streak: number;
  total_study_time: number;
  avatar: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

// Tipos para Cursos
export interface Subject {
  id: number;
  name: string;
  description: string;
  category: string;
  color_hex: string;
  icon: string;
  difficulty_level: number;
  is_active: boolean;
  order: number;
}

export interface Topic {
  id: number;
  subject: number;
  name: string;
  description: string;
  order: number;
  is_active: boolean;
}

export interface Lesson {
  id: number;
  topic: number;
  title: string;
  content: string;
  lesson_type: 'theory' | 'practice' | 'quiz' | 'case_study';
  difficulty_level: number;
  estimated_duration: number;
  xp_reward: number;
  order: number;
  is_active: boolean;
  prerequisites: number[];
}

export interface UserLesson {
  id: number;
  user: number;
  lesson: number;
  is_completed: boolean;
  progress_percentage: number;
  time_spent: number;
  started_at: string;
  completed_at: string | null;
  xp_earned: number;
}

// Tipos para Questões
export interface ExamBoard {
  id: number;
  name: string;
  acronym: string;
  description: string;
  website: string;
  is_active: boolean;
}

export interface Question {
  id: number;
  title: string;
  question_text: string;
  question_type: string;
  subject: number;
  subject_name?: string;
  topic?: number | null;
  exam_board: number;
  exam_name: string;
  exam_year: number;
  difficulty_level: number;
  explanation?: string;
  tags?: string[];
  is_active?: boolean;
  created_at: string;
  updated_at: string;
  options?: QuestionOption[];
}

export interface QuestionOption {
  id: number;
  question: number;
  option_text: string;
  is_correct: boolean;
  order?: number;
  explanation?: string;
}

export interface UserAnswer {
  id: number;
  user: number;
  question: number;
  selected_option: number | null;
  is_correct: boolean;
  time_spent: number;
  answered_at: string;
  explanation_viewed: boolean;
}

export interface Quiz {
  id: number;
  title: string;
  description: string;
  created_by: number;
  questions: number[];
  time_limit: number;
  difficulty_level: number;
  is_public: boolean;
  created_at: string;
}

export interface QuizAttempt {
  id: number;
  user: number;
  quiz: number;
  score: number;
  total_questions: number;
  correct_answers: number;
  time_spent: number;
  completed: boolean;
  started_at: string;
  completed_at: string | null;
}

// Tipos para Gamificação
export interface Achievement {
  id: number;
  title: string;
  description: string;
  icon: string;
  rarity: string;
  achievement_type: string;
  xp_reward: number;
  coin_reward: number;
  requirements: string;
  is_active?: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserAchievement {
  id: number;
  user: number;
  achievement: Achievement;
  earned_at: string;
  progress: number;
}

export interface Leaderboard {
  id: number;
  name: string;
  description: string;
  leaderboard_type: 'weekly' | 'monthly' | 'all_time' | 'subject';
  subject: number | null;
  period_start: string | null;
  period_end: string | null;
  is_active: boolean;
  entries?: LeaderboardEntry[];
}

export interface LeaderboardEntry {
  id: number;
  leaderboard: number;
  user: User;
  score: number;
  position: number;
  subject_performance: any;
}

export interface StoreItem {
  id: number;
  name: string;
  description: string;
  coin_price: number;
  item_type: 'avatar' | 'theme' | 'boost' | 'feature' | 'avatars' | 'themes' | 'boosts' | 'badges' | 'effects';
  rarity: string;
  duration_hours: number | null;
  item_data: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserPurchase {
  id: number;
  user: number;
  item: StoreItem;
  quantity: number;
  total_cost: number;
  purchased_at: string;
  is_active: boolean;
}

export interface DailyChallenge {
  id: number;
  title: string;
  description: string;
  challenge_type: string;
  target_value: number;
  xp_reward: number;
  coin_reward: number;
  date: string;
  is_active: boolean;
}

// Tipos para UI
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface NotificationState {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  autoClose?: boolean;
  duration?: number;
} 