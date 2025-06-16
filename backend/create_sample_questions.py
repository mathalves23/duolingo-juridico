#!/usr/bin/env python
"""
Script para criar questões de exemplo para testar a integração
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionOption, ExamBoard
from courses.models import Subject

def create_sample_questions():
    print("Criando questões de exemplo...")
    
    # Criar banca de exemplo
    banca, created = ExamBoard.objects.get_or_create(
        acronym='CESPE',
        defaults={
            'name': 'Centro de Seleção e de Promoção de Eventos',
            'description': 'Banca CESPE/CEBRASPE',
            'website': 'https://www.cebraspe.org.br',
            'is_active': True
        }
    )
    if created:
        print(f"Banca criada: {banca.name}")
    
    # Buscar disciplinas
    subjects = Subject.objects.all()[:3]  # Pegar as 3 primeiras
    
    questions_data = [
        {
            'title': 'Princípios Constitucionais',
            'question_text': 'Sobre os princípios fundamentais da Constituição Federal de 1988, assinale a alternativa correta:',
            'subject': 'Direito Constitucional',
            'options': [
                ('A dignidade da pessoa humana é fundamento da República Federativa do Brasil.', True),
                ('A soberania não é considerada um fundamento do Estado brasileiro.', False),
                ('Os valores sociais do trabalho são objetivos fundamentais da República.', False),
                ('A cidadania não está prevista como fundamento constitucional.', False)
            ]
        },
        {
            'title': 'Atos Administrativos',
            'question_text': 'Quanto aos atos administrativos, é CORRETO afirmar que:',
            'subject': 'Direito Administrativo',
            'options': [
                ('A presunção de legitimidade permite a execução imediata dos atos administrativos.', True),
                ('Todo ato administrativo é irrevogável.', False),
                ('A imperatividade está presente em todos os atos administrativos.', False),
                ('A autoexecutoriedade independe de previsão legal.', False)
            ]
        },
        {
            'title': 'Crimes contra a Pessoa',
            'question_text': 'No Código Penal brasileiro, o crime de homicídio simples está previsto no artigo:',
            'subject': 'Direito Penal',
            'options': [
                ('Art. 121', True),
                ('Art. 129', False),
                ('Art. 155', False),
                ('Art. 171', False)
            ]
        }
    ]
    
    for q_data in questions_data:
        # Encontrar a disciplina correspondente
        subject = subjects.filter(name__icontains=q_data['subject'].split()[1]).first()
        
        if not subject:
            subject = subjects.first()  # Usar a primeira se não encontrar
            
        # Criar questão
        question = Question.objects.create(
            title=q_data['title'],
            question_text=q_data['question_text'],
            question_type='multiple_choice',
            subject=subject,
            exam_board=banca,
            exam_name='Concurso Exemplo',
            exam_year=2024,
            difficulty_level=2,
            explanation=f'Explicação para: {q_data["title"]}',
            is_active=True
        )
        
        # Criar opções
        for i, (text, is_correct) in enumerate(q_data['options']):
            QuestionOption.objects.create(
                question=question,
                option_text=text,
                is_correct=is_correct,
                order=i+1
            )
        
        print(f"Questão criada: {question.title}")
    
    print(f"Total de questões: {Question.objects.count()}")

if __name__ == '__main__':
    create_sample_questions() 