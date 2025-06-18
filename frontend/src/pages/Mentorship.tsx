import React, { useState } from 'react';
import {
  UserGroupIcon,
  StarIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  VideoCameraIcon,
  CalendarIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  MapPinIcon,
  CheckBadgeIcon,
  HeartIcon,
  PhoneIcon,
  EnvelopeIcon,
  GlobeAltIcon,
  TrophyIcon,
  BookOpenIcon,
  LightBulbIcon,
  UserPlusIcon,
  UserIcon,
  MagnifyingGlassIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import {
  StarIcon as StarSolid,
  HeartIcon as HeartSolid,
  CheckBadgeIcon as CheckBadgeSolid
} from '@heroicons/react/24/solid';
import Card from '../components/Card';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

interface Mentor {
  id: string;
  name: string;
  title: string;
  specialties: string[];
  experience: number;
  rating: number;
  totalReviews: number;
  location: string;
  avatar: string;
  bio: string;
  education: string[];
  certifications: string[];
  languages: string[];
  hourlyRate?: number;
  availability: 'available' | 'busy' | 'offline';
  responseTime: string;
  totalSessions: number;
  isVerified: boolean;
  isPremium: boolean;
  socialLinks: {
    linkedin?: string;
    website?: string;
    email?: string;
  };
  skills: string[];
  achievements: string[];
}

interface Session {
  id: string;
  mentorId: string;
  mentorName: string;
  date: Date;
  duration: number;
  type: 'video' | 'audio' | 'chat';
  status: 'scheduled' | 'completed' | 'cancelled';
  topic: string;
  rating?: number;
  feedback?: string;
  price: number;
}

interface MentorshipProgram {
  id: string;
  title: string;
  description: string;
  mentor: string;
  duration: string;
  sessions: number;
  price: number;
  level: 'iniciante' | 'intermediario' | 'avancado';
  topics: string[];
  rating: number;
  enrollments: number;
}

const Mentorship: React.FC = () => {
  const { user } = useAuth();
  const { success, info } = useNotification();
  const [activeTab, setActiveTab] = useState<'mentors' | 'programs' | 'sessions' | 'network'>('mentors');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedMentor, setSelectedMentor] = useState<Mentor | null>(null);

  const [filters, setFilters] = useState({
    specialty: '',
    experience: '',
    rating: '',
    availability: '',
    priceRange: '',
    location: ''
  });

  const [mentors] = useState<Mentor[]>([
    {
      id: '1',
      name: 'Dr. Carlos Eduardo Silva',
      title: 'Advogado Sênior e Professor de Direito',
      specialties: ['Direito Civil', 'Direito Empresarial', 'Contratos'],
      experience: 15,
      rating: 4.9,
      totalReviews: 247,
      location: 'São Paulo, SP',
      avatar: '👨‍💼',
      bio: 'Advogado com mais de 15 anos de experiência em direito empresarial e civil. Professor universitário e autor de diversos artigos jurídicos. Especialista em contratos complexos e consultoria empresarial.',
      education: ['Direito - USP', 'Mestrado em Direito Civil - PUC-SP'],
      certifications: ['OAB-SP', 'Especialista em Direito Empresarial'],
      languages: ['Português', 'Inglês', 'Espanhol'],
      hourlyRate: 250,
      availability: 'available',
      responseTime: '2h em média',
      totalSessions: 892,
      isVerified: true,
      isPremium: true,
      socialLinks: {
        linkedin: 'linkedin.com/in/carlos-silva',
        website: 'carlossilva.adv.br',
        email: 'carlos@exemplo.com'
      },
      skills: ['Negociação', 'Mediação', 'Consultoria Empresarial', 'Redação Jurídica'],
      achievements: ['Top 1% Mentores 2023', 'Melhor Avaliação do Ano', '500+ Sessões Concluídas']
    },
    {
      id: '2',
      name: 'Dra. Ana Paula Ferreira',
      title: 'Procuradora Federal e Especialista em Direito Público',
      specialties: ['Direito Administrativo', 'Direito Constitucional', 'Concursos Públicos'],
      experience: 12,
      rating: 4.8,
      totalReviews: 189,
      location: 'Brasília, DF',
      avatar: '👩‍💼',
      bio: 'Procuradora Federal com vasta experiência em direito público. Especialista em preparação para concursos jurídicos e consultoria em direito administrativo.',
      education: ['Direito - UnB', 'Especialização em Direito Público - FGV'],
      certifications: ['OAB-DF', 'Procuradora Federal'],
      languages: ['Português', 'Inglês'],
      hourlyRate: 200,
      availability: 'available',
      responseTime: '1h em média',
      totalSessions: 654,
      isVerified: true,
      isPremium: false,
      socialLinks: {
        linkedin: 'linkedin.com/in/ana-ferreira',
        email: 'ana@exemplo.com'
      },
      skills: ['Concursos Públicos', 'Direito Administrativo', 'Pareceres Jurídicos'],
      achievements: ['Especialista Certificada', 'Mentora do Ano 2022']
    },
    {
      id: '3',
      name: 'Dr. Roberto Mendes',
      title: 'Defensor Público e Especialista em Direitos Humanos',
      specialties: ['Direito Penal', 'Direitos Humanos', 'Processo Penal'],
      experience: 8,
      rating: 4.7,
      totalReviews: 156,
      location: 'Rio de Janeiro, RJ',
      avatar: '👨‍⚖️',
      bio: 'Defensor Público com experiência em direito penal e direitos humanos. Apaixonado por justiça social e formação de novos advogados.',
      education: ['Direito - UERJ', 'Mestrado em Direitos Humanos - PUC-Rio'],
      certifications: ['OAB-RJ', 'Defensor Público'],
      languages: ['Português'],
      hourlyRate: 150,
      availability: 'busy',
      responseTime: '4h em média',
      totalSessions: 423,
      isVerified: true,
      isPremium: false,
      socialLinks: {
        linkedin: 'linkedin.com/in/roberto-mendes'
      },
      skills: ['Defesa Criminal', 'Direitos Humanos', 'Advocacy'],
      achievements: ['Defensor do Ano 2021', 'Especialista em Direitos Humanos']
    }
  ]);

  const [programs] = useState<MentorshipProgram[]>([
    {
      id: '1',
      title: 'Preparação Completa para OAB',
      description: 'Programa intensivo de 3 meses para aprovação no exame da OAB com mentoria personalizada.',
      mentor: 'Dr. Carlos Eduardo Silva',
      duration: '3 meses',
      sessions: 12,
      price: 1800,
      level: 'intermediario',
      topics: ['Direito Civil', 'Direito Penal', 'Direito Constitucional', 'Ética Profissional'],
      rating: 4.9,
      enrollments: 89
    },
    {
      id: '2',
      title: 'Carreira em Concursos Públicos',
      description: 'Mentoria especializada para quem quer seguir carreira pública na área jurídica.',
      mentor: 'Dra. Ana Paula Ferreira',
      duration: '6 meses',
      sessions: 20,
      price: 2400,
      level: 'avancado',
      topics: ['Direito Administrativo', 'Direito Constitucional', 'Estratégia de Estudos'],
      rating: 4.8,
      enrollments: 67
    },
    {
      id: '3',
      title: 'Primeiros Passos no Direito',
      description: 'Programa introdutório para estudantes de direito e recém-formados.',
      mentor: 'Dr. Roberto Mendes',
      duration: '2 meses',
      sessions: 8,
      price: 800,
      level: 'iniciante',
      topics: ['Fundamentos do Direito', 'Ética Profissional', 'Carreira Jurídica'],
      rating: 4.7,
      enrollments: 124
    }
  ]);

  const [sessions] = useState<Session[]>([
    {
      id: '1',
      mentorId: '1',
      mentorName: 'Dr. Carlos Eduardo Silva',
      date: new Date('2024-01-25T14:00:00'),
      duration: 60,
      type: 'video',
      status: 'scheduled',
      topic: 'Revisão de Contratos Empresariais',
      price: 250
    },
    {
      id: '2',
      mentorId: '2',
      mentorName: 'Dra. Ana Paula Ferreira',
      date: new Date('2024-01-20T10:00:00'),
      duration: 90,
      type: 'video',
      status: 'completed',
      topic: 'Preparação para Concurso de Procurador',
      rating: 5,
      feedback: 'Excelente sessão! Muito esclarecedora sobre estratégias de estudo.',
      price: 300
    }
  ]);

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case 'available': return 'text-green-600 bg-green-100';
      case 'busy': return 'text-yellow-600 bg-yellow-100';
      case 'offline': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAvailabilityText = (availability: string) => {
    switch (availability) {
      case 'available': return 'Disponível';
      case 'busy': return 'Ocupado';
      case 'offline': return 'Offline';
      default: return 'Indisponível';
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'iniciante': return 'text-green-600 bg-green-100';
      case 'intermediario': return 'text-yellow-600 bg-yellow-100';
      case 'avancado': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const bookSession = (mentor: Mentor) => {
    success(
      'Solicitação Enviada! 📅',
      `Sua solicitação de mentoria com ${mentor.name} foi enviada. Você receberá uma confirmação em breve.`
    );
  };

  const joinProgram = (program: MentorshipProgram) => {
    success(
      'Inscrição Realizada! 🎓',
      `Você se inscreveu no programa "${program.title}". Acesse sua área de programas para mais detalhes.`
    );
  };

  const renderMentors = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Mentores Disponíveis</h2>
          <p className="text-gray-600">Conecte-se com profissionais experientes</p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <FunnelIcon className="w-4 h-4" />
          Filtros
        </button>
      </div>

      {showFilters && (
        <Card className="p-6">
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Especialidade</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Todas as especialidades</option>
                <option value="civil">Direito Civil</option>
                <option value="penal">Direito Penal</option>
                <option value="empresarial">Direito Empresarial</option>
                <option value="administrativo">Direito Administrativo</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Experiência</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Qualquer experiência</option>
                <option value="5">5+ anos</option>
                <option value="10">10+ anos</option>
                <option value="15">15+ anos</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Disponibilidade</label>
              <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">Qualquer status</option>
                <option value="available">Disponível</option>
                <option value="busy">Ocupado</option>
              </select>
            </div>
          </div>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        {mentors.map((mentor) => (
          <Card key={mentor.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start gap-4">
              <div className="relative">
                <div className="text-4xl">{mentor.avatar}</div>
                {mentor.isVerified && (
                  <CheckBadgeSolid className="absolute -top-1 -right-1 w-5 h-5 text-blue-500" />
                )}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-lg font-semibold text-gray-900">{mentor.name}</h3>
                  {mentor.isPremium && (
                    <span className="text-xs bg-gold-100 text-gold-800 px-2 py-1 rounded-full font-medium">
                      PRO
                    </span>
                  )}
                </div>
                
                <p className="text-sm text-gray-600 mb-2">{mentor.title}</p>
                
                <div className="flex items-center gap-4 mb-3 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <BriefcaseIcon className="w-4 h-4" />
                    {mentor.experience} anos
                  </div>
                  <div className="flex items-center gap-1">
                    <StarSolid className="w-4 h-4 text-yellow-500" />
                    {mentor.rating} ({mentor.totalReviews})
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPinIcon className="w-4 h-4" />
                    {mentor.location}
                  </div>
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${getAvailabilityColor(mentor.availability)}`}>
                    {getAvailabilityText(mentor.availability)}
                  </span>
                  <span className="text-xs text-gray-500">
                    Responde em {mentor.responseTime}
                  </span>
                </div>

                <div className="mb-3">
                  <p className="text-sm text-gray-600 line-clamp-2">{mentor.bio}</p>
                </div>

                <div className="flex flex-wrap gap-1 mb-4">
                  {mentor.specialties.slice(0, 3).map((specialty, index) => (
                    <span key={index} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {specialty}
                    </span>
                  ))}
                  {mentor.specialties.length > 3 && (
                    <span className="text-xs text-gray-500">+{mentor.specialties.length - 3}</span>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm">
                    <span className="font-semibold text-gray-900">R$ {mentor.hourlyRate}</span>
                    <span className="text-gray-500">/hora</span>
                  </div>
                  
                  <div className="flex gap-2">
                    <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors text-sm">
                      Ver Perfil
                    </button>
                    <button
                      onClick={() => bookSession(mentor)}
                      className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors text-sm"
                    >
                      Agendar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderPrograms = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Programas de Mentoria</h2>
        <p className="text-gray-600">Programas estruturados para seu desenvolvimento profissional</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {programs.map((program) => (
          <Card key={program.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{program.title}</h3>
              <p className="text-sm text-gray-600 mb-3">{program.description}</p>
              
              <div className="flex items-center gap-2 mb-3">
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getLevelColor(program.level)}`}>
                  {program.level}
                </span>
                <div className="flex items-center gap-1">
                  <StarSolid className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm">{program.rating}</span>
                </div>
              </div>

              <div className="space-y-2 mb-4 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <UserIcon className="w-4 h-4" />
                  <span>{program.mentor}</span>
                </div>
                <div className="flex items-center gap-2">
                  <ClockIcon className="w-4 h-4" />
                  <span>{program.duration} • {program.sessions} sessões</span>
                </div>
                <div className="flex items-center gap-2">
                  <UserGroupIcon className="w-4 h-4" />
                  <span>{program.enrollments} inscritos</span>
                </div>
              </div>

              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Tópicos abordados:</h4>
                <div className="flex flex-wrap gap-1">
                  {program.topics.map((topic, index) => (
                    <span key={index} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <span className="text-2xl font-bold text-gray-900">R$ {program.price.toLocaleString()}</span>
                  <span className="text-sm text-gray-500 block">ou 12x de R$ {Math.round(program.price / 12)}</span>
                </div>
                
                <button
                  onClick={() => joinProgram(program)}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Inscrever-se
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderSessions = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Minhas Sessões</h2>
        <p className="text-gray-600">Histórico e agendamentos de mentoria</p>
      </div>

      <div className="space-y-4">
        {sessions.map((session) => (
          <Card key={session.id} className="p-6">
            <div className="flex items-center gap-4">
              <div className="text-3xl">👨‍💼</div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-lg font-semibold text-gray-900">{session.mentorName}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    session.status === 'completed' ? 'text-green-600 bg-green-100' :
                    session.status === 'scheduled' ? 'text-blue-600 bg-blue-100' :
                    'text-red-600 bg-red-100'
                  }`}>
                    {session.status === 'completed' ? 'Concluída' :
                     session.status === 'scheduled' ? 'Agendada' : 'Cancelada'}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-2">{session.topic}</p>
                
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <CalendarIcon className="w-4 h-4" />
                    {session.date.toLocaleDateString('pt-BR')} às {session.date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="flex items-center gap-1">
                    <ClockIcon className="w-4 h-4" />
                    {session.duration} min
                  </div>
                  <div className="flex items-center gap-1">
                    {session.type === 'video' ? <VideoCameraIcon className="w-4 h-4" /> :
                     session.type === 'audio' ? <PhoneIcon className="w-4 h-4" /> :
                     <ChatBubbleLeftRightIcon className="w-4 h-4" />}
                    {session.type === 'video' ? 'Videoconferência' :
                     session.type === 'audio' ? 'Áudio' : 'Chat'}
                  </div>
                </div>

                {session.rating && (
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <StarSolid key={i} className={`w-4 h-4 ${i < session.rating! ? 'text-yellow-500' : 'text-gray-300'}`} />
                      ))}
                    </div>
                    {session.feedback && (
                      <span className="text-sm text-gray-600">"{session.feedback}"</span>
                    )}
                  </div>
                )}
              </div>
              
              <div className="text-right">
                <div className="text-lg font-semibold text-gray-900">R$ {session.price}</div>
                {session.status === 'scheduled' && (
                  <div className="flex gap-2 mt-2">
                    <button className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors">
                      Entrar
                    </button>
                    <button className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 transition-colors">
                      Reagendar
                    </button>
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderNetwork = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Rede Profissional</h2>
        <p className="text-gray-600">Conecte-se com outros profissionais e estudantes</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <UserGroupIcon className="w-8 h-8 text-blue-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Grupos de Estudo</h3>
              <p className="text-sm text-gray-600">Participe de grupos temáticos</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">OAB 2024 - Preparação</h4>
                <p className="text-sm text-gray-600">145 membros ativos</p>
              </div>
              <button className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors">
                Participar
              </button>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">Direito Digital</h4>
                <p className="text-sm text-gray-600">89 membros ativos</p>
              </div>
              <button className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors">
                Participar
              </button>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <TrophyIcon className="w-8 h-8 text-yellow-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Eventos e Webinars</h3>
              <p className="text-sm text-gray-600">Participe de eventos exclusivos</p>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900">Webinar: Novas Tendências do Direito</h4>
              <p className="text-sm text-gray-600">Amanhã, 19h • Online</p>
              <button className="mt-2 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 transition-colors">
                Inscrever-se
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );

  const tabs = [
    { id: 'mentors', label: 'Mentores', icon: UserGroupIcon },
    { id: 'programs', label: 'Programas', icon: AcademicCapIcon },
    { id: 'sessions', label: 'Minhas Sessões', icon: CalendarIcon },
    { id: 'network', label: 'Networking', icon: ChatBubbleLeftRightIcon }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-700 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <UserGroupIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Mentoria & Networking</h1>
            <p className="text-purple-100">
              Conecte-se com profissionais experientes e acelere sua carreira jurídica
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
            placeholder="Buscar mentores, especialidades ou programas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </Card>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-4 gap-6">
        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <UserGroupIcon className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{mentors.length}</div>
          <div className="text-sm text-gray-600">Mentores Ativos</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <AcademicCapIcon className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{programs.length}</div>
          <div className="text-sm text-gray-600">Programas Disponíveis</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <CalendarIcon className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{sessions.length}</div>
          <div className="text-sm text-gray-600">Suas Sessões</div>
        </Card>

        <Card className="p-6 text-center">
          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-3">
            <StarSolid className="w-6 h-6 text-yellow-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900">4.8</div>
          <div className="text-sm text-gray-600">Avaliação Média</div>
        </Card>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
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
        {activeTab === 'mentors' && renderMentors()}
        {activeTab === 'programs' && renderPrograms()}
        {activeTab === 'sessions' && renderSessions()}
        {activeTab === 'network' && renderNetwork()}
      </div>
    </div>
  );
};

export default Mentorship; 