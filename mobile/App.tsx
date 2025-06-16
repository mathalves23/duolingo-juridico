import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  StatusBar,
  SafeAreaView,
  Alert,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import FlashMessage from 'react-native-flash-message';
import NetInfo from '@react-native-community/netinfo';

// Contexts
import { AuthProvider } from './src/contexts/AuthContext';
import { ThemeProvider } from './src/contexts/ThemeContext';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import QuestionsScreen from './src/screens/QuestionsScreen';
import QuizzesScreen from './src/screens/QuizzesScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import SubjectsScreen from './src/screens/SubjectsScreen';
import AchievementsScreen from './src/screens/AchievementsScreen';
import StoreScreen from './src/screens/StoreScreen';

// Components
import LoadingScreen from './src/components/LoadingScreen';

// Types
import { RootStackParamList, MainTabParamList } from './src/types/navigation';

const Stack = createStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

// Configuração dos ícones das abas
const getTabBarIcon = (route: string, focused: boolean, color: string, size: number) => {
  let iconName: string;

  switch (route) {
    case 'Dashboard':
      iconName = 'dashboard';
      break;
    case 'Questions':
      iconName = 'quiz';
      break;
    case 'Subjects':
      iconName = 'book';
      break;
    case 'Quizzes':
      iconName = 'assignment';
      break;
    case 'Profile':
      iconName = 'person';
      break;
    default:
      iconName = 'circle';
  }

  return <Icon name={iconName} size={size} color={color} />;
};

// Navegação principal com abas
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => 
          getTabBarIcon(route.name, focused, color, size),
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          height: 60,
          paddingBottom: 5,
          paddingTop: 5,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerStyle: {
          backgroundColor: '#2563eb',
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          title: 'Início',
          tabBarLabel: 'Início',
        }}
      />
      <Tab.Screen 
        name="Subjects" 
        component={SubjectsScreen}
        options={{
          title: 'Disciplinas',
          tabBarLabel: 'Disciplinas',
        }}
      />
      <Tab.Screen 
        name="Questions" 
        component={QuestionsScreen}
        options={{
          title: 'Questões',
          tabBarLabel: 'Questões',
        }}
      />
      <Tab.Screen 
        name="Quizzes" 
        component={QuizzesScreen}
        options={{
          title: 'Simulados',
          tabBarLabel: 'Simulados',
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Perfil',
          tabBarLabel: 'Perfil',
        }}
      />
    </Tab.Navigator>
  );
}

// Componente principal da aplicação
function App(): JSX.Element {
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    // Verificar conectividade
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected ?? false);
      
      if (!state.isConnected) {
        Alert.alert(
          'Sem Conexão',
          'Verifique sua conexão com a internet para continuar estudando.',
          [{ text: 'OK' }]
        );
      }
    });

    // Simular carregamento inicial
    setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    return () => unsubscribe();
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <ThemeProvider>
      <AuthProvider>
        <SafeAreaView style={styles.container}>
          <StatusBar 
            barStyle="light-content" 
            backgroundColor="#2563eb" 
          />
          
          <NavigationContainer>
            <Stack.Navigator
              screenOptions={{
                headerShown: false,
              }}
            >
              <Stack.Screen 
                name="Login" 
                component={LoginScreen}
                options={{
                  title: 'Entrar',
                }}
              />
              <Stack.Screen 
                name="Main" 
                component={MainTabNavigator}
              />
              <Stack.Screen 
                name="Analytics" 
                component={AnalyticsScreen}
                options={{
                  headerShown: true,
                  title: 'Estatísticas',
                  headerStyle: {
                    backgroundColor: '#2563eb',
                  },
                  headerTintColor: '#ffffff',
                }}
              />
              <Stack.Screen 
                name="Achievements" 
                component={AchievementsScreen}
                options={{
                  headerShown: true,
                  title: 'Conquistas',
                  headerStyle: {
                    backgroundColor: '#2563eb',
                  },
                  headerTintColor: '#ffffff',
                }}
              />
              <Stack.Screen 
                name="Store" 
                component={StoreScreen}
                options={{
                  headerShown: true,
                  title: 'Loja',
                  headerStyle: {
                    backgroundColor: '#2563eb',
                  },
                  headerTintColor: '#ffffff',
                }}
              />
            </Stack.Navigator>
          </NavigationContainer>

          <FlashMessage position="top" />
        </SafeAreaView>
      </AuthProvider>
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
});

export default App; 