# 🗄️ Como Alimentar o Banco de Dados - Duolingo Jurídico

## 📋 Visão Geral

Este guia mostra como popular a aplicação com **milhares de questões, documentos, materiais e simulados jurídicos** de forma automatizada e inteligente.

## 🎯 Objetivo

Transformar a aplicação em uma **base de dados jurídica completa** com:
- **5.000+ questões** de todas as matérias jurídicas
- **1.000+ documentos legais** (leis, decretos, súmulas)
- **500+ materiais de estudo** (resumos, esquemas, videoaulas)
- **100+ simulados completos** (OAB, concursos, magistratura)

## 🏗️ Arquitetura do Sistema

### 1. Gerador de Conteúdo (`contentGenerator.ts`)
```typescript
// Gera conteúdo automaticamente
ContentGenerator.generateQuestions('Direito Civil', 500)
ContentGenerator.generateLegalDocuments(100)
ContentGenerator.generateStudyMaterials(50)
ContentGenerator.generateSimulationExams(10)
```

### 2. Base de Dados Massiva (`massiveContent.ts`)
```typescript
// Conteúdo pré-gerado para uso imediato
MASSIVE_QUESTIONS: 5000+ questões
LEGAL_DOCUMENTS: 1000+ documentos
STUDY_MATERIALS: 500+ materiais
SIMULATION_EXAMS: 100+ simulados
```

### 3. Script de População (`populateDatabase.ts`)
```typescript
// Popula o banco automaticamente
populateDatabase() // Tudo de uma vez
populateSubjectContent('Direito Penal', 500) // Por matéria
```

## 🚀 Métodos de População

### Método 1: População Automática Completa

```bash
# 1. Executar script de população
cd frontend
npm run populate-db

# Ou via código
import { populateDatabase } from './scripts/populateDatabase';
await populateDatabase();
```

**Resultado:**
- ✅ 5.000+ questões geradas automaticamente
- ✅ 1.000+ documentos legais
- ✅ 500+ materiais de estudo
- ✅ 100+ simulados completos
- ✅ Índices de busca criados
- ✅ Estatísticas atualizadas

### Método 2: População por Matéria

```typescript
// Popular matéria específica
await populateSubjectContent('Direito Constitucional', 1000);
await populateSubjectContent('Direito Civil', 800);
await populateSubjectContent('Direito Penal', 600);
```

### Método 3: Interface Web (Recomendado)

1. Acesse `/content-manager` na aplicação
2. Use a aba "Popular Dados"
3. Escolha entre:
   - **População Massiva**: Tudo automaticamente
   - **Por Matéria**: Específico por disciplina
   - **Preview**: Visualizar antes de inserir

## 📚 Estrutura do Conteúdo

### 🎯 Questões Jurídicas (5.000+)

#### Por Matéria:
- **Direito Constitucional**: 500 questões
- **Direito Administrativo**: 500 questões
- **Direito Civil**: 500 questões
- **Direito Penal**: 500 questões
- **Direito Processual Civil**: 400 questões
- **Direito Processual Penal**: 400 questões
- **Direito do Trabalho**: 400 questões
- **Direito Tributário**: 400 questões
- **Direito Empresarial**: 300 questões
- **Direito do Consumidor**: 300 questões
- **Direito Ambiental**: 200 questões
- **Direito Previdenciário**: 200 questões
- **Outras matérias**: 1.400 questões

#### Por Dificuldade:
- **Fácil**: 2.000 questões (40%)
- **Médio**: 2.500 questões (50%)
- **Difícil**: 500 questões (10%)

#### Por Banca:
- **CESPE/CEBRASPE**: 1.500 questões
- **FGV**: 1.200 questões
- **VUNESP**: 800 questões
- **FCC**: 700 questões
- **ESAF**: 500 questões
- **Outras**: 300 questões

### 📋 Documentos Legais (1.000+)

#### Por Tipo:
- **Leis**: 400 documentos
- **Decretos**: 200 documentos
- **Portarias**: 150 documentos
- **Resoluções**: 100 documentos
- **Súmulas**: 100 documentos
- **Jurisprudência**: 50 documentos

