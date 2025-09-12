# AutoPost - Gerador Automático de Posts

Sistema automatizado para geração de posts de blog sobre tecnologia usando IA (Google Gemini).

## 🔥 NOVA VERSÃO - Foco em Notícias Recentes

### ✅ Sistema de Tendências Atuais
- Base de dados com empresas, produtos e tecnologias em alta
- Seleção inteligente de tópicos baseada em trends reais
- Contexto temporal específico para notícias urgentes
- Métricas realistas (usuários, receita, crescimento)

### ✅ Geração de Títulos Otimizada
- Fórmulas jornalísticas para títulos impactantes
- Palavras-chave de urgência (BREAKING, EXCLUSIVO, CONFIRMADO)
- Elementos específicos: empresas, produtos, eventos
- Títulos que soam como breaking news reais

## 🆕 Melhorias Implementadas

### ✅ Fontes de Referência
- Geração automática de 3-5 fontes credíveis para cada artigo
- Seção "Fontes" adicionada automaticamente ao final dos posts
- Fontes baseadas em sites reais: TechCrunch, The Verge, Tecmundo, etc.

### ✅ Sistema de Cache Inteligente
- Evita tópicos duplicados ou muito similares
- Cache persistente de até 50 tópicos recentes
- Verificação de similaridade por hash MD5

### ✅ Metadados Aprimorados
- Tags automáticas baseadas no conteúdo
- Resumo (summary) gerado automaticamente
- Categorização automática
- Timestamps com fuso horário brasileiro

### ✅ Validação de Qualidade
- Verificação de tamanho mínimo do artigo
- Validação de estrutura (subtítulos)
- Sistema de retry para melhorar qualidade

### ✅ Configuração Centralizada
- Arquivo `config.py` para personalização fácil
- Parâmetros ajustáveis sem modificar código principal
- Configurações de retry, cache e formatação

### ✅ Utilitários de Gerenciamento
- Script `utils.py` para estatísticas e manutenção
- Limpeza automática de cache antigo
- Relatórios de posts gerados

## 📁 Estrutura de Arquivos

```
├── autopost.py          # Script principal melhorado
├── config.py            # Configurações centralizadas
├── trends.py            # Base de dados de tendências atuais
├── utils.py             # Utilitários e estatísticas
├── .cache/              # Cache de tópicos (criado automaticamente)
│   └── topics_cache.json
├── content/posts/       # Posts gerados
└── .env                 # Chave da API Gemini
```

## 🚀 Como Usar

### Instalação
```bash
pip install google-generativeai python-dotenv
```

### Configuração
1. Adicione sua chave do Google Gemini no arquivo `.env`:
```
GOOGLE_API_KEY=sua_chave_aqui
```

### Execução
```bash
# Gerar novo post
python autopost.py

# Ver estatísticas
python utils.py stats

# Limpar cache
python utils.py clear
```

## ⚙️ Configurações Disponíveis

Edite `config.py` para personalizar:

- **Tamanho do artigo**: `ARTICLE_MIN_WORDS`, `ARTICLE_MAX_WORDS`
- **Cache**: `MAX_CACHED_TOPICS`, `CACHE_RETENTION_DAYS`
- **Retry**: `MAX_API_RETRIES`, `MAX_TOPIC_ATTEMPTS`
- **Metadados**: `HUGO_AUTHOR`, `HUGO_CATEGORY`
- **Fuso horário**: `TIMEZONE_OFFSET`

## 📊 Utilitários

```bash
# Estatísticas completas
python utils.py stats

# Apenas cache
python utils.py cache

# Apenas posts
python utils.py posts

# Limpeza automática
python utils.py cleanup
```

## 🔧 Melhorias Técnicas

### Sistema de Retry Robusto
- Múltiplas tentativas para chamadas da API
- Regeneração automática em caso de conteúdo de baixa qualidade
- Fallbacks para referências e tags

### Cache Inteligente
- Evita repetição de tópicos similares
- Armazenamento eficiente com hash MD5
- Limpeza automática de entradas antigas

### Geração de Metadados
- Tags automáticas baseadas no conteúdo
- Resumos extraídos do início do artigo
- Timestamps precisos com fuso horário

### Validação de Qualidade
- Verificação de tamanho mínimo
- Contagem de subtítulos
- Estrutura markdown válida

## 📈 Exemplo de Post Gerado

```markdown
---
title: "Nova IA da OpenAI Revoluciona Programação"
date: 2025-09-12T10:30:00-03:00
draft: false
summary: "OpenAI lança nova ferramenta de IA que promete..."
tags:
  - inteligencia-artificial
  - programacao
  - openai
categories:
  - Tecnologia
author: "AutoPost AI"
---

## Introdução
[Conteúdo do artigo...]

## Fontes

1. TechCrunch
2. The Verge
3. Site oficial da OpenAI
```

## 🛠️ Troubleshooting

### Cache corrompido
```bash
python utils.py clear
```

### Posts de baixa qualidade
- Ajuste `ARTICLE_MIN_WORDS` em `config.py`
- Aumente `MAX_ARTICLE_ATTEMPTS`

### Tópicos repetitivos
- Verifique o cache: `python utils.py cache`
- Limpe se necessário: `python utils.py clear`

## 🎯 Exemplos de Títulos Gerados

Com as melhorias, o script agora gera títulos como:

- "CONFIRMADO: OpenAI lança GPT-5 com 10x mais poder"
- "EXCLUSIVO: Meta adquire startup de IA por US$ 15 bilhões" 
- "Apple anuncia iPhone 17 com tela holográfica para 2026"
- "VAZOU: Google prepara Gemini 2.0 que supera humanos"
- "OFICIAL: Microsoft integra IA em Windows 12"

## 🔄 Atualizando Tendências

Para manter o conteúdo atual, edite o arquivo `trends.py`:

```python
# Adicione novas empresas em alta
HOT_COMPANIES.append("Nova Startup")

# Atualize produtos trending
TRENDING_PRODUCTS.append("Novo Produto 2026")

# Modifique tecnologias emergentes
EMERGING_TECH.append("Nova Tecnologia")
```

## 📝 Próximas Melhorias

- [x] ✅ Sistema de tendências atuais
- [x] ✅ Títulos com urgência jornalística  
- [x] ✅ Dados e métricas realistas
- [x] ✅ Fontes categorizadas por tipo
- [ ] Integração com APIs de notícias reais
- [ ] Geração de imagens automática
- [ ] Agendamento de posts
- [ ] Análise de SEO
- [ ] Múltiplos idiomas