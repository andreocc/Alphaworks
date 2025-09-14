# 🚀 Guia de Instalação - AutoPost

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS, ou Linux
- Python 3.8 ou superior
- Git instalado e configurado

### Contas Necessárias
- Conta Google para acessar o Google AI Studio
- Repositório Git configurado (GitHub, GitLab, etc.)

## 🔧 Instalação

### 1. Clone o Repositório
```bash
git clone <seu-repositorio>
cd autopost
```

### 2. Crie um Ambiente Virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# No Windows: notepad .env
# No macOS/Linux: nano .env
```

### 5. Obtenha a API Key do Google AI
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada
5. Cole no arquivo `.env`: `GEMINI_API_KEY=sua_chave_aqui`

### 6. Configure o Git (se necessário)
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

## ✅ Teste a Instalação

### Teste Básico
```bash
python -c "from autopost import setup_gemini_api; print('✅ Importação OK' if setup_gemini_api() else '❌ Erro na API')"
```

### Teste Completo
```bash
python autopost.py
```

## 🔧 Configurações Avançadas

### Personalizar Configurações
Edite o arquivo `config.py` para ajustar:
- Número mínimo/máximo de palavras
- Configurações de SEO
- Fontes de referência
- Categorias e tags

### Configurar Hooks do Git (Opcional)
Para commits automáticos mais seguros:
```bash
# Criar hook pre-commit
echo "python -m py_compile autopost.py" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 🚨 Solução de Problemas

### Erro: "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### Erro: "API Key not found"
1. Verifique se o arquivo `.env` existe
2. Confirme se a variável `GEMINI_API_KEY` está definida
3. Teste a chave no Google AI Studio

### Erro: "Git not configured"
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

### Erro: "Permission denied" (Linux/macOS)
```bash
chmod +x autopost.py
```

## 📊 Uso Básico

### Gerar um Post
```bash
python autopost.py
```

### Gerar Post com Tipo Específico
```bash
# Modificar as probabilidades em config.py
# Ou usar os métodos específicos no código
```

## 🔄 Atualizações

### Atualizar Dependências
```bash
pip install --upgrade -r requirements.txt
```

### Atualizar o Sistema
```bash
git pull origin main
pip install --upgrade -r requirements.txt
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs de erro
2. Confirme todas as configurações
3. Teste a conectividade com a API
4. Verifique as permissões de arquivo

## 🎯 Próximos Passos

Após a instalação bem-sucedida:
1. Execute alguns testes para familiarizar-se
2. Personalize as configurações conforme necessário
3. Configure automação (cron, Task Scheduler, etc.)
4. Monitore a qualidade dos posts gerados