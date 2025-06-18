// Sistema de Geração Massiva de Conteúdo Jurídico
export interface Question {
  id: string;
  subject: string;
  topic: string;
  difficulty: 'easy' | 'medium' | 'hard';
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
  source: string;
  examBoard?: string;
  year?: number;
  tags: string[];
}

export interface LegalDocument {
  id: string;
  title: string;
  type: 'lei' | 'decreto' | 'portaria' | 'resolucao' | 'instrucao_normativa' | 'sumula' | 'jurisprudencia';
  number: string;
  year: number;
  content: string;
  summary: string;
  keywords: string[];
  subject: string;
  status: 'vigente' | 'revogado' | 'suspenso';
}

export interface StudyMaterial {
  id: string;
  title: string;
  subject: string;
  topic: string;
  type: 'artigo' | 'resumo' | 'esquema' | 'mapa_mental' | 'video' | 'podcast';
  content: string;
  difficulty: 'basico' | 'intermediario' | 'avancado';
  estimatedTime: number; // em minutos
  author: string;
  tags: string[];
}

export interface SimulationExam {
  id: string;
  title: string;
  examBoard: string;
  type: 'oab' | 'concurso' | 'magistratura' | 'mpu' | 'defensoria';
  year: number;
  questions: Question[];
  timeLimit: number; // em minutos
  passingScore: number;
  subjects: string[];
}

// Dados base para geração de conteúdo
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

const CONSTITUTIONAL_TOPICS = [
  'Princípios Fundamentais',
  'Direitos e Garantias Fundamentais',
  'Direitos Sociais',
  'Direitos de Nacionalidade',
  'Direitos Políticos',
  'Organização do Estado',
  'Organização dos Poderes',
  'Poder Executivo',
  'Poder Legislativo',
  'Poder Judiciário',
  'Funções Essenciais à Justiça',
  'Defesa do Estado',
  'Tributação e Orçamento',
  'Ordem Econômica e Financeira',
  'Ordem Social',
  'Controle de Constitucionalidade',
  'Ações Constitucionais',
  'Emendas Constitucionais'
];

const ADMINISTRATIVE_TOPICS = [
  'Princípios da Administração Pública',
  'Organização Administrativa',
  'Atos Administrativos',
  'Poderes Administrativos',
  'Licitações e Contratos',
  'Serviços Públicos',
  'Servidores Públicos',
  'Responsabilidade Civil do Estado',
  'Processo Administrativo',
  'Controle da Administração',
  'Improbidade Administrativa',
  'Agências Reguladoras',
  'Parcerias Público-Privadas',
  'Concessões e Permissões'
];

const CIVIL_TOPICS = [
  'Pessoas Naturais',
  'Pessoas Jurídicas',
  'Bens',
  'Fatos Jurídicos',
  'Negócios Jurídicos',
  'Prescrição e Decadência',
  'Obrigações',
  'Contratos em Geral',
  'Contratos Específicos',
  'Responsabilidade Civil',
  'Direitos Reais',
  'Posse',
  'Propriedade',
  'Direito de Família',
  'Casamento',
  'União Estável',
  'Filiação',
  'Adoção',
  'Tutela e Curatela',
  'Sucessões',
  'Inventário e Partilha'
];

const CRIMINAL_TOPICS = [
  'Aplicação da Lei Penal',
  'Crime',
  'Tipicidade',
  'Antijuridicidade',
  'Culpabilidade',
  'Tentativa',
  'Concurso de Pessoas',
  'Concurso de Crimes',
  'Penas',
  'Medidas de Segurança',
  'Crimes contra a Vida',
  'Crimes contra a Honra',
  'Crimes contra o Patrimônio',
  'Crimes contra a Liberdade',
  'Crimes contra a Administração',
  'Lei de Drogas',
  'Crimes Hediondos',
  'Violência Doméstica'
];

const EXAM_BOARDS = [
  'FGV', 'CESPE/CEBRASPE', 'VUNESP', 'FCC', 'ESAF', 'CESGRANRIO',
  'AOCP', 'FUNCAB', 'IBFC', 'INSTITUTO AOCP', 'QUADRIX', 'CONSULPLAN',
  'IDECAN', 'IADES', 'FUNDEP', 'COPS-UEL', 'UFPR', 'FAURGS'
];

// Gerador de questões
export class ContentGenerator {
  private static questionId = 1;
  private static documentId = 1;
  private static materialId = 1;
  private static examId = 1;

