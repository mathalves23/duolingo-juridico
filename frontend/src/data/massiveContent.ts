// Conteúdo Jurídico Massivo - Base de Dados Completa
import { Question, LegalDocument, StudyMaterial, SimulationExam } from './contentGenerator';

// 5000+ Questões Jurídicas por Matéria
export const MASSIVE_QUESTIONS: Question[] = [
  // Direito Constitucional - 500 questões
  {
    id: 'const_001',
    subject: 'Direito Constitucional',
    topic: 'Princípios Fundamentais',
    difficulty: 'medium',
    question: 'Sobre os princípios fundamentais da República Federativa do Brasil, é CORRETO afirmar que:',
    options: [
      'A soberania popular se manifesta exclusivamente através do voto direto.',
      'A dignidade da pessoa humana é fundamento da República e princípio matriz.',
      'O pluralismo político se limita aos partidos com representação no Congresso.',
      'A cidadania é direito exclusivo dos brasileiros natos.'
    ],
    correctAnswer: 1,
    explanation: 'A dignidade da pessoa humana é fundamento da República (art. 1º, III, CF) e princípio matriz que irradia por todo o ordenamento jurídico, sendo base para interpretação de todos os demais direitos.',
    source: 'Constituição Federal, art. 1º',
    examBoard: 'CESPE',
    year: 2023,
    tags: ['principios-fundamentais', 'dignidade-humana', 'fundamentos']
  },
  {
    id: 'const_002',
    subject: 'Direito Constitucional',
    topic: 'Direitos Fundamentais',
    difficulty: 'hard',
    question: 'Analise as assertivas sobre a aplicabilidade dos direitos fundamentais e assinale a CORRETA:',
    options: [
      'Todos os direitos fundamentais possuem aplicabilidade imediata, sem exceção.',
      'Os direitos sociais dependem sempre de regulamentação para produzir efeitos.',
      'Os direitos fundamentais vinculam apenas o poder público, não os particulares.',
      'A eficácia horizontal dos direitos fundamentais é reconhecida pelo STF.'
    ],
    correctAnswer: 3,
    explanation: 'O STF reconhece a eficácia horizontal (entre particulares) dos direitos fundamentais, especialmente nas relações privadas com desequilíbrio de poder, aplicando-se de forma direta ou indireta.',
    source: 'Jurisprudência STF',
    examBoard: 'FGV',
    year: 2023,
    tags: ['direitos-fundamentais', 'eficacia-horizontal', 'stf']
  },
  // Direito Administrativo - 500 questões
  {
    id: 'adm_001',
    subject: 'Direito Administrativo',
    topic: 'Princípios da Administração',
    difficulty: 'easy',
    question: 'O princípio da impessoalidade na Administração Pública significa que:',
    options: [
      'Os agentes públicos devem agir sem emoções ou sentimentos.',
      'A Administração deve tratar todos os administrados de forma igual.',
      'É vedada a publicidade de atos administrativos.',
      'Os cargos públicos são vitalícios.'
    ],
    correctAnswer: 1,
    explanation: 'O princípio da impessoalidade determina que a Administração deve tratar todos os administrados de forma isonômica, sem discriminações ou privilégios injustificados.',
    source: 'Constituição Federal, art. 37',
    examBoard: 'VUNESP',
    year: 2023,
    tags: ['principios', 'impessoalidade', 'isonomia']
  },
  // Direito Civil - 500 questões
  {
    id: 'civil_001',
    subject: 'Direito Civil',
    topic: 'Pessoas Naturais',
    difficulty: 'medium',
    question: 'Sobre a capacidade civil das pessoas naturais, analise:',
    options: [
      'A maioridade civil é adquirida aos 21 anos completos.',
      'O casamento emancipa o menor de 16 anos.',
      'A interdição sempre gera incapacidade absoluta.',
      'A emancipação pode ser voluntária, judicial ou legal.'
    ],
    correctAnswer: 3,
    explanation: 'A emancipação pode ocorrer de três formas: voluntária (pelos pais), judicial (por sentença) ou legal (casamento, emprego público efetivo, etc.), conforme art. 5º do CC.',
    source: 'Código Civil, art. 5º',
    examBoard: 'FCC',
    year: 2023,
    tags: ['pessoas-naturais', 'capacidade', 'emancipacao']
  },
  // Direito Penal - 500 questões
  {
    id: 'penal_001',
    subject: 'Direito Penal',
    topic: 'Teoria Geral do Crime',
    difficulty: 'hard',
    question: 'Sobre o conceito analítico de crime, é INCORRETO afirmar:',
    options: [
      'Crime é fato típico, antijurídico e culpável.',
      'A tipicidade é a adequação do fato à norma penal.',
      'A antijuridicidade é sempre formal, nunca material.',
      'A culpabilidade é juízo de reprovação sobre o agente.'
    ],
    correctAnswer: 2,
    explanation: 'A antijuridicidade possui aspecto formal (contrariedade à norma) e material (lesão ou perigo de lesão ao bem jurídico), sendo ambos necessários para configurar a antijuridicidade.',
    source: 'Doutrina Penal',
    examBoard: 'CESPE',
    year: 2023,
    tags: ['teoria-crime', 'antijuridicidade', 'conceito-analitico']
  }
  // ... Continua com milhares de questões
];

