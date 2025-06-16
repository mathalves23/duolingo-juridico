import React, { useState, useRef, useEffect } from 'react';
import {
  CameraIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  EyeIcon,
  CubeTransparentIcon,
  SparklesIcon,
  DocumentTextIcon,
  ScaleIcon,
  BuildingLibraryIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

interface ARObject {
  id: string;
  type: 'constitution' | 'law' | 'court' | 'concept' | 'timeline' | 'diagram';
  title: string;
  description: string;
  content: any;
  position: { x: number; y: number; z: number };
  scale: number;
  rotation: { x: number; y: number; z: number };
}

interface ARScene {
  id: string;
  name: string;
  description: string;
  objects: ARObject[];
  background?: string;
  lighting?: string;
}

const ARLearning: React.FC = () => {
  const [isARActive, setIsARActive] = useState(false);
  const [currentScene, setCurrentScene] = useState<ARScene | null>(null);
  const [selectedObject, setSelectedObject] = useState<ARObject | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deviceSupported, setDeviceSupported] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    checkARSupport();
    return () => {
      stopCamera();
    };
  }, []);

  const checkARSupport = async () => {
    try {
      // Verificar suporte a WebRTC e getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError('Seu dispositivo não suporta acesso à câmera');
        return;
      }

      // Verificar suporte a WebXR (quando disponível)
      if ('xr' in navigator) {
        const xr = (navigator as any).xr;
        if (xr) {
          const supported = await xr.isSessionSupported('immersive-ar');
          setDeviceSupported(supported);
        }
      }

      // Para demonstração, considerar como suportado
      setDeviceSupported(true);
    } catch (error) {
      console.error('Erro ao verificar suporte AR:', error);
      setError('Erro ao verificar compatibilidade');
    }
  };

  const startCamera = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', 
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        await videoRef.current.play();
        setIsARActive(true);
        
        // Iniciar com cena padrão
        loadScene('constitutional-basics');
      }
    } catch (error) {
      console.error('Erro ao acessar câmera:', error);
      setError('Não foi possível acessar a câmera. Verifique as permissões.');
    } finally {
      setIsLoading(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsARActive(false);
    setCurrentScene(null);
    setSelectedObject(null);
  };

  const loadScene = (sceneId: string) => {
    const scenes: Record<string, ARScene> = {
      'constitutional-basics': {
        id: 'constitutional-basics',
        name: 'Direito Constitucional Básico',
        description: 'Fundamentos da Constituição Federal',
        objects: [
          {
            id: 'cf88-structure',
            type: 'constitution',
            title: 'Estrutura da CF/88',
            description: 'Visualização 3D da estrutura da Constituição Federal',
            content: {
              titles: [
                'Título I - Dos Princípios Fundamentais',
                'Título II - Dos Direitos e Garantias Fundamentais',
                'Título III - Da Organização do Estado',
                'Título IV - Da Organização dos Poderes',
                'Título V - Da Defesa do Estado e das Instituições Democráticas'
              ],
              totalArticles: 250,
              amendments: 118
            },
            position: { x: 0, y: 0, z: -2 },
            scale: 1,
            rotation: { x: 0, y: 0, z: 0 }
          },
          {
            id: 'fundamental-rights',
            type: 'concept',
            title: 'Direitos Fundamentais',
            description: 'Árvore interativa dos direitos fundamentais',
            content: {
              categories: [
                'Direitos Individuais',
                'Direitos Coletivos',
                'Direitos Sociais',
                'Direitos de Nacionalidade',
                'Direitos Políticos'
              ],
              keyArticles: ['Art. 5º', 'Art. 6º', 'Art. 12º', 'Art. 14º']
            },
            position: { x: 2, y: 0, z: -2 },
            scale: 0.8,
            rotation: { x: 0, y: -30, z: 0 }
          },
          {
            id: 'separation-powers',
            type: 'diagram',
            title: 'Separação dos Poderes',
            description: 'Diagrama interativo da separação de poderes',
            content: {
              powers: [
                {
                  name: 'Poder Executivo',
                  function: 'Administrar e executar leis',
                  head: 'Presidente da República',
                  color: '#EF4444'
                },
                {
                  name: 'Poder Legislativo',
                  function: 'Criar e aprovar leis',
                  head: 'Congresso Nacional',
                  color: '#3B82F6'
                },
                {
                  name: 'Poder Judiciário',
                  function: 'Interpretar e aplicar leis',
                  head: 'Supremo Tribunal Federal',
                  color: '#10B981'
                }
              ]
            },
            position: { x: -2, y: 0, z: -2 },
            scale: 1.2,
            rotation: { x: 0, y: 30, z: 0 }
          }
        ]
      },
      'administrative-law': {
        id: 'administrative-law',
        name: 'Direito Administrativo',
        description: 'Princípios e conceitos do Direito Administrativo',
        objects: [
          {
            id: 'limpe-principles',
            type: 'concept',
            title: 'Princípios LIMPE',
            description: 'Visualização dos princípios da Administração Pública',
            content: {
              principles: [
                { letter: 'L', name: 'Legalidade', description: 'A administração só pode fazer o que a lei permite' },
                { letter: 'I', name: 'Impessoalidade', description: 'Tratamento igual para todos' },
                { letter: 'M', name: 'Moralidade', description: 'Atos devem ser éticos e honestos' },
                { letter: 'P', name: 'Publicidade', description: 'Transparência dos atos' },
                { letter: 'E', name: 'Eficiência', description: 'Melhor relação custo-benefício' }
              ]
            },
            position: { x: 0, y: 0, z: -1.5 },
            scale: 1,
            rotation: { x: 0, y: 0, z: 0 }
          }
        ]
      }
    };

    const scene = scenes[sceneId];
    if (scene) {
      setCurrentScene(scene);
      // Animar entrada dos objetos
      setTimeout(() => {
        scene.objects.forEach((obj, index) => {
          setTimeout(() => {
            // Animação de entrada personalizada para cada objeto
          }, index * 500);
        });
      }, 100);
    }
  };

  const handleObjectClick = (object: ARObject) => {
    setSelectedObject(object);
  };

  const renderARObject = (object: ARObject) => {
    const baseStyle: React.CSSProperties = {
      position: 'absolute',
      left: `${50 + object.position.x * 10}%`,
      top: `${50 + object.position.y * 10}%`,
      transform: `translate(-50%, -50%) scale(${object.scale}) rotateY(${object.rotation.y}deg)`,
      transition: 'all 0.5s ease-in-out',
      cursor: 'pointer',
      zIndex: 10
    };

    const iconMap = {
      constitution: BookOpenIcon,
      law: ScaleIcon,
      court: BuildingLibraryIcon,
      concept: AcademicCapIcon,
      timeline: DocumentTextIcon,
      diagram: CubeTransparentIcon
    };

    const IconComponent = iconMap[object.type];

    return (
      <div
        key={object.id}
        style={baseStyle}
        onClick={() => handleObjectClick(object)}
        className="bg-white bg-opacity-90 backdrop-blur-sm rounded-xl p-4 shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-300"
      >
        <div className="text-center">
          <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <IconComponent className="w-6 h-6 text-white" />
          </div>
          <h3 className="text-sm font-semibold text-gray-800 mb-1">{object.title}</h3>
          <p className="text-xs text-gray-600">{object.description}</p>
          <div className="mt-2 flex justify-center space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>
      </div>
    );
  };

  const renderObjectDetails = () => {
    if (!selectedObject) return null;

    return (
      <div className="absolute bottom-4 left-4 right-4 bg-white bg-opacity-95 backdrop-blur-sm rounded-xl p-4 shadow-xl max-h-64 overflow-y-auto">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-bold text-gray-800">{selectedObject.title}</h3>
          <button
            onClick={() => setSelectedObject(null)}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <XMarkIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="space-y-3">
          {selectedObject.type === 'constitution' && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Estrutura da Constituição:</h4>
              <ul className="space-y-1">
                {selectedObject.content.titles.map((title: string, index: number) => (
                  <li key={index} className="text-sm text-gray-600 flex items-center">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                    {title}
                  </li>
                ))}
              </ul>
              <div className="mt-3 grid grid-cols-2 gap-4 text-center">
                <div className="bg-blue-50 p-2 rounded">
                  <div className="text-xl font-bold text-blue-600">{selectedObject.content.totalArticles}</div>
                  <div className="text-xs text-gray-600">Artigos</div>
                </div>
                <div className="bg-green-50 p-2 rounded">
                  <div className="text-xl font-bold text-green-600">{selectedObject.content.amendments}</div>
                  <div className="text-xs text-gray-600">Emendas</div>
                </div>
              </div>
            </div>
          )}

          {selectedObject.type === 'concept' && selectedObject.id === 'fundamental-rights' && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Categorias de Direitos:</h4>
              <div className="grid grid-cols-2 gap-2">
                {selectedObject.content.categories.map((category: string, index: number) => (
                  <div key={index} className="bg-gray-50 p-2 rounded text-sm text-center">
                    {category}
                  </div>
                ))}
              </div>
              <div className="mt-3">
                <h5 className="font-semibold text-gray-600 mb-1">Artigos-chave:</h5>
                <div className="flex space-x-2">
                  {selectedObject.content.keyArticles.map((article: string, index: number) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                      {article}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {selectedObject.type === 'diagram' && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Os Três Poderes:</h4>
              <div className="space-y-2">
                {selectedObject.content.powers.map((power: any, index: number) => (
                  <div key={index} className="border rounded-lg p-3" style={{ borderColor: power.color }}>
                    <div className="flex items-center mb-1">
                      <div 
                        className="w-3 h-3 rounded-full mr-2" 
                        style={{ backgroundColor: power.color }}
                      ></div>
                      <h5 className="font-semibold text-gray-800">{power.name}</h5>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">{power.function}</p>
                    <p className="text-xs text-gray-500">Chefia: {power.head}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedObject.type === 'concept' && selectedObject.id === 'limpe-principles' && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Princípios da Administração Pública:</h4>
              <div className="space-y-2">
                {selectedObject.content.principles.map((principle: any, index: number) => (
                  <div key={index} className="bg-gray-50 p-3 rounded-lg">
                    <div className="flex items-center mb-1">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                        {principle.letter}
                      </div>
                      <h5 className="font-semibold text-gray-800">{principle.name}</h5>
                    </div>
                    <p className="text-sm text-gray-600 ml-11">{principle.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="mt-4 flex space-x-2">
          <button className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors">
            Estudar Mais
          </button>
          <button className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
            Fazer Quiz
          </button>
        </div>
      </div>
    );
  };

  if (!deviceSupported) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <CubeTransparentIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">AR não suportado</h2>
          <p className="text-gray-500 mb-4">
            Seu dispositivo não suporta recursos de Realidade Aumentada ou não tem câmera disponível.
          </p>
          <div className="text-sm text-gray-400">
            <p>Requisitos mínimos:</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Câmera traseira</li>
              <li>Navegador moderno</li>
              <li>Conexão HTTPS</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (!isARActive) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
        <div className="text-center text-white max-w-md">
          <div className="mb-8">
            <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CubeTransparentIcon className="w-12 h-12" />
            </div>
            <h1 className="text-2xl font-bold mb-2">Aprendizado em AR</h1>
            <p className="text-blue-100 mb-6">
              Explore conceitos jurídicos em realidade aumentada. Visualize a Constituição, 
              entenda princípios e interaja com conteúdo 3D.
            </p>
          </div>

          <div className="space-y-4 mb-8">
            <div className="flex items-center justify-center space-x-3 text-sm">
              <SparklesIcon className="w-5 h-5" />
              <span>Visualização 3D interativa</span>
            </div>
            <div className="flex items-center justify-center space-x-3 text-sm">
              <EyeIcon className="w-5 h-5" />
              <span>Exploração imersiva</span>
            </div>
            <div className="flex items-center justify-center space-x-3 text-sm">
              <ChatBubbleLeftRightIcon className="w-5 h-5" />
              <span>Conteúdo explicativo</span>
            </div>
          </div>

          {error && (
            <div className="bg-red-500 bg-opacity-20 border border-red-300 rounded-lg p-3 mb-4">
              <p className="text-sm">{error}</p>
            </div>
          )}

          <button
            onClick={startCamera}
            disabled={isLoading}
            className="w-full bg-white text-blue-600 py-3 px-6 rounded-lg font-semibold hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                <span>Iniciando câmera...</span>
              </>
            ) : (
              <>
                <CameraIcon className="w-5 h-5" />
                <span>Iniciar AR</span>
              </>
            )}
          </button>

          <div className="mt-6 text-xs text-blue-200 space-y-1">
            <p>🔒 Sua privacidade é protegida</p>
            <p>📱 Funciona melhor em dispositivos móveis</p>
            <p>🌐 Requer permissão de câmera</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black">
      {/* Vídeo da câmera */}
      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover"
        autoPlay
        playsInline
        muted
      />

      {/* Canvas para processamento AR */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
      />

      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-black bg-opacity-50 backdrop-blur-sm p-4 z-20">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-white text-sm font-medium">
              {currentScene?.name || 'Carregando cena...'}
            </span>
          </div>
          <button
            onClick={stopCamera}
            className="p-2 bg-red-500 hover:bg-red-600 rounded-full transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>

      {/* Cenas disponíveis */}
      <div className="absolute top-20 right-4 space-y-2 z-20">
        <button
          onClick={() => loadScene('constitutional-basics')}
          className={`block w-12 h-12 rounded-full shadow-lg transition-colors ${
            currentScene?.id === 'constitutional-basics' 
              ? 'bg-blue-500 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
          title="Direito Constitucional"
        >
          <BookOpenIcon className="w-6 h-6 mx-auto" />
        </button>
        <button
          onClick={() => loadScene('administrative-law')}
          className={`block w-12 h-12 rounded-full shadow-lg transition-colors ${
            currentScene?.id === 'administrative-law' 
              ? 'bg-green-500 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
          title="Direito Administrativo"
        >
          <ScaleIcon className="w-6 h-6 mx-auto" />
        </button>
      </div>

      {/* Objetos AR */}
      <div className="absolute inset-0">
        {currentScene?.objects.map(renderARObject)}
      </div>

      {/* Detalhes do objeto selecionado */}
      {renderObjectDetails()}

      {/* Instruções */}
      {!selectedObject && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 backdrop-blur-sm rounded-lg px-4 py-2 z-20">
          <p className="text-white text-sm text-center">
            <MagnifyingGlassIcon className="w-4 h-4 inline mr-1" />
            Toque nos objetos para explorar
          </p>
        </div>
      )}
    </div>
  );
};

export default ARLearning; 