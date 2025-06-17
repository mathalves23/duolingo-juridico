import React, { useState, useEffect } from 'react';
import {
  UserGroupIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CogIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ClockIcon,
  ShieldCheckIcon,
  BellIcon
} from '@heroicons/react/24/outline';
import Card from '../components/Card';
import { useAuth } from '../contexts/AuthContext';

interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalQuestions: number;
  newUsers: number;
  avgSessionTime: number;
  revenue: number;
}

interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  isStaff: boolean;
  dateJoined: string;
  lastLogin: string;
  totalXP: number;
  subscriptionType: 'free' | 'premium' | 'pro';
}

interface Question {
  id: number;
  title: string;
  subject: string;
  difficulty: number;
  isActive: boolean;
  createdAt: string;
  answersCount: number;
  correctRate: number;
}

const AdminPanel: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'users' | 'questions' | 'analytics' | 'settings'>('dashboard');
  
  // Estados para dados
  const [stats, setStats] = useState<AdminStats>({
    totalUsers: 1234,
    activeUsers: 567,
    totalQuestions: 5678,
    newUsers: 89,
    avgSessionTime: 45,
    revenue: 12450
  });

  const [users, setUsers] = useState<User[]>([
    {
      id: 1,
      username: 'estudante1',
      email: 'estudante1@email.com',
      firstName: 'João',
      lastName: 'Silva',
      isActive: true,
      isStaff: false,
      dateJoined: '2024-01-15',
      lastLogin: '2024-01-20',
      totalXP: 2850,
      subscriptionType: 'premium'
    },
    {
      id: 2,
      username: 'estudante2',
      email: 'estudante2@email.com',
      firstName: 'Maria',
      lastName: 'Santos',
      isActive: true,
      isStaff: false,
      dateJoined: '2024-01-10',
      lastLogin: '2024-01-19',
      totalXP: 4200,
      subscriptionType: 'free'
    },
    {
      id: 3,
      username: 'professor1',
      email: 'professor1@email.com',
      firstName: 'Carlos',
      lastName: 'Oliveira',
      isActive: true,
      isStaff: true,
      dateJoined: '2023-12-01',
      lastLogin: '2024-01-20',
      totalXP: 8500,
      subscriptionType: 'pro'
    }
  ]);

  const [questions, setQuestions] = useState<Question[]>([
    {
      id: 1,
      title: 'Princípios Constitucionais Fundamentais',
      subject: 'Direito Constitucional',
      difficulty: 3,
      isActive: true,
      createdAt: '2024-01-15',
      answersCount: 234,
      correctRate: 67.5
    },
    {
      id: 2,
      title: 'Contratos de Compra e Venda',
      subject: 'Direito Civil',
      difficulty: 2,
      isActive: true,
      createdAt: '2024-01-14',
      answersCount: 189,
      correctRate: 72.1
    },
    {
      id: 3,
      title: 'Crimes contra o Patrimônio',
      subject: 'Direito Penal',
      difficulty: 4,
      isActive: false,
      createdAt: '2024-01-13',
      answersCount: 156,
      correctRate: 58.3
    }
  ]);

  // Verificar se o usuário é admin
  if (!user || user.username !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Acesso Negado</h1>
          <p className="text-gray-600">Você não tem permissão para acessar esta área.</p>
        </div>
      </div>
    );
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Usuários Totais</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</p>
              <div className="flex items-center mt-2">
                <ArrowUpIcon className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-500 ml-1">+12% vs mês anterior</span>
              </div>
            </div>
            <UserGroupIcon className="w-12 h-12 text-blue-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Usuários Ativos</p>
              <p className="text-3xl font-bold text-gray-900">{stats.activeUsers}</p>
              <div className="flex items-center mt-2">
                <ArrowUpIcon className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-500 ml-1">+8% vs semana anterior</span>
              </div>
            </div>
            <CheckCircleIcon className="w-12 h-12 text-green-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total de Questões</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalQuestions.toLocaleString()}</p>
              <div className="flex items-center mt-2">
                <ArrowUpIcon className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-500 ml-1">+45 esta semana</span>
              </div>
            </div>
            <DocumentTextIcon className="w-12 h-12 text-purple-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Receita (R$)</p>
              <p className="text-3xl font-bold text-gray-900">R$ {stats.revenue.toLocaleString()}</p>
              <div className="flex items-center mt-2">
                <ArrowUpIcon className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-500 ml-1">+15% vs mês anterior</span>
              </div>
            </div>
            <ChartBarIcon className="w-12 h-12 text-orange-500" />
          </div>
        </Card>
      </div>

      {/* Activity Chart */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Atividade dos Usuários</h3>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <ChartBarIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">Gráfico de atividade seria renderizado aqui</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Últimas Atividades</h3>
          <div className="space-y-4">
            {[
              { type: 'user', message: 'Novo usuário registrado: maria.silva@email.com', time: '5 min atrás' },
              { type: 'question', message: 'Nova questão criada: Princípios do Direito Penal', time: '15 min atrás' },
              { type: 'payment', message: 'Pagamento premium processado: R$ 29,90', time: '1h atrás' },
              { type: 'user', message: 'Usuário banido por violação de termos', time: '2h atrás' }
            ].map((activity, index) => (
              <div key={index} className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  activity.type === 'user' ? 'bg-blue-500' :
                  activity.type === 'question' ? 'bg-green-500' :
                  activity.type === 'payment' ? 'bg-orange-500' : 'bg-red-500'
                }`}></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );

  const renderUsers = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Gerenciamento de Usuários</h2>
        <div className="flex gap-2">
          <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">
            <PlusIcon className="w-4 h-4" />
            Novo Usuário
          </button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuário
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assinatura
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  XP Total
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Último Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                        {user.firstName.charAt(0)}{user.lastName.charAt(0)}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.firstName} {user.lastName}
                        </div>
                        <div className="text-sm text-gray-500">@{user.username}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user.isActive ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.subscriptionType === 'pro' ? 'bg-purple-100 text-purple-800' :
                      user.subscriptionType === 'premium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.subscriptionType.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.totalXP.toLocaleString()} XP
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.lastLogin).toLocaleDateString('pt-BR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center gap-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button className="text-green-600 hover:text-green-900">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );

  const renderQuestions = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Gerenciamento de Questões</h2>
        <div className="flex gap-2">
          <button className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2">
            <PlusIcon className="w-4 h-4" />
            Nova Questão
          </button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Questão
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Matéria
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dificuldade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Respostas
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Taxa de Acerto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {questions.map((question) => (
                <tr key={question.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">
                      {question.title}
                    </div>
                    <div className="text-sm text-gray-500">
                      Criada em {new Date(question.createdAt).toLocaleDateString('pt-BR')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {question.subject}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-3 h-3 rounded-full mr-1 ${
                            i < question.difficulty ? 'bg-yellow-400' : 'bg-gray-200'
                          }`}
                        />
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      question.isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {question.isActive ? 'Ativa' : 'Inativa'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {question.answersCount}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <div className={`text-sm font-medium ${
                        question.correctRate > 70 ? 'text-green-600' :
                        question.correctRate > 50 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {question.correctRate}%
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center gap-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button className="text-green-600 hover:text-green-900">
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button className="text-red-600 hover:text-red-900">
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: ChartBarIcon },
    { id: 'users', label: 'Usuários', icon: UserGroupIcon },
    { id: 'questions', label: 'Questões', icon: DocumentTextIcon },
    { id: 'analytics', label: 'Analytics', icon: ChartBarIcon },
    { id: 'settings', label: 'Configurações', icon: CogIcon }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <ShieldCheckIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Painel Administrativo</h1>
            <p className="text-gray-300">
              Bem-vindo, {user.first_name}! Gerencie a plataforma Duolingo Jurídico.
            </p>
          </div>
        </div>
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
                    ? 'border-gray-800 text-gray-800'
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
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'questions' && renderQuestions()}
        {activeTab === 'analytics' && (
          <div className="text-center py-12">
            <ChartBarIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Avançado</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
        {activeTab === 'settings' && (
          <div className="text-center py-12">
            <CogIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Configurações do Sistema</h3>
            <p className="text-gray-600">Funcionalidade em desenvolvimento...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;