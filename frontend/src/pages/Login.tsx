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
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Left Side: Motivational/Branding */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-gray-900 via-primary-900 to-gray-800 items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-legal-pattern opacity-5"></div>
        <div className="z-10 text-center">
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="bg-gradient-to-br from-primary-500 via-primary-600 to-navy-700 p-6 rounded-3xl shadow-glow animate-float">
                <TrophySolid className="h-20 w-20 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-gold-500 rounded-full animate-pulse flex items-center justify-center">
                <SparklesIcon className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-4 animate-slideInDown">Duolingo Jurídico</h1>
          <p className="text-primary-200 text-xl font-light mb-8 animate-slideInUp">
            Sua jornada para a aprovação começa aqui.
          </p>
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 animate-fadeInUp">
            <div className="flex items-start space-x-4">
              <div className="bg-gold-500/10 rounded-full p-2 flex-shrink-0">
                <AcademicCapIcon className="h-6 w-6 text-gold-400" />
              </div>
              <p className="text-white/90 text-md italic leading-relaxed">
                "{motivationalQuote}"
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side: Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white">Bem-vindo(a) de volta!</h2>
            <p className="mt-2 text-primary-200">Faça login para continuar seus estudos.</p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit} noValidate>
            <input type="hidden" name="remember" defaultValue="true" />
            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <label htmlFor="username" className="sr-only">
                  Nome de usuário
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                    <UserIcon className="h-5 w-5 text-gray-400" />
                  </span>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    className={`input-glass w-full pl-10 ${errors.username ? 'border-red-500' : 'border-gray-600'}`}
                    placeholder="Nome de usuário"
                    value={formData.username}
                    onChange={handleChange}
                  />
                </div>
                {errors.username && <p className="mt-2 text-sm text-red-500">{errors.username}</p>}
              </div>
              <div className="pt-4">
                <label htmlFor="password-login" className="sr-only">
                  Senha
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                    <LockClosedIcon className="h-5 w-5 text-gray-400" />
                  </span>
                  <input
                    id="password-login"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    className={`input-glass w-full pl-10 ${errors.password ? 'border-red-500' : 'border-gray-600'}`}
                    placeholder="Senha"
                    value={formData.password}
                    onChange={handleChange}
                  />
                  <span className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-gray-400 hover:text-white"
                      aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                    >
                      {showPassword ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </span>
                </div>
                {errors.password && <p className="mt-2 text-sm text-red-500">{errors.password}</p>}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <a href="#" className="font-medium text-primary-400 hover:text-primary-300">
                  Esqueceu sua senha?
                </a>
              </div>
            </div>

            {errors.general && (
                <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-lg relative flex items-start space-x-2">
                  <ExclamationTriangleIcon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <span>{errors.general}</span>
                </div>
            )}

            <div>
              <Button
                type="submit"
                fullWidth
                variant="primary"
                size="lg"
                disabled={!isFormValid || loading}
                icon={ArrowRightIcon}
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>
            </div>
          </form>
          <div className="text-center mt-6">
            <p className="text-sm text-gray-400">
              Não tem uma conta?{' '}
              <Link to="/register" className="font-medium text-primary-400 hover:text-primary-300">
                Cadastre-se
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const inputGlass = `
  appearance-none rounded-lg relative block w-full px-3 py-3 bg-white/5 border border-gray-600 
  placeholder-gray-500 text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 
  focus:z-10 sm:text-sm transition-all duration-300
`;

const cardGlass = `
  bg-white/10 backdrop-filter backdrop-blur-lg border border-white/20 rounded-3xl
`;

const shadowGlow = `
  shadow-[0_0_20px_rgba(59,130,246,0.5)]
`;

const shadowGlowGold = `
  shadow-[0_0_20px_rgba(252,211,77,0.5)]
`;

// Keyframes for animations
const keyframes = `
  @keyframes float {
// ... existing code ...
  }

  .animate-slideInUp {
    animation: slideInUp 0.8s ease-out backwards;
  }
  .input-glass {
    appearance-none;
    border-radius: 0.5rem;
    position: relative;
    display: block;
    width: 100%;
    padding: 0.75rem;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgb(75 85 99);
    color: white;
    transition: all 0.3s;
  }
  .input-glass::placeholder {
    color: rgb(156 163 175);
  }
  .input-glass:focus {
    outline: none;
    z-index: 10;
    --tw-ring-color: rgb(59 130 246);
    border-color: rgb(59 130 246);
  }
`;

function LoginStyles() {
  return <style>{keyframes}</style>;
}

export default function LoginPageWithStyles() {
  return (
    <>
      <LoginStyles />
      <Login />
    </>
  );
} 