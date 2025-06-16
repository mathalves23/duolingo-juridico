# 🔧 Corrigindo Deploy do Netlify - Duolingo Jurídico

## 🎯 Problema Identificado
O deploy foi feito do repositório inteiro em vez de apenas a aplicação React.

## ✅ Solução Correta

### Passo 1: Limpar Deploy Atual
1. Acesse https://app.netlify.com/projects/duo-juris/overview
2. Vá em **Site settings** → **Build & deploy** → **Deploy settings**
3. Clique em **Edit settings**

### Passo 2: Configurar Deploy Correto
Configure exatamente assim:

#### Configurações de Build:
- **Repository:** `https://github.com/mathalves23/duolingo-juridico`
- **Branch to deploy:** `main` (ou `master`)
- **Base directory:** `frontend`
- **Build command:** `npm run build`
- **Publish directory:** `frontend/build`

#### Variáveis de Ambiente:
Adicione estas variáveis em **Environment variables**:
```
NODE_VERSION = 18
REACT_APP_API_URL = https://concurseiro-backend.onrender.com/api/v1
REACT_APP_APP_NAME = Duolingo Jurídico
```

### Passo 3: Verificar Arquivo netlify.toml
O arquivo `netlify.toml` na raiz está correto e deve ser mantido.

### Passo 4: Deploy Manual (Alternativa Rápida)
Se quiser resultado imediato:

1. **Via Drag & Drop:**
   - Vá em **Deploys** → **Deploy manually**
   - Arraste apenas a pasta `frontend/build` para a área de upload
   - ✅ Site funcionando em 30 segundos!

2. **Via CLI (se preferir):**
   ```bash
   # Instalar Netlify CLI
   npm install -g netlify-cli
   
   # Fazer login
   netlify login
   
   # Deploy da pasta build
   netlify deploy --prod --dir=frontend/build --site=duo-juris
   ```

### Passo 5: Forçar Novo Deploy
Após ajustar as configurações:
1. Clique em **Trigger deploy** → **Deploy site**
2. Aguarde o build completar

## 🔍 Verificação Final

Após o deploy, sua aplicação deve estar funcionando em:
`https://duo-juris.netlify.app` (ou sua URL personalizada)

## 🚨 Possíveis Problemas e Soluções

### Se aparecer erro de build:
1. Verifique se o `NODE_VERSION` está definido como `18`
2. Confirme que o `base directory` está como `frontend`
3. Certifique-se que o repositório GitHub está atualizado

### Se a página aparecer em branco:
1. Verifique se o `publish directory` está como `frontend/build`
2. Confirme se os redirecionamentos estão configurados (arquivo `_redirects`)

### Se a API não conectar:
1. Verifique se `REACT_APP_API_URL` está correto
2. Teste o endpoint da API: https://concurseiro-backend.onrender.com/api/v1

## 📞 Teste Rápido
Depois do deploy, acesse sua URL e:
1. ✅ Página inicial carrega
2. ✅ Login/cadastro funciona
3. ✅ Dashboard aparece
4. ✅ Questões carregam

---

## 🎉 Resultado Final
Sua aplicação **Duolingo Jurídico** estará funcionando perfeitamente no Netlify! 🚀 