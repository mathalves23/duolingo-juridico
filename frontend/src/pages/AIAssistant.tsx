import React, { useState, useRef, useEffect } from 'react';
import { 
  SparklesIcon, 
  ChatBubbleLeftRightIcon, 
  DocumentTextIcon,
  ScaleIcon,
  BeakerIcon,
  CpuChipIcon,
  AcademicCapIcon,
  BookOpenIcon,
  LightBulbIcon,
  MicrophoneIcon,
  PaperAirplaneIcon,
  ClockIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import AIChat from '../components/AIChat';
import Card from '../components/Card';

interface AITool {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  color: string;
  features: string[];
  isAvailable: boolean;
  isPremium?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messageCount: number;
}

const AIAssistant: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'tools' | 'history'>('chat');
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([
    {
      id: '1',
      title: 'Dúvidas sobre Direito Constitucional',
      lastMessage: 'Obrigado pela explicação sobre hierarquia das normas!',
      timestamp: new Date(Date.now() - 3600000),
      messageCount: 15
    },
    {
      id: '2',
      title: 'Estratégias para OAB',
      lastMessage: 'Como melhorar minha pontuação em Direito Civil?',
      timestamp: new Date(Date.now() - 7200000),
      messageCount: 8
    },
    {
      id: '3',
      title: 'Análise de Jurisprudência',
      lastMessage: 'Preciso entender melhor o STF sobre esse tema',
      timestamp: new Date(Date.now() - 86400000),
      messageCount: 22
    }
  ]);

  const aiTools: AITool[] = [
    {
      id: 'legal-advisor',
      name: 'Consultor Jurídico',
      description: 'Chat especializado em diferentes áreas do direito com respostas fundamentadas',
      icon: ScaleIcon,
      color: 'blue',
      features: [
        'Respostas com fundamentação legal',
        'Análise de casos complexos',
        'Sugestões de jurisprudência',
        'Interpretação de normas'
      ],
      isAvailable: true
    },
    {
      id: 'document-analyzer',
      name: 'Analisador de Documentos',
      description: 'Análise automática de contratos, petições e documentos jurídicos',
      icon: DocumentTextIcon,
      color: 'green',
      features: [
        'Análise de cláusulas contratuais',
        'Identificação de riscos',
        'Sugestões de melhorias',
        'Revisão de petições'
      ],
      isAvailable: true,
      isPremium: true
    },
    {
      id: 'case-researcher',
      name: 'Pesquisador de Precedentes',
      description: 'Busca inteligente de jurisprudência e precedentes relevantes',
      icon: BeakerIcon,
      color: 'purple',
      features: [
        'Busca por similaridade',
        'Análise de tendências',
        'Resumos automáticos',
        'Timeline jurisprudencial'
      ],
      isAvailable: true,
      isPremium: true
    },
    {
      id: 'study-planner',
      name: 'Planejador de Estudos',
      description: 'IA que cria planos de estudo personalizados baseados no seu desempenho',
      icon: AcademicCapIcon,
      color: 'indigo',
      features: [
        'Planos adaptativos',
        'Cronograma otimizado',
        'Revisões programadas',
        'Metas personalizadas'
      ],
      isAvailable: true
    },
    {
      id: 'legal-writer',
      name: 'Redator Jurídico',
      description: 'Assistente para redação de peças processuais e documentos legais',
      icon: BookOpenIcon,
      color: 'orange',
      features: [
        'Templates profissionais',
        'Correção gramatical',
        'Sugestões de linguagem',
        'Formatação automática'
      ],
      isAvailable: false
    },
    {
      id: 'exam-simulator',
      name: 'Simulador Inteligente',
      description: 'Geração de questões personalizadas baseadas no seu nível e fraquezas',
      icon: CpuChipIcon,
      color: 'red',
      features: [
        'Questões adaptativas',
        'Análise de performance',
        'Explicações detalhadas',
        'Simulados completos'
      ],
      isAvailable: true
    }
  ];

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}min atrás`;
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60);
      return `${hours}h atrás`;
    } else {
      const days = Math.floor(diffInMinutes / 1440);
      return `${days}d atrás`;
    }
  };

  const renderChatTab = () => (
    <div className="grid lg:grid-cols-4 gap-6 h-full">
      {/* Chat Sessions Sidebar */}
      <div className="lg:col-span-1">
        <Card className="h-full">
          <div className="p-4 border-b">
            <h3 className="font-semibold text-gray-900">Conversas Recentes</h3>
            <button className="mt-2 w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors text-sm">
              + Nova Conversa
            </button>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {chatSessions.map((session) => (
              <div
                key={session.id}
                className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <h4 className="font-medium text-sm text-gray-900 truncate">
                  {session.title}
                </h4>
                <p className="text-xs text-gray-600 mt-1 truncate">
                  {session.lastMessage}
                </p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(session.timestamp)}
                  </span>
                  <div className="flex items-center gap-1">
                    <ChatBubbleLeftRightIcon className="w-3 h-3 text-gray-400" />
                    <span className="text-xs text-gray-500">{session.messageCount}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Main Chat Area */}
      <div className="lg:col-span-3">
        <div className="h-[600px]">
          <AIChat isOpen={isChatOpen} />
        </div>
      </div>
    </div>
  );

  const renderToolsTab = () => (
    <div className="space-y-6">
      <div className="text-center">
        <SparklesIcon className="w-16 h-16 text-blue-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Ferramentas de IA Jurídica</h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Explore nosso conjunto completo de ferramentas de inteligência artificial 
          especializadas em direito para otimizar seus estudos e prática profissional.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {aiTools.map((tool) => {
          const IconComponent = tool.icon;
          return (
            <Card key={tool.id} className="relative overflow-hidden">
              {tool.isPremium && (
                <div className="absolute top-4 right-4">
                  <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                    PRO
                  </div>
                </div>
              )}
              
              <div className="p-6">
                <div className={`w-12 h-12 bg-${tool.color}-100 rounded-lg flex items-center justify-center mb-4`}>
                  <IconComponent className={`w-6 h-6 text-${tool.color}-600`} />
                </div>
                
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {tool.name}
                </h3>
                
                <p className="text-gray-600 text-sm mb-4">
                  {tool.description}
                </p>
                
                <div className="space-y-2 mb-4">
                  {tool.features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div className={`w-1.5 h-1.5 bg-${tool.color}-500 rounded-full`}></div>
                      <span className="text-xs text-gray-600">{feature}</span>
                    </div>
                  ))}
                </div>
                
                <button
                  disabled={!tool.isAvailable}
                  className={`w-full py-2 px-4 rounded-lg font-medium text-sm transition-colors ${
                    tool.isAvailable
                      ? `bg-${tool.color}-500 text-white hover:bg-${tool.color}-600`
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {tool.isAvailable ? 'Usar Ferramenta' : 'Em Breve'}
                </button>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-4 gap-4 mt-8">
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Consultas Hoje</p>
              <p className="text-2xl font-bold">23</p>
            </div>
            <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-200" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Documentos Analisados</p>
              <p className="text-2xl font-bold">7</p>
            </div>
            <DocumentTextIcon className="w-8 h-8 text-green-200" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Precedentes Encontrados</p>
              <p className="text-2xl font-bold">45</p>
            </div>
            <BeakerIcon className="w-8 h-8 text-purple-200" />
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Tempo Economizado</p>
              <p className="text-2xl font-bold">4.2h</p>
            </div>
            <ClockIcon className="w-8 h-8 text-orange-200" />
          </div>
        </div>
      </div>
    </div>
  );

  const renderHistoryTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Histórico de Interações</h2>
        <div className="flex gap-2">
          <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option>Todos os tipos</option>
            <option>Chat</option>
            <option>Análise de documentos</option>
            <option>Pesquisa de precedentes</option>
          </select>
          <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option>Últimos 7 dias</option>
            <option>Último mês</option>
            <option>Últimos 3 meses</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {[
          {
            id: '1',
            type: 'chat',
            title: 'Consulta sobre Direito Constitucional',
            summary: 'Discussão sobre hierarquia das normas e princípios constitucionais',
            timestamp: new Date(Date.now() - 3600000),
            tags: ['Constitucional', 'Hierarquia', 'Princípios'],
            rating: 5
          },
          {
            id: '2',
            type: 'document',
            title: 'Análise de Contrato de Prestação de Serviços',
            summary: 'Revisão de cláusulas contratuais e identificação de riscos',
            timestamp: new Date(Date.now() - 7200000),
            tags: ['Contrato', 'Análise', 'Riscos'],
            rating: 4
          },
          {
            id: '3',
            type: 'research',
            title: 'Pesquisa sobre Responsabilidade Civil',
            summary: 'Levantamento de jurisprudência sobre danos morais',
            timestamp: new Date(Date.now() - 86400000),
            tags: ['Civil', 'Jurisprudência', 'Danos'],
            rating: 5
          }
        ].map((item) => (
          <Card key={item.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-2 h-2 rounded-full ${
                    item.type === 'chat' ? 'bg-blue-500' :
                    item.type === 'document' ? 'bg-green-500' : 'bg-purple-500'
                  }`}></div>
                  <h3 className="font-medium text-gray-900">{item.title}</h3>
                  <span className="text-xs text-gray-500 ml-auto">
                    {formatTimeAgo(item.timestamp)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{item.summary}</p>
                
                <div className="flex items-center gap-2">
                  <TagIcon className="w-4 h-4 text-gray-400" />
                  <div className="flex gap-1">
                    {item.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-1 ml-4">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-4 h-4 ${
                      i < item.rating ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                  >
                    ⭐
                  </div>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <SparklesIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Assistente Jurídico IA</h1>
            <p className="text-blue-100">
              Sua inteligência artificial especializada em direito brasileiro
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'chat', label: 'Chat Inteligente', icon: ChatBubbleLeftRightIcon },
            { id: 'tools', label: 'Ferramentas', icon: CpuChipIcon },
            { id: 'history', label: 'Histórico', icon: ClockIcon }
          ].map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'chat' && renderChatTab()}
        {activeTab === 'tools' && renderToolsTab()}
        {activeTab === 'history' && renderHistoryTab()}
      </div>
    </div>
  );
};

export default AIAssistant;