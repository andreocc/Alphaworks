# 📖 Manual de Operação - Sistema AutoPost

## 🎯 Visão Geral

O AutoPost é um sistema automatizado para geração de conteúdo educativo sobre tecnologia usando IA (Google Gemini). O sistema prioriza **credibilidade**, **ética** e **valor educativo** ao invés de sensacionalismo.

---

## 📁 Componentes do Sistema

### 1. 🚀 `autopost.py` - Motor Principal

**Função**: Script principal que orquestra todo o processo de geração de conteúdo.

**Responsabilidades**:
- Geração de tópicos educativos
- Criação de artigos técnicos
- Validação ética do conteúdo
- Integração com Hugo (frontmatter)
- Commit automático no Git

**Como usar**:
```bash
# Execução básica
python autopost.py

# Com validação de diretrizes éticas
python autopost.py  # (sempre verifica ethical_guidelines.md)
```

**Fluxo de execução**:
1. Carrega configurações (`config.py` + `trends.py`)
2. Verifica diretrizes éticas (`ethical_guidelines.md`)
3. Gera tópico educativo (evita duplicatas via cache)
4. Cria artigo com validação de qualidade
5. Gera metadados Hugo (tags, resumo, categorias)
6. Salva arquivo markdown
7. Commit e push automático

---

### 2. ⚙️ `config.py` - Configurações Centralizadas

**Função**: Centraliza todas as configurações do sistema.

**Parâmetros Principais**:

#### 📝 Configurações de Conteúdo
```python
ARTICLE_MIN_WORDS = 700        # Tamanho mínimo do artigo
ARTICLE_MAX_WORDS = 900        # Tamanho máximo do artigo
MIN_SUBTITLES = 2              # Mínimo de subtítulos
MAX_TAGS = 6                   # Máximo de tags por post
```

#### 💾 Configurações de Cache
```python
MAX_CACHED_TOPICS = 50         # Máximo de tópicos no cache
CACHE_RETENTION_DAYS = 30      # Dias para manter cache
```

#### 🔄 Configurações de Retry
```python
MAX_API_RETRIES = 3            # Tentativas de chamada da API
MAX_TOPIC_ATTEMPTS = 5         # Tentativas de gerar tópico
MAX_ARTICLE_ATTEMPTS = 3       # Tentativas de gerar artigo
```

#### 🏷️ Configurações do Hugo
```python
HUGO_AUTHOR = "Alphaworks"     # Autor dos posts
HUGO_CATEGORY = "Tecnologia"   # Categoria padrão
TIMEZONE_OFFSET = -3           # Fuso horário (Brasília)
```

**Como personalizar**:
1. Edite `config.py`
2. Modifique os valores desejados
3. Reinicie o sistema

---

### 3. 📊 `trends.py` - Base de Dados Tecnológica

**Função**: Mantém dados atualizados sobre tecnologias, empresas e tendências.

**Componentes Principais**:

#### 🏢 Empresas em Alta
```python
HOT_COMPANIES = [
    "OpenAI", "Anthropic", "Meta", "Google", 
    "Microsoft", "Apple", "NVIDIA", ...
]
```

#### 📱 Produtos Trending
```python
TRENDING_PRODUCTS = [
    "ChatGPT-4o", "Claude 3.5 Sonnet", 
    "iPhone 16 Pro", "Windows 11 24H2", ...
]
```

#### 🔬 Tecnologias Emergentes
```python
EMERGING_TECH = [
    "IA generativa", "computação quântica", 
    "edge computing", "6G", ...
]
```

#### 📚 Tipos de Conteúdo Educativo
```python
EDUCATIONAL_CONTENT_TYPES = [
    "Como funciona", "Guia completo", 
    "Análise detalhada", "Comparativo", ...
]
```

#### 🏭 Setores de Aplicação
```python
APPLICATION_SECTORS = [
    "saúde", "educação", "finanças", 
    "startups", "desenvolvimento", ...
]
```

#### 📰 Fontes Credíveis
```python
CREDIBLE_SOURCES = {
    "tech_news": ["TechCrunch", "The Verge", ...],
    "brazilian": ["Tecmundo", "Olhar Digital", ...],
    "business": ["Bloomberg", "Reuters", ...],
    "official": ["Blog oficial da Apple", ...]
}
```

**Como atualizar**:
1. Edite `trends.py`
2. Adicione novas empresas, produtos ou tecnologias
3. Mantenha as listas atualizadas mensalmente

---

### 4. 🛡️ `ethical_guidelines.md` - Diretrizes Éticas

**Função**: Define princípios éticos e diretrizes de credibilidade.

**Princípios Fundamentais**:

