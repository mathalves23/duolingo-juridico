export interface Subject {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  lessons: number;
  completed: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  category: 'civil' | 'criminal' | 'constitutional' | 'administrative' | 'labor' | 'tax' | 'procedural';
  topics: string[];
  estimatedHours: number;
}

export const subjectsData: Subject[] = [
  {
    id: '1',
    name: 'Direito Constitucional',
    description: 'Estude a Constituição Federal, direitos fundamentais, organização do Estado e controle de constitucionalidade.',
    icon: '⚖️',
    color: 'blue',
    lessons: 85,
    completed: 0,
    difficulty: 'intermediate',
    category: 'constitutional',
    topics: [
      'Princípios Fundamentais',
      'Direitos e Garantias Fundamentais',
      'Organização do Estado',
      'Organização dos Poderes',
      'Controle de Constitucionalidade',
      'Ordem Econômica e Financeira',
      'Ordem Social'
    ],
    estimatedHours: 120
  },
  {
    id: '2',
    name: 'Direito Administrativo',
    description: 'Aprenda sobre administração pública, atos administrativos, licitações e contratos administrativos.',
    icon: '🏛️',
    color: 'green',
    lessons: 78,
    completed: 0,
    difficulty: 'intermediate',
    category: 'administrative',
    topics: [
      'Princípios da Administração',
      'Organização Administrativa',
      'Atos Administrativos',
      'Poderes Administrativos',
      'Licitações e Contratos',
      'Serviços Públicos',
      'Responsabilidade Civil',
      'Processo Administrativo'
    ],
    estimatedHours: 110
  },
  {
    id: '3',
    name: 'Direito Civil',
    description: 'Domine o Código Civil, pessoas, bens, obrigações, contratos e responsabilidade civil.',
    icon: '👥',
    color: 'purple',
    lessons: 95,
    completed: 0,
    difficulty: 'advanced',
    category: 'civil',
    topics: [
      'Parte Geral - Pessoas',
      'Parte Geral - Bens',
      'Parte Geral - Fatos Jurídicos',
      'Obrigações',
      'Contratos',
      'Responsabilidade Civil',
      'Direitos Reais',
      'Direito de Família',
      'Direito das Sucessões'
    ],
    estimatedHours: 150
  },
  {
    id: '4',
    name: 'Direito Penal',
    description: 'Estude crimes, penas, teoria do delito e parte especial do Código Penal.',
    icon: '⚔️',
    color: 'red',
    lessons: 72,
    completed: 0,
    difficulty: 'advanced',
    category: 'criminal',
    topics: [
      'Aplicação da Lei Penal',
      'Teoria Geral do Crime',
      'Tentativa e Consumação',
      'Concurso de Pessoas',
      'Penas e Medidas de Segurança',
      'Crimes contra a Pessoa',
      'Crimes contra o Patrimônio',
      'Crimes contra a Administração',
      'Lei de Drogas',
      'Crimes Hediondos'
    ],
    estimatedHours: 100
  },
  {
    id: '5',
    name: 'Direito Processual Civil',
    description: 'Aprenda o novo CPC, procedimentos, recursos e execução civil.',
    icon: '📋',
    color: 'indigo',
    lessons: 88,
    completed: 0,
    difficulty: 'advanced',
    category: 'procedural',
    topics: [
      'Normas Processuais',
      'Jurisdição e Competência',
      'Sujeitos do Processo',
      'Atos Processuais',
      'Petição Inicial',
      'Respostas do Réu',
      'Provas',
      'Sentença e Coisa Julgada',
      'Recursos',
      'Processo de Execução'
    ],
    estimatedHours: 130
  },
  {
    id: '6',
    name: 'Direito Processual Penal',
    description: 'Domine o processo penal, inquérito policial, ação penal e recursos criminais.',
    icon: '🔍',
    color: 'orange',
    lessons: 65,
    completed: 0,
    difficulty: 'intermediate',
    category: 'procedural',
    topics: [
      'Aplicação da Lei Processual',
      'Inquérito Policial',
      'Ação Penal',
      'Competência Criminal',
      'Prisões e Liberdade Provisória',
      'Citação e Intimação',
      'Provas',
      'Procedimentos',
      'Recursos',
      'Execução Penal'
    ],
    estimatedHours: 90
  },
  {
    id: '7',
    name: 'Direito do Trabalho',
    description: 'Estude a CLT, contrato de trabalho, direitos trabalhistas e organização sindical.',
    icon: '👷',
    color: 'yellow',
    lessons: 68,
    completed: 0,
    difficulty: 'intermediate',
    category: 'labor',
    topics: [
      'Relação de Trabalho',
      'Contrato de Trabalho',
      'Jornada de Trabalho',
      'Salário e Remuneração',
      'Férias e Descansos',
      'FGTS e PIS',
      'Estabilidade e Garantias',
      'Extinção do Contrato',
      'Organização Sindical',
      'Greve e Dissídios'
    ],
    estimatedHours: 85
  },
  {
    id: '8',
    name: 'Direito Tributário',
    description: 'Aprenda sobre tributos, CTN, competência tributária e processo tributário.',
    icon: '💰',
    color: 'emerald',
    lessons: 75,
    completed: 0,
    difficulty: 'advanced',
    category: 'tax',
    topics: [
      'Sistema Tributário Nacional',
      'Competência Tributária',
      'Tributos e suas Espécies',
      'Legislação Tributária',
      'Obrigação Tributária',
      'Crédito Tributário',
      'Administração Tributária',
      'Processo Administrativo',
      'Processo Judicial Tributário',
      'Impostos Federais'
    ],
    estimatedHours: 105
  },
  {
    id: '9',
    name: 'Direito Empresarial',
    description: 'Domine o direito societário, títulos de crédito, falência e recuperação judicial.',
    icon: '🏢',
    color: 'teal',
    lessons: 55,
    completed: 0,
    difficulty: 'intermediate',
    category: 'civil',
    topics: [
      'Empresa e Empresário',
      'Sociedades Empresárias',
      'Títulos de Crédito',
      'Contratos Empresariais',
      'Propriedade Industrial',
      'Falência',
      'Recuperação Judicial',
      'Registro de Empresas'
    ],
    estimatedHours: 70
  },
  {
    id: '10',
    name: 'Direitos Humanos',
    description: 'Estude a proteção internacional e nacional dos direitos fundamentais da pessoa humana.',
    icon: '🤝',
    color: 'pink',
    lessons: 45,
    completed: 0,
    difficulty: 'beginner',
    category: 'constitutional',
    topics: [
      'Teoria Geral dos Direitos Humanos',
      'Sistema Internacional de Proteção',
      'Sistema Interamericano',
      'Direitos Humanos na Constituição',
      'Ações Constitucionais',
      'Grupos Vulneráveis',
      'Defensoria Pública'
    ],
    estimatedHours: 60
  },
  {
    id: '11',
    name: 'Direito Previdenciário',
    description: 'Aprenda sobre seguridade social, benefícios previdenciários e custeio.',
    icon: '🛡️',
    color: 'cyan',
    lessons: 58,
    completed: 0,
    difficulty: 'intermediate',
    category: 'labor',
    topics: [
      'Seguridade Social',
      'Regime Geral de Previdência',
      'Segurados e Dependentes',
      'Carência e Período de Graça',
      'Benefícios Previdenciários',
      'Custeio da Previdência',
      'Salário-de-Contribuição',
      'Processo Previdenciário'
    ],
    estimatedHours: 75
  },
  {
    id: '12',
    name: 'Direito Ambiental',
    description: 'Domine a proteção do meio ambiente, licenciamento e responsabilidade ambiental.',
    icon: '🌱',
    color: 'lime',
    lessons: 42,
    completed: 0,
    difficulty: 'beginner',
    category: 'administrative',
    topics: [
      'Princípios do Direito Ambiental',
      'Política Nacional do Meio Ambiente',
      'Licenciamento Ambiental',
      'Responsabilidade Ambiental',
      'Crimes Ambientais',
      'Áreas de Preservação',
      'Código Florestal',
      'Recursos Hídricos'
    ],
    estimatedHours: 55
  }
];

