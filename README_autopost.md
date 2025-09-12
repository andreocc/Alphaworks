# AutoPost - Gerador Automático de Posts

Sistema automatizado para geração de posts de blog sobre tecnologia usando IA (Google Gemini).

## 📚 VERSÃO ÉTICA - Foco em Conteúdo Educativo

### ✅ Sistema de Conteúdo Responsável
- Artigos educativos e análises técnicas ao invés de "notícias"
- Base de conhecimento sobre tecnologias e conceitos
- Contexto educativo focado em valor real para o leitor
- Diretrizes éticas rigorosas para credibilidade

### ✅ Geração de Títulos Educativos
- Fórmulas para conteúdo educativo (Guia, Como, Análise)
- Palavras-chave informativas ao invés de sensacionalistas
- Foco em explicar, comparar e educar
- Títulos que agregam valor técnico real

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
├── autopost.py              # Script principal (foco educativo)
├── config.py                # Configurações centralizadas
├── trends.py                # Base de dados de tecnologias
├── utils.py                 # Utilitários e estatísticas
├── ethical_guidelines.md    # Diretrizes éticas do projeto
├── .cache/                  # Cache de tópicos (criado automaticamente)
│   └── topics_cache.json
├── content/posts/           # Posts educativos gerados
└── .env                     # Chave da API Gemini
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

## 🎯 Exemplos de Títulos Educativos

Com o foco ético, o script agora gera títulos como:

- "Como a Inteligência Artificial está transformando o desenvolvimento"
- "Guia completo: Entendendo computação em nuvem em 2025"
- "Análise: Comparativo entre React e Vue.js para desenvolvedores"
- "Fundamentos de cibersegurança para pequenas empresas"
- "Tendências: O futuro da computação quântica explicado"

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

## 🛡️ Diretrizes Éticas

### ✅ O que fazemos:
- **Conteúdo educativo** que explica conceitos e tecnologias
- **Análises técnicas** baseadas em conhecimento estabelecido  
- **Guias práticos** para desenvolvedores e profissionais
- **Comparativos** equilibrados entre tecnologias
- **Fontes credíveis** e referências reais

### ❌ O que NÃO fazemos:
- Inventar notícias ou eventos específicos
- Criar dados ou estatísticas falsas
- Usar linguagem sensacionalista
- Afirmar fatos não verificáveis
- Gerar "breaking news" fictícias

## 📝 Próximas Melhorias

- [x] ✅ Sistema de conteúdo educativo
- [x] ✅ Diretrizes éticas rigorosas
- [x] ✅ Títulos informativos (não sensacionalistas)
- [x] ✅ Fontes categorizadas e credíveis
- [x] ✅ Validação de credibilidade
- [ ] Integração com APIs de documentação técnica
- [ ] Geração de diagramas explicativos
- [ ] Sistema de revisão de qualidade
- [ ] Análise de SEO educativo
- [ ] Múltiplos idiomas