  // Gera questões massivas por matéria
  static generateQuestions(subject: string, count: number = 100): Question[] {
    const questions: Question[] = [];
    const topics = this.getTopicsBySubject(subject);
    
    for (let i = 0; i < count; i++) {
      const topic = topics[Math.floor(Math.random() * topics.length)];
      const difficulty = this.getRandomDifficulty();
      const examBoard = EXAM_BOARDS[Math.floor(Math.random() * EXAM_BOARDS.length)];
      
      questions.push({
        id: `q_${this.questionId++}`,
        subject,
        topic,
        difficulty,
        question: this.generateQuestionText(subject, topic, difficulty),
        options: this.generateOptions(subject, topic),
        correctAnswer: Math.floor(Math.random() * 4),
        explanation: this.generateExplanation(subject, topic),
        source: this.generateSource(subject),
        examBoard,
        year: 2020 + Math.floor(Math.random() * 4),
        tags: this.generateTags(subject, topic)
      });
    }
    
    return questions;
  }

  // Gera documentos legais
  static generateLegalDocuments(count: number = 500): LegalDocument[] {
    const documents: LegalDocument[] = [];
    const types: LegalDocument['type'][] = ['lei', 'decreto', 'portaria', 'resolucao', 'instrucao_normativa', 'sumula', 'jurisprudencia'];
    
    for (let i = 0; i < count; i++) {
      const type = types[Math.floor(Math.random() * types.length)];
      const subject = LEGAL_SUBJECTS[Math.floor(Math.random() * LEGAL_SUBJECTS.length)];
      
      documents.push({
        id: `doc_${this.documentId++}`,
        title: this.generateDocumentTitle(type, subject),
        type,
        number: this.generateDocumentNumber(type),
        year: 1988 + Math.floor(Math.random() * 36),
        content: this.generateDocumentContent(type, subject),
        summary: this.generateDocumentSummary(type, subject),
        keywords: this.generateDocumentKeywords(subject),
        subject,
        status: Math.random() > 0.1 ? 'vigente' : 'revogado'
      });
    }
    
    return documents;
  }

  // Gera material de estudo
  static generateStudyMaterials(count: number = 200): StudyMaterial[] {
    const materials: StudyMaterial[] = [];
    const types: StudyMaterial['type'][] = ['artigo', 'resumo', 'esquema', 'mapa_mental', 'video', 'podcast'];
    
    for (let i = 0; i < count; i++) {
      const subject = LEGAL_SUBJECTS[Math.floor(Math.random() * LEGAL_SUBJECTS.length)];
      const topics = this.getTopicsBySubject(subject);
      const topic = topics[Math.floor(Math.random() * topics.length)];
      const type = types[Math.floor(Math.random() * types.length)];
      
      materials.push({
        id: `mat_${this.materialId++}`,
        title: this.generateMaterialTitle(subject, topic, type),
        subject,
        topic,
        type,
        content: this.generateMaterialContent(subject, topic, type),
        difficulty: this.getRandomDifficultyLevel(),
        estimatedTime: this.getEstimatedTime(type),
        author: this.generateAuthor(),
        tags: this.generateTags(subject, topic)
      });
    }
    
    return materials;
  }

  // Gera simulados
  static generateSimulationExams(count: number = 50): SimulationExam[] {
    const exams: SimulationExam[] = [];
    const types: SimulationExam['type'][] = ['oab', 'concurso', 'magistratura', 'mpu', 'defensoria'];
    
    for (let i = 0; i < count; i++) {
      const type = types[Math.floor(Math.random() * types.length)];
      const examBoard = EXAM_BOARDS[Math.floor(Math.random() * EXAM_BOARDS.length)];
      const subjects = this.getRandomSubjects(3, 8);
      
      // Gera questões para o simulado
      const questions: Question[] = [];
      const questionsPerSubject = Math.floor(80 / subjects.length);
      
      subjects.forEach(subject => {
        questions.push(...this.generateQuestions(subject, questionsPerSubject));
      });
      
      exams.push({
        id: `exam_${this.examId++}`,
        title: this.generateExamTitle(type, examBoard),
        examBoard,
        type,
        year: 2020 + Math.floor(Math.random() * 4),
        questions,
        timeLimit: this.getExamTimeLimit(type),
        passingScore: this.getPassingScore(type),
        subjects
      });
    }
    
    return exams;
  }

  // Métodos auxiliares
  private static getTopicsBySubject(subject: string): string[] {
    switch (subject) {
      case 'Direito Constitucional':
        return CONSTITUTIONAL_TOPICS;
      case 'Direito Administrativo':
        return ADMINISTRATIVE_TOPICS;
      case 'Direito Civil':
        return CIVIL_TOPICS;
      case 'Direito Penal':
        return CRIMINAL_TOPICS;
      default:
        return ['Tópico Geral 1', 'Tópico Geral 2', 'Tópico Geral 3'];
    }
  }

