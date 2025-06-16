#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo
"""

import os
import sys
import django
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Subject, Topic, Lesson
from questions.models import ExamBoard, Question, QuestionOption
from gamification.models import Achievement, StoreItem, DailyChallenge
from ai_service.models import AIModel

User = get_user_model()

def create_users():
    """Criar usuários de exemplo"""
    print("Criando usuários...")
    
    # Superusuário
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@duolingojuridico.com',
            password='admin123',
            first_name='Admin',
            last_name='Sistema'
        )
        print(f"✓ Superusuário criado: {admin.username}")
    
    # Usuário demo
    if not User.objects.filter(username='demo').exists():
        demo_user = User.objects.create_user(
            username='demo',
            email='demo@duolingojuridico.com',
            password='demo123',
            first_name='Usuário',
            last_name='Demo'
        )
        
        # Criar perfil do usuário demo
        from accounts.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=demo_user,
            defaults={
                'bio': 'Usuário de demonstração do Duolingo Jurídico',
                'target_exam': 'Concurso Público Federal',
                'experience_level': 'intermediate',
                'study_goals': 'Aprovação em concurso público',
                'xp_points': 1250,
                'coins': 340,
                'current_streak': 7,
                'best_streak': 15,
                'total_study_time': 2340
            }
        )
        demo_user.profile = profile
        demo_user.save()
        print(f"✓ Usuário demo criado: {demo_user.username}")

def create_subjects():
    """Criar disciplinas jurídicas"""
    print("Criando disciplinas...")
    
    subjects_data = [
        {
            'name': 'Direito Constitucional',
            'description': 'Estudo da Constituição Federal e seus princípios fundamentais',
            'category': 'law',
            'color_hex': '#3B82F6',
            'order': 1
        },
        {
            'name': 'Direito Administrativo',
            'description': 'Princípios e normas da Administração Pública',
            'category': 'law',
            'color_hex': '#10B981',
            'order': 2
        },
        {
            'name': 'Direito Penal',
            'description': 'Crimes, penas e medidas de segurança',
            'category': 'law',
            'color_hex': '#EF4444',
            'order': 3
        },
        {
            'name': 'Direito Civil',
            'description': 'Relações jurídicas entre particulares',
            'category': 'law',
            'color_hex': '#8B5CF6',
            'order': 4
        },
        {
            'name': 'Direito Processual Civil',
            'description': 'Procedimentos e ritos do processo civil',
            'category': 'law',
            'color_hex': '#F59E0B',
            'order': 5
        },
        {
            'name': 'Direito do Trabalho',
            'description': 'Relações trabalhistas e direitos dos trabalhadores',
            'category': 'law',
            'color_hex': '#06B6D4',
            'order': 6
        },
        {
            'name': 'Direito Tributário',
            'description': 'Sistema tributário nacional e impostos',
            'category': 'law',
            'color_hex': '#84CC16',
            'order': 7
        }
    ]
    
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            defaults=subject_data
        )
        if created:
            print(f"✓ Disciplina criada: {subject.name}")

def create_topics_and_lessons():
    """Criar tópicos e lições"""
    print("Criando tópicos e lições...")
    
    # Direito Constitucional
    const_subject = Subject.objects.get(name='Direito Constitucional')
    
    topics_data = [
        {
            'subject': const_subject,
            'name': 'Princípios Fundamentais',
            'description': 'Fundamentos da República Federativa do Brasil',
            'order': 1,
            'lessons': [
                {
                    'title': 'Fundamentos da República',
                    'content': 'A República Federativa do Brasil tem como fundamentos: soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e da livre iniciativa, pluralismo político.',
                    'lesson_type': 'theory',
                    'difficulty_level': 2,
                    'estimated_duration': 30,
                    'xp_reward': 50,
                    'order': 1
                },
                {
                    'title': 'Objetivos Fundamentais',
                    'content': 'Os objetivos fundamentais da República incluem: construir uma sociedade livre, justa e solidária; garantir o desenvolvimento nacional; erradicar a pobreza e a marginalização.',
                    'lesson_type': 'theory',
                    'difficulty_level': 2,
                    'estimated_duration': 25,
                    'xp_reward': 45,
                    'order': 2
                }
            ]
        },
        {
            'subject': const_subject,
            'name': 'Direitos e Garantias Fundamentais',
            'description': 'Direitos individuais, coletivos, sociais e políticos',
            'order': 2,
            'lessons': [
                {
                    'title': 'Direitos Individuais',
                    'content': 'Todos são iguais perante a lei, sem distinção de qualquer natureza. São invioláveis o direito à vida, à liberdade, à igualdade, à segurança e à propriedade.',
                    'lesson_type': 'theory',
                    'difficulty_level': 3,
                    'estimated_duration': 40,
                    'xp_reward': 60,
                    'order': 1
                }
            ]
        }
    ]
    
    for topic_data in topics_data:
        topic, created = Topic.objects.get_or_create(
            subject=topic_data['subject'],
            name=topic_data['name'],
            defaults={
                'description': topic_data['description'],
                'order': topic_data['order']
            }
        )
        
        if created:
            print(f"✓ Tópico criado: {topic.name}")
            
            # Criar lições
            for lesson_data in topic_data['lessons']:
                lesson, lesson_created = Lesson.objects.get_or_create(
                    topic=topic,
                    title=lesson_data['title'],
                    defaults={
                        'content': lesson_data['content'],
                        'lesson_type': lesson_data['lesson_type'],
                        'difficulty_level': lesson_data['difficulty_level'],
                        'estimated_minutes': lesson_data['estimated_duration'],
                        'xp_reward': lesson_data['xp_reward'],
                        'order': lesson_data['order']
                    }
                )
                if lesson_created:
                    print(f"  ✓ Lição criada: {lesson.title}")

def create_exam_boards():
    """Criar bancas de concurso"""
    print("Criando bancas de concurso...")
    
    boards_data = [
        {
            'name': 'Centro de Seleção e de Promoção de Eventos',
            'acronym': 'CESPE/CEBRASPE',
            'description': 'Uma das principais bancas de concursos públicos do Brasil',
            'website': 'https://www.cebraspe.org.br'
        },
        {
            'name': 'Fundação Carlos Chagas',
            'acronym': 'FCC',
            'description': 'Banca tradicional em concursos públicos',
            'website': 'https://www.concursosfcc.com.br'
        },
        {
            'name': 'Fundação Getúlio Vargas',
            'acronym': 'FGV',
            'description': 'Banca renomada em concursos de alto nível',
            'website': 'https://www.fgv.br'
        },
        {
            'name': 'Fundação Vunesp',
            'acronym': 'VUNESP',
            'description': 'Banca especializada em concursos do estado de São Paulo',
            'website': 'https://www.vunesp.com.br'
        }
    ]
    
    for board_data in boards_data:
        board, created = ExamBoard.objects.get_or_create(
            acronym=board_data['acronym'],
            defaults=board_data
        )
        if created:
            print(f"✓ Banca criada: {board.acronym}")

def create_questions():
    """Criar questões de exemplo"""
    print("Criando questões...")
    
    const_subject = Subject.objects.get(name='Direito Constitucional')
    cespe = ExamBoard.objects.get(acronym='CESPE/CEBRASPE')
    
    questions_data = [
        {
            'subject': const_subject,
            'exam_board': cespe,
            'statement': 'Segundo a Constituição Federal, são fundamentos da República Federativa do Brasil:',
            'explanation': 'Os fundamentos estão previstos no art. 1º da CF/88: soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e da livre iniciativa, pluralismo político.',
            'difficulty_level': 2,
            'year': 2023,
            'source': 'Concurso Público Federal - 2023',
            'tags': ['fundamentos', 'república', 'constituição'],
            'options': [
                {
                    'text': 'Soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e da livre iniciativa, pluralismo político.',
                    'is_correct': True,
                    'order': 1,
                    'explanation': 'Correta. Estes são exatamente os cinco fundamentos previstos no art. 1º da CF/88.'
                },
                {
                    'text': 'Liberdade, igualdade, fraternidade, justiça social e desenvolvimento nacional.',
                    'is_correct': False,
                    'order': 2,
                    'explanation': 'Incorreta. Estes não são os fundamentos previstos na Constituição.'
                },
                {
                    'text': 'Democracia, república, federação, estado de direito e separação de poderes.',
                    'is_correct': False,
                    'order': 3,
                    'explanation': 'Incorreta. Estes são princípios constitucionais, mas não os fundamentos do art. 1º.'
                },
                {
                    'text': 'Soberania nacional, independência, autodeterminação dos povos e não intervenção.',
                    'is_correct': False,
                    'order': 4,
                    'explanation': 'Incorreta. Estes são princípios das relações internacionais, não fundamentos da República.'
                }
            ]
        },
        {
            'subject': const_subject,
            'exam_board': cespe,
            'statement': 'A respeito dos direitos e garantias fundamentais, é correto afirmar que:',
            'explanation': 'O princípio da igualdade está previsto no caput do art. 5º da CF/88 e é um dos pilares dos direitos fundamentais.',
            'difficulty_level': 3,
            'year': 2023,
            'source': 'Concurso Público Federal - 2023',
            'tags': ['direitos fundamentais', 'igualdade', 'liberdade'],
            'options': [
                {
                    'text': 'Todos são iguais perante a lei, sem distinção de qualquer natureza.',
                    'is_correct': True,
                    'order': 1,
                    'explanation': 'Correta. Esta é a redação literal do caput do art. 5º da CF/88.'
                },
                {
                    'text': 'A igualdade material sempre prevalece sobre a igualdade formal.',
                    'is_correct': False,
                    'order': 2,
                    'explanation': 'Incorreta. Ambas as dimensões da igualdade coexistem no ordenamento jurídico.'
                },
                {
                    'text': 'Os direitos fundamentais são absolutos e não admitem limitações.',
                    'is_correct': False,
                    'order': 3,
                    'explanation': 'Incorreta. Os direitos fundamentais podem sofrer limitações em casos específicos.'
                },
                {
                    'text': 'Apenas brasileiros natos podem invocar direitos fundamentais.',
                    'is_correct': False,
                    'order': 4,
                    'explanation': 'Incorreta. Os direitos fundamentais se estendem também aos estrangeiros residentes no país.'
                }
            ]
        }
    ]
    
    for question_data in questions_data:
        question, created = Question.objects.get_or_create(
            statement=question_data['statement'],
            defaults={
                'title': question_data['statement'][:100] + '...',
                'question_type': 'multiple_choice',
                'subject': question_data['subject'],
                'exam_board': question_data['exam_board'],
                'exam_name': question_data['source'],
                'exam_year': question_data['year'],
                'difficulty_level': question_data['difficulty_level'],
                'tags': question_data['tags']
            }
        )
        
        if created:
            print(f"✓ Questão criada: {question.statement[:50]}...")
            
            # Criar opções
            letters = ['A', 'B', 'C', 'D', 'E']
            for i, option_data in enumerate(question_data['options']):
                option, option_created = QuestionOption.objects.get_or_create(
                    question=question,
                    letter=letters[i],
                    defaults={
                        'text': option_data['text'],
                        'is_correct': option_data['is_correct'],
                        'order': option_data['order'],
                        'explanation': option_data['explanation']
                    }
                )

def create_achievements():
    """Criar conquistas"""
    print("Criando conquistas...")
    
    achievements_data = [
        {
            'name': 'Primeiro Passo',
            'description': 'Complete sua primeira lição',
            'achievement_type': 'lessons',
            'rarity': 'common',
            'badge_color': '#10B981',
            'xp_reward': 50,
            'coin_reward': 10,
            'requirements': {'total_lessons': 1}
        },
        {
            'name': 'Sequência de Fogo',
            'description': 'Mantenha uma sequência de 7 dias',
            'achievement_type': 'streak',
            'rarity': 'rare',
            'badge_color': '#F59E0B',
            'xp_reward': 100,
            'coin_reward': 25,
            'requirements': {'days': 7}
        },
        {
            'name': 'Conhecedor',
            'description': 'Responda 100 questões corretamente',
            'achievement_type': 'accuracy',
            'rarity': 'epic',
            'badge_color': '#8B5CF6',
            'xp_reward': 200,
            'coin_reward': 50,
            'requirements': {'correct_answers': 100}
        },
        {
            'name': 'Especialista Constitucional',
            'description': 'Complete todos os tópicos de Direito Constitucional',
            'achievement_type': 'special',
            'rarity': 'legendary',
            'badge_color': '#3B82F6',
            'xp_reward': 300,
            'coin_reward': 75,
            'requirements': {'subject_completion': 'Direito Constitucional'}
        }
    ]
    
    for achievement_data in achievements_data:
        achievement, created = Achievement.objects.get_or_create(
            name=achievement_data['name'],
            defaults=achievement_data
        )
        if created:
            print(f"✓ Conquista criada: {achievement.name}")

def create_store_items():
    """Criar itens da loja"""
    print("Criando itens da loja...")
    
    items_data = [
        {
            'name': 'Avatar Advogado',
            'description': 'Avatar personalizado de advogado',
            'coin_price': 100,
            'item_type': 'avatar',
            'item_data': {'avatar_id': 'lawyer_01', 'rarity': 'common'}
        },
        {
            'name': 'Tema Escuro Premium',
            'description': 'Tema escuro elegante para a interface',
            'coin_price': 150,
            'item_type': 'theme',
            'item_data': {'theme_id': 'dark_premium', 'rarity': 'rare'}
        },
        {
            'name': 'Boost de XP 2x',
            'description': 'Dobra o XP ganho por 24 horas',
            'coin_price': 200,
            'item_type': 'boost',
            'duration_hours': 24,
            'item_data': {'boost_type': 'xp', 'multiplier': 2}
        },
        {
            'name': 'Dicas da IA Premium',
            'description': 'Acesso a explicações detalhadas da IA',
            'coin_price': 300,
            'item_type': 'premium',
            'duration_hours': 720,  # 30 dias
            'item_data': {'feature_id': 'ai_premium'}
        }
    ]
    
    for item_data in items_data:
        item, created = StoreItem.objects.get_or_create(
            name=item_data['name'],
            defaults=item_data
        )
        if created:
            print(f"✓ Item da loja criado: {item.name}")

def create_daily_challenges():
    """Criar desafios diários"""
    print("Criando desafios diários...")
    
    from datetime import date, timedelta
    
    challenges_data = [
        {
            'title': 'Maratona de Questões',
            'description': 'Responda 10 questões hoje',
            'challenge_type': 'quiz',
            'requirements': {'questions_answered': 10},
            'xp_reward': 100,
            'coin_reward': 20,
            'date': date.today()
        },
        {
            'title': 'Estudioso Dedicado',
            'description': 'Estude por 30 minutos hoje',
            'challenge_type': 'time_limit',
            'requirements': {'study_minutes': 30},
            'xp_reward': 75,
            'coin_reward': 15,
            'date': date.today() + timedelta(days=2)
        },
        {
            'title': 'Acerto em Cheio',
            'description': 'Acerte 5 questões seguidas',
            'challenge_type': 'accuracy',
            'requirements': {'consecutive_correct': 5},
            'xp_reward': 150,
            'coin_reward': 30,
            'date': date.today() + timedelta(days=3)
        }
    ]
    
    for challenge_data in challenges_data:
        challenge, created = DailyChallenge.objects.get_or_create(
            title=challenge_data['title'],
            date=challenge_data['date'],
            defaults=challenge_data
        )
        if created:
            print(f"✓ Desafio diário criado: {challenge.title}")

def create_ai_models():
    """Criar modelos de IA"""
    print("Criando modelos de IA...")
    
    models_data = [
        {
            'name': 'GPT-4 Turbo',
            'model_type': 'explanation',
            'provider': 'openai',
            'model_name': 'gpt-4-turbo',
            'system_prompt': 'Você é um assistente especializado em Direito brasileiro. Forneça explicações claras e precisas.',
            'is_default': True,
            'max_tokens': 4000,
            'temperature': 0.7,
            'cost_per_token': 0.00003
        },
        {
            'name': 'GPT-3.5 Turbo',
            'model_type': 'adaptive_learning',
            'provider': 'openai',
            'model_name': 'gpt-3.5-turbo',
            'system_prompt': 'Você é um tutor de estudos jurídicos. Forneça recomendações personalizadas.',
            'is_default': True,
            'max_tokens': 2000,
            'temperature': 0.5,
            'cost_per_token': 0.000002
        }
    ]
    
    for model_data in models_data:
        model, created = AIModel.objects.get_or_create(
            name=model_data['name'],
            model_type=model_data['model_type'],
            defaults=model_data
        )
        if created:
            print(f"✓ Modelo de IA criado: {model.name}")

def main():
    """Função principal"""
    print("🚀 Iniciando população do banco de dados...")
    print("=" * 50)
    
    try:
        create_users()
        create_subjects()
        create_topics_and_lessons()
        create_exam_boards()
        create_questions()
        create_achievements()
        create_store_items()
        create_daily_challenges()
        create_ai_models()
        
        print("=" * 50)
        print("✅ Banco de dados populado com sucesso!")
        print("\n📊 Resumo:")
        print(f"   • Usuários: {User.objects.count()}")
        print(f"   • Disciplinas: {Subject.objects.count()}")
        print(f"   • Tópicos: {Topic.objects.count()}")
        print(f"   • Lições: {Lesson.objects.count()}")
        print(f"   • Bancas: {ExamBoard.objects.count()}")
        print(f"   • Questões: {Question.objects.count()}")
        print(f"   • Conquistas: {Achievement.objects.count()}")
        print(f"   • Itens da Loja: {StoreItem.objects.count()}")
        print(f"   • Desafios Diários: {DailyChallenge.objects.count()}")
        print(f"   • Modelos de IA: {AIModel.objects.count()}")
        
        print("\n🎯 Credenciais de acesso:")
        print("   • Admin: admin / admin123")
        print("   • Demo: demo / demo123")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco de dados: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 