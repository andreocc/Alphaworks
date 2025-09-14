# Visão Geral do Sistema AutoPost

## 📁 Arquivos e Suas Funções

### 🔧 `config.py` - Configurações Centralizadas
**Status: ✅ USADO ATIVAMENTE**

Constantes utilizadas no `autopost.py`:
- `ARTICLE_MIN_WORDS` / `ARTICLE_MAX_WORDS` - Tamanho dos artigos
- `MAX_API_RETRIES` - Tentativas de chamada da API
- `MAX_CACHED_TOPICS` - Limite do cache de tópicos
- `MAX_TOPIC_ATTEMPTS` / `MAX_ARTICLE_ATTEMPTS` - Tentativas de geração
- `TIMEZONE_OFFSET` - Fuso horário brasileiro
- `HUGO_AUTHOR` / `HUGO_CATEGORY` - Metadados do Hugo

### 📊 `trends.py` - Base de Dados de Tecnologias
**Status: ✅ USADO ATIVAMENTE**

Constantes utilizadas no `autopost.py`:
- `EDUCATIONAL_CONTENT_TYPES` - Tipos de conteúdo educativo
- `EDUCATIONAL_KEYWORDS` - Palavras-chave para títulos
- `APPLICATION_SECTORS` - Setores de aplicação
- `TECHNICAL_CONCEPTS` - Conceitos técnicos
- `CREDIBLE_SOURCES` - Fontes categorizadas por tipo
- `HOT_COMPANIES` / `TRENDING_PRODUCTS` / `EMERGING_TECH` - Contexto tecnológico

### 📋 `ethical_guidelines.md` - Diretrizes Éticas
**Status: ✅ VERIFICADO NO STARTUP**

Uso no sistema:
- Verificação de existência no startup
- Referência para validação ética
- Guia para desenvolvimento responsável
- Documentação dos princípios do projeto

### 🛠️ `utils.py` - Utilitários de Gerenciamento
**Status: ✅ INDEPENDENTE**

Funcionalidades:
- Estatísticas do cache e posts
- Limpeza de dados antigos
- Relatórios de uso
- Manutenção do sistema

## 🔄 Fluxo de Uso dos Arquivos

### 1. Inicialização
```python
from config import *        # Carrega todas as configurações
from trends import *        # Carrega base de dados de tecnologias
load_ethical_guidelines()   # Verifica diretrizes éticas
```

### 2. Geração de Tópico
```python
# Usa constantes do trends.py:
content_type = random.choice(EDUCATIONAL_CONTENT_TYPES)
educational_keyword = random.choice(EDUCATIONAL_KEYWORDS)
application_sector = random.choice(APPLICATION_SECTORS)
```

### 3. Geração de Artigo
```python
# Usa configurações do config.py:
f"- {ARTICLE_MIN_WORDS}-{ARTICLE_MAX_WORDS} palavras"
```

### 4. Seleção de Fontes
```python
# Usa fontes do trends.py:
references.append(random.choice(CREDIBLE_SOURCES["brazilian"]))
references.extend(random.sample(CREDIBLE_SOURCES["tech_news"], 2))
```

### 5. Validação Ética
```python
# Segue diretrizes do ethical_guidelines.md:
validate_ethical_guidelines(title, content)
```

### 6. Criação do Post
```python
# Usa configurações do config.py:
categories: - {HUGO_CATEGORY}
author: "{HUGO_AUTHOR}"
```

## ✅ Confirmação de Integração

Todos os arquivos estão sendo utilizados:

- **config.py**: ✅ 8 constantes ativas
- **trends.py**: ✅ 6 arrays principais em uso
- **ethical_guidelines.md**: ✅ Verificado no startup
- **utils.py**: ✅ Funciona independentemente

## 🎯 Benefícios da Arquitetura

1. **Modularidade**: Cada arquivo tem responsabilidade específica
2. **Manutenibilidade**: Fácil atualização de configurações
3. **Escalabilidade**: Novos tipos de conteúdo facilmente adicionáveis
4. **Ética**: Diretrizes claras e verificáveis
5. **Flexibilidade**: Configurações centralizadas e ajustáveis

## 🔄 Como Atualizar

### Para adicionar nova tecnologia:
Edite `trends.py` → adicione em `EMERGING_TECH` ou `TRENDING_PRODUCTS`

### Para mudar configurações:
Edite `config.py` → ajuste limites, tamanhos, tentativas

### Para adicionar nova diretriz ética:
Edite `ethical_guidelines.md` → documente nova regra

### Para ver estatísticas:
Execute `python utils.py stats`

---

**Sistema totalmente integrado e funcional! 🚀**