#### ✅ O que FAZEMOS:
- Conteúdo educativo que explica conceitos
- Análises técnicas baseadas em conhecimento estabelecido
- Guias práticos para profissionais
- Comparativos equilibrados entre tecnologias
- Fontes credíveis e referências reais

#### ❌ O que NÃO fazemos:
- Inventar notícias ou eventos específicos
- Criar dados ou estatísticas falsas
- Usar linguagem sensacionalista
- Afirmar fatos não verificáveis
- Gerar "breaking news" fictícias

**Validação Automática**:
O sistema verifica automaticamente:
- Palavras sensacionalistas no título
- Timestamps específicos no conteúdo
- Presença de indicadores educativos
- Conformidade com diretrizes éticas

**Como usar**:
- Consulte antes de modificar o sistema
- Use como referência para novos tipos de conteúdo
- Atualize quando necessário

---

### 5. 🛠️ `utils.py` - Utilitários de Gerenciamento

**Função**: Ferramentas para manutenção e monitoramento do sistema.

**Comandos Disponíveis**:

#### 📊 Estatísticas Completas
```bash
python utils.py stats
```
**Saída**:
- Número de tópicos em cache
- Última atualização do cache
- Últimos 10 tópicos gerados
- Total de posts criados
- Posts por mês
- Post mais recente

#### 🗑️ Limpeza de Cache
```bash
python utils.py clear
```
**Função**: Remove todos os tópicos do cache

#### 🧹 Limpeza Automática
```bash
python utils.py cleanup
```
**Função**: Remove cache com mais de 30 dias

#### 💾 Apenas Cache
```bash
python utils.py cache
```
**Função**: Mostra apenas estatísticas do cache

#### 📄 Apenas Posts
```bash
python utils.py posts
```
**Função**: Mostra apenas estatísticas dos posts

**Quando usar**:
- **Diariamente**: `python utils.py stats` (monitoramento)
- **Semanalmente**: `python utils.py cleanup` (manutenção)
- **Quando necessário**: `python utils.py clear` (reset)

---

## 🔧 Operações Principais

### 🚀 Geração de Conteúdo

#### Execução Padrão
```bash
python autopost.py
```

**Processo**:
1. ✅ Carrega configurações
2. ✅ Verifica diretrizes éticas
3. 🧠 Gera tópico educativo único
4. ✍️ Cria artigo com 700-900 palavras
5. 🏷️ Gera tags automáticas
6. 📝 Cria arquivo Hugo
7. 🚀 Commit e push no Git

#### Saída Esperada
```
📚 Iniciando geração de conteúdo educativo...
📅 Data/hora: 12/09/2025 14:30:15
🎯 Foco: Artigos técnicos educativos e análises
✅ Diretrizes éticas carregadas
🧠 Gerando tópico educativo sobre tecnologia...
✅ Tópico gerado: Guia completo: Implementando IA generativa em startups
📚 Selecionando fontes credíveis...
✅ 4 fontes selecionadas: Tecmundo, TechCrunch, The Verge, Blog oficial da OpenAI
✍️ Escrevendo artigo educativo sobre: "Guia completo: Implementando IA generativa em startups"...
✅ Artigo gerado com sucesso (incluindo fontes).
🏷️ Gerando tags para o post...
📝 Formatando e salvando o post para o Hugo...
✅ Post salvo em: 2025-09-12-guia-completo-implementando-ia-generativa-em-startups.md
📊 Tags geradas: inteligencia-artificial, startups, guia, implementacao
🚀 Fazendo commit do novo post...
✅ Commit local realizado com sucesso!
📡 Enviando para o repositório remoto (git push)...
✅ Push realizado com sucesso!

✨ Artigo educativo 'Guia completo: Implementando IA generativa em startups' publicado com sucesso! ✨
📄 Arquivo: 2025-09-12-guia-completo-implementando-ia-generativa-em-startups.md
📊 Tamanho: 1247 caracteres
📚 Tipo: Conteúdo educativo e técnico
🕒 Processo concluído em: 14:32:18
```

### 📊 Monitoramento

#### Verificar Status do Sistema
```bash
python utils.py stats
```

#### Verificar Configurações
```bash
python -c "from config import *; print(f'Artigos: {ARTICLE_MIN_WORDS}-{ARTICLE_MAX_WORDS} palavras')"
```

#### Testar Geração de Tópico
```bash
python -c "from autopost import generate_new_topic, setup_api; setup_api(); print('Tópico:', generate_new_topic())"
```

---

## 🔍 Troubleshooting

### ❌ Problemas Comuns

