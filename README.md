# 🎯 Duolingo Jurídico - Aplicativo de Concursos Públicos

Aplicativo educacional gamificado para estudo de concursos públicos brasileiros, desenvolvido nos moldes do Duolingo.

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.11+**
- **Django 4.2+** 
- **Django REST Framework**
- **PostgreSQL**
- **Redis** (cache e tasks)
- **Celery** (tasks assíncronas)

### Frontend Web
- **React 18+**
- **TypeScript**
- **Material-UI / Ant Design**
- **Redux Toolkit**

### Mobile
- **React Native**
- **Expo**
- **TypeScript**

### Infraestrutura
- **Docker & Docker Compose**
- **AWS / Google Cloud**
- **Firebase** (push notifications, analytics)
- **OpenAI GPT-4** (IA explicativa)

## 📚 Funcionalidades Principais

### ✅ MVP Implementado
- 🏛️ **7 Disciplinas**: Direito Constitucional, Administrativo, Penal, Civil, Português, Raciocínio Lógico, Informática
- 🎯 **Sistema de Lições**: Progressão por níveis (1-5)
- 🎮 **Gamificação**: XP, moedas, streaks, ranking
- 📝 **Tipos de Questão**: Múltipla escolha, V/F, lacunas, flashcards
- 🤖 **IA Explicativa**: Feedback inteligente em respostas erradas
- 📊 **Simulados**: Por banca, disciplina e dificuldade
- 🔄 **Repetição Espaçada**: Sistema de revisão inteligente

### 🔮 Próximas Funcionalidades
- 📖 **Redação** com correção por IA
- 🎥 **Videoaulas** integradas
- 👥 **Comunidade** e fóruns
- 📈 **Planos de estudo** personalizados
- 🔄 **Atualização automática** das leis

## 🎯 Disciplinas Disponíveis

### 📘 Direito
- Direito Constitucional
- Direito Administrativo  
- Direito Penal
- Direito Civil
- Direito Processual Civil
- Direito do Trabalho
- Direito Tributário
- E muitas outras...

### 🧠 Outras Matérias
- Língua Portuguesa
- Matemática e Raciocínio Lógico
- Informática
- Administração Pública
- Atualidades

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker (opcional)

### Backend (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend (React)
```bash
cd frontend
npm install
npm start
```

### Mobile (React Native)
```bash
cd mobile
npm install
expo start
```

## 🗂️ Estrutura do Projeto

```
duolingo-juridico/
├── backend/              # Django REST API
├── frontend/             # React Web App
├── mobile/               # React Native App
├── docker-compose.yml    # Ambiente de desenvolvimento
├── requirements.txt      # Dependências Python
└── README.md
```

## 📊 Modelo de Negócios

### 🆓 Plano Gratuito
- 5 lições por dia
- 1 simulado por semana
- Ranking básico

### 💎 Plano Premium
- Lições ilimitadas
- Simulados ilimitados
- Relatórios detalhados
- IA avançada
- Suporte prioritário

## 🎮 Sistema de Gamificação

- 🏆 **XP e Níveis**: Progressão por experiência
- 🪙 **Moedas**: Compra de itens na loja  
- 🔥 **Streaks**: Dias consecutivos de estudo
- 🥇 **Rankings**: Competição semanal/mensal
- 🏅 **Conquistas**: Emblemas e troféus especiais

## 🤖 Inteligência Artificial

- 💡 **Explicações contextuais** para respostas erradas
- 🎯 **Simulados adaptativos** baseados no desempenho
- 📚 **Sugestões de revisão** personalizadas
- 🔍 **RAG** com jurisprudência e doutrina

## 🔒 Segurança e LGPD

- 🔐 Criptografia de dados sensíveis
- ✅ Consentimento explícito LGPD
- 🗑️ Exclusão integral de dados
- 📝 Logs de auditoria

## 📞 Suporte

- 📧 Email: suporte@duolingojuridico.com.br
- 💬 Chat: Disponível no app
- 🐛 Issues: GitHub Issues

## 📜 Licença

Copyright (c) 2024 Duolingo Jurídico. Todos os direitos reservados. 