  private static getRandomDifficulty(): 'easy' | 'medium' | 'hard' {
    const rand = Math.random();
    if (rand < 0.4) return 'easy';
    if (rand < 0.8) return 'medium';
    return 'hard';
  }

  private static getRandomDifficultyLevel(): 'basico' | 'intermediario' | 'avancado' {
    const rand = Math.random();
    if (rand < 0.4) return 'basico';
    if (rand < 0.8) return 'intermediario';
    return 'avancado';
  }

  private static generateQuestionText(subject: string, topic: string, difficulty: string): string {
    const templates = [
      `Sobre ${topic} em ${subject}, ${difficulty === 'easy' ? 'é correto afirmar que' : 'analise as assertivas e marque a alternativa correta'}:`,
      `No contexto de ${topic}, ${difficulty === 'hard' ? 'considerando a jurisprudência consolidada' : 'segundo a doutrina majoritária'}:`,
      `Acerca de ${topic} no âmbito do ${subject}, ${difficulty === 'medium' ? 'julgue os itens' : 'assinale a alternativa correta'}:`,
      `${difficulty === 'hard' ? 'Em uma situação hipotética envolvendo' : 'Quanto a'} ${topic}:`
    ];
    
    return templates[Math.floor(Math.random() * templates.length)];
  }

  private static generateOptions(subject: string, topic: string): string[] {
    const options = [
      `A aplicação do princípio da ${topic.toLowerCase()} deve ser interpretada restritivamente.`,
      `O entendimento doutrinário consolidado sobre ${topic.toLowerCase()} estabelece critérios objetivos.`,
      `A jurisprudência do STF pacificou o tema relacionado a ${topic.toLowerCase()}.`,
      `As normas constitucionais sobre ${topic.toLowerCase()} possuem aplicabilidade imediata.`
    ];
    
    return options;
  }

  private static generateExplanation(subject: string, topic: string): string {
    return `A resposta correta baseia-se no entendimento consolidado sobre ${topic} no âmbito do ${subject}. 
    A doutrina majoritária e a jurisprudência dos tribunais superiores convergem neste sentido, 
    considerando os princípios fundamentais e a aplicação prática das normas vigentes.`;
  }

  private static generateSource(subject: string): string {
    const sources = [
      'Constituição Federal de 1988',
      'Código Civil',
      'Código Penal',
      'CLT',
      'CPC',
      'CPP',
      'CTN',
      'Lei 8.078/90 (CDC)',
      'Lei 8.429/92 (LIA)',
      'Lei 9.784/99'
    ];
    
    return sources[Math.floor(Math.random() * sources.length)];
  }

  private static generateTags(subject: string, topic: string): string[] {
    const baseTags = [subject.toLowerCase().replace(/\s+/g, '-')];
    const topicTags = topic.toLowerCase().replace(/\s+/g, '-').split('-');
    const additionalTags = ['concurso', 'oab', 'magistratura', 'mpu'];
    
    return [...baseTags, ...topicTags.slice(0, 2), ...additionalTags.slice(0, 2)];
  }

  private static generateDocumentTitle(type: string, subject: string): string {
    const titles = {
      lei: `Lei sobre ${subject}`,
      decreto: `Decreto regulamentando ${subject}`,
      portaria: `Portaria disciplinando ${subject}`,
      resolucao: `Resolução sobre ${subject}`,
      instrucao_normativa: `Instrução Normativa - ${subject}`,
      sumula: `Súmula sobre ${subject}`,
      jurisprudencia: `Jurisprudência consolidada - ${subject}`
    };
    
    return titles[type as keyof typeof titles] || `Documento sobre ${subject}`;
  }

  private static generateDocumentNumber(type: string): string {
    const year = 1988 + Math.floor(Math.random() * 36);
    const number = Math.floor(Math.random() * 9999) + 1;
    return `${number}/${year}`;
  }

  private static generateDocumentContent(type: string, subject: string): string {
    return `Conteúdo completo do documento sobre ${subject}. 
    Este ${type} estabelece as diretrizes e procedimentos aplicáveis, 
    considerando a legislação vigente e os princípios constitucionais.
    
    Art. 1º - Estabelece as normas gerais sobre ${subject}.
    Art. 2º - Define os procedimentos aplicáveis.
    Art. 3º - Dispõe sobre as penalidades.`;
  }

