import React, { useState, useEffect } from 'react';
import { 
  ShoppingBagIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  PaintBrushIcon,
  RocketLaunchIcon,
  UserCircleIcon,
  CheckCircleIcon,
  StarIcon,
  FireIcon,
  ClockIcon,
  GiftIcon,
  BookOpenIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckSolid } from '@heroicons/react/24/solid';
import { useAuth } from '../contexts/AuthContext';
import { StoreItem } from '../types';
import { apiService } from '../services/api';

interface PurchaseModalProps {
  item: StoreItem | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  userCoins: number;
}

const PurchaseModal: React.FC<PurchaseModalProps> = ({ item, isOpen, onClose, onConfirm, userCoins }) => {
  if (!isOpen || !item) return null;

  const canAfford = userCoins >= item.coin_price;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full">
        <div className="text-center">
          <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShoppingBagIcon className="h-8 w-8 text-blue-600" />
          </div>
          
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Confirmar Compra
          </h3>
          
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <h4 className="font-semibold text-gray-900">{item.name}</h4>
            <p className="text-sm text-gray-600 mt-1">{item.description}</p>
            <div className="flex items-center justify-center mt-3">
              <CurrencyDollarIcon className="h-5 w-5 text-green-600 mr-1" />
              <span className="font-bold text-lg text-gray-900">{item.coin_price}</span>
              <span className="text-gray-600 ml-1">moedas</span>
            </div>
          </div>

          <div className="flex items-center justify-between bg-gray-100 rounded-lg p-3 mb-6">
            <span className="text-gray-600">Suas moedas:</span>
            <span className="font-bold text-gray-900">{userCoins}</span>
          </div>

          {!canAfford && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-red-600 text-sm">
                Você não tem moedas suficientes para esta compra.
              </p>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 btn btn-outline"
            >
              Cancelar
            </button>
            <button
              onClick={onConfirm}
              disabled={!canAfford}
              className="flex-1 btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Comprar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Store: React.FC = () => {
  const { user } = useAuth();
  const [storeItems, setStoreItems] = useState<StoreItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<StoreItem | null>(null);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [ownedItems, setOwnedItems] = useState<number[]>([]);

  const categories = [
    { id: 'all', name: 'Todos', icon: SparklesIcon },
    { id: 'avatar', name: 'Avatares', icon: UserCircleIcon },
    { id: 'theme', name: 'Temas', icon: PaintBrushIcon },
    { id: 'boost', name: 'Boosts', icon: RocketLaunchIcon },
    { id: 'feature', name: 'Recursos', icon: StarIcon }
  ];

  useEffect(() => {
    loadStoreItems();
  }, []);

  const loadStoreItems = async () => {
    try {
      const items = await apiService.getStoreItems();
      setStoreItems(items);
      
      // Mock owned items - in real app, fetch from user profile
      setOwnedItems([1, 5]);
    } catch (error) {
      console.error('Erro ao carregar itens da loja:', error);
      
      // Mock data for development
      const mockItems: StoreItem[] = [
        {
          id: 1,
          name: 'Avatar Juiz',
          description: 'Avatar exclusivo de magistrado para seu perfil',
          item_type: 'avatar',
          coin_price: 100,
          is_available: true,
          rarity: 'rare',
          item_data: JSON.stringify({ image_url: '/avatars/judge.png' }),
          duration_hours: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          name: 'Boost XP 2x',
          description: 'Dobra o XP ganho por 24 horas',
          item_type: 'boost',
          coin_price: 50,
          is_available: true,
          rarity: 'common',
          item_data: JSON.stringify({ multiplier: 2 }),
          duration_hours: 24,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 3,
          name: 'Tema Escuro Premium',
          description: 'Tema escuro elegante com detalhes dourados',
          item_type: 'theme',
          coin_price: 75,
          is_available: true,
          rarity: 'rare',
          item_data: JSON.stringify({ theme_id: 'dark_premium' }),
          duration_hours: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 4,
          name: 'Emblema Dedicado',
          description: 'Mostra seu comprometimento com os estudos',
          item_type: 'feature',
          coin_price: 80,
          is_available: true,
          rarity: 'rare',
          item_data: JSON.stringify({ badge_id: 'dedicated' }),
          duration_hours: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 5,
          name: 'Avatar Advogado',
          description: 'Avatar profissional de advogado',
          item_type: 'avatar',
          coin_price: 90,
          is_available: true,
          rarity: 'common',
          item_data: JSON.stringify({ image_url: '/avatars/lawyer.png' }),
          duration_hours: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 6,
          name: 'Proteção de Sequência',
          description: 'Protege sua sequência por 3 dias mesmo se você não estudar',
          item_type: 'boost',
          coin_price: 120,
          is_available: true,
          rarity: 'epic',
          item_data: JSON.stringify({ protection_days: 3 }),
          duration_hours: 72,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 7,
          name: 'Efeito Partículas Douradas',
          description: 'Adiciona efeito visual especial ao completar questões',
          item_type: 'feature',
          coin_price: 150,
          is_available: true,
          rarity: 'epic',
          item_data: JSON.stringify({ effect_id: 'golden_particles' }),
          duration_hours: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 8,
          name: 'Tema Minimalista',
          description: 'Interface limpa e focada nos estudos',
          item_type: 'theme',
          coin_price: 60,
          is_available: true,
          rarity: 'common',
          item_data: JSON.stringify({ theme_id: 'minimal' }),
          duration_hours: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ];
      
      setStoreItems(mockItems);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (item: StoreItem) => {
    setSelectedItem(item);
    setShowPurchaseModal(true);
  };

  const confirmPurchase = async () => {
    if (!selectedItem) return;

    try {
      await apiService.purchaseItem(selectedItem.id);
      setOwnedItems(prev => [...prev, selectedItem.id]);
      setShowPurchaseModal(false);
      setSelectedItem(null);
      
      // Show success feedback
      alert(`${selectedItem.name} comprado com sucesso!`);
    } catch (error) {
      console.error('Erro ao comprar item:', error);
      alert('Erro ao processar compra. Tente novamente.');
    }
  };

  const getItemIcon = (itemType: string) => {
    switch (itemType) {
      case 'avatar':
        return UserCircleIcon;
      case 'theme':
        return PaintBrushIcon;
      case 'boost':
        return RocketLaunchIcon;
      case 'feature':
        return StarIcon;
      default:
        return SparklesIcon;
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common':
        return 'border-gray-300 bg-gray-50';
      case 'rare':
        return 'border-blue-300 bg-blue-50';
      case 'epic':
        return 'border-purple-300 bg-purple-50';
      case 'legendary':
        return 'border-yellow-300 bg-yellow-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  const getRarityBadge = (rarity: string) => {
    const colors = {
      common: 'bg-gray-100 text-gray-800',
      rare: 'bg-blue-100 text-blue-800',
      epic: 'bg-purple-100 text-purple-800',
      legendary: 'bg-yellow-100 text-yellow-800'
    };
    
    const names = {
      common: 'Comum',
      rare: 'Raro',
      epic: 'Épico',
      legendary: 'Lendário'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[rarity as keyof typeof colors]}`}>
        {names[rarity as keyof typeof names]}
      </span>
    );
  };

  const isItemOwned = (itemId: number) => {
    return ownedItems.includes(itemId);
  };

  const filteredItems = storeItems.filter(item => {
    if (selectedCategory === 'all') return true;
    return item.item_type === selectedCategory;
  });

  const userCoins = user?.profile?.coins || 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Loja Virtual</h1>
            <p className="text-green-100 mt-2">
              Use suas moedas para personalizar sua experiência de aprendizado
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-xl p-4">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-8 w-8 text-white mr-3" />
              <div>
                <p className="text-green-100 text-sm">Suas moedas</p>
                <p className="text-2xl font-bold text-white">{userCoins}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="card">
        <div className="p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Categorias</h2>
          <div className="flex flex-wrap gap-2">
            {categories.map(category => {
              const IconComponent = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <IconComponent className="h-4 w-4 mr-2" />
                  {category.name}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredItems.map(item => {
          const IconComponent = getItemIcon(item.item_type);
          const isOwned = isItemOwned(item.id);
          const canAfford = userCoins >= item.coin_price;

          return (
            <div
              key={item.id}
              className={`card relative overflow-hidden ${getRarityColor(item.rarity)} ${
                isOwned ? 'opacity-75' : ''
              }`}
            >
              {/* Rarity Badge */}
              <div className="absolute top-3 right-3">
                {getRarityBadge(item.rarity)}
              </div>

              {/* Owned Badge */}
              {isOwned && (
                <div className="absolute top-3 left-3">
                  <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium flex items-center">
                    <CheckSolid className="h-3 w-3 mr-1" />
                    Possui
                  </div>
                </div>
              )}

              <div className="p-6">
                {/* Item Icon */}
                <div className="text-center mb-4">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-xl shadow-sm mb-3">
                    <IconComponent className="h-8 w-8 text-gray-600" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">{item.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                </div>

                {/* Duration (for temporary items) */}
                {item.duration_hours && (
                  <div className="flex items-center justify-center text-sm text-gray-600 mb-4">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    <span>Duração: {item.duration_hours}h</span>
                  </div>
                )}

                {/* Price */}
                <div className="text-center mb-4">
                  <div className="flex items-center justify-center">
                    <CurrencyDollarIcon className="h-5 w-5 text-green-600 mr-1" />
                    <span className="text-xl font-bold text-gray-900">{item.coin_price}</span>
                    <span className="text-gray-600 ml-1">moedas</span>
                  </div>
                </div>

                {/* Purchase Button */}
                <button
                  onClick={() => handlePurchase(item)}
                  disabled={isOwned || !canAfford}
                  className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                    isOwned
                      ? 'bg-green-100 text-green-800 cursor-default'
                      : canAfford
                      ? 'bg-primary-600 text-white hover:bg-primary-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {isOwned ? 'Item Possuído' : canAfford ? 'Comprar' : 'Moedas Insuficientes'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <ShoppingBagIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Nenhum item encontrado
          </h3>
          <p className="text-gray-600">
            Esta categoria não possui itens disponíveis no momento.
          </p>
        </div>
      )}

      {/* How to Earn Coins */}
      <div className="card">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <GiftIcon className="h-6 w-6 mr-2 text-green-600" />
            Como Ganhar Moedas
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <CheckCircleIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Responder Questões</h3>
              <p className="text-sm text-gray-600 mt-1">5 moedas por resposta correta</p>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <BookOpenIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Completar Lições</h3>
              <p className="text-sm text-gray-600 mt-1">10 moedas por lição</p>
            </div>
            
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <FireIcon className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Manter Sequência</h3>
              <p className="text-sm text-gray-600 mt-1">Bônus diário crescente</p>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <StarIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h3 className="font-semibold text-gray-900">Conquistar Objetivos</h3>
              <p className="text-sm text-gray-600 mt-1">Até 100 moedas por conquista</p>
            </div>
          </div>
        </div>
      </div>

      {/* Purchase Modal */}
      <PurchaseModal
        item={selectedItem}
        isOpen={showPurchaseModal}
        onClose={() => {
          setShowPurchaseModal(false);
          setSelectedItem(null);
        }}
        onConfirm={confirmPurchase}
        userCoins={userCoins}
      />
    </div>
  );
};

export default Store; 