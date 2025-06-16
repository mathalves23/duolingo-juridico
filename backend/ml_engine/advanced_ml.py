"""
Engine de Machine Learning Avançado - Duolingo Jurídico
Sistema completo de IA para personalização e otimização do aprendizado
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import pickle
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"

class DifficultyLevel(Enum):
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5

class PredictionType(Enum):
    SUCCESS_PROBABILITY = "success_probability"
    COMPLETION_TIME = "completion_time"
    OPTIMAL_DIFFICULTY = "optimal_difficulty"
    CHURN_RISK = "churn_risk"
    ENGAGEMENT_SCORE = "engagement_score"

@dataclass
class LearningProfile:
    """Perfil de aprendizado do usuário"""
    user_id: str
    learning_style: LearningStyle
    preferred_pace: float  # 0.5 = lento, 1.0 = normal, 2.0 = rápido
    attention_span: int  # minutos
    optimal_session_length: int  # minutos
    best_study_times: List[int]  # horas do dia (0-23)
    difficulty_preference: float  # 0.0 = fácil, 1.0 = difícil
    motivation_factors: List[str]
    weak_areas: List[str]
    strong_areas: List[str]
    learning_goals: List[str]
    last_updated: datetime

@dataclass
class ContentRecommendation:
    """Recomendação de conteúdo"""
    content_id: str
    content_type: str
    title: str
    description: str
    difficulty_level: DifficultyLevel
    estimated_time: int  # minutos
    relevance_score: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    reasoning: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]

@dataclass
class LearningPathStep:
    """Passo no caminho de aprendizado"""
    step_id: str
    content_id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    estimated_time: int
    prerequisites: List[str]
    learning_objectives: List[str]
    assessment_criteria: List[str]
    adaptive_parameters: Dict[str, Any]

@dataclass
class PredictionResult:
    """Resultado de predição"""
    prediction_type: PredictionType
    value: float
    confidence: float
    factors: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: datetime

class AdvancedMLEngine:
    """Engine principal de Machine Learning"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_extractors = {}
        self.logger = logging.getLogger(__name__)
        
        # Inicializa modelos
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa modelos de ML"""
        
        # Modelo de predição de sucesso
        self.models['success_predictor'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Modelo de predição de tempo de conclusão
        self.models['completion_time_predictor'] = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        
        # Modelo de clustering de usuários
        self.models['user_clusterer'] = KMeans(
            n_clusters=5,
            random_state=42
        )
        
        # Modelo de predição de churn
        self.models['churn_predictor'] = RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            random_state=42
        )
        
        # Scalers para normalização
        self.scalers['user_features'] = StandardScaler()
        self.scalers['content_features'] = StandardScaler()
        
        self.logger.info("ML models initialized")
    
    def train_models(self, training_data: Dict[str, pd.DataFrame]):
        """Treina todos os modelos com dados históricos"""
        
        try:
            # Treina modelo de predição de sucesso
            if 'user_performance' in training_data:
                self._train_success_predictor(training_data['user_performance'])
            
            # Treina modelo de tempo de conclusão
            if 'completion_times' in training_data:
                self._train_completion_time_predictor(training_data['completion_times'])
            
            # Treina clustering de usuários
            if 'user_profiles' in training_data:
                self._train_user_clusterer(training_data['user_profiles'])
            
            # Treina modelo de churn
            if 'user_activity' in training_data:
                self._train_churn_predictor(training_data['user_activity'])
            
            # Salva modelos treinados
            self._save_models()
            
            self.logger.info("All models trained successfully")
            
        except Exception as e:
            self.logger.error(f"Error training models: {e}")
    
    def _train_success_predictor(self, data: pd.DataFrame):
        """Treina modelo de predição de sucesso"""
        
        # Extrai features
        features = self._extract_user_features(data)
        target = data['success'].values
        
        # Normaliza features
        features_scaled = self.scalers['user_features'].fit_transform(features)
        
        # Treina modelo
        X_train, X_test, y_train, y_test = train_test_split(
            features_scaled, target, test_size=0.2, random_state=42
        )
        
        self.models['success_predictor'].fit(X_train, y_train)
        
        # Avalia modelo
        y_pred = self.models['success_predictor'].predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"Success predictor accuracy: {accuracy:.3f}")
    
    def _train_completion_time_predictor(self, data: pd.DataFrame):
        """Treina modelo de predição de tempo de conclusão"""
        
        features = self._extract_content_features(data)
        target = data['completion_time'].values
        
        features_scaled = self.scalers['content_features'].fit_transform(features)
        
        X_train, X_test, y_train, y_test = train_test_split(
            features_scaled, target, test_size=0.2, random_state=42
        )
        
        self.models['completion_time_predictor'].fit(X_train, y_train)
        
        y_pred = self.models['completion_time_predictor'].predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        self.logger.info(f"Completion time predictor MSE: {mse:.3f}")
    
    def _train_user_clusterer(self, data: pd.DataFrame):
        """Treina clustering de usuários"""
        
        features = self._extract_user_profile_features(data)
        features_scaled = self.scalers['user_features'].fit_transform(features)
        
        self.models['user_clusterer'].fit(features_scaled)
        
        self.logger.info("User clustering model trained")
    
    def _train_churn_predictor(self, data: pd.DataFrame):
        """Treina modelo de predição de churn"""
        
        features = self._extract_activity_features(data)
        target = data['churned'].values
        
        features_scaled = self.scalers['user_features'].fit_transform(features)
        
        X_train, X_test, y_train, y_test = train_test_split(
            features_scaled, target, test_size=0.2, random_state=42
        )
        
        self.models['churn_predictor'].fit(X_train, y_train)
        
        y_pred = self.models['churn_predictor'].predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"Churn predictor accuracy: {accuracy:.3f}")
    
    def predict_success_probability(self, user_id: str, content_id: str) -> PredictionResult:
        """Prediz probabilidade de sucesso do usuário em conteúdo específico"""
        
        try:
            # Obtém features do usuário e conteúdo
            user_features = self._get_user_features(user_id)
            content_features = self._get_content_features(content_id)
            
            # Combina features
            combined_features = np.concatenate([user_features, content_features])
            features_scaled = self.scalers['user_features'].transform([combined_features])
            
            # Faz predição
            probability = self.models['success_predictor'].predict_proba(features_scaled)[0][1]
            confidence = max(self.models['success_predictor'].predict_proba(features_scaled)[0])
            
            # Identifica fatores importantes
            feature_importance = self.models['success_predictor'].feature_importances_
            factors = self._get_important_factors(feature_importance, combined_features)
            
            # Gera recomendações
            recommendations = self._generate_success_recommendations(probability, factors)
            
            return PredictionResult(
                prediction_type=PredictionType.SUCCESS_PROBABILITY,
                value=probability,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting success probability: {e}")
            return self._default_prediction_result(PredictionType.SUCCESS_PROBABILITY)
    
    def predict_completion_time(self, user_id: str, content_id: str) -> PredictionResult:
        """Prediz tempo de conclusão para usuário e conteúdo específicos"""
        
        try:
            user_features = self._get_user_features(user_id)
            content_features = self._get_content_features(content_id)
            
            combined_features = np.concatenate([user_features, content_features])
            features_scaled = self.scalers['content_features'].transform([combined_features])
            
            predicted_time = self.models['completion_time_predictor'].predict(features_scaled)[0]
            
            # Calcula confiança baseada na variância das árvores
            confidence = 0.8  # Simplificado
            
            factors = [
                {'factor': 'Histórico do usuário', 'impact': 0.4},
                {'factor': 'Complexidade do conteúdo', 'impact': 0.3},
                {'factor': 'Estilo de aprendizado', 'impact': 0.3}
            ]
            
            recommendations = [
                f"Tempo estimado: {predicted_time:.0f} minutos",
                "Considere dividir em sessões menores se necessário",
                "Faça pausas regulares para melhor absorção"
            ]
            
            return PredictionResult(
                prediction_type=PredictionType.COMPLETION_TIME,
                value=predicted_time,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting completion time: {e}")
            return self._default_prediction_result(PredictionType.COMPLETION_TIME)
    
    def predict_churn_risk(self, user_id: str) -> PredictionResult:
        """Prediz risco de churn do usuário"""
        
        try:
            activity_features = self._get_user_activity_features(user_id)
            features_scaled = self.scalers['user_features'].transform([activity_features])
            
            churn_probability = self.models['churn_predictor'].predict_proba(features_scaled)[0][1]
            confidence = max(self.models['churn_predictor'].predict_proba(features_scaled)[0])
            
            # Identifica fatores de risco
            factors = [
                {'factor': 'Frequência de uso', 'impact': 0.35},
                {'factor': 'Engajamento com conteúdo', 'impact': 0.25},
                {'factor': 'Tempo desde último acesso', 'impact': 0.20},
                {'factor': 'Taxa de conclusão', 'impact': 0.20}
            ]
            
            # Gera recomendações baseadas no risco
            if churn_probability > 0.7:
                recommendations = [
                    "Alto risco de churn - intervenção imediata necessária",
                    "Enviar conteúdo personalizado",
                    "Oferecer suporte adicional",
                    "Considerar incentivos especiais"
                ]
            elif churn_probability > 0.4:
                recommendations = [
                    "Risco moderado - monitorar de perto",
                    "Aumentar engajamento com gamificação",
                    "Enviar lembretes personalizados"
                ]
            else:
                recommendations = [
                    "Baixo risco de churn",
                    "Manter estratégias atuais",
                    "Focar em crescimento e expansão"
                ]
            
            return PredictionResult(
                prediction_type=PredictionType.CHURN_RISK,
                value=churn_probability,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting churn risk: {e}")
            return self._default_prediction_result(PredictionType.CHURN_RISK)
    
    def get_user_cluster(self, user_id: str) -> Dict[str, Any]:
        """Obtém cluster do usuário e características"""
        
        try:
            user_features = self._get_user_profile_features(user_id)
            features_scaled = self.scalers['user_features'].transform([user_features])
            
            cluster = self.models['user_clusterer'].predict(features_scaled)[0]
            
            # Características dos clusters (pré-definidas)
            cluster_characteristics = {
                0: {
                    'name': 'Estudantes Iniciantes',
                    'description': 'Usuários novos, aprendendo conceitos básicos',
                    'learning_style': 'Visual e prático',
                    'preferred_content': 'Introdutório, com muitos exemplos'
                },
                1: {
                    'name': 'Profissionais Focados',
                    'description': 'Usuários experientes com objetivos específicos',
                    'learning_style': 'Direto e eficiente',
                    'preferred_content': 'Avançado, casos práticos'
                },
                2: {
                    'name': 'Estudantes Regulares',
                    'description': 'Usuários consistentes, progresso steady',
                    'learning_style': 'Misto, adaptável',
                    'preferred_content': 'Progressivo, bem estruturado'
                },
                3: {
                    'name': 'Exploradores',
                    'description': 'Usuários curiosos, exploram diversos tópicos',
                    'learning_style': 'Experimental',
                    'preferred_content': 'Variado, interdisciplinar'
                },
                4: {
                    'name': 'Especialistas',
                    'description': 'Usuários avançados, buscam especialização',
                    'learning_style': 'Analítico e profundo',
                    'preferred_content': 'Especializado, cutting-edge'
                }
            }
            
            return {
                'cluster_id': int(cluster),
                'characteristics': cluster_characteristics.get(cluster, {}),
                'similar_users_count': self._get_cluster_size(cluster),
                'recommended_strategies': self._get_cluster_strategies(cluster)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user cluster: {e}")
            return {'cluster_id': 0, 'characteristics': {}}
    
    # Métodos de extração de features
    
    def _extract_user_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extrai features do usuário"""
        features = []
        
        for _, row in data.iterrows():
            user_features = [
                row.get('total_study_time', 0),
                row.get('lessons_completed', 0),
                row.get('average_score', 0),
                row.get('streak_days', 0),
                row.get('login_frequency', 0),
                row.get('difficulty_preference', 0.5),
                row.get('session_length_avg', 30),
                row.get('time_since_last_login', 0)
            ]
            features.append(user_features)
        
        return np.array(features)
    
    def _extract_content_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extrai features do conteúdo"""
        features = []
        
        for _, row in data.iterrows():
            content_features = [
                row.get('difficulty_level', 3),
                row.get('content_length', 100),
                row.get('interaction_count', 5),
                row.get('average_rating', 4.0),
                row.get('completion_rate', 0.7),
                row.get('prerequisite_count', 0),
                row.get('multimedia_elements', 1),
                row.get('assessment_count', 3)
            ]
            features.append(content_features)
        
        return np.array(features)
    
    def _extract_user_profile_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extrai features do perfil do usuário"""
        features = []
        
        for _, row in data.iterrows():
            profile_features = [
                row.get('learning_style_visual', 0),
                row.get('learning_style_auditory', 0),
                row.get('learning_style_kinesthetic', 0),
                row.get('preferred_pace', 1.0),
                row.get('attention_span', 30),
                row.get('optimal_session_length', 45),
                row.get('difficulty_preference', 0.5),
                row.get('motivation_score', 0.7)
            ]
            features.append(profile_features)
        
        return np.array(features)
    
    def _extract_activity_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extrai features de atividade"""
        features = []
        
        for _, row in data.iterrows():
            activity_features = [
                row.get('days_since_last_login', 0),
                row.get('weekly_session_count', 3),
                row.get('average_session_duration', 25),
                row.get('content_completion_rate', 0.6),
                row.get('engagement_score', 0.7),
                row.get('social_interaction_count', 2),
                row.get('achievement_unlock_rate', 0.1),
                row.get('support_ticket_count', 0)
            ]
            features.append(activity_features)
        
        return np.array(features)
    
    # Métodos auxiliares
    
    def _get_user_features(self, user_id: str) -> np.ndarray:
        """Obtém features de um usuário específico"""
        # Em produção, buscar do banco de dados
        # Aqui simulamos features
        return np.array([
            100,  # total_study_time
            25,   # lessons_completed
            0.75, # average_score
            7,    # streak_days
            0.8,  # login_frequency
            0.6,  # difficulty_preference
            35,   # session_length_avg
            1     # time_since_last_login
        ])
    
    def _get_content_features(self, content_id: str) -> np.ndarray:
        """Obtém features de um conteúdo específico"""
        # Simulação de features de conteúdo
        return np.array([
            3,    # difficulty_level
            150,  # content_length
            8,    # interaction_count
            4.2,  # average_rating
            0.72, # completion_rate
            2,    # prerequisite_count
            3,    # multimedia_elements
            5     # assessment_count
        ])
    
    def _get_user_profile_features(self, user_id: str) -> np.ndarray:
        """Obtém features do perfil do usuário"""
        return np.array([
            1,    # learning_style_visual
            0,    # learning_style_auditory
            0,    # learning_style_kinesthetic
            1.2,  # preferred_pace
            35,   # attention_span
            45,   # optimal_session_length
            0.6,  # difficulty_preference
            0.8   # motivation_score
        ])
    
    def _get_user_activity_features(self, user_id: str) -> np.ndarray:
        """Obtém features de atividade do usuário"""
        return np.array([
            2,    # days_since_last_login
            4,    # weekly_session_count
            28,   # average_session_duration
            0.68, # content_completion_rate
            0.75, # engagement_score
            3,    # social_interaction_count
            0.15, # achievement_unlock_rate
            0     # support_ticket_count
        ])
    
    def _get_important_factors(self, feature_importance: np.ndarray, features: np.ndarray) -> List[Dict[str, Any]]:
        """Identifica fatores mais importantes"""
        feature_names = [
            'Tempo de estudo', 'Lições completadas', 'Score médio', 'Streak',
            'Frequência de login', 'Preferência de dificuldade', 'Duração da sessão',
            'Tempo desde último login'
        ]
        
        factors = []
        for i, importance in enumerate(feature_importance[:len(feature_names)]):
            if importance > 0.05:  # Apenas fatores significativos
                factors.append({
                    'factor': feature_names[i],
                    'importance': float(importance),
                    'value': float(features[i]) if i < len(features) else 0.0
                })
        
        return sorted(factors, key=lambda x: x['importance'], reverse=True)[:5]
    
    def _generate_success_recommendations(self, probability: float, factors: List[Dict]) -> List[str]:
        """Gera recomendações baseadas na probabilidade de sucesso"""
        recommendations = []
        
        if probability < 0.3:
            recommendations.extend([
                "Considere revisar pré-requisitos antes de continuar",
                "Tente conteúdo de nível mais básico primeiro",
                "Use recursos de ajuda e tutoriais"
            ])
        elif probability < 0.6:
            recommendations.extend([
                "Dedique mais tempo para prática",
                "Revise conceitos fundamentais",
                "Considere estudar em grupo"
            ])
        else:
            recommendations.extend([
                "Você tem boa chance de sucesso!",
                "Mantenha o ritmo atual de estudos",
                "Considere desafios mais avançados"
            ])
        
        return recommendations
    
    def _get_cluster_size(self, cluster_id: int) -> int:
        """Obtém tamanho do cluster"""
        # Simulação
        cluster_sizes = {0: 150, 1: 200, 2: 300, 3: 100, 4: 80}
        return cluster_sizes.get(cluster_id, 100)
    
    def _get_cluster_strategies(self, cluster_id: int) -> List[str]:
        """Obtém estratégias recomendadas para o cluster"""
        strategies = {
            0: ["Conteúdo visual", "Progressão gradual", "Muito feedback"],
            1: ["Casos práticos", "Conteúdo direto", "Aplicação imediata"],
            2: ["Estrutura clara", "Progressão linear", "Avaliações regulares"],
            3: ["Variedade de tópicos", "Conexões interdisciplinares", "Exploração livre"],
            4: ["Conteúdo avançado", "Análise profunda", "Pesquisa independente"]
        }
        return strategies.get(cluster_id, ["Estratégia padrão"])
    
    def _default_prediction_result(self, prediction_type: PredictionType) -> PredictionResult:
        """Retorna resultado padrão em caso de erro"""
        return PredictionResult(
            prediction_type=prediction_type,
            value=0.5,
            confidence=0.3,
            factors=[],
            recommendations=["Dados insuficientes para predição precisa"],
            timestamp=datetime.now()
        )
    
    def _save_models(self):
        """Salva modelos treinados"""
        try:
            model_path = getattr(settings, 'ML_MODELS_PATH', '/tmp/ml_models/')
            
            for name, model in self.models.items():
                joblib.dump(model, f"{model_path}/{name}.pkl")
            
            for name, scaler in self.scalers.items():
                joblib.dump(scaler, f"{model_path}/{name}_scaler.pkl")
            
            self.logger.info("Models saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Carrega modelos salvos"""
        try:
            model_path = getattr(settings, 'ML_MODELS_PATH', '/tmp/ml_models/')
            
            for name in self.models.keys():
                try:
                    self.models[name] = joblib.load(f"{model_path}/{name}.pkl")
                except FileNotFoundError:
                    self.logger.warning(f"Model {name} not found, using default")
            
            for name in self.scalers.keys():
                try:
                    self.scalers[name] = joblib.load(f"{model_path}/{name}_scaler.pkl")
                except FileNotFoundError:
                    self.logger.warning(f"Scaler {name} not found, using default")
            
            self.logger.info("Models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")

