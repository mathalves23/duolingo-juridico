import axios, { AxiosInstance } from 'axios';
import { 
  AuthResponse, 
  LoginRequest, 
  RegisterRequest, 
  User, 
  UserProfile,
  Subject,
  Topic,
  Lesson,
  Question,
  Quiz,
  Achievement,
  Leaderboard,
  StoreItem,
  DailyChallenge,
  PaginatedResponse 
} from '../types';

// Configuração da API baseada no ambiente
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://concurseiro-backend.onrender.com/api/v1'
    : 'http://localhost:8000/api/v1');

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para adicionar token de autenticação
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Interceptor para lidar com refresh token
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                refresh: refreshToken,
              });

              const { access } = response.data;
              localStorage.setItem('access_token', access);

              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Refresh token inválido, fazer logout
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Métodos de autenticação
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/login/', credentials);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/register/', userData);
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await this.api.post('/auth/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  }

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await this.api.post('/auth/logout/', { refresh: refreshToken });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/user/');
    return response.data;
  }

  async updateProfile(profileData: Partial<UserProfile>): Promise<UserProfile> {
    const response = await this.api.patch<UserProfile>('/auth/profile/', profileData);
    return response.data;
  }

  // Métodos de cursos
  async getSubjects(): Promise<Subject[]> {
    const response = await this.api.get<PaginatedResponse<Subject>>('/courses/subjects/');
    return response.data.results;
  }

  async getSubject(id: number): Promise<Subject> {
    const response = await this.api.get<Subject>(`/courses/subjects/${id}/`);
    return response.data;
  }

  async getTopicsBySubject(subjectId: number): Promise<Topic[]> {
    const response = await this.api.get<PaginatedResponse<Topic>>(`/courses/topics/?subject=${subjectId}`);
    return response.data.results;
  }

  async getLessonsByTopic(topicId: number): Promise<Lesson[]> {
    const response = await this.api.get<PaginatedResponse<Lesson>>(`/courses/lessons/?topic=${topicId}`);
    return response.data.results;
  }

  async getLesson(id: number): Promise<Lesson> {
    const response = await this.api.get<Lesson>(`/courses/lessons/${id}/`);
    return response.data;
  }

  async markLessonAsCompleted(lessonId: number): Promise<void> {
    await this.api.post(`/courses/lessons/${lessonId}/complete/`);
  }

  async getUserProgress(subjectId?: number): Promise<any> {
    const url = subjectId ? `/courses/subjects/${subjectId}/progress/` : '/courses/progress/';
    const response = await this.api.get(url);
    return response.data;
  }

  // Métodos de questões
  async getQuestions(params?: {
    subject?: number;
    topic?: number;
    difficulty?: number;
    exam_board?: number;
    page?: number;
  }): Promise<PaginatedResponse<Question>> {
    const response = await this.api.get<PaginatedResponse<Question>>('/questions/questions/', {
      params,
    });
    return response.data;
  }

  async getQuestion(id: number): Promise<Question> {
    const response = await this.api.get<Question>(`/questions/questions/${id}/`);
    return response.data;
  }

  async answerQuestion(questionId: number, selectedOptionId: number): Promise<any> {
    const response = await this.api.post(`/questions/questions/${questionId}/answer/`, {
      selected_option: selectedOptionId,
    });
    return response.data;
  }

  async createQuiz(quizData: {
    title: string;
    description: string;
    questions: number[];
    time_limit: number;
    difficulty_level: number;
    is_public: boolean;
  }): Promise<Quiz> {
    const response = await this.api.post<Quiz>('/questions/quizzes/', quizData);
    return response.data;
  }

  async getQuizzes(): Promise<PaginatedResponse<Quiz>> {
    const response = await this.api.get<PaginatedResponse<Quiz>>('/questions/quizzes/');
    return response.data;
  }

  async startQuiz(quizId: number): Promise<any> {
    const response = await this.api.post(`/questions/quizzes/${quizId}/start/`);
    return response.data;
  }

  async getQuestionStats(): Promise<any> {
    const response = await this.api.get('/questions/questions/stats/');
    return response.data;
  }

  // Métodos de gamificação
  async getAchievements(): Promise<Achievement[]> {
    const response = await this.api.get<PaginatedResponse<Achievement>>('/gamification/achievements/');
    return response.data.results;
  }

  async getUserAchievements(): Promise<any[]> {
    const response = await this.api.get('/gamification/achievements/user_achievements/');
    return response.data;
  }

  async getLeaderboards(): Promise<Leaderboard[]> {
    const response = await this.api.get<PaginatedResponse<Leaderboard>>('/gamification/leaderboards/');
    return response.data.results;
  }

  async getLeaderboard(id: number): Promise<Leaderboard> {
    const response = await this.api.get<Leaderboard>(`/gamification/leaderboards/${id}/`);
    return response.data;
  }

  async getStoreItems(): Promise<StoreItem[]> {
    const response = await this.api.get<PaginatedResponse<StoreItem>>('/gamification/store-items/');
    return response.data.results;
  }

  async purchaseItem(itemId: number, quantity: number = 1): Promise<any> {
    const response = await this.api.post(`/gamification/store-items/${itemId}/purchase/`, {
      quantity,
    });
    return response.data;
  }

  async getDailyChallenges(): Promise<DailyChallenge[]> {
    const response = await this.api.get<PaginatedResponse<DailyChallenge>>('/gamification/daily-challenges/');
    return response.data.results;
  }

  async getUserStats(): Promise<any> {
    const response = await this.api.get('/gamification/stats/');
    return response.data;
  }

  // Métodos de IA
  async getAIExplanation(questionId: number): Promise<any> {
    const response = await this.api.post('/ai/feedback/request_explanation/', {
      question_id: questionId,
    });
    return response.data;
  }

  async getStudyRecommendations(): Promise<any> {
    const response = await this.api.get('/ai/recommendations/');
    return response.data;
  }

  async generatePersonalizedQuiz(preferences: any): Promise<any> {
    const response = await this.api.post('/ai/recommendations/generate_recommendations/', preferences);
    return response.data;
  }

  async getLearningAnalytics(): Promise<any> {
    const response = await this.api.get('/ai/analytics/learning_analytics/');
    return response.data;
  }

  // Métodos utilitários
  async uploadFile(file: File, endpoint: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Configuração de token
  setAuthToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  removeAuthToken(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
}

export const apiService = new ApiService();
export default apiService; 