export const getDifficultyColor = (difficulty: Subject['difficulty']) => {
  switch (difficulty) {
    case 'beginner':
      return 'text-green-600 bg-green-100';
    case 'intermediate':
      return 'text-yellow-600 bg-yellow-100';
    case 'advanced':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

export const getCategoryColor = (category: Subject['category']) => {
  switch (category) {
    case 'civil':
      return 'bg-purple-100 text-purple-800';
    case 'criminal':
      return 'bg-red-100 text-red-800';
    case 'constitutional':
      return 'bg-blue-100 text-blue-800';
    case 'administrative':
      return 'bg-green-100 text-green-800';
    case 'labor':
      return 'bg-yellow-100 text-yellow-800';
    case 'tax':
      return 'bg-emerald-100 text-emerald-800';
    case 'procedural':
      return 'bg-indigo-100 text-indigo-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const getCategoryName = (category: Subject['category']) => {
  switch (category) {
    case 'civil':
      return 'Direito Civil';
    case 'criminal':
      return 'Direito Penal';
    case 'constitutional':
      return 'Direito Constitucional';
    case 'administrative':
      return 'Direito Administrativo';
    case 'labor':
      return 'Direito do Trabalho';
    case 'tax':
      return 'Direito Tributário';
    case 'procedural':
      return 'Direito Processual';
    default:
      return 'Outros';
  }
}; 