  private static generateDocumentSummary(type: string, subject: string): string {
    return `Resumo executivo do ${type} sobre ${subject}, destacando os principais pontos e alterações introduzidas.`;
  }

  private static generateDocumentKeywords(subject: string): string[] {
    return [
      subject.toLowerCase(),
      'legislação',
      'normas',
      'procedimentos',
      'direitos',
      'deveres',
      'aplicação'
    ];
  }

  private static generateMaterialTitle(subject: string, topic: string, type: string): string {
    const titles = {
      artigo: `Artigo Científico: ${topic} em ${subject}`,
      resumo: `Resumo Executivo: ${topic}`,
      esquema: `Esquema Didático: ${topic}`,
      mapa_mental: `Mapa Mental: ${topic}`,
      video: `Videoaula: ${topic}`,
      podcast: `Podcast Jurídico: ${topic}`
    };
    
    return titles[type as keyof typeof titles] || `Material sobre ${topic}`;
  }

  private static generateMaterialContent(subject: string, topic: string, type: string): string {
    return `Conteúdo detalhado sobre ${topic} no contexto de ${subject}.
    Este material de ${type} aborda os aspectos fundamentais, 
    jurisprudência relevante e aplicação prática.`;
  }

  private static getEstimatedTime(type: string): number {
    const times = {
      artigo: 30,
      resumo: 15,
      esquema: 10,
      mapa_mental: 20,
      video: 45,
      podcast: 60
    };
    
    return times[type as keyof typeof times] || 30;
  }

  private static generateAuthor(): string {
    const authors = [
      'Prof. Dr. João Silva',
      'Dra. Maria Santos',
      'Prof. Carlos Oliveira',
      'Dra. Ana Costa',
      'Prof. Pedro Almeida',
      'Dra. Laura Ferreira'
    ];
    
    return authors[Math.floor(Math.random() * authors.length)];
  }

  private static getRandomSubjects(min: number, max: number): string[] {
    const count = min + Math.floor(Math.random() * (max - min + 1));
    const shuffled = [...LEGAL_SUBJECTS].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  }

  private static generateExamTitle(type: string, examBoard: string): string {
    const titles = {
      oab: `Exame de Ordem - ${examBoard}`,
      concurso: `Concurso Público - ${examBoard}`,
      magistratura: `Concurso para Magistratura - ${examBoard}`,
      mpu: `Concurso MPU - ${examBoard}`,
      defensoria: `Concurso Defensoria - ${examBoard}`
    };
    
    return titles[type as keyof typeof titles] || `Simulado ${examBoard}`;
  }

  private static getExamTimeLimit(type: string): number {
    const times = {
      oab: 300,
      concurso: 240,
      magistratura: 360,
      mpu: 300,
      defensoria: 300
    };
    
    return times[type as keyof typeof times] || 240;
  }

  private static getPassingScore(type: string): number {
    const scores = {
      oab: 50,
      concurso: 60,
      magistratura: 70,
      mpu: 60,
      defensoria: 60
    };
    
    return scores[type as keyof typeof scores] || 60;
  }
}

// Função para gerar todo o conteúdo de uma vez
export function generateAllContent() {
  console.log('🚀 Iniciando geração massiva de conteúdo jurídico...');
  
  const allQuestions: Question[] = [];
  const allDocuments: LegalDocument[] = [];
  const allMaterials: StudyMaterial[] = [];
  const allExams: SimulationExam[] = [];
  
  // Gera questões para cada matéria
  LEGAL_SUBJECTS.forEach(subject => {
    console.log(`📚 Gerando questões para ${subject}...`);
    allQuestions.push(...ContentGenerator.generateQuestions(subject, 200));
  });
  
  // Gera documentos legais
  console.log('📋 Gerando documentos legais...');
  allDocuments.push(...ContentGenerator.generateLegalDocuments(1000));
  
  // Gera materiais de estudo
  console.log('📖 Gerando materiais de estudo...');
  allMaterials.push(...ContentGenerator.generateStudyMaterials(500));
  
  // Gera simulados
  console.log('🎯 Gerando simulados...');
  allExams.push(...ContentGenerator.generateSimulationExams(100));
  
  console.log('✅ Geração concluída!');
  console.log(`📊 Estatísticas:`);
  console.log(`   - Questões: ${allQuestions.length}`);
  console.log(`   - Documentos: ${allDocuments.length}`);
  console.log(`   - Materiais: ${allMaterials.length}`);
  console.log(`   - Simulados: ${allExams.length}`);
  
  return {
    questions: allQuestions,
    documents: allDocuments,
    materials: allMaterials,
    exams: allExams
  };
} 