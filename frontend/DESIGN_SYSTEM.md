# Sistema de Design - Duolingo Jurídico

## 🎨 Paleta de Cores

### Cores Principais
- **Primary**: Azul jurídico elegante (#6366f1 - #1e1b4b)
- **Navy**: Azul marinho sofisticado (#f8fafc - #020617)
- **Gold**: Dourado premium (#fffbeb - #451a03)

### Cores Funcionais
- **Success**: Verde (#ecfdf5 - #022c22)
- **Warning**: Laranja (#fff7ed - #431407)
- **Danger**: Vermelho (#fef2f2 - #450a0a)

## 🎭 Componentes Visuais

### Botões
```tsx
// Botão primário com gradiente
<button className="btn btn-primary">
  Texto do Botão
</button>

// Botão dourado premium
<button className="btn btn-gold">
  Premium
</button>

// Botão outline
<button className="btn btn-outline">
  Secundário
</button>
```

### Cards
```tsx
// Card padrão com glassmorphism
<div className="card">
  Conteúdo
</div>

// Card premium com efeito dourado
<div className="card card-premium">
  Conteúdo Premium
</div>

// Card com hover e glow
<div className="card card-hover hover-glow">
  Conteúdo Interativo
</div>
```

### Inputs
```tsx
// Input moderno com glassmorphism
<input className="input" placeholder="Digite aqui..." />

// Input com erro
<input className="input input-error" />

// Input com sucesso
<input className="input input-success" />
```

## ✨ Efeitos Visuais

### Animações
- `animate-fadeInUp`: Fade in com movimento para cima
- `animate-slideInRight`: Slide da direita
- `animate-slideInLeft`: Slide da esquerda
- `animate-scaleIn`: Escala de entrada
- `animate-float`: Flutuação suave
- `animate-pulse`: Pulsação
- `animate-ping`: Ping expandindo

### Sombras
- `shadow-soft`: Sombra suave
- `shadow-medium`: Sombra média
- `shadow-strong`: Sombra forte
- `shadow-glow`: Brilho colorido
- `shadow-glow-gold`: Brilho dourado

### Efeitos de Hover
- `hover-lift`: Elevação no hover
- `hover-glow`: Brilho no hover
- `hover-scale`: Escala no hover

## 🎯 Glassmorphism

### Background com Blur
```tsx
<div className="bg-white/80 backdrop-blur-sm">
  Conteúdo com glassmorphism
</div>
```

### Bordas Translúcidas
```tsx
<div className="border border-white/30">
  Borda translúcida
</div>
```

## 📱 Responsividade

### Breakpoints
- `sm`: 640px+
- `md`: 768px+
- `lg`: 1024px+
- `xl`: 1280px+

### Classes Responsivas
```tsx
// Ocultar em mobile
<div className="hidden md:block">
  Visível apenas em desktop
</div>

// Grid responsivo
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Grid adaptativo
</div>
```

## 🎨 Gradientes

### Gradientes de Fundo
- `bg-legal-gradient`: Gradiente jurídico escuro
- `bg-hero-gradient`: Gradiente para hero sections
- `bg-card-gradient`: Gradiente suave para cards

### Gradientes de Texto
```tsx
<h1 className="title-primary">
  Título com gradiente
</h1>

<h2 className="title-gold">
  Título dourado
</h2>
```

## 🔧 Utilitários

### Loading States
```tsx
// Spinner simples
<div className="loading-spinner"></div>

// Loading dots
<div className="loading-dots">
  <div className="loading-dot"></div>
  <div className="loading-dot"></div>
  <div className="loading-dot"></div>
</div>
```

### Badges
```tsx
<span className="badge badge-primary">Novo</span>
<span className="badge badge-gold">Premium</span>
<span className="badge badge-success">Completo</span>
```

### Alertas
```tsx
<div className="alert alert-info">
  Informação importante
</div>

<div className="alert alert-success">
  Operação realizada com sucesso
</div>
```

## 🎪 Exemplos de Uso

### Hero Section
```tsx
<div className="bg-gradient-to-br from-primary-600 via-primary-700 to-navy-800 rounded-3xl p-8 text-white shadow-strong">
  <h1 className="text-4xl font-bold mb-4">
    Bem-vindo ao Duolingo Jurídico
  </h1>
  <p className="text-primary-100 text-lg">
    Sua jornada para a aprovação começa aqui
  </p>
</div>
```

### Card de Estatística
```tsx
<div className="card hover-lift hover-glow">
  <div className="flex items-center space-x-4">
    <div className="bg-gradient-to-br from-gold-500 to-gold-600 p-4 rounded-2xl shadow-glow-gold">
      <TrophyIcon className="h-8 w-8 text-white" />
    </div>
    <div>
      <p className="text-sm font-semibold text-navy-600">XP Total</p>
      <p className="text-3xl font-bold text-navy-800">1,250</p>
    </div>
  </div>
</div>
```

### Formulário Moderno
```tsx
<form className="space-y-6">
  <div>
    <label className="label">Nome de usuário</label>
    <input 
      className="input bg-white/80 backdrop-blur-sm" 
      placeholder="Digite seu usuário"
    />
  </div>
  <button className="btn btn-primary w-full">
    Entrar
  </button>
</form>
```

## 🌟 Melhores Práticas

1. **Use glassmorphism** para elementos sobrepostos
2. **Combine gradientes** com sombras para profundidade
3. **Aplique animações** com moderação para não sobrecarregar
4. **Mantenha consistência** nas cores e espaçamentos
5. **Teste responsividade** em diferentes dispositivos
6. **Use hover effects** para melhorar interatividade
7. **Implemente loading states** para melhor UX

## 🎨 Inspiração Visual

O design foi inspirado em:
- **Glassmorphism**: Transparências e blur effects
- **Neumorphism**: Sombras suaves e profundidade
- **Material Design**: Elevações e animações
- **Temática Jurídica**: Cores elegantes e profissionais
- **Gamificação**: Elementos visuais motivacionais 