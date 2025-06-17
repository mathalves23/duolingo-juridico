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
  ExclamationTriangleIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline';
import {
  TrophyIcon as TrophySolid
} from '@heroicons/react/24/solid';
import Button from '../components/Button';
import Loading from '../components/Loading';

const Register: React.FC = () => {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isFormValid, setIsFormValid] = useState(false);
  const [motivationalQuote, setMotivationalQuote] = useState('');

  const quotes = [
    "A jornada de mil milhas começa com um simples passo. - Lao Tzu",
    "O conhecimento é poder. - Francis Bacon",
    "Educar a mente sem educar o coração não é educação. - Aristóteles",
    "A educação é a arma mais poderosa que você pode usar para mudar o mundo. - Nelson Mandela",
    "O futuro pertence àqueles que acreditam na beleza de seus sonhos. - Eleanor Roosevelt"
  ];

  useEffect(() => {
    setMotivationalQuote(quotes[Math.floor(Math.random() * quotes.length)]);
  }, []);

  useEffect(() => {
    const isValid = 
      formData.username.trim() !== '' && 
      formData.email.trim() !== '' && 
      formData.first_name.trim() !== '' && 
      formData.last_name.trim() !== '' && 
      formData.password.length >= 6 && 
      formData.password === formData.confirmPassword;
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

    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Nome é obrigatório';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Sobrenome é obrigatório';
    }

    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Senhas não coincidem';
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
      await register(formData);
      navigate('/');
    } catch (error: any) {
      setErrors({
        general: error.response?.data?.detail || 'Erro ao criar conta. Tente novamente.'
      });
    }
  };

  if (loading.isLoading) {
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
            Inicie sua jornada para a aprovação hoje mesmo.
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

      {/* Right Side: Register Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white">Crie sua conta</h2>
            <p className="mt-2 text-primary-200">Comece sua jornada rumo à aprovação.</p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleSubmit} noValidate>
            <div className="space-y-4">
              {/* Nome e Sobrenome */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="sr-only">Nome</label>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    autoComplete="given-name"
                    required
                    className={`input-glass w-full ${errors.first_name ? 'border-red-500' : 'border-gray-600'}`}
                    placeholder="Nome"
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                  {errors.first_name && <p className="mt-1 text-xs text-red-500">{errors.first_name}</p>}
                </div>
                <div>
                  <label htmlFor="last_name" className="sr-only">Sobrenome</label>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    autoComplete="family-name"
                    required
                    className={`input-glass w-full ${errors.last_name ? 'border-red-500' : 'border-gray-600'}`}
                    placeholder="Sobrenome"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                  {errors.last_name && <p className="mt-1 text-xs text-red-500">{errors.last_name}</p>}
                </div>
              </div>

              {/* Nome de usuário */}
              <div>
                <label htmlFor="username" className="sr-only">Nome de usuário</label>
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

              {/* Email */}
              <div>
                <label htmlFor="email" className="sr-only">Email</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                    <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                  </span>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    className={`input-glass w-full pl-10 ${errors.email ? 'border-red-500' : 'border-gray-600'}`}
                    placeholder="Email"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </div>
                {errors.email && <p className="mt-2 text-sm text-red-500">{errors.email}</p>}
              </div>

              {/* Senha */}
              <div>
                <label htmlFor="password" className="sr-only">Senha</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                    <LockClosedIcon className="h-5 w-5 text-gray-400" />
                  </span>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="new-password"
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

              {/* Confirmar senha */}
              <div>
                <label htmlFor="confirmPassword" className="sr-only">Confirmar senha</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                    <LockClosedIcon className="h-5 w-5 text-gray-400" />
                  </span>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    className={`input-glass w-full pl-10 ${errors.confirmPassword ? 'border-red-500' : 'border-gray-600'}`}
                    placeholder="Confirmar senha"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                  />
                  <span className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="text-gray-400 hover:text-white"
                      aria-label={showConfirmPassword ? 'Ocultar senha' : 'Mostrar senha'}
                    >
                      {showConfirmPassword ? (
                        <EyeSlashIcon className="h-5 w-5" />
                      ) : (
                        <EyeIcon className="h-5 w-5" />
                      )}
                    </button>
                  </span>
                </div>
                {errors.confirmPassword && <p className="mt-2 text-sm text-red-500">{errors.confirmPassword}</p>}
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
                disabled={!isFormValid || loading.isLoading}
                icon={ArrowRightIcon}
              >
                {loading.isLoading ? 'Criando conta...' : 'Criar conta'}
              </Button>
            </div>
          </form>
          <div className="text-center mt-6">
            <p className="text-sm text-gray-400">
              Já tem uma conta?{' '}
              <Link to="/login" className="font-medium text-primary-400 hover:text-primary-300">
                Faça login
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register; 