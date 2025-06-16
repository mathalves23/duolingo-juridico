import React, { useState, useRef, useEffect } from 'react';
import {
  BeakerIcon,
  RocketLaunchIcon,
  CpuChipIcon,
  ScaleIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  MicrophoneIcon,
  VideoCameraIcon,
  UserGroupIcon,
  ClockIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  PlayIcon,
  PauseIcon,
  SpeakerWaveIcon
} from '@heroicons/react/24/outline';

// Mock auth hook
const useAuth = () => ({
  user: {
    id: '1',
    username: 'usuario_demo',
    email: 'demo@example.com',
    first_name: 'Demo',
    last_name: 'User'
  },
  isAuthenticated: true
});

interface TrialParticipant {
  id: string;
  name: string;
  role: 'judge' | 'prosecutor' | 'defense' | 'witness' | 'jury';
  avatar: string;
  isAI: boolean;
  personality?: string;
  experience?: string;
}

interface TrialCase {
  id: string;
  title: string;
  description: string;
  type: 'criminal' | 'civil' | 'constitutional' | 'administrative';
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  participants: TrialParticipant[];
  evidence: Evidence[];
  timeLimit: number; // minutes
  learningObjectives: string[];
}

interface Evidence {
  id: string;
  type: 'document' | 'witness_testimony' | 'physical' | 'digital' | 'expert_report';
  title: string;
  description: string;
  content: any;
  admissible: boolean;
  relevance: number;
}

interface AIJudgeDecision {
  decision: 'favor_prosecution' | 'favor_defense' | 'hung_jury' | 'mistrial';
  reasoning: string;
  score: number;
  feedback: string[];
  improvements: string[];
}