#### Por Matéria:
- **Constitucional**: 200 documentos
- **Administrativo**: 150 documentos
- **Civil**: 150 documentos
- **Penal**: 100 documentos
- **Trabalhista**: 100 documentos
- **Tributário**: 100 documentos
- **Outras**: 200 documentos

### 📖 Materiais de Estudo (500+)

#### Por Tipo:
- **Resumos**: 150 materiais
- **Esquemas**: 100 materiais
- **Mapas Mentais**: 80 materiais
- **Artigos**: 70 materiais
- **Videoaulas**: 60 materiais
- **Podcasts**: 40 materiais

#### Por Dificuldade:
- **Básico**: 200 materiais
- **Intermediário**: 200 materiais
- **Avançado**: 100 materiais

### 🎯 Simulados (100+)

#### Por Tipo:
- **OAB 1ª Fase**: 30 simulados
- **Concursos Públicos**: 25 simulados
- **Magistratura**: 15 simulados
- **MPU**: 15 simulados
- **Defensoria**: 15 simulados

#### Por Banca:
- **FGV**: 25 simulados
- **CESPE**: 20 simulados
- **VUNESP**: 15 simulados
- **FCC**: 15 simulados
- **Outras**: 25 simulados

## 🔧 Configuração Técnica

### 1. Variáveis de Ambiente

```env
# .env.local
REACT_APP_API_URL=http://localhost:3001/api
REACT_APP_DB_BATCH_SIZE=50
REACT_APP_DB_DELAY=1000
```

### 2. Scripts NPM

```json
// package.json
{
  "scripts": {
    "populate-db": "ts-node src/scripts/populateDatabase.ts",
    "populate-subject": "ts-node src/scripts/populateSubject.ts",
    "clear-db": "ts-node src/scripts/clearDatabase.ts",
    "backup-db": "ts-node src/scripts/backupDatabase.ts"
  }
}
```

### 3. Configuração do Banco

```typescript
// Configurações otimizadas
const DB_CONFIG = {
  batchSize: 50, // Registros por lote
  delayBetweenBatches: 1000, // 1s entre lotes
  maxRetries: 3, // Tentativas em caso de erro
  timeout: 30000 // Timeout de 30s
};
```

## 📊 Monitoramento e Estatísticas

### Dashboard de Conteúdo
```typescript
// Estatísticas em tempo real
{
  totalQuestions: 5000,
  totalDocuments: 1000,
  totalMaterials: 500,
  totalExams: 100,
  questionsBySubject: {...},
  questionsByDifficulty: {...},
  lastUpdated: "2024-01-01T00:00:00Z"
}
```

### Logs do Sistema
```bash
📚 Gerando questões para Direito Civil...
✅ Lote 1/10 inserido com sucesso
📋 Gerando documentos legais...
🎯 Gerando simulados...
✅ População concluída! 5000 questões inseridas
```

## 🎮 Interface de Gerenciamento

### Painel Administrativo (`/content-manager`)

#### Aba "Visão Geral"
- 📊 Estatísticas gerais
- 📈 Gráficos por matéria
- 🕒 Última atualização
- 📱 Status do sistema

#### Aba "Popular Dados"
- 🚀 População massiva (tudo)
- 📚 Por matéria específica
- 👁️ Preview das questões
- ⚙️ Configurações avançadas

#### Aba "Gerenciar"
- 💾 Backup do banco
- 📥 Restaurar backup
- 🗑️ Limpar dados
- 📋 Logs do sistema

## 🔍 Sistema de Busca Inteligente

### Índices Criados Automaticamente
```typescript
// Índices para busca rápida
{
  questions: ['subject', 'topic', 'difficulty', 'tags'],
  documents: ['title', 'keywords', 'subject', 'type'],
  materials: ['title', 'subject', 'topic', 'tags'],
  exams: ['title', 'examBoard', 'type', 'subjects']
}
```

### Busca Semântica
```typescript
// Busca inteligente
searchContent('direitos fundamentais')
// Retorna questões, documentos e materiais relacionados
```