#### 1. Erro de API Key
**Sintoma**: `ERRO: A variável de ambiente GOOGLE_API_KEY não foi encontrada`
**Solução**:
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Verifique o conteúdo (sem mostrar a chave)
echo "GOOGLE_API_KEY está definida: $(grep -q GOOGLE_API_KEY .env && echo 'SIM' || echo 'NÃO')"
```

#### 2. Cache Corrompido
**Sintoma**: Tópicos duplicados ou erro ao carregar cache
**Solução**:
```bash
python utils.py clear
```

#### 3. Posts de Baixa Qualidade
**Sintoma**: Artigos muito curtos ou sem estrutura
**Solução**:
1. Edite `config.py`:
```python
ARTICLE_MIN_WORDS = 800  # Aumentar mínimo
MAX_ARTICLE_ATTEMPTS = 5  # Mais tentativas
```

#### 4. Erro de Git
**Sintoma**: Falha no commit ou push
**Solução**:
```bash
# Verifique configuração do Git
git config --list | grep user

# Configure se necessário
git config user.name "Seu Nome"
git config user.email "seu@email.com"
```

#### 5. Conteúdo Não Ético
**Sintoma**: Títulos sensacionalistas ou conteúdo inadequado
**Solução**:
- O sistema já valida automaticamente
- Verifique `ethical_guidelines.md`
- Ajuste validação em `validate_ethical_guidelines()`

---

## 📈 Manutenção

### 🗓️ Rotina Diária
```bash
# Verificar status
python utils.py stats

# Gerar conteúdo
python autopost.py
```

### 🗓️ Rotina Semanal
```bash
# Limpeza automática
python utils.py cleanup

# Verificar posts gerados
python utils.py posts
```

### 🗓️ Rotina Mensal
1. **Atualizar tendências**:
   - Editar `trends.py`
   - Adicionar novas empresas/produtos
   - Remover itens obsoletos

2. **Revisar configurações**:
   - Verificar `config.py`
   - Ajustar limites se necessário

3. **Backup do cache**:
```bash
cp .cache/topics_cache.json .cache/topics_cache_backup.json
```

---

## 🎛️ Personalização Avançada

### 🎨 Modificar Tipos de Conteúdo

**Arquivo**: `trends.py`
```python
EDUCATIONAL_CONTENT_TYPES = [
    "Como funciona",
    "Guia completo", 
    "SEU NOVO TIPO AQUI",  # Adicione aqui
    "Análise detalhada"
]
```

### 🏷️ Adicionar Novas Tags

**Arquivo**: `config.py`
```python
COMMON_TECH_TAGS = [
    "inteligencia-artificial",
    "sua-nova-tag",  # Adicione aqui
    "startups"
]
```

### 📰 Adicionar Novas Fontes

**Arquivo**: `trends.py`
```python
CREDIBLE_SOURCES = {
    "tech_news": [
        "TechCrunch",
        "Sua Nova Fonte",  # Adicione aqui
        "The Verge"
    ]
}
```

### ⚙️ Ajustar Comportamento

**Arquivo**: `config.py`
```python
# Para artigos mais longos
ARTICLE_MIN_WORDS = 1000
ARTICLE_MAX_WORDS = 1500

# Para mais tentativas
MAX_ARTICLE_ATTEMPTS = 5

# Para cache maior
MAX_CACHED_TOPICS = 100
```

---

## 📋 Checklist de Operação

### ✅ Antes de Executar
- [ ] Arquivo `.env` com `GOOGLE_API_KEY` configurado
- [ ] Git configurado (`user.name` e `user.email`)
- [ ] Diretório `content/posts/` existe
- [ ] Conexão com internet ativa

### ✅ Após Execução
- [ ] Post gerado em `content/posts/`
- [ ] Commit realizado no Git
- [ ] Push enviado para repositório
- [ ] Cache atualizado em `.cache/`

### ✅ Manutenção Regular
- [ ] Verificar estatísticas semanalmente
- [ ] Limpar cache mensalmente
- [ ] Atualizar tendências mensalmente
- [ ] Revisar diretrizes éticas trimestralmente

---

## 🆘 Suporte e Contato

### 📚 Documentação Adicional
- `README_autopost.md` - Visão geral e instalação
- `ethical_guidelines.md` - Diretrizes éticas completas
- `system_overview.md` - Arquitetura do sistema

### 🔧 Logs e Debug
- Logs da API: `gemini_error.log`
- Cache: `.cache/topics_cache.json`
- Posts: `content/posts/`

### 🚨 Em Caso de Emergência
1. **Parar execução**: `Ctrl+C`
2. **Limpar cache**: `python utils.py clear`
3. **Verificar logs**: `cat gemini_error.log`
4. **Restaurar backup**: Restaurar arquivos de backup

---

**📖 Manual atualizado em: Setembro 2025**
**🔄 Versão do sistema: 2.0 (Ética)**