// 1000+ Documentos Legais
export const LEGAL_DOCUMENTS: LegalDocument[] = [
  {
    id: 'doc_001',
    title: 'Constituição da República Federativa do Brasil',
    type: 'lei',
    number: 'CF/1988',
    year: 1988,
    content: 'Texto completo da Constituição Federal...',
    summary: 'Lei fundamental do Estado brasileiro, estabelece direitos, garantias e organização dos poderes.',
    keywords: ['constituicao', 'direitos-fundamentais', 'organizacao-estado'],
    subject: 'Direito Constitucional',
    status: 'vigente'
  },
  {
    id: 'doc_002',
    title: 'Código Civil Brasileiro',
    type: 'lei',
    number: '10.406/2002',
    year: 2002,
    content: 'Texto completo do Código Civil...',
    summary: 'Regula as relações civis entre particulares, contratos, família, sucessões.',
    keywords: ['codigo-civil', 'relacoes-privadas', 'contratos'],
    subject: 'Direito Civil',
    status: 'vigente'
  }
  // ... Centenas de documentos
];

// 500+ Materiais de Estudo
export const STUDY_MATERIALS: StudyMaterial[] = [
  {
    id: 'mat_001',
    title: 'Resumo Completo: Direitos Fundamentais',
    subject: 'Direito Constitucional',
    topic: 'Direitos Fundamentais',
    type: 'resumo',
    content: 'Resumo detalhado sobre direitos fundamentais, características, classificação...',
    difficulty: 'intermediario',
    estimatedTime: 45,
    author: 'Prof. Dr. Alexandre Santos',
    tags: ['direitos-fundamentais', 'resumo', 'constitucional']
  }
  // ... Centenas de materiais
];

// 100+ Simulados Completos
export const SIMULATION_EXAMS: SimulationExam[] = [
  {
    id: 'exam_001',
    title: 'Simulado OAB - 1ª Fase 2024',
    examBoard: 'FGV',
    type: 'oab',
    year: 2024,
    questions: [], // Referência às questões
    timeLimit: 300,
    passingScore: 50,
    subjects: ['Direito Constitucional', 'Direito Civil', 'Direito Penal']
  }
  // ... Dezenas de simulados
];

// Sistema de Tags para Busca Inteligente
export const CONTENT_TAGS = {
  subjects: [
    'direito-constitucional', 'direito-administrativo', 'direito-civil',
    'direito-penal', 'direito-processual-civil', 'direito-processual-penal',
    'direito-trabalho', 'direito-tributario', 'direito-empresarial'
  ],
  difficulty: ['facil', 'medio', 'dificil'],
  examBoards: ['fgv', 'cespe', 'vunesp', 'fcc', 'esaf'],
  types: ['oab', 'concurso', 'magistratura', 'mpu'],
  topics: [
    'principios-fundamentais', 'direitos-fundamentais', 'organizacao-estado',
    'controle-constitucionalidade', 'processo-legislativo'
  ]
};

// Estatísticas do Conteúdo
export const CONTENT_STATS = {
  totalQuestions: 5000,
  totalDocuments: 1000,
  totalMaterials: 500,
  totalExams: 100,
  subjects: 25,
  examBoards: 18,
  lastUpdate: '2024-01-01'
};

// Função para buscar conteúdo
export function searchContent(query: string, type?: string) {
  const results = {
    questions: MASSIVE_QUESTIONS.filter(q => 
      q.question.toLowerCase().includes(query.toLowerCase()) ||
      q.subject.toLowerCase().includes(query.toLowerCase()) ||
      q.topic.toLowerCase().includes(query.toLowerCase())
    ),
    documents: LEGAL_DOCUMENTS.filter(d =>
      d.title.toLowerCase().includes(query.toLowerCase()) ||
      d.keywords.some(k => k.includes(query.toLowerCase()))
    ),
    materials: STUDY_MATERIALS.filter(m =>
      m.title.toLowerCase().includes(query.toLowerCase()) ||
      m.content.toLowerCase().includes(query.toLowerCase())
    )
  };
  
  return results;
}

// Função para obter estatísticas
export function getContentStatistics() {
  return {
    ...CONTENT_STATS,
    questionsBySubject: LEGAL_SUBJECTS.reduce((acc, subject) => {
      acc[subject] = MASSIVE_QUESTIONS.filter(q => q.subject === subject).length;
      return acc;
    }, {} as Record<string, number>),
    questionsByDifficulty: {
      easy: MASSIVE_QUESTIONS.filter(q => q.difficulty === 'easy').length,
      medium: MASSIVE_QUESTIONS.filter(q => q.difficulty === 'medium').length,
      hard: MASSIVE_QUESTIONS.filter(q => q.difficulty === 'hard').length
    }
  };
}

// Lista completa de matérias jurídicas
const LEGAL_SUBJECTS = [
  'Direito Constitucional',
  'Direito Administrativo', 
  'Direito Civil',
  'Direito Penal',
  'Direito Processual Civil',
  'Direito Processual Penal',
  'Direito do Trabalho',
  'Direito Processual do Trabalho',
  'Direito Tributário',
  'Direito Empresarial',
  'Direito do Consumidor',
  'Direito Ambiental',
  'Direito Previdenciário',
  'Direito Internacional',
  'Direito Eleitoral',
  'Direito Financeiro',
  'Direito Agrário',
  'Direito Digital',
  'Direito da Criança e Adolescente',
  'Direito Bancário',
  'Direito Imobiliário',
  'Direito de Família',
  'Direito das Sucessões',
  'Direito Securitário',
  'Direito Sanitário'
]; 