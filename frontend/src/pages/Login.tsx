import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import {
  EyeIcon,
  EyeSlashIcon,
  AcademicCapIcon,
  SparklesIcon,
  UserIcon,
  LockClosedIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import {
  TrophyIcon as TrophySolid,
  StarIcon as StarSolid,
  FireIcon as FireSolid,
  HeartIcon as HeartSolid
} from '@heroicons/react/24/solid';
import Button from '../components/Button';
import Loading from '../components/Loading';

const Login: React.FC = () => {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isFormValid, setIsFormValid] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [motivationalQuote, setMotivationalQuote] = useState('');

  const quotes = [
    "A justiça é a primeira virtude das instituições sociais. - John Rawls",
    "O direito é a arte do bom e do justo. - Ulpiano",
    "A lei é a razão livre de paixão. - Aristóteles",
    "Justiça atrasada é justiça negada. - William E. Gladstone",
    "O conhecimento das leis é o começo da sabedoria. - Cícero"
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    setMotivationalQuote(quotes[Math.floor(Math.random() * quotes.length)]);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const isValid = formData.username.trim() !== '' && formData.password.length >= 6;
    setIsFormValid(isValid);
  }, [formData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Nome de usuário é obrigatório';
    }

    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      navigate('/');
    } catch (error: any) {
      setErrors({
        general: error.response?.data?.detail || 'Erro ao fazer login. Verifique suas credenciais.'
      });
    }
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  if (loading) {
    return <Loading type="legal" />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-primary-900 to-navy-800 relative overflow-hidden flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Background Decorations */}
      <div className="absolute inset-0 bg-legal-pattern opacity-10"></div>
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-primary-500/20 to-transparent rounded-full blur-3xl animate-float"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-tl from-gold-500/20 to-transparent rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>

      {/* Floating Legal Elements */}
      <div className="absolute top-20 left-20 animate-float">
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 shadow-soft">
          <TrophySolid className="h-8 w-8 text-gold-400" />
        </div>
      </div>
      <div className="absolute top-40 right-20 animate-float" style={{ animationDelay: '1s' }}>
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 shadow-soft">
          <StarSolid className="h-8 w-8 text-primary-400" />
        </div>
      </div>

      <div className="max-w-md w-full space-y-8 relative z-10">
        {/* Time and Greeting */}
        <div className="text-center mb-4 animate-fadeInDown">
          <p className="text-primary-200 text-sm font-medium">
            {getGreeting()}, {currentTime.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>

        {/* Main Card */}
        <div className="card-glass p-8 animate-fadeInUp">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="bg-gradient-to-br from-primary-500 via-primary-600 to-navy-700 p-6 rounded-3xl shadow-glow animate-float">
                  <TrophySolid className="h-16 w-16 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-gold-500 rounded-full animate-pulse flex items-center justify-center">
                  <SparklesIcon className="h-3 w-3 text-white" />
                </div>
              </div>
            </div>
            <h1 className="text-4xl font-bold text-white mb-2 animate-slideInDown">
              Bem-vindo de volta! 👋
            </h1>
            <p className="text-primary-100 text-lg font-medium animate-slideInDown">
              Continue sua jornada rumo à aprovação
            </p>
            <div className="flex items-center justify-center space-x-2 mt-4 animate-slideInDown">
              <SparklesIcon className="h-5 w-5 text-gold-400 animate-pulse" />
              <span className="text-gold-400 font-semibold text-sm">Duolingo Jurídico</span>
              <SparklesIcon className="h-5 w-5 text-gold-400 animate-pulse" />
            </div>
          </div>

          {/* Motivational Quote */}
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 mb-8 border border-white/20 animate-slideInUp">
            <div className="flex items-start space-x-3">
              <div className="bg-gold-500/20 rounded-full p-2 flex-shrink-0">
                <SparklesIcon className="h-4 w-4 text-gold-400" />
              </div>
              <p className="text-white/90 text-sm italic font-medium leading-relaxed">
                "{motivationalQuote}"
              </p>
            </div>
          </div>

          {/* Features Preview */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="text-center animate-slideInLeft">
              <div className="bg-gradient-to-br from-gold-500 to-gold-600 p-4 rounded-2xl mx-auto w-fit shadow-glow-gold hover:scale-110 transition-all duration-300 cursor-pointer">
                <StarSolid className="h-8 w-8 text-white" />
              </div>
              <p className="text-sm text-white font-semibold mt-3">Ganhe XP</p>
              <p className="text-xs text-primary-200">Evolua constantemente</p>
            </div>
            <div className="text-center animate-slideInLeft" style={{ animationDelay: '100ms' }}>
              <div className="bg-gradient-to-br from-danger-500 to-warning-500 p-4 rounded-2xl mx-auto w-fit shadow-glow hover:scale-110 transition-all duration-300 cursor-pointer">
                <FireSolid className="h-8 w-8 text-white" />
              </div>
              <p className="text-sm text-white font-semibold mt-3">Sequências</p>
              <p className="text-xs text-primary-200">Mantenha o ritmo</p>
            </div>
            <div className="text-center animate-slideInLeft" style={{ animationDelay: '200ms' }}>
              <div className="bg-gradient-to-br from-primary-500 to-navy-600 p-4 rounded-2xl mx-auto w-fit shadow-glow hover:scale-110 transition-all duration-300 cursor-pointer">
                <AcademicCapIcon className="h-8 w-8 text-white" />
              </div>
              <p className="text-sm text-white font-semibold mt-3">Aprenda</p>
              <p className="text-xs text-primary-200">Direito na prática</p>
            </div>
          </div>

          {/* Login Form */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            {errors.general && (
              <div className="alert alert-danger animate-slideInDown">
                <div className="flex items-center space-x-2">
                  <ExclamationTriangleIcon className="h-5 w-5" />
                  <p className="text-sm font-medium">{errors.general}</p>
                </div>
              </div>
            )}

            <div className="space-y-5">
              {/* Username */}
              <div className="animate-slideInRight">
                <label htmlFor="username" className="label text-white flex items-center">
                  <UserIcon className="h-4 w-4 mr-2" />
                  Nome de usuário ou email
                </label>
                <div className="relative">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    className={`input-glass ${errors.username ? 'input-error' : ''} ${
                      formData.username ? 'input-success' : ''
                    }`}
                    placeholder="Digite seu nome de usuário"
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <UserIcon className="h-5 w-5 text-white/60" />
                  </div>
                  {formData.username && !errors.username && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                      <CheckCircleIcon className="h-5 w-5 text-success-400" />
                    </div>
                  )}
                </div>
                {errors.username && (
                  <p className="mt-2 text-sm text-danger-300 font-medium animate-slideInDown flex items-center">
                    <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                    {errors.username}
                  </p>
                )}
              </div>

              {/* Password */}
              <div className="animate-slideInRight" style={{ animationDelay: '100ms' }}>
                <label htmlFor="password" className="label text-white flex items-center">
                  <LockClosedIcon className="h-4 w-4 mr-2" />
                  Senha
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className={`input-glass ${errors.password ? 'input-error' : ''} ${
                      formData.password.length >= 6 ? 'input-success' : ''
                    }`}
                    placeholder="Digite sua senha"
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockClosedIcon className="h-5 w-5 text-white/60" />
                  </div>
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center space-x-2">
                    {formData.password.length >= 6 && !errors.password && (
                      <CheckCircleIcon className="h-5 w-5 text-success-400" />
                    )}
                    <button
                      type="button"
                      className="text-white/60 hover:text-white transition-colors"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
                {errors.password && (
                  <p className="mt-2 text-sm text-danger-300 font-medium animate-slideInDown flex items-center">
                    <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                    {errors.password}
                  </p>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="animate-slideInUp">
              <Button
                type="submit"
                variant="gradient"
                size="lg"
                fullWidth
                loading={loading}
                disabled={!isFormValid}
                glow
                animate
                icon={ArrowRightIcon}
                iconPosition="right"
                className="font-bold text-lg"
              >
                {loading ? 'Entrando...' : 'Entrar na Plataforma'}
              </Button>
            </div>
          </form>

          {/* Sign Up Link */}
          <div className="text-center mt-8 animate-slideInUp">
            <p className="text-white/80">
              Não tem uma conta?{' '}
              <Link
                to="/register"
                className="font-semibold text-primary-300 hover:text-primary-200 transition-colors"
              >
                Cadastre-se gratuitamente
              </Link>
            </p>
          </div>

          {/* Stats Preview */}
          <div className="mt-8 pt-6 border-t border-white/20 animate-slideInUp">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="flex items-center justify-center mb-2">
                  <HeartSolid className="h-5 w-5 text-danger-400 mr-1" />
                  <span className="text-white font-bold">50k+</span>
                </div>
                <p className="text-xs text-white/60">Estudantes</p>
              </div>
              <div>
                <div className="flex items-center justify-center mb-2">
                  <TrophySolid className="h-5 w-5 text-gold-400 mr-1" />
                  <span className="text-white font-bold">95%</span>
                </div>
                <p className="text-xs text-white/60">Aprovação</p>
              </div>
              <div>
                <div className="flex items-center justify-center mb-2">
                  <StarSolid className="h-5 w-5 text-primary-400 mr-1" />
                  <span className="text-white font-bold">4.9</span>
                </div>
                <p className="text-xs text-white/60">Avaliação</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 