class PersonalizedLearningEngine:
    """Engine de aprendizado personalizado"""
    
    def __init__(self):
        self.ml_engine = AdvancedMLEngine()
        self.logger = logging.getLogger(__name__)
    
    def generate_learning_path(self, user_id: str, learning_goals: List[str]) -> List[LearningPathStep]:
        """Gera caminho de aprendizado personalizado"""
        
        try:
            # Obtém perfil do usuário
            user_cluster = self.ml_engine.get_user_cluster(user_id)
            
            # Gera passos baseados nos objetivos e cluster
            learning_path = []
            
            for i, goal in enumerate(learning_goals):
                # Prediz dificuldade ótima
                optimal_difficulty = self._predict_optimal_difficulty(user_id, goal)
                
                # Cria passo do caminho
                step = LearningPathStep(
                    step_id=f"step_{i+1}",
                    content_id=f"content_{goal.lower().replace(' ', '_')}",
                    title=f"Aprender {goal}",
                    description=f"Dominar conceitos fundamentais de {goal}",
                    difficulty=optimal_difficulty,
                    estimated_time=self._estimate_learning_time(user_id, goal),
                    prerequisites=self._get_prerequisites(goal),
                    learning_objectives=self._get_learning_objectives(goal),
                    assessment_criteria=self._get_assessment_criteria(goal),
                    adaptive_parameters=self._get_adaptive_parameters(user_id, goal)
                )
                
                learning_path.append(step)
            
            return learning_path
            
        except Exception as e:
            self.logger.error(f"Error generating learning path: {e}")
            return []
    
    def recommend_content(self, user_id: str, limit: int = 10) -> List[ContentRecommendation]:
        """Recomenda conteúdo personalizado"""
        
        try:
            # Obtém perfil e cluster do usuário
            user_cluster = self.ml_engine.get_user_cluster(user_id)
            
            # Simula recomendações baseadas no cluster
            recommendations = []
            
            # Conteúdo baseado no cluster
            cluster_content = self._get_cluster_content(user_cluster['cluster_id'])
            
            for i, content in enumerate(cluster_content[:limit]):
                # Prediz relevância
                relevance_score = self._calculate_relevance_score(user_id, content['id'])
                
                recommendation = ContentRecommendation(
                    content_id=content['id'],
                    content_type=content['type'],
                    title=content['title'],
                    description=content['description'],
                    difficulty_level=DifficultyLevel(content['difficulty']),
                    estimated_time=content['estimated_time'],
                    relevance_score=relevance_score,
                    confidence=0.8,
                    reasoning=self._get_recommendation_reasoning(user_cluster, content),
                    prerequisites=content.get('prerequisites', []),
                    learning_objectives=content.get('objectives', [])
                )
                
                recommendations.append(recommendation)
            
            # Ordena por relevância
            recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error recommending content: {e}")
            return []
    
    def adapt_difficulty(self, user_id: str, current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta dificuldade baseada na performance atual"""
        
        try:
            # Analisa performance
            accuracy = current_performance.get('accuracy', 0.5)
            response_time = current_performance.get('response_time', 30)
            engagement = current_performance.get('engagement', 0.5)
            
            # Calcula ajuste de dificuldade
            if accuracy > 0.8 and response_time < 20:
                difficulty_adjustment = 0.2  # Aumentar dificuldade
                recommendation = "Aumentar dificuldade - usuário demonstra domínio"
            elif accuracy < 0.5 or response_time > 60:
                difficulty_adjustment = -0.3  # Diminuir dificuldade
                recommendation = "Diminuir dificuldade - usuário com dificuldades"
            else:
                difficulty_adjustment = 0.0  # Manter dificuldade
                recommendation = "Manter dificuldade atual"
            
            return {
                'difficulty_adjustment': difficulty_adjustment,
                'recommendation': recommendation,
                'confidence': 0.85,
                'factors': {
                    'accuracy': accuracy,
                    'response_time': response_time,
                    'engagement': engagement
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error adapting difficulty: {e}")
            return {'difficulty_adjustment': 0.0, 'recommendation': 'Manter atual'}
    
    # Métodos auxiliares
    
    def _predict_optimal_difficulty(self, user_id: str, topic: str) -> DifficultyLevel:
        """Prediz dificuldade ótima para tópico"""
        # Simulação baseada no perfil do usuário
        user_features = self.ml_engine._get_user_features(user_id)
        avg_score = user_features[2]  # average_score
        
        if avg_score > 0.8:
            return DifficultyLevel.ADVANCED
        elif avg_score > 0.6:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    def _estimate_learning_time(self, user_id: str, topic: str) -> int:
        """Estima tempo de aprendizado"""
        # Simulação baseada no histórico do usuário
        base_time = 45  # minutos
        
        user_features = self.ml_engine._get_user_features(user_id)
        pace_factor = user_features[5]  # difficulty_preference como proxy para pace
        
        return int(base_time * (2 - pace_factor))
    
    def _get_prerequisites(self, topic: str) -> List[str]:
        """Obtém pré-requisitos para tópico"""
        prerequisites_map = {
            'Direito Constitucional': ['Teoria Geral do Direito'],
            'Direito Civil': ['Direito Constitucional'],
            'Direito Penal': ['Direito Constitucional'],
            'Direito Processual': ['Direito Civil', 'Direito Penal']
        }
        return prerequisites_map.get(topic, [])
    
    def _get_learning_objectives(self, topic: str) -> List[str]:
        """Obtém objetivos de aprendizado"""
        objectives_map = {
            'Direito Constitucional': [
                'Compreender princípios constitucionais',
                'Analisar direitos fundamentais',
                'Aplicar controle de constitucionalidade'
            ],
            'Direito Civil': [
                'Dominar teoria geral dos contratos',
                'Compreender responsabilidade civil',
                'Aplicar direitos reais'
            ]
        }
        return objectives_map.get(topic, ['Dominar conceitos fundamentais'])
    
    def _get_assessment_criteria(self, topic: str) -> List[str]:
        """Obtém critérios de avaliação"""
        return [
            'Compreensão conceitual',
            'Aplicação prática',
            'Análise crítica',
            'Resolução de problemas'
        ]
    
    def _get_adaptive_parameters(self, user_id: str, topic: str) -> Dict[str, Any]:
        """Obtém parâmetros adaptativos"""
        return {
            'min_accuracy_threshold': 0.7,
            'max_attempts': 3,
            'hint_frequency': 'medium',
            'feedback_detail': 'high',
            'pace_adjustment': 'auto'
        }
    
    def _get_cluster_content(self, cluster_id: int) -> List[Dict[str, Any]]:
        """Obtém conteúdo recomendado para cluster"""
        cluster_content = {
            0: [  # Estudantes Iniciantes
                {
                    'id': 'intro_direito_001',
                    'type': 'lesson',
                    'title': 'Introdução ao Direito',
                    'description': 'Conceitos básicos e fundamentais',
                    'difficulty': 1,
                    'estimated_time': 30
                }
            ],
            1: [  # Profissionais Focados
                {
                    'id': 'casos_praticos_001',
                    'type': 'case_study',
                    'title': 'Casos Práticos Avançados',
                    'description': 'Análise de casos reais',
                    'difficulty': 4,
                    'estimated_time': 60
                }
            ]
        }
        return cluster_content.get(cluster_id, [])
    
    def _calculate_relevance_score(self, user_id: str, content_id: str) -> float:
        """Calcula score de relevância"""
        # Simulação baseada em múltiplos fatores
        base_score = 0.7
        
        # Ajustes baseados no perfil do usuário
        user_features = self.ml_engine._get_user_features(user_id)
        engagement_factor = user_features[4]  # login_frequency
        
        return min(1.0, base_score + (engagement_factor * 0.3))
    
    def _get_recommendation_reasoning(self, user_cluster: Dict, content: Dict) -> List[str]:
        """Obtém razões para recomendação"""
        return [
            f"Adequado para {user_cluster['characteristics'].get('name', 'seu perfil')}",
            f"Nível de dificuldade apropriado",
            f"Alinha com seu estilo de aprendizado"
        ]

# Instâncias globais
ml_engine = AdvancedMLEngine()
personalized_learning_engine = PersonalizedLearningEngine()

# Funções de utilidade
def predict_user_success(user_id: str, content_id: str) -> PredictionResult:
    """Prediz sucesso do usuário"""
    return ml_engine.predict_success_probability(user_id, content_id)

def get_personalized_recommendations(user_id: str, limit: int = 5) -> List[ContentRecommendation]:
    """Obtém recomendações personalizadas"""
    return personalized_learning_engine.recommend_content(user_id, limit)

def generate_adaptive_learning_path(user_id: str, goals: List[str]) -> List[LearningPathStep]:
    """Gera caminho de aprendizado adaptativo"""
    return personalized_learning_engine.generate_learning_path(user_id, goals)

def analyze_user_learning_pattern(user_id: str) -> Dict[str, Any]:
    """Analisa padrão de aprendizado do usuário"""
    cluster_info = ml_engine.get_user_cluster(user_id)
    churn_risk = ml_engine.predict_churn_risk(user_id)
    
    return {
        'cluster': cluster_info,
        'churn_risk': asdict(churn_risk),
        'learning_style': cluster_info['characteristics'].get('learning_style', 'Misto'),
        'recommended_strategies': cluster_info.get('recommended_strategies', [])
    } 