## 🚀 Execução Passo a Passo

### 1. Preparação
```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
```

### 2. População Inicial
```bash
# Método 1: Script automático
npm run populate-db

# Método 2: Interface web
npm start
# Acesse http://localhost:3000/content-manager
```

### 3. Verificação
```bash
# Verificar estatísticas
curl http://localhost:3001/api/stats

# Ou via interface
# Acesse /content-manager > Visão Geral
```

### 4. Backup (Recomendado)
```bash
# Criar backup após população
npm run backup-db

# Ou via interface
# Acesse /content-manager > Gerenciar > Fazer Backup
```

## ⚡ Otimizações de Performance

### 1. Inserção em Lotes
- ✅ 50 registros por lote
- ✅ 1 segundo entre lotes
- ✅ Retry automático em caso de erro

### 2. Índices de Busca
- ✅ Índices compostos por matéria + dificuldade
- ✅ Índices de texto para busca semântica
- ✅ Índices por tags para filtros rápidos

### 3. Cache Inteligente
- ✅ Cache de questões frequentes
- ✅ Cache de estatísticas
- ✅ Invalidação automática

## 🔧 Customização Avançada

### 1. Adicionar Nova Matéria
```typescript
// 1. Adicionar em LEGAL_SUBJECTS
const LEGAL_SUBJECTS = [
  ...existing,
  'Nova Matéria Jurídica'
];

// 2. Definir tópicos específicos
const NOVA_MATERIA_TOPICS = [
  'Tópico 1',
  'Tópico 2',
  'Tópico 3'
];

// 3. Gerar conteúdo
const questions = ContentGenerator.generateQuestions('Nova Matéria Jurídica', 500);
```

### 2. Personalizar Geração
```typescript
// Personalizar dificuldade
const customDifficulty = {
  easy: 0.3,    // 30% fácil
  medium: 0.5,  // 50% médio
  hard: 0.2     // 20% difícil
};

// Personalizar bancas
const customExamBoards = ['CESPE', 'FGV', 'VUNESP'];
```

### 3. Integração com APIs Externas
```typescript
// Buscar questões de APIs externas
async function importFromExternalAPI() {
  const response = await fetch('https://api.questoes-juridicas.com/questions');
  const externalQuestions = await response.json();
  
  // Converter para formato interno
  const questions = externalQuestions.map(convertToInternalFormat);
  
  // Inserir no banco
  await insertInBatches(questions, '/questions/bulk');
}
```

## 📈 Resultados Esperados

### Após População Completa:
- ✅ **5.000+ questões** de alta qualidade
- ✅ **25+ matérias** jurídicas cobertas
- ✅ **18+ bancas** representadas
- ✅ **1.000+ documentos** legais atualizados
- ✅ **500+ materiais** de estudo diversos
- ✅ **100+ simulados** completos
- ✅ **Sistema de busca** otimizado
- ✅ **Analytics** detalhados

### Impacto na Aplicação:
- 🚀 **Experiência rica** para usuários
- 📊 **Dados suficientes** para IA/ML
- 🎯 **Preparação completa** para concursos
- 📚 **Base sólida** para estudos
- 🏆 **Diferencial competitivo** no mercado

## 🔮 Próximos Passos

### 1. Expansão do Conteúdo
- [ ] Adicionar mais 5.000 questões
- [ ] Incluir questões de 2024
- [ ] Integrar com APIs oficiais
- [ ] Adicionar jurisprudência recente

### 2. Melhorias na IA
- [ ] IA para geração de questões
- [ ] Análise de padrões de erro
- [ ] Recomendações personalizadas
- [ ] Correção automática

### 3. Funcionalidades Avançadas
- [ ] Simulados adaptativos
- [ ] Ranking nacional
- [ ] Certificações oficiais
- [ ] Integração com universidades

---

**🎯 Objetivo Final:** Criar a **maior e mais completa base de dados jurídica** do Brasil, com conteúdo de qualidade profissional para revolucionar o ensino jurídico digital.

**📊 Meta:** 10.000+ questões, 2.000+ documentos, 1.000+ materiais até o final de 2024. 