const LegalTechLab: React.FC = () => {
  const { user } = useAuth();
  const [currentTool, setCurrentTool] = useState<'simulator' | 'ai_assistant' | 'case_analyzer' | 'contract_gen'>('simulator');
  const [activeTrial, setActiveTrial] = useState<TrialCase | null>(null);
  const [trialState, setTrialState] = useState<'lobby' | 'opening' | 'evidence' | 'closing' | 'verdict'>('lobby');
  const [currentSpeaker, setCurrentSpeaker] = useState<TrialParticipant | null>(null);
  const [trialTime, setTrialTime] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [userRole, setUserRole] = useState<'prosecutor' | 'defense' | 'observer'>('observer');
  const [trialScore, setTrialScore] = useState(0);

  const audioRef = useRef<HTMLAudioElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (activeTrial && trialState !== 'lobby' && trialState !== 'verdict') {
      interval = setInterval(() => {
        setTrialTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [activeTrial, trialState]);

  const mockTrialCases: TrialCase[] = [
    {
      id: 'constitutional-case-1',
      title: 'Liberdade de Expressão vs. Dignidade Humana',
      description: 'Caso envolvendo conflito entre direitos fundamentais em manifestação pública',
      type: 'constitutional',
      difficulty: 'intermediate',
      participants: [
        {
          id: 'judge-ai',
          name: 'Dra. Constitucionalista IA',
          role: 'judge',
          avatar: '/avatars/judge-female.png',
          isAI: true,
          personality: 'Rigorosa mas justa, especialista em direitos fundamentais',
          experience: '15 anos no STF'
        },
        {
          id: 'prosecutor-ai',
          name: 'Dr. Ministério Público IA',
          role: 'prosecutor',
          avatar: '/avatars/prosecutor-male.png',
          isAI: true,
          personality: 'Defensor dos direitos da personalidade',
          experience: '10 anos como promotor'
        },
        {
          id: 'defense-human',
          name: user?.first_name || 'Estudante',
          role: 'defense',
          avatar: '/avatars/default.png',
          isAI: false
        }
      ],
      evidence: [
        {
          id: 'video-manifestacao',
          type: 'digital',
          title: 'Vídeo da Manifestação',
          description: 'Gravação mostrando os fatos ocorridos',
          content: { url: '/evidence/video1.mp4', duration: 120 },
          admissible: true,
          relevance: 9
        },
        {
          id: 'depoimento-vitima',
          type: 'witness_testimony',
          title: 'Depoimento da Vítima',
          description: 'Relato da pessoa ofendida',
          content: { text: 'Depoimento detalhado...' },
          admissible: true,
          relevance: 8
        }
      ],
      timeLimit: 45,
      learningObjectives: [
        'Compreender conflitos entre direitos fundamentais',
        'Aplicar técnica de ponderação',
        'Analisar jurisprudência do STF'
      ]
    },
    {
      id: 'administrative-case-1',
      title: 'Licitação Suspeita',
      description: 'Processo de licitação com possíveis irregularidades',
      type: 'administrative',
      difficulty: 'advanced',
      participants: [
        {
          id: 'judge-admin',
          name: 'Dr. Tribunal de Contas IA',
          role: 'judge',
          avatar: '/avatars/judge-male.png',
          isAI: true,
          personality: 'Especialista em direito administrativo',
          experience: '20 anos no TCU'
        }
      ],
      evidence: [],
      timeLimit: 60,
      learningObjectives: [
        'Entender princípios licitatórios',
        'Identificar irregularidades',
        'Aplicar Lei 14.133/21'
      ]
    }
  ];

  const startTrial = (trialCase: TrialCase, role: 'prosecutor' | 'defense' | 'observer') => {
    setActiveTrial(trialCase);
    setUserRole(role);
    setTrialState('opening');
    setTrialTime(0);
    setTrialScore(0);
    
    // Definir primeiro orador
    if (role === 'prosecutor') {
      setCurrentSpeaker(trialCase.participants.find(p => p.role === 'prosecutor') || null);
    } else {
      setCurrentSpeaker(trialCase.participants.find(p => p.role === 'defense') || null);
    }
  };

  const endTrial = () => {
    setActiveTrial(null);
    setTrialState('lobby');
    setCurrentSpeaker(null);
    setTrialTime(0);
    setIsRecording(false);
  };

  const nextPhase = () => {
    const phases: Array<typeof trialState> = ['opening', 'evidence', 'closing', 'verdict'];
    const currentIndex = phases.indexOf(trialState);
    if (currentIndex < phases.length - 1) {
      setTrialState(phases[currentIndex + 1]);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.start();
      setIsRecording(true);
      
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        setIsRecording(false);
        // Processar gravação com IA
        processAudioWithAI();
      };
    } catch (error) {
      console.error('Erro ao acessar microfone:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  const processAudioWithAI = async () => {
    // Simular processamento de IA
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Feedback da IA sobre a argumentação
    const feedback = generateAIFeedback();
    setTrialScore(prev => prev + feedback.score);
  };

  const generateAIFeedback = () => {
    const feedbacks = [
      {
        score: 85,
        message: "Excelente uso de precedentes jurisprudenciais!",
        improvement: "Considere abordar o aspecto constitucional mais profundamente."
      },
      {
        score: 70,
        message: "Boa fundamentação legal.",
        improvement: "Sua argumentação poderia ser mais persuasiva."
      },
      {
        score: 95,
        message: "Argumentação impecável! Uso magistral da doutrina.",
        improvement: "Continue assim!"
      }
    ];
    
    return feedbacks[Math.floor(Math.random() * feedbacks.length)];
  };

  const renderTrialSimulator = () => {
    if (!activeTrial) {
      return (
        <div className="space-y-6">
          <div className="text-center">
            <ScaleIcon className="w-16 h-16 text-blue-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Simulador de Tribunais</h2>
            <p className="text-gray-600 mb-6">
              Pratique suas habilidades jurídicas em simulações realistas com IA
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {mockTrialCases.map((trialCase) => (
              <div key={trialCase.id} className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">{trialCase.title}</h3>
                    <p className="text-gray-600 text-sm mb-3">{trialCase.description}</p>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    trialCase.difficulty === 'beginner' ? 'bg-green-100 text-green-800' :
                    trialCase.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    trialCase.difficulty === 'advanced' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {trialCase.difficulty}
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-sm text-gray-600">
                    <ClockIcon className="w-4 h-4 mr-2" />
                    {trialCase.timeLimit} minutos
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <UserGroupIcon className="w-4 h-4 mr-2" />
                    {trialCase.participants.length} participantes
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <DocumentTextIcon className="w-4 h-4 mr-2" />
                    {trialCase.evidence.length} evidências
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Objetivos de Aprendizado:</h4>
                  <ul className="space-y-1">
                    {trialCase.learningObjectives.map((objective, index) => (
                      <li key={index} className="text-xs text-gray-600 flex items-center">
                        <CheckCircleIcon className="w-3 h-3 mr-2 text-green-500" />
                        {objective}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => startTrial(trialCase, 'prosecutor')}
                    className="flex-1 bg-red-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-red-600 transition-colors"
                  >
                    Promotor
                  </button>
                  <button
                    onClick={() => startTrial(trialCase, 'defense')}
                    className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
                  >
                    Defensor
                  </button>
                  <button
                    onClick={() => startTrial(trialCase, 'observer')}
                    className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-600 transition-colors"
                  >
                    Observar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Header do Tribunal */}
        <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold mb-2">{activeTrial.title}</h2>
              <div className="flex items-center space-x-4 text-sm">
                <span>Fase: {trialState}</span>
                <span>Tempo: {Math.floor(trialTime / 60)}:{(trialTime % 60).toString().padStart(2, '0')}</span>
                <span>Pontuação: {trialScore}</span>
              </div>
            </div>
            <button
              onClick={endTrial}
              className="p-2 hover:bg-blue-600 rounded-full transition-colors"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Área do Tribunal */}
        <div className="p-6">
          <div className="grid grid-cols-12 gap-4 mb-6">
            {/* Juiz */}
            <div className="col-span-12 md:col-span-4 text-center">
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="w-16 h-16 bg-black rounded-full mx-auto mb-2 flex items-center justify-center">
                  <ScaleIcon className="w-8 h-8 text-white" />
                </div>
                <h3 className="font-semibold">Juiz Presidente</h3>
                <p className="text-sm text-gray-600">
                  {activeTrial.participants.find(p => p.role === 'judge')?.name}
                </p>
              </div>
            </div>

            {/* Promotoria */}
            <div className="col-span-6 md:col-span-4">
              <div className={`border-2 rounded-lg p-4 ${userRole === 'prosecutor' ? 'border-red-500 bg-red-50' : 'border-gray-200'}`}>
                <h3 className="font-semibold text-red-700 mb-2">Ministério Público</h3>
                <p className="text-sm text-gray-600">
                  {activeTrial.participants.find(p => p.role === 'prosecutor')?.name}
                </p>
                {currentSpeaker?.role === 'prosecutor' && (
                  <div className="mt-2 flex items-center text-red-600">
                    <SpeakerWaveIcon className="w-4 h-4 mr-1" />
                    <span className="text-xs">Falando...</span>
                  </div>
                )}
              </div>
            </div>

            {/* Defesa */}
            <div className="col-span-6 md:col-span-4">
              <div className={`border-2 rounded-lg p-4 ${userRole === 'defense' ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
                <h3 className="font-semibold text-blue-700 mb-2">Defesa</h3>
                <p className="text-sm text-gray-600">
                  {activeTrial.participants.find(p => p.role === 'defense')?.name}
                </p>
                {currentSpeaker?.role === 'defense' && (
                  <div className="mt-2 flex items-center text-blue-600">
                    <SpeakerWaveIcon className="w-4 h-4 mr-1" />
                    <span className="text-xs">Falando...</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Controles de Fala */}
          {userRole !== 'observer' && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-gray-800">Sua vez de falar</h4>
                  <p className="text-sm text-gray-600">
                    {trialState === 'opening' && 'Apresente suas alegações iniciais'}
                    {trialState === 'evidence' && 'Apresente suas evidências'}
                    {trialState === 'closing' && 'Faça suas considerações finais'}
                  </p>
                </div>
                <div className="flex space-x-2">
                  {!isRecording ? (
                    <button
                      onClick={startRecording}
                      className="flex items-center space-x-2 bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition-colors"
                    >
                      <MicrophoneIcon className="w-4 h-4" />
                      <span>Falar</span>
                    </button>
                  ) : (
                    <button
                      onClick={stopRecording}
                      className="flex items-center space-x-2 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors animate-pulse"
                    >
                      <div className="w-4 h-4 bg-white rounded-full"></div>
                      <span>Parar</span>
                    </button>
                  )}
                  <button
                    onClick={nextPhase}
                    className="bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Próxima Fase
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Evidências */}
          {trialState === 'evidence' && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-800 mb-3">Evidências Disponíveis</h4>
              <div className="grid md:grid-cols-2 gap-3">
                {activeTrial.evidence.map((evidence) => (
                  <div key={evidence.id} className="bg-white border rounded-lg p-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <h5 className="font-medium text-gray-800">{evidence.title}</h5>
                        <p className="text-sm text-gray-600">{evidence.description}</p>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs ${
                        evidence.admissible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {evidence.admissible ? 'Admissível' : 'Inadmissível'}
                      </div>
                    </div>
                    <div className="mt-2 flex items-center">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${evidence.relevance * 10}%` }}
                        ></div>
                      </div>
                      <span className="ml-2 text-xs text-gray-500">
                        Relevância: {evidence.relevance}/10
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderAIAssistant = () => (
    <div className="space-y-6">
      <div className="text-center">
        <CpuChipIcon className="w-16 h-16 text-purple-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Assistente Jurídico IA</h2>
        <p className="text-gray-600 mb-6">
          IA especializada em análise jurídica e pesquisa de precedentes
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <DocumentTextIcon className="w-8 h-8 text-blue-500 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Análise de Contratos</h3>
          <p className="text-gray-600 text-sm mb-4">
            Upload de contratos para análise automática de cláusulas e riscos
          </p>
          <button className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors">
            Analisar Contrato
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <ScaleIcon className="w-8 h-8 text-green-500 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Pesquisa Jurisprudencial</h3>
          <p className="text-gray-600 text-sm mb-4">
            IA que busca precedentes relevantes em segundos
          </p>
          <button className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition-colors">
            Pesquisar Casos
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <ChatBubbleLeftRightIcon className="w-8 h-8 text-purple-500 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Consultor Virtual</h3>
          <p className="text-gray-600 text-sm mb-4">
            Chat com IA especializada em diferentes áreas do direito
          </p>
          <button className="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition-colors">
            Iniciar Chat
          </button>
        </div>
      </div>
    </div>
  );

  const renderCaseAnalyzer = () => (
    <div className="space-y-6">
      <div className="text-center">
        <BeakerIcon className="w-16 h-16 text-orange-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Analisador de Casos</h2>
        <p className="text-gray-600 mb-6">
          Ferramenta avançada para análise de casos complexos
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Upload de Processo</h3>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">Arraste e solte os arquivos do processo aqui</p>
          <button className="bg-orange-500 text-white py-2 px-6 rounded-lg hover:bg-orange-600 transition-colors">
            Selecionar Arquivos
          </button>
        </div>
      </div>
    </div>
  );

  const renderContractGenerator = () => (
    <div className="space-y-6">
      <div className="text-center">
        <RocketLaunchIcon className="w-16 h-16 text-blue-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Gerador de Contratos</h2>
        <p className="text-gray-600 mb-6">
          Crie contratos personalizados com IA jurídica
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Tipos de Contrato</h3>
          <div className="space-y-2">
            {[
              'Contrato de Trabalho',
              'Contrato de Locação',
              'Contrato de Prestação de Serviços',
              'Contrato de Compra e Venda',
              'Contrato de Sociedade',
              'Contrato de Confidencialidade'
            ].map((type, index) => (
              <button
                key={index}
                className="w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Configurações</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Partes Envolvidas
              </label>
              <input 
                type="number" 
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="Número de partes"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Complexidade
              </label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option>Simples</option>
                <option>Intermediário</option>
                <option>Complexo</option>
              </select>
            </div>
            <button className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors">
              Gerar Contrato
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Legal Tech Lab</h1>
          <p className="text-gray-600">
            Laboratório de tecnologia jurídica avançada com IA
          </p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-lg">
            <div className="flex space-x-1">
              {[
                { id: 'simulator', name: 'Simulador', icon: ScaleIcon },
                { id: 'ai_assistant', name: 'IA Jurídica', icon: CpuChipIcon },
                { id: 'case_analyzer', name: 'Analisador', icon: BeakerIcon },
                { id: 'contract_gen', name: 'Contratos', icon: RocketLaunchIcon }
              ].map((tool) => (
                <button
                  key={tool.id}
                  onClick={() => setCurrentTool(tool.id as any)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    currentTool === tool.id
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <tool.icon className="w-4 h-4" />
                  <span className="font-medium">{tool.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div>
          {currentTool === 'simulator' && renderTrialSimulator()}
          {currentTool === 'ai_assistant' && renderAIAssistant()}
          {currentTool === 'case_analyzer' && renderCaseAnalyzer()}
          {currentTool === 'contract_gen' && renderContractGenerator()}
        </div>
      </div>
    </div>
  );
};

export default LegalTechLab; 