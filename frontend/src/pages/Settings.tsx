import React, { useState, useEffect } from 'react';
import { 
  UserIcon,
  BellIcon,
  ShieldCheckIcon,
  PaintBrushIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  EyeIcon,
  KeyIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { UserProfile } from '../types';

// Local interfaces for settings
interface LocalNotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  study_reminders: boolean;
  achievement_alerts: boolean;
  leaderboard_updates: boolean;
  weekly_reports: boolean;
}

interface LocalPrivacySettings {
  profile_visibility: 'public' | 'friends' | 'private';
  show_progress: boolean;
  show_achievements: boolean;
  show_study_time: boolean;
  allow_friend_requests: boolean;
}

interface SettingsSection {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  description: string;
}

const Settings: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeSection, setActiveSection] = useState<string>('profile');
  const [loading, setLoading] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    bio: user?.profile?.bio || '',
    phone_number: user?.profile?.phone_number || '',
    target_exam: user?.profile?.target_exam || '',
    experience_level: user?.profile?.experience_level || 'beginner' as 'beginner' | 'intermediate' | 'advanced',
    preferred_study_time: user?.profile?.preferred_study_time || 'morning',
    study_goals: user?.profile?.study_goals || ''
  });

  // Notification settings
  const [notificationSettings, setNotificationSettings] = useState<LocalNotificationSettings>({
    email_notifications: true,
    push_notifications: true,
    study_reminders: true,
    achievement_alerts: true,
    leaderboard_updates: false,
    weekly_reports: true
  });

  // Privacy settings
  const [privacySettings, setPrivacySettings] = useState<LocalPrivacySettings>({
    profile_visibility: 'public',
    show_progress: true,
    show_achievements: true,
    show_study_time: false,
    allow_friend_requests: true
  });

  const sections: SettingsSection[] = [
    {
      id: 'profile',
      name: 'Perfil',
      icon: UserIcon,
      description: 'Informações pessoais e preferências de estudo'
    },
    {
      id: 'notifications',
      name: 'Notificações',
      icon: BellIcon,
      description: 'Configure como e quando receber notificações'
    },
    {
      id: 'privacy',
      name: 'Privacidade',
      icon: ShieldCheckIcon,
      description: 'Controle a visibilidade dos seus dados'
    },
    {
      id: 'appearance',
      name: 'Aparência',
      icon: PaintBrushIcon,
      description: 'Tema, idioma e personalização da interface'
    },
    {
      id: 'account',
      name: 'Conta',
      icon: KeyIcon,
      description: 'Segurança, senha e gerenciamento da conta'
    }
  ];

  useEffect(() => {
    if (user?.profile) {
      setProfileForm({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        bio: user.profile.bio,
        phone_number: user.profile.phone_number,
        target_exam: user.profile.target_exam,
        experience_level: user.profile.experience_level,
        preferred_study_time: user.profile.preferred_study_time,
        study_goals: user.profile.study_goals
      });
    }
  }, [user]);

  const handleProfileUpdate = async (data: typeof profileForm) => {
    setLoading(true);
    try {
      // In a real implementation, you would call the API
      // await apiService.updateProfile(data);
      alert('Perfil atualizado com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar perfil:', error);
      alert('Erro ao atualizar perfil. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationUpdate = async (settings: LocalNotificationSettings) => {
    setLoading(true);
    try {
      // In a real implementation, you would call an API
      // await apiService.updateNotificationSettings(settings);
      setNotificationSettings(settings);
      alert('Configurações de notificação atualizadas!');
    } catch (error) {
      console.error('Erro ao atualizar notificações:', error);
      alert('Erro ao atualizar configurações. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handlePrivacyUpdate = async (settings: LocalPrivacySettings) => {
    setLoading(true);
    try {
      // In a real implementation, you would call an API
      // await apiService.updatePrivacySettings(settings);
      setPrivacySettings(settings);
      alert('Configurações de privacidade atualizadas!');
    } catch (error) {
      console.error('Erro ao atualizar privacidade:', error);
      alert('Erro ao atualizar configurações. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const renderProfileSection = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações Pessoais</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={user?.first_name || ''}
              onChange={(e) => setProfileForm(prev => ({ ...prev, first_name: e.target.value }))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sobrenome
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={user?.last_name || ''}
              onChange={(e) => setProfileForm(prev => ({ ...prev, last_name: e.target.value }))}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50"
              value={user?.email || ''}
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">
              Para alterar o email, entre em contato com o suporte
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Telefone
            </label>
            <input
              type="tel"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={profileForm.phone_number || ''}
              onChange={(e) => setProfileForm(prev => ({ ...prev, phone_number: e.target.value }))}
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferências de Estudo</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nível de Experiência
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={profileForm.experience_level || 'beginner'}
              onChange={(e) => setProfileForm(prev => ({ ...prev, experience_level: e.target.value as any }))}
            >
              <option value="beginner">Iniciante</option>
              <option value="intermediate">Intermediário</option>
              <option value="advanced">Avançado</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Horário Preferido de Estudo
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={profileForm.preferred_study_time || 'morning'}
              onChange={(e) => setProfileForm(prev => ({ ...prev, preferred_study_time: e.target.value }))}
            >
              <option value="morning">Manhã (6h - 12h)</option>
              <option value="afternoon">Tarde (12h - 18h)</option>
              <option value="evening">Noite (18h - 24h)</option>
              <option value="flexible">Flexível</option>
            </select>
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Concurso Alvo
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={profileForm.target_exam || ''}
              onChange={(e) => setProfileForm(prev => ({ ...prev, target_exam: e.target.value }))}
              placeholder="Ex: Magistratura Federal, Procuradoria, etc."
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Objetivos de Estudo
            </label>
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={3}
              value={profileForm.study_goals || ''}
              onChange={(e) => setProfileForm(prev => ({ ...prev, study_goals: e.target.value }))}
              placeholder="Descreva seus objetivos e metas de estudo..."
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => handleProfileUpdate(profileForm)}
          disabled={loading}
          className="btn btn-primary disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar Alterações'}
        </button>
      </div>
    </div>
  );

  const renderNotificationsSection = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notificações por Email</h3>
        <div className="space-y-4">
          {[
            { key: 'email_notifications', label: 'Notificações gerais por email', description: 'Receba atualizações importantes sobre sua conta' },
            { key: 'study_reminders', label: 'Lembretes de estudo', description: 'Receba lembretes para manter sua sequência de estudos' },
            { key: 'achievement_alerts', label: 'Alertas de conquistas', description: 'Seja notificado quando conquistar novos objetivos' },
            { key: 'weekly_reports', label: 'Relatórios semanais', description: 'Receba um resumo semanal do seu progresso' },
            { key: 'marketing_emails', label: 'Emails promocionais', description: 'Receba ofertas especiais e novidades da plataforma' }
          ].map(item => (
            <div key={item.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{item.label}</p>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={notificationSettings[item.key as keyof LocalNotificationSettings]}
                  onChange={(e) => setNotificationSettings(prev => ({ ...prev, [item.key]: e.target.checked }))}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notificações Push</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Notificações push</p>
              <p className="text-sm text-gray-600">Receba notificações no seu dispositivo</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={notificationSettings.push_notifications}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, push_notifications: e.target.checked }))}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => handleNotificationUpdate(notificationSettings)}
          disabled={loading}
          className="btn btn-primary disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </div>
    </div>
  );

  const renderPrivacySection = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Visibilidade do Perfil</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quem pode ver seu perfil?
            </label>
            <select
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={privacySettings.profile_visibility}
              onChange={(e) => setPrivacySettings(prev => ({ ...prev, profile_visibility: e.target.value as any }))}
            >
              <option value="public">Público - Qualquer pessoa</option>
              <option value="friends">Amigos - Apenas pessoas que você segue</option>
              <option value="private">Privado - Apenas você</option>
            </select>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Compartilhamento de Dados</h3>
        <div className="space-y-4">
          {[
            { key: 'show_progress', label: 'Mostrar progresso', description: 'Permite que outros vejam seu progresso nos estudos' },
            { key: 'show_achievements', label: 'Mostrar conquistas', description: 'Exibe suas conquistas e emblemas no perfil' },
            { key: 'show_study_time', label: 'Mostrar tempo de estudo', description: 'Permite que outros vejam quanto tempo você estudou' },
            { key: 'allow_friend_requests', label: 'Permitir solicitações de amizade', description: 'Outros usuários podem enviar solicitações de amizade' }
          ].map(item => (
            <div key={item.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{item.label}</p>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={Boolean(privacySettings[item.key as keyof LocalPrivacySettings])}
                  onChange={(e) => setPrivacySettings(prev => ({ ...prev, [item.key]: e.target.checked }))}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => handlePrivacyUpdate(privacySettings)}
          disabled={loading}
          className="btn btn-primary disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </div>
    </div>
  );

  const renderAppearanceSection = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tema</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { id: 'light', name: 'Claro', description: 'Tema padrão com fundo claro' },
            { id: 'dark', name: 'Escuro', description: 'Tema escuro para estudos noturnos' },
            { id: 'auto', name: 'Automático', description: 'Segue as configurações do sistema' }
          ].map(theme => (
            <div key={theme.id} className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-primary-300">
              <div className="flex items-center mb-2">
                <input
                  type="radio"
                  name="theme"
                  value={theme.id}
                  className="mr-3"
                  defaultChecked={theme.id === 'light'}
                />
                <h4 className="font-medium text-gray-900">{theme.name}</h4>
              </div>
              <p className="text-sm text-gray-600">{theme.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Idioma</h3>
        <select
          className="w-full md:w-64 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          defaultValue="pt-BR"
        >
          <option value="pt-BR">Português (Brasil)</option>
          <option value="en-US">English (US)</option>
          <option value="es-ES">Español</option>
        </select>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Acessibilidade</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Texto grande</p>
              <p className="text-sm text-gray-600">Aumenta o tamanho da fonte em toda a aplicação</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Alto contraste</p>
              <p className="text-sm text-gray-600">Melhora a visibilidade para pessoas com deficiência visual</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAccountSection = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Segurança</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Alterar senha</p>
              <p className="text-sm text-gray-600">Última alteração há 3 meses</p>
            </div>
            <button
              onClick={() => setShowPasswordModal(true)}
              className="btn btn-outline"
            >
              Alterar
            </button>
          </div>
          
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Autenticação de dois fatores</p>
              <p className="text-sm text-gray-600">Adicione uma camada extra de segurança</p>
            </div>
            <button className="btn btn-outline">
              Configurar
            </button>
          </div>
          
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Sessões ativas</p>
              <p className="text-sm text-gray-600">Gerencie dispositivos conectados à sua conta</p>
            </div>
            <button className="btn btn-outline">
              Ver sessões
            </button>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Dados da Conta</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">Exportar dados</p>
              <p className="text-sm text-gray-600">Baixe uma cópia de todos os seus dados</p>
            </div>
            <button className="btn btn-outline">
              Exportar
            </button>
          </div>
          
          <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
            <div>
              <p className="font-medium text-red-900">Excluir conta</p>
              <p className="text-sm text-red-600">Esta ação não pode ser desfeita</p>
            </div>
            <button
              onClick={() => setShowDeleteModal(true)}
              className="btn bg-red-600 text-white hover:bg-red-700"
            >
              Excluir
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'profile':
        return renderProfileSection();
      case 'notifications':
        return renderNotificationsSection();
      case 'privacy':
        return renderPrivacySection();
      case 'appearance':
        return renderAppearanceSection();
      case 'account':
        return renderAccountSection();
      default:
        return renderProfileSection();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-500 to-gray-600 rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold">Configurações</h1>
        <p className="text-gray-100 mt-2">
          Personalize sua experiência e gerencie sua conta
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="p-4">
              <nav className="space-y-2">
                {sections.map(section => {
                  const IconComponent = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        activeSection === section.id
                          ? 'bg-primary-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex items-center">
                        <IconComponent className="h-5 w-5 mr-3" />
                        <div>
                          <p className="font-medium">{section.name}</p>
                          <p className={`text-xs mt-1 ${
                            activeSection === section.id ? 'text-primary-100' : 'text-gray-500'
                          }`}>
                            {section.description}
                          </p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="card">
            <div className="p-6">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <div className="text-center">
              <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Excluir Conta
              </h3>
              
              <p className="text-gray-600 mb-6">
                Tem certeza que deseja excluir sua conta? Esta ação não pode ser desfeita e todos os seus dados serão perdidos permanentemente.
              </p>

              <div className="flex space-x-3">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="flex-1 btn btn-outline"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => {
                    // Handle account deletion
                    setShowDeleteModal(false);
                    alert('Funcionalidade em desenvolvimento');
                  }}
                  className="flex-1 btn bg-red-600 text-white hover:bg-red-700"
                >
                  Excluir
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <div className="text-center mb-6">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <KeyIcon className="h-8 w-8 text-blue-600" />
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Alterar Senha
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Senha atual
                </label>
                <input
                  type="password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nova senha
                </label>
                <input
                  type="password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmar nova senha
                </label>
                <input
                  type="password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowPasswordModal(false)}
                className="flex-1 btn btn-outline"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  // Handle password change
                  setShowPasswordModal(false);
                  alert('Senha alterada com sucesso!');
                }}
                className="flex-1 btn btn-primary"
              >
                Alterar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings; 