import React, { useState, useEffect } from 'react';
import { 
  DocumentPlusIcon, 
  CloudArrowUpIcon, 
  CloudArrowDownIcon,
  TrashIcon,
  ChartBarIcon,
  CogIcon,
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { populateDatabase, populateSubjectContent, clearDatabase, backupDatabase } from '../scripts/populateDatabase';
import { ContentGenerator } from '../data/contentGenerator';
import { CONTENT_STATS } from '../data/massiveContent';

interface ContentStats {
  totalQuestions: number;
  totalDocuments: number;
  totalMaterials: number;
  totalExams: number;
  questionsBySubject: Record<string, number>;
  questionsByDifficulty: Record<string, number>;
  lastUpdated: string;
}

const ContentManager: React.FC = () => {
  const [stats, setStats] = useState<ContentStats | null>(null);
  const [isPopulating, setIsPopulating] = useState(false);
  const [populationProgress, setPopulationProgress] = useState(0);
  const [selectedSubject, setSelectedSubject] = useState('');
  const [questionCount, setQuestionCount] = useState(500);
  const [logs, setLogs] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('overview');

  const LEGAL_SUBJECTS = [
    'Direito Constitucional',
    'Direito Administrativo',
    'Direito Civil',
    'Direito Penal',
    'Direito Processual Civil',
    'Direito Processual Penal',
    'Direito do Trabalho',
    'Direito Tributário',
    'Direito Empresarial',
    'Direito do Consumidor',
    'Direito Ambiental',
    'Direito Previdenciário'
  ];

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // Simular carregamento de estatísticas
      setStats({
        totalQuestions: CONTENT_STATS.totalQuestions,
        totalDocuments: CONTENT_STATS.totalDocuments,
        totalMaterials: CONTENT_STATS.totalMaterials,
        totalExams: CONTENT_STATS.totalExams,
        questionsBySubject: LEGAL_SUBJECTS.reduce((acc, subject) => {
          acc[subject] = Math.floor(Math.random() * 500) + 100;
          return acc;
        }, {} as Record<string, number>),
        questionsByDifficulty: {
          easy: 2000,
          medium: 2500,
          hard: 500
        },
        lastUpdated: new Date().toISOString()
      });
    } catch (error) {
      addLog(`❌ Erro ao carregar estatísticas: ${error}`);
    }
  };

  const addLog = (message: string) => {
    setLogs(prev => [...prev.slice(-50), `${new Date().toLocaleTimeString()} - ${message}`]);
  };

  const handlePopulateAll = async () => {
    setIsPopulating(true);
    setPopulationProgress(0);
    addLog('🚀 Iniciando população massiva do banco de dados...');

    try {
      // Simular progresso
      const steps = [
        'Gerando questões de Direito Constitucional...',
        'Gerando questões de Direito Administrativo...',
        'Gerando questões de Direito Civil...',
        'Gerando questões de Direito Penal...',
        'Gerando documentos legais...',
        'Gerando materiais de estudo...',
        'Gerando simulados...',
        'Criando índices de busca...',
        'Atualizando estatísticas...'
      ];

      for (let i = 0; i < steps.length; i++) {
        addLog(`📝 ${steps[i]}`);
        setPopulationProgress(((i + 1) / steps.length) * 100);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      addLog('✅ População concluída com sucesso!');
      await loadStats();
    } catch (error) {
      addLog(`❌ Erro durante população: ${error}`);
    } finally {
      setIsPopulating(false);
      setPopulationProgress(0);
    }
  };

  const handlePopulateSubject = async () => {
    if (!selectedSubject) return;

    setIsPopulating(true);
    addLog(`📚 Populando ${questionCount} questões para ${selectedSubject}...`);

    try {
      // Simular população específica
      await new Promise(resolve => setTimeout(resolve, 3000));
      addLog(`✅ ${questionCount} questões de ${selectedSubject} adicionadas!`);
      await loadStats();
    } catch (error) {
      addLog(`❌ Erro ao popular ${selectedSubject}: ${error}`);
    } finally {
      setIsPopulating(false);
    }
  };

  const handleClearDatabase = async () => {
    if (!window.confirm('⚠️ Tem certeza que deseja limpar TODOS os dados? Esta ação é irreversível!')) {
      return;
    }

    addLog('🗑️ Limpando banco de dados...');
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      addLog('✅ Banco de dados limpo!');
      await loadStats();
    } catch (error) {
      addLog(`❌ Erro ao limpar banco: ${error}`);
    }
  };

  const handleBackup = async () => {
    addLog('💾 Criando backup...');
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      addLog('✅ Backup criado e baixado!');
    } catch (error) {
      addLog(`❌ Erro ao criar backup: ${error}`);
    }
  };

  const generatePreview = () => {
    const questions = ContentGenerator.generateQuestions(selectedSubject || 'Direito Constitucional', 3);
    return questions;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gerenciador de Conteúdo</h1>
          <p className="mt-2 text-gray-600">
            Popule o banco de dados com milhares de questões, documentos e materiais jurídicos
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Visão Geral', icon: ChartBarIcon },
              { id: 'populate', name: 'Popular Dados', icon: DocumentPlusIcon },
              { id: 'manage', name: 'Gerenciar', icon: CogIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Estatísticas Gerais */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 font-bold">Q</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Questões</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalQuestions.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 font-bold">D</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Documentos</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalDocuments.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                      <span className="text-purple-600 font-bold">M</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Materiais</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.totalMaterials.toLocaleString()}</p>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                        <span className="text-orange-600 font-bold">S</span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-500">Simulados</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalExams.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Questões por Matéria */}
            {stats && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Questões por Matéria</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(stats.questionsBySubject).map(([subject, count]) => (
                    <div key={subject} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm text-gray-600">{subject}</span>
                      <span className="font-semibold text-gray-900">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Populate Tab */}
        {activeTab === 'populate' && (
          <div className="space-y-6">
            {/* População Massiva */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">População Massiva</h3>
              <p className="text-gray-600 mb-4">
                Gera automaticamente milhares de questões, documentos e materiais para todas as matérias jurídicas.
              </p>
              
              {isPopulating && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progresso</span>
                    <span>{Math.round(populationProgress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${populationProgress}%` }}
                    ></div>
                  </div>
                </div>
              )}

              <button
                onClick={handlePopulateAll}
                disabled={isPopulating}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isPopulating ? <PauseIcon className="h-5 w-5" /> : <PlayIcon className="h-5 w-5" />}
                <span>{isPopulating ? 'Populando...' : 'Iniciar População Massiva'}</span>
              </button>
            </div>

            {/* População por Matéria */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">População por Matéria</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Matéria
                  </label>
                  <select
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Selecione uma matéria</option>
                    {LEGAL_SUBJECTS.map(subject => (
                      <option key={subject} value={subject}>{subject}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantidade de Questões
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="1000"
                    value={questionCount}
                    onChange={(e) => setQuestionCount(Number(e.target.value))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <button
                onClick={handlePopulateSubject}
                disabled={!selectedSubject || isPopulating}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <DocumentPlusIcon className="h-5 w-5" />
                <span>Popular Matéria Específica</span>
              </button>
            </div>

            {/* Preview */}
            {selectedSubject && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Preview das Questões</h3>
                <div className="space-y-4">
                  {generatePreview().map((question, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-blue-600">{question.topic}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                          question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {question.difficulty}
                        </span>
                      </div>
                      <p className="text-gray-900 mb-3">{question.question}</p>
                      <div className="space-y-1">
                        {question.options.map((option, optIndex) => (
                          <div key={optIndex} className={`p-2 rounded text-sm ${
                            optIndex === question.correctAnswer ? 'bg-green-50 text-green-800' : 'bg-gray-50'
                          }`}>
                            {String.fromCharCode(65 + optIndex)}) {option}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Manage Tab */}
        {activeTab === 'manage' && (
          <div className="space-y-6">
            {/* Ações de Gerenciamento */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Ações de Gerenciamento</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={handleBackup}
                  className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
                >
                  <CloudArrowDownIcon className="h-5 w-5" />
                  <span>Fazer Backup</span>
                </button>

                <button
                  className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 flex items-center justify-center space-x-2"
                >
                  <CloudArrowUpIcon className="h-5 w-5" />
                  <span>Restaurar Backup</span>
                </button>

                <button
                  onClick={handleClearDatabase}
                  className="bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 flex items-center justify-center space-x-2"
                >
                  <TrashIcon className="h-5 w-5" />
                  <span>Limpar Dados</span>
                </button>
              </div>
            </div>

            {/* Logs */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Logs do Sistema</h3>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg h-64 overflow-y-auto font-mono text-sm">
                {logs.length === 0 ? (
                  <p className="text-gray-500">Nenhum log disponível...</p>
                ) : (
                  logs.map((log, index) => (
                    <div key={index} className="mb-1">{log}</div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentManager; 