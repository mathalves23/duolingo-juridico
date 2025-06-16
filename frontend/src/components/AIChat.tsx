import React, { useState, useRef, useEffect } from 'react';
import {
  PaperAirplaneIcon,
  MicrophoneIcon,
  StopIcon,
  SparklesIcon,
  UserIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';

interface AIChatProps {
  isOpen?: boolean;
  onClose?: () => void;
  context?: any;
}

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

interface QuickAction {
  id: string;
  label: string;
  prompt: string;
  icon?: string;
}

const AIChat: React.FC<AIChatProps> = ({ isOpen = true, onClose, context }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Olá! Sou seu assistente jurídico inteligente. Como posso ajudá-lo hoje? Posso explicar conceitos, tirar dúvidas sobre questões ou ajudar com estratégias de estudo.',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  const quickActions: QuickAction[] = [
    {
      id: '1',
      label: 'Explicar esta questão',
      prompt: 'Você pode me explicar esta questão de forma simples?',
      icon: '📚'
    },
    {
      id: '2',
      label: 'Dicas de estudo',
      prompt: 'Que dicas você tem para melhorar meus estudos neste tópico?',
      icon: '💡'
    },
    {
      id: '3',
      label: 'Conceitos relacionados',
      prompt: 'Quais conceitos estão relacionados a esta matéria?',
      icon: '🔗'
    },
    {
      id: '4',
      label: 'Motivação',
      prompt: 'Preciso de algumas palavras motivacionais para continuar estudando!',
      icon: '🚀'
    }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Inicializar Web Speech API se disponível
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'pt-BR';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateAIResponse = async (userMessage: string): Promise<string> => {
    // Simular resposta da IA baseada no contexto
    const responses = [
      'Excelente pergunta! Com base no contexto da questão sobre Direito Constitucional, posso explicar que...',
      'Vejo que você está estudando um tópico importante. Deixe-me explicar de forma clara...',
      'Esta é uma área fundamental do direito. Para entender melhor, considere que...',
      'Ótima questão para aprofundar seus conhecimentos! O conceito principal aqui é...',
      'Com base em seu progresso atual, recomendo focar nos seguintes pontos...'
    ];

    return new Promise((resolve) => {
      setTimeout(() => {
        const response = responses[Math.floor(Math.random() * responses.length)] + 
        " Neste caso específico, a legislação estabelece critérios claros que devem ser observados. " +
        "Lembre-se de sempre verificar a fonte normativa e a jurisprudência atualizada sobre o tema.";
        resolve(response);
      }, 1500);
    });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const aiResponse = await generateAIResponse(inputMessage);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Erro ao gerar resposta da IA:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: 'Desculpe, houve um erro ao processar sua mensagem. Tente novamente.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickAction = (action: QuickAction) => {
    setInputMessage(action.prompt);
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true);
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      setIsListening(false);
      recognitionRef.current.stop();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (!isOpen) return null;

  return (
    <div className="flex flex-col h-96 bg-white rounded-lg border shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <SparklesIcon className="w-5 h-5" />
          <h3 className="font-semibold">Assistente Jurídico IA</h3>
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
          >
            ✕
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.type === 'ai' && (
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                <ComputerDesktopIcon className="w-4 h-4 text-white" />
              </div>
            )}
            
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              message.type === 'user' 
                ? 'bg-blue-500 text-white ml-auto' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              <p className="text-sm">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {formatTime(message.timestamp)}
              </p>
            </div>

            {message.type === 'user' && (
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                <UserIcon className="w-4 h-4 text-gray-600" />
              </div>
            )}
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <ComputerDesktopIcon className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="p-3 border-t bg-gray-50">
        <div className="grid grid-cols-2 gap-2 mb-3">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => handleQuickAction(action)}
              className="text-xs p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
            >
              <span className="mr-1">{action.icon}</span>
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Digite sua pergunta..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
            />
            
            {/* Voice Input Button */}
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={!recognitionRef.current}
              className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded transition-colors ${
                isListening 
                  ? 'text-red-500 hover:text-red-600' 
                  : 'text-gray-400 hover:text-gray-600'
              } disabled:opacity-50`}
            >
              {isListening ? (
                <StopIcon className="w-4 h-4" />
              ) : (
                <MicrophoneIcon className="w-4 h-4" />
              )}
            </button>
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>

        {isListening && (
          <div className="mt-2 text-xs text-red-600 flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            Escutando... Fale agora
          </div>
        )}
      </div>
    </div>
  );
};

export default AIChat; 