import React, { useState, useEffect } from 'react';
import { 
  StarIcon as CrownIcon, 
  CheckIcon, 
  XMarkIcon,
  CreditCardIcon,
  BanknotesIcon,
  QrCodeIcon,
  DocumentTextIcon,
  SparklesIcon,
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import { StarIcon as CrownSolid } from '@heroicons/react/24/solid';

interface SubscriptionPlan {
  id: number;
  name: string;
  plan_type: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  max_questions_per_day: number;
  max_quizzes_per_day: number;
  ai_explanations: boolean;
  advanced_analytics: boolean;
  priority_support: boolean;
}

interface PaymentMethod {
  id: string;
  name: string;
  icon: React.ComponentType<any>;
  description: string;
}

const Premium: React.FC = () => {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [currentSubscription, setCurrentSubscription] = useState<any>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentData, setPaymentData] = useState<any>(null);

  const paymentMethods: PaymentMethod[] = [
    {
      id: 'pix',
      name: 'PIX',
      icon: QrCodeIcon,
      description: 'Pagamento instantâneo'
    },
    {
      id: 'credit_card',
      name: 'Cartão de Crédito',
      icon: CreditCardIcon,
      description: 'Visa, Mastercard, Elo'
    },
    {
      id: 'debit_card',
      name: 'Cartão de Débito',
      icon: CreditCardIcon,
      description: 'Débito automático'
    },
    {
      id: 'boleto',
      name: 'Boleto Bancário',
      icon: DocumentTextIcon,
      description: 'Vencimento em 3 dias'
    }
  ];

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/api/v1/subscriptions/plans/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlans(data);
      }
    } catch (error) {
      console.error('Erro ao buscar planos:', error);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/api/v1/subscriptions/status/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      }
    } catch (error) {
      console.error('Erro ao buscar assinatura atual:', error);
    }
  };

  const createPayment = async () => {
    if (!selectedPlan || !selectedPaymentMethod) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/api/v1/subscriptions/create-payment/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          subscription_plan_id: selectedPlan.id,
          payment_method: selectedPaymentMethod,
          billing_period: billingPeriod
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPaymentData(data);
        setShowPaymentModal(true);
      } else {
        alert('Erro ao criar pagamento');
      }
    } catch (error) {
      console.error('Erro ao criar pagamento:', error);
      alert('Erro ao processar pagamento');
    } finally {
      setLoading(false);
    }
  };

  const confirmPayment = async () => {
    if (!paymentData) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:5050/api/v1/subscriptions/confirm-payment/${paymentData.payment_id}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        alert('Pagamento confirmado! Sua assinatura foi ativada.');
        setShowPaymentModal(false);
        fetchCurrentSubscription();
      } else {
        alert('Erro ao confirmar pagamento');
      }
    } catch (error) {
      console.error('Erro ao confirmar pagamento:', error);
      alert('Erro ao confirmar pagamento');
    } finally {
      setLoading(false);
    }
  };

  const cancelSubscription = async () => {
    if (!confirm('Tem certeza que deseja cancelar sua assinatura?')) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5050/api/v1/subscriptions/cancel/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        alert('Assinatura cancelada com sucesso');
        fetchCurrentSubscription();
      } else {
        alert('Erro ao cancelar assinatura');
      }
    } catch (error) {
      console.error('Erro ao cancelar assinatura:', error);
      alert('Erro ao cancelar assinatura');
    } finally {
      setLoading(false);
    }
  };

  const getDiscountPercentage = (monthly: number, yearly: number) => {
    const monthlyTotal = monthly * 12;
    const discount = ((monthlyTotal - yearly) / monthlyTotal) * 100;
    return Math.round(discount);
  };

  const getPlanIcon = (planType: string) => {
    switch (planType) {
      case 'premium':
        return <CrownIcon className="w-8 h-8 text-yellow-500" />;
      case 'premium_plus':
        return <CrownSolid className="w-8 h-8 text-purple-500" />;
      default:
        return <SparklesIcon className="w-8 h-8 text-blue-500" />;
    }
  };

  const getPlanColor = (planType: string) => {
    switch (planType) {
      case 'premium':
        return 'border-yellow-500 bg-yellow-50';
      case 'premium_plus':
        return 'border-purple-500 bg-purple-50';
      default:
        return 'border-blue-500 bg-blue-50';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <CrownSolid className="w-16 h-16 text-yellow-500" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Desbloqueie Todo o Potencial
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Acelere seus estudos com recursos premium, IA avançada e análises detalhadas
          </p>
        </div>

        {/* Status da Assinatura Atual */}
        {currentSubscription?.has_subscription && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Plano Atual: {currentSubscription.plan_name}
                </h3>
                <p className="text-gray-600">
                  Status: {currentSubscription.status} • 
                  {currentSubscription.days_remaining} dias restantes
                </p>
              </div>
              <button
                onClick={cancelSubscription}
                className="px-4 py-2 text-red-600 border border-red-600 rounded-lg hover:bg-red-50"
                disabled={loading}
              >
                Cancelar Assinatura
              </button>
            </div>
          </div>
        )}

        {/* Toggle de Período de Cobrança */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-md">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                billingPeriod === 'monthly'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Mensal
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`px-6 py-2 rounded-md font-medium transition-colors ${
                billingPeriod === 'yearly'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Anual
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Economize até 30%
              </span>
            </button>
          </div>
        </div>

        {/* Planos */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {plans.map((plan) => {
            const price = billingPeriod === 'monthly' ? plan.price_monthly : plan.price_yearly;
            const isPopular = plan.plan_type === 'premium';
            
            return (
              <div
                key={plan.id}
                className={`relative bg-white rounded-xl shadow-lg p-8 border-2 transition-all hover:shadow-xl ${
                  selectedPlan?.id === plan.id
                    ? getPlanColor(plan.plan_type)
                    : 'border-gray-200 hover:border-gray-300'
                } ${isPopular ? 'ring-2 ring-yellow-500' : ''}`}
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-yellow-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Mais Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  {getPlanIcon(plan.plan_type)}
                  <h3 className="text-2xl font-bold text-gray-900 mt-4">{plan.name}</h3>
                  <p className="text-gray-600 mt-2">{plan.description}</p>
                </div>

                <div className="text-center mb-6">
                  <div className="flex items-baseline justify-center">
                    <span className="text-4xl font-bold text-gray-900">
                      R$ {price.toFixed(2)}
                    </span>
                    <span className="text-gray-600 ml-2">
                      /{billingPeriod === 'monthly' ? 'mês' : 'ano'}
                    </span>
                  </div>
                  {billingPeriod === 'yearly' && (
                    <p className="text-green-600 text-sm mt-1">
                      Economize {getDiscountPercentage(plan.price_monthly, plan.price_yearly)}%
                    </p>
                  )}
                </div>

                <div className="space-y-4 mb-8">
                  <div className="flex items-center">
                    <CheckIcon className="w-5 h-5 text-green-500 mr-3" />
                    <span>{plan.max_questions_per_day} questões por dia</span>
                  </div>
                  <div className="flex items-center">
                    <CheckIcon className="w-5 h-5 text-green-500 mr-3" />
                    <span>{plan.max_quizzes_per_day} simulados por dia</span>
                  </div>
                  {plan.ai_explanations && (
                    <div className="flex items-center">
                      <BoltIcon className="w-5 h-5 text-blue-500 mr-3" />
                      <span>Explicações com IA</span>
                    </div>
                  )}
                  {plan.advanced_analytics && (
                    <div className="flex items-center">
                      <ChartBarIcon className="w-5 h-5 text-purple-500 mr-3" />
                      <span>Analytics Avançado</span>
                    </div>
                  )}
                  {plan.priority_support && (
                    <div className="flex items-center">
                      <ChatBubbleLeftRightIcon className="w-5 h-5 text-orange-500 mr-3" />
                      <span>Suporte Prioritário</span>
                    </div>
                  )}
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-center">
                      <CheckIcon className="w-5 h-5 text-green-500 mr-3" />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => setSelectedPlan(plan)}
                  className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                    selectedPlan?.id === plan.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {selectedPlan?.id === plan.id ? 'Selecionado' : 'Selecionar Plano'}
                </button>
              </div>
            );
          })}
        </div>

        {/* Métodos de Pagamento */}
        {selectedPlan && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">
              Escolha o Método de Pagamento
            </h3>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {paymentMethods.map((method) => (
                <button
                  key={method.id}
                  onClick={() => setSelectedPaymentMethod(method.id)}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    selectedPaymentMethod === method.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <method.icon className="w-8 h-8 mx-auto mb-2 text-gray-600" />
                  <h4 className="font-medium text-gray-900">{method.name}</h4>
                  <p className="text-sm text-gray-600">{method.description}</p>
                </button>
              ))}
            </div>

            <button
              onClick={createPayment}
              disabled={!selectedPaymentMethod || loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processando...' : `Pagar R$ ${(billingPeriod === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_yearly).toFixed(2)}`}
            </button>
          </div>
        )}

        {/* Modal de Pagamento */}
        {showPaymentModal && paymentData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold">Finalizar Pagamento</h3>
                <button
                  onClick={() => setShowPaymentModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>

              <div className="text-center mb-6">
                <p className="text-gray-600 mb-4">
                  Valor: R$ {paymentData.amount}
                </p>
                
                {selectedPaymentMethod === 'pix' && (
                  <div>
                    <QrCodeIcon className="w-24 h-24 mx-auto mb-4 text-gray-400" />
                    <p className="text-sm text-gray-600">
                      Escaneie o QR Code ou copie o código PIX
                    </p>
                  </div>
                )}
                
                {selectedPaymentMethod === 'boleto' && (
                  <div>
                    <BanknotesIcon className="w-24 h-24 mx-auto mb-4 text-gray-400" />
                    <p className="text-sm text-gray-600">
                      Código de barras do boleto gerado
                    </p>
                  </div>
                )}
                
                {(selectedPaymentMethod === 'credit_card' || selectedPaymentMethod === 'debit_card') && (
                  <div>
                    <CreditCardIcon className="w-24 h-24 mx-auto mb-4 text-gray-400" />
                    <p className="text-sm text-gray-600">
                      Você será redirecionado para finalizar o pagamento
                    </p>
                  </div>
                )}
              </div>

              <button
                onClick={confirmPayment}
                disabled={loading}
                className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? 'Confirmando...' : 'Confirmar Pagamento'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Premium; 