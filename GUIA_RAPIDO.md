# ⚡ Guia Rápido - AutoPost

## 🚀 Comandos Essenciais

### Operação Principal
```bash
python autopost.py                    # Gerar novo post educativo
```

### Monitoramento
```bash
python utils.py stats                 # Ver estatísticas completas
python utils.py cache                 # Ver apenas cache
python utils.py posts                 # Ver apenas posts
```

### Manutenção
```bash
python utils.py clear                 # Limpar cache
python utils.py cleanup               # Limpeza automática (>30 dias)
```

### Testes
```bash
# Testar configurações
python -c "from config import *; print(f'Config OK: {ARTICLE_MIN_WORDS}-{ARTICLE_MAX_WORDS} palavras')"

# Testar geração de tópico
python -c "from autopost import generate_new_topic, setup_api; setup_api(); print(generate_new_topic())"

# Testar integração
python -c "from autopost import *; from config import *; from trends import *; print('✅ Tudo integrado!')"
```

---

## 📁 Estrutura de Arquivos

```
📦 AutoPost/
├── 🚀 autopost.py              # Motor principal
├── ⚙️ config.py                # Configurações
├── 📊 trends.py                # Base de dados tech
├── 🛡️ ethical_guidelines.md    # Diretrizes éticas
├── 🛠️ utils.py                 # Utilitários
├── 📖 MANUAL_OPERACAO.md       # Manual completo
├── ⚡ GUIA_RAPIDO.md           # Este guia
├── 🔑 .env                     # Chave da API
└── 📁 .cache/                  # Cache do sistema
    └── topics_cache.json
```

---

## ⚙️ Configurações Principais

### `config.py` - Ajustes Rápidos
```python
ARTICLE_MIN_WORDS = 700        # Tamanho mínimo
ARTICLE_MAX_WORDS = 900        # Tamanho máximo
MAX_CACHED_TOPICS = 50         # Limite do cache
MAX_API_RETRIES = 3            # Tentativas da API
HUGO_AUTHOR = "Alphaworks"     # Seu nome/empresa
```

### `trends.py` - Atualizações Frequentes
```python
# Adicione novas empresas aqui
HOT_COMPANIES = ["OpenAI", "Meta", "SUA_EMPRESA"]

# Adicione novos produtos aqui  
TRENDING_PRODUCTS = ["ChatGPT-4o", "SEU_PRODUTO"]

# Adicione novas tecnologias aqui
EMERGING_TECH = ["IA generativa", "SUA_TECH"]
```

---

## 🔧 Troubleshooting Rápido

| Problema | Solução Rápida |
|----------|----------------|
| ❌ Erro de API Key | Verificar `.env` com `GOOGLE_API_KEY=sua_chave` |
| 🔄 Tópicos duplicados | `python utils.py clear` |
| 📝 Posts muito curtos | Aumentar `ARTICLE_MIN_WORDS` em `config.py` |
| 🚫 Erro de Git | `git config user.name "Nome"` e `git config user.email "email"` |
| 💾 Cache corrompido | `python utils.py clear` |

---

## 📊 Saída Normal do Sistema

```
📚 Iniciando geração de conteúdo educativo...
✅ Diretrizes éticas carregadas
🧠 Gerando tópico educativo sobre tecnologia...
✅ Tópico gerado: Guia completo: [TÍTULO]
📚 Selecionando fontes credíveis...
✅ 4 fontes selecionadas: [FONTES]
✍️ Escrevendo artigo educativo...
✅ Artigo gerado com sucesso
🏷️ Gerando tags para o post...
📝 Formatando e salvando o post...
✅ Post salvo em: [ARQUIVO].md
🚀 Fazendo commit do novo post...
✅ Push realizado com sucesso!
✨ Artigo publicado com sucesso! ✨
```

---

## 🎯 Tipos de Conteúdo Gerados

- **Guias**: "Como implementar X em Y"
- **Análises**: "Comparativo entre A e B"  
- **Explicações**: "Entendendo conceitos de X"
- **Tendências**: "O futuro da tecnologia X"
- **Fundamentos**: "Introdução à tecnologia Y"

---

## 🛡️ Validação Ética Automática

O sistema **automaticamente rejeita**:
- ❌ Títulos sensacionalistas ("BREAKING", "EXCLUSIVO")
- ❌ Conteúdo com timestamps específicos ("hoje", "ontem")
- ❌ Informações não verificáveis
- ❌ Linguagem de urgência desnecessária

O sistema **sempre inclui**:
- ✅ Fontes credíveis reais
- ✅ Conteúdo educativo e técnico
- ✅ Análises equilibradas
- ✅ Valor prático para o leitor

---

## 📈 Métricas de Sucesso

### Cache Saudável
- 📊 10-50 tópicos em cache
- 🔄 Atualização recente (< 7 dias)
- 🚫 Sem duplicatas

### Posts de Qualidade
- 📝 700-900 palavras
- 🏷️ 3-6 tags relevantes
- 📚 3-5 fontes credíveis
- ✅ Aprovação ética automática

### Sistema Estável
- 🚀 Execução sem erros
- 💾 Cache funcionando
- 🔄 Git commits automáticos
- 📊 Estatísticas consistentes

---

## 🔄 Rotina Recomendada

### Diário
```bash
python utils.py stats    # Verificar status
python autopost.py       # Gerar conteúdo
```

### Semanal  
```bash
python utils.py cleanup  # Limpeza automática
```

### Mensal
1. Atualizar `trends.py` com novas tecnologias
2. Revisar `config.py` se necessário
3. Backup do cache: `cp .cache/topics_cache.json backup/`

---

## 📞 Ajuda Rápida

### Ver Comandos Disponíveis
```bash
python utils.py          # Lista todos os comandos
```

### Ver Configurações Atuais
```bash
python -c "from config import *; print('Min:', ARTICLE_MIN_WORDS, 'Max:', ARTICLE_MAX_WORDS)"
```

### Ver Estatísticas Resumidas
```bash
python -c "from utils import *; cache=load_cache(); print(f'Cache: {len(cache.get(\"used_topics\", []))} tópicos')"
```

---

**⚡ Guia atualizado: Setembro 2025**