import React, { useState, useEffect } from 'react';
import {
  BookOpenIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  StarIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  BookmarkIcon,
  ClockIcon,
  TagIcon,
  UserIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  LightBulbIcon,
  ScaleIcon,
  BuildingLibraryIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import {
  StarIcon as StarSolid,
  BookmarkIcon as BookmarkSolid,
  HeartIcon as HeartSolid
} from '@heroicons/react/24/solid';
import Card from '../components/Card';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

interface Document {
  id: string;
  title: string;
  author: string;
  type: 'lei' | 'decreto' | 'jurisprudencia' | 'doutrina' | 'sumula' | 'artigo';
  subject: string;
  description: string;
  content: string;
  publishedDate: Date;
  views: number;
  downloads: number;
  rating: number;
  totalRatings: number;
  tags: string[];
  isFavorite: boolean;
  isBookmarked: boolean;
  source: string;
  difficulty: 'iniciante' | 'intermediario' | 'avancado';
  estimatedReadTime: number;
  relatedTopics: string[];
  lastUpdated?: Date;
  isPremium?: boolean;
}

interface SearchFilters {
  type: string;
  subject: string;
  difficulty: string;
  dateRange: string;
  sortBy: string;
  onlyFavorites: boolean;
  onlyBookmarked: boolean;
}

const Library: React.FC = () => {
  const { user } = useAuth();
  const { success, info } = useNotification();
  const [activeTab, setActiveTab] = useState<'all' | 'favorites' | 'bookmarks' | 'recent' | 'trending'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isReading, setIsReading] = useState(false);

  const [filters, setFilters] = useState<SearchFilters>({
    type: '',
    subject: '',
    difficulty: '',
    dateRange: '',
    sortBy: 'relevance',
    onlyFavorites: false,
    onlyBookmarked: false
  });

  const [documents] = useState<Document[]>([
    {
      id: '1',
      title: 'Constituição Federal de 1988',
      author: 'Assembleia Nacional Constituinte',
      type: 'lei',
      subject: 'Direito Constitucional',
      description: 'Texto completo da Constituição da República Federativa do Brasil de 1988, com todas as emendas constitucionais.',
      content: 'CONSTITUIÇÃO DA REPÚBLICA FEDERATIVA DO BRASIL DE 1988...',
      publishedDate: new Date('1988-10-05'),
      views: 15420,
      downloads: 3240,
      rating: 4.9,
      totalRatings: 1250,
      tags: ['Constituição', 'Direitos Fundamentais', 'Organização do Estado'],
      isFavorite: true,
      isBookmarked: true,
      source: 'Planalto',
      difficulty: 'intermediario',
      estimatedReadTime: 480,
      relatedTopics: ['Direitos Fundamentais', 'Organização dos Poderes', 'Federalismo']
    },
    {
      id: '2',
      title: 'Código Civil Brasileiro - Lei 10.406/2002',
      author: 'Congresso Nacional',
      type: 'lei',
      subject: 'Direito Civil',
      description: 'Código Civil brasileiro em vigor, regulamentando as relações civis entre pessoas físicas e jurídicas.',
      content: 'LEI No 10.406, DE 10 DE JANEIRO DE 2002...',
      publishedDate: new Date('2002-01-10'),
      views: 12800,
      downloads: 2890,
      rating: 4.8,
      totalRatings: 980,
      tags: ['Código Civil', 'Pessoa Natural', 'Contratos', 'Obrigações'],
      isFavorite: false,
      isBookmarked: true,
      source: 'Planalto',
      difficulty: 'intermediario',
      estimatedReadTime: 720,
      relatedTopics: ['Contratos', 'Responsabilidade Civil', 'Direitos Reais']
    },
    {
      id: '3',
      title: 'Súmula Vinculante nº 11 - STF',
      author: 'Supremo Tribunal Federal',
      type: 'sumula',
      subject: 'Direito Processual Penal',
      description: 'Uso de algemas: só é lícito o uso de algemas em casos de resistência e de fundado receio de fuga ou de perigo à integridade física própria ou alheia.',
      content: 'Só é lícito o uso de algemas em casos de resistência e de fundado receio de fuga ou de perigo à integridade física própria ou alheia, por parte do preso ou de terceiros, justificada a excepcionalidade por escrito, sob pena de responsabilidade disciplinar, civil e penal do agente ou da autoridade e de nulidade da prisão ou do ato processual a que se refere, sem prejuízo da responsabilidade civil do Estado.',
      publishedDate: new Date('2008-08-13'),
      views: 8940,
      downloads: 1240,
      rating: 4.7,
      totalRatings: 420,
      tags: ['Algemas', 'Prisão', 'Direitos Fundamentais', 'STF'],
      isFavorite: true,
      isBookmarked: false,
      source: 'STF',
      difficulty: 'avancado',
      estimatedReadTime: 15,
      relatedTopics: ['Prisão', 'Direitos do Preso', 'Processo Penal']
    },
    {
      id: '4',
      title: 'Marco Civil da Internet - Lei 12.965/2014',
      author: 'Congresso Nacional',
      type: 'lei',
      subject: 'Direito Digital',
      description: 'Estabelece princípios, garantias, direitos e deveres para o uso da Internet no Brasil.',
      content: 'LEI Nº 12.965, DE 23 DE ABRIL DE 2014...',
      publishedDate: new Date('2014-04-23'),
      views: 6780,
      downloads: 1890,
      rating: 4.6,
      totalRatings: 340,
      tags: ['Internet', 'Privacidade', 'Dados Pessoais', 'Tecnologia'],
      isFavorite: false,
      isBookmarked: false,
      source: 'Planalto',
      difficulty: 'intermediario',
      estimatedReadTime: 90,
      relatedTopics: ['LGPD', 'Privacidade Digital', 'Crimes Cibernéticos'],
      isPremium: true
    },
    {
      id: '5',
      title: 'Teoria Geral dos Contratos',
      author: 'Prof. Dr. Maria Silva',
      type: 'doutrina',
      subject: 'Direito Civil',
      description: 'Análise completa sobre a teoria geral dos contratos no direito civil brasileiro.',
      content: 'A teoria geral dos contratos representa um dos pilares fundamentais do direito civil...',
      publishedDate: new Date('2023-09-15'),
      views: 4520,
      downloads: 890,
      rating: 4.8,
      totalRatings: 180,
      tags: ['Contratos', 'Teoria Geral', 'Obrigações', 'Doutrina'],
      isFavorite: false,
      isBookmarked: true,
      source: 'Revista Jurídica',
      difficulty: 'avancado',
      estimatedReadTime: 45,
      relatedTopics: ['Formação dos Contratos', 'Vícios do Consentimento', 'Extinção dos Contratos']
    }
  ]);

  const [recentDocuments] = useState<Document[]>(
    documents.slice(0, 3)
  );

  const [trendingDocuments] = useState<Document[]>(
    documents.sort((a, b) => b.views - a.views).slice(0, 4)
  );

  const documentTypes = [
    { value: '', label: 'Todos os tipos' },
    { value: 'lei', label: 'Leis' },
    { value: 'decreto', label: 'Decretos' },
    { value: 'jurisprudencia', label: 'Jurisprudência' },
    { value: 'doutrina', label: 'Doutrina' },
    { value: 'sumula', label: 'Súmulas' },
    { value: 'artigo', label: 'Artigos' }
  ];

  const subjects = [
    { value: '', label: 'Todas as matérias' },
    { value: 'Direito Constitucional', label: 'Direito Constitucional' },
    { value: 'Direito Civil', label: 'Direito Civil' },
    { value: 'Direito Penal', label: 'Direito Penal' },
    { value: 'Direito Processual Civil', label: 'Direito Processual Civil' },
    { value: 'Direito Processual Penal', label: 'Direito Processual Penal' },
    { value: 'Direito Administrativo', label: 'Direito Administrativo' },
    { value: 'Direito Tributário', label: 'Direito Tributário' },
    { value: 'Direito Digital', label: 'Direito Digital' }
  ];

  const difficulties = [
    { value: '', label: 'Todos os níveis' },
    { value: 'iniciante', label: 'Iniciante' },
    { value: 'intermediario', label: 'Intermediário' },
    { value: 'avancado', label: 'Avançado' }
  ];

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesType = !filters.type || doc.type === filters.type;
    const matchesSubject = !filters.subject || doc.subject === filters.subject;
    const matchesDifficulty = !filters.difficulty || doc.difficulty === filters.difficulty;
    const matchesFavorites = !filters.onlyFavorites || doc.isFavorite;
    const matchesBookmarks = !filters.onlyBookmarked || doc.isBookmarked;

    return matchesSearch && matchesType && matchesSubject && matchesDifficulty && matchesFavorites && matchesBookmarks;
  });

  const getDocumentIcon = (type: string) => {
    switch (type) {
      case 'lei': return '📜';
      case 'decreto': return '📋';
      case 'jurisprudencia': return '⚖️';
      case 'doutrina': return '📚';
      case 'sumula': return '📄';
      case 'artigo': return '📰';
      default: return '📄';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'iniciante': return 'text-green-600 bg-green-100';
      case 'intermediario': return 'text-yellow-600 bg-yellow-100';
      case 'avancado': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const toggleFavorite = (docId: string) => {
    // Implementar lógica de favorito
    success('Adicionado aos favoritos! ⭐', 'Documento salvo na sua lista de favoritos.');
  };

  const toggleBookmark = (docId: string) => {
    // Implementar lógica de bookmark
    info('Marcador adicionado! 🔖', 'Documento salvo para leitura posterior.');
  };

  const openDocument = (doc: Document) => {
    setSelectedDocument(doc);
    setIsReading(true);
  };

  const downloadDocument = (doc: Document) => {
    success('Download iniciado! 📥', `Baixando: ${doc.title}`);
  };

  const shareDocument = (doc: Document) => {
    info('Link copiado! 🔗', 'Link do documento copiado para a área de transferência.');
  };

  const renderDocumentCard = (doc: Document) => (
    <Card key={doc.id} className="p-6 hover:shadow-lg transition-all duration-300 group">
      <div className="flex items-start gap-4">
        <div className="text-3xl">{getDocumentIcon(doc.type)}</div>
        
        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors cursor-pointer"
                  onClick={() => openDocument(doc)}>
                {doc.title}
                {doc.isPremium && (
                  <span className="ml-2 text-xs bg-gold-100 text-gold-800 px-2 py-1 rounded-full font-medium">
                    PRO
                  </span>
                )}
              </h3>
              <p className="text-sm text-gray-600 mb-1">{doc.author}</p>
              <p className="text-sm text-gray-500">{doc.description}</p>
            </div>
            
            <div className="flex items-center gap-2 ml-4">
              <button
                onClick={() => toggleFavorite(doc.id)}
                className={`p-2 rounded-lg transition-colors ${
                  doc.isFavorite ? 'text-red-500 bg-red-50' : 'text-gray-400 hover:text-red-500 hover:bg-red-50'
                }`}
              >
                {doc.isFavorite ? <HeartSolid className="w-4 h-4" /> : <StarIcon className="w-4 h-4" />}
              </button>
              <button
                onClick={() => toggleBookmark(doc.id)}
                className={`p-2 rounded-lg transition-colors ${
                  doc.isBookmarked ? 'text-blue-500 bg-blue-50' : 'text-gray-400 hover:text-blue-500 hover:bg-blue-50'
                }`}
              >
                {doc.isBookmarked ? <BookmarkSolid className="w-4 h-4" /> : <BookmarkIcon className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4 mb-3 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <CalendarIcon className="w-4 h-4" />
              {doc.publishedDate.toLocaleDateString('pt-BR')}
            </div>
            <div className="flex items-center gap-1">
              <ClockIcon className="w-4 h-4" />
              {doc.estimatedReadTime} min
            </div>
            <div className="flex items-center gap-1">
              <EyeIcon className="w-4 h-4" />
              {doc.views.toLocaleString()}
            </div>
            <div className="flex items-center gap-1">
              <StarSolid className="w-4 h-4 text-yellow-500" />
              {doc.rating} ({doc.totalRatings})
            </div>
          </div>

          <div className="flex items-center gap-2 mb-4">
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor(doc.difficulty)}`}>
              {doc.difficulty}
            </span>
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              {doc.subject}
            </span>
          </div>

          <div className="flex flex-wrap gap-1 mb-4">
            {doc.tags.slice(0, 4).map((tag, index) => (
              <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                #{tag}
              </span>
            ))}
            {doc.tags.length > 4 && (
              <span className="text-xs text-gray-500">+{doc.tags.length - 4} mais</span>
            )}
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={() => openDocument(doc)}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
            >
              <EyeIcon className="w-4 h-4" />
              Ler
            </button>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => downloadDocument(doc)}
                className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <ArrowDownTrayIcon className="w-4 h-4" />
              </button>
              <button
                onClick={() => shareDocument(doc)}
                className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              >
                <ShareIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );

  const renderFilters = () => (
    <Card className="p-6">
      <div className="grid md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
          <select
            value={filters.type}
            onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {documentTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Matéria</label>
          <select
            value={filters.subject}
            onChange={(e) => setFilters(prev => ({ ...prev, subject: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {subjects.map(subject => (
              <option key={subject.value} value={subject.value}>{subject.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Dificuldade</label>
          <select
            value={filters.difficulty}
            onChange={(e) => setFilters(prev => ({ ...prev, difficulty: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {difficulties.map(difficulty => (
              <option key={difficulty.value} value={difficulty.value}>{difficulty.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ordenar por</label>
          <select
            value={filters.sortBy}
            onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="relevance">Relevância</option>
            <option value="date">Data de publicação</option>
            <option value="rating">Avaliação</option>
            <option value="views">Mais visualizados</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-4">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={filters.onlyFavorites}
            onChange={(e) => setFilters(prev => ({ ...prev, onlyFavorites: e.target.checked }))}
            className="rounded text-blue-500 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Apenas favoritos</span>
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={filters.onlyBookmarked}
            onChange={(e) => setFilters(prev => ({ ...prev, onlyBookmarked: e.target.checked }))}
            className="rounded text-blue-500 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Apenas marcados</span>
        </label>
      </div>
    </Card>
  );

  const renderContent = () => {
    const documentsToShow = activeTab === 'favorites' 
      ? documents.filter(d => d.isFavorite)
      : activeTab === 'bookmarks'
      ? documents.filter(d => d.isBookmarked)
      : activeTab === 'recent'
      ? recentDocuments
      : activeTab === 'trending'
      ? trendingDocuments
      : filteredDocuments;

    return (
      <div className="space-y-6">
        {showFilters && renderFilters()}
        
        <div className="flex items-center justify-between">
          <p className="text-gray-600">
            {documentsToShow.length} documento{documentsToShow.length !== 1 ? 's' : ''} encontrado{documentsToShow.length !== 1 ? 's' : ''}
          </p>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <FunnelIcon className="w-4 h-4" />
            {showFilters ? 'Ocultar' : 'Mostrar'} Filtros
          </button>
        </div>

        <div className="space-y-4">
          {documentsToShow.map(renderDocumentCard)}
        </div>

        {documentsToShow.length === 0 && (
          <div className="text-center py-12">
            <BookOpenIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum documento encontrado</h3>
            <p className="text-gray-600">Tente ajustar os filtros ou termos de busca.</p>
          </div>
        )}
      </div>
    );
  };

  const tabs = [
    { id: 'all', label: 'Todos', count: documents.length },
    { id: 'favorites', label: 'Favoritos', count: documents.filter(d => d.isFavorite).length },
    { id: 'bookmarks', label: 'Marcados', count: documents.filter(d => d.isBookmarked).length },
    { id: 'recent', label: 'Recentes', count: recentDocuments.length },
    { id: 'trending', label: 'Em Alta', count: trendingDocuments.length }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <BuildingLibraryIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Biblioteca Jurídica Digital</h1>
            <p className="text-indigo-100">
              Acesso completo à legislação, jurisprudência e doutrina brasileira
            </p>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <Card className="p-6">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por título, autor, conteúdo ou tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="mt-4 flex items-center gap-2">
          <SparklesIcon className="w-5 h-5 text-purple-500" />
          <span className="text-sm text-gray-600">
            <strong>Busca Inteligente:</strong> Use termos como "responsabilidade civil contrato" ou "STF direitos fundamentais"
          </span>
        </div>
      </Card>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-4 gap-6">
        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <DocumentTextIcon className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{documents.length}</div>
          <div className="text-sm text-gray-600">Documentos</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <ArrowTrendingUpIcon className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {documents.reduce((acc, doc) => acc + doc.views, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Visualizações</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <StarSolid className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {documents.filter(d => d.isFavorite).length}
          </div>
          <div className="text-sm text-gray-600">Favoritos</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <BookmarkSolid className="w-6 h-6 text-yellow-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {documents.filter(d => d.isBookmarked).length}
          </div>
          <div className="text-sm text-gray-600">Marcados</div>
        </Card>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
              <span className={`text-xs px-2 py-1 rounded-full ${
                activeTab === tab.id
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {renderContent()}

      {/* AI Recommendations */}
      <Card className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <LightBulbIcon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Recomendações Personalizadas</h3>
            <p className="text-sm text-gray-600">Baseado no seu histórico de estudos e interesses</p>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-4">
          {documents.slice(0, 3).map((doc) => (
            <div key={doc.id} className="bg-white p-4 rounded-lg border cursor-pointer hover:shadow-md transition-shadow"
                 onClick={() => openDocument(doc)}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{getDocumentIcon(doc.type)}</span>
                <span className="font-medium text-gray-900 text-sm">{doc.title}</span>
              </div>
              <p className="text-xs text-gray-600 mb-2">{doc.description.substring(0, 80)}...</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-blue-600">{doc.subject}</span>
                <span className="text-xs text-gray-500">{doc.estimatedReadTime} min</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Library; 