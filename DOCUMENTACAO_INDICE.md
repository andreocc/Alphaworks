# 📚 Índice da Documentação - Sistema AutoPost

## 🎯 Documentação Disponível

### 📖 Manuais Principais

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[MANUAL_OPERACAO.md](MANUAL_OPERACAO.md)** | Manual completo com todos os componentes | Referência completa, troubleshooting |
| **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)** | Comandos essenciais e referência rápida | Uso diário, consulta rápida |
| **[README_autopost.md](README_autopost.md)** | Visão geral e instalação do sistema | Primeira instalação, overview |

### 🛡️ Diretrizes e Ética

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[ethical_guidelines.md](ethical_guidelines.md)** | Princípios éticos e diretrizes de credibilidade | Desenvolvimento, validação de conteúdo |

### 🔧 Documentação Técnica

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[system_overview.md](system_overview.md)** | Arquitetura e integração dos componentes | Desenvolvimento, manutenção técnica |

---

## 🚀 Por Onde Começar?

### 👋 Novo Usuário
1. **[README_autopost.md](README_autopost.md)** - Entenda o que é o sistema
2. **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)** - Comandos básicos
3. **[ethical_guidelines.md](ethical_guidelines.md)** - Princípios do sistema

### 🔧 Operador Diário
1. **[GUIA_RAPIDO.md](GUIA_RAPIDO.md)** - Comandos do dia a dia
2. **[MANUAL_OPERACAO.md](MANUAL_OPERACAO.md)** - Quando precisar de detalhes

### 👨‍💻 Desenvolvedor/Administrador
1. **[system_overview.md](system_overview.md)** - Arquitetura do sistema
2. **[MANUAL_OPERACAO.md](MANUAL_OPERACAO.md)** - Operação completa
3. **[ethical_guidelines.md](ethical_guidelines.md)** - Diretrizes de desenvolvimento

---

## 📁 Estrutura dos Arquivos de Código

### 🔧 Arquivos de Configuração

| Arquivo | Função | Documentado em |
|---------|--------|----------------|
| `config.py` | Configurações centralizadas | [MANUAL_OPERACAO.md](MANUAL_OPERACAO.md#2-️-configpy---configurações-centralizadas) |
| `trends.py` | Base de dados tecnológica | [MANUAL_OPERACAO.md](MANUAL_OPERACAO.md#3--trendspy---base-de-dados-tecnológica) |
| `.env` | Chave da API Gemini | [GUIA_RAPIDO.md](GUIA_RAPIDO.md#-troubleshooting-rápido) |

### 🚀 Arquivos Executáveis

| Arquivo | Função | Documentado em |
|---------|--------|----------------|
| `autopost.py` | Motor principal do sistema | [MANUAL_OPERACAO.md](MANUAL_OPERACAO.md#1--autopostpy---motor-principal) |
| `utils.py` | Utilitários e manutenção | [MANUAL_OPERACAO.md](MANUAL_OPERACAO.md#5-️-utilspy---utilitários-de-gerenciamento) |

### 📊 Arquivos de Dados

| Arquivo/Diretório | Função | Documentado em |
|-------------------|--------|----------------|
| `.cache/topics_cache.json` | Cache de tópicos gerados | [GUIA_RAPIDO.md](GUIA_RAPIDO.md#-monitoramento) |
| `content/posts/` | Posts gerados pelo sistema | [MANUAL_OPERACAO.md](MANUAL_OPERACAO.md#-operações-principais) |

---

## 🔍 Busca Rápida por Tópico

### 🚀 Operação Básica
- **Gerar post**: [GUIA_RAPIDO.md - Comandos Essenciais](GUIA_RAPIDO.md#-comandos-essenciais)
- **Ver estatísticas**: [GUIA_RAPIDO.md - Monitoramento](GUIA_RAPIDO.md#-monitoramento)
- **Limpar cache**: [GUIA_RAPIDO.md - Manutenção](GUIA_RAPIDO.md#-manutenção)

### ⚙️ Configuração
- **Ajustar tamanho dos artigos**: [MANUAL_OPERACAO.md - config.py](MANUAL_OPERACAO.md#-configurações-de-conteúdo)
- **Adicionar novas tecnologias**: [MANUAL_OPERACAO.md - trends.py](MANUAL_OPERACAO.md#-como-atualizar)
- **Modificar autor/categoria**: [MANUAL_OPERACAO.md - Hugo](MANUAL_OPERACAO.md#️-configurações-do-hugo)

### 🛠️ Troubleshooting
- **Erro de API**: [GUIA_RAPIDO.md - Troubleshooting](GUIA_RAPIDO.md#-troubleshooting-rápido)
- **Problemas detalhados**: [MANUAL_OPERACAO.md - Troubleshooting](MANUAL_OPERACAO.md#-troubleshooting)
- **Cache corrompido**: [MANUAL_OPERACAO.md - Cache](MANUAL_OPERACAO.md#2-cache-corrompido)

### 🛡️ Ética e Qualidade
- **Diretrizes éticas**: [ethical_guidelines.md](ethical_guidelines.md)
- **Validação automática**: [MANUAL_OPERACAO.md - Validação](MANUAL_OPERACAO.md#validação-automática)
- **Tipos de conteúdo**: [GUIA_RAPIDO.md - Tipos](GUIA_RAPIDO.md#-tipos-de-conteúdo-gerados)

### 🔧 Desenvolvimento
- **Arquitetura do sistema**: [system_overview.md](system_overview.md)
- **Integração de componentes**: [system_overview.md - Fluxo](system_overview.md#-fluxo-de-uso-dos-arquivos)
- **Personalização avançada**: [MANUAL_OPERACAO.md - Personalização](MANUAL_OPERACAO.md#-personalização-avançada)

---

## 📋 Checklists Rápidos

### ✅ Instalação Inicial
- [ ] Ler [README_autopost.md](README_autopost.md)
- [ ] Configurar `.env` com `GOOGLE_API_KEY`
- [ ] Testar com [GUIA_RAPIDO.md - Testes](GUIA_RAPIDO.md#testes)
- [ ] Executar primeiro post com `python autopost.py`

### ✅ Uso Diário
- [ ] Verificar status: `python utils.py stats`
- [ ] Gerar conteúdo: `python autopost.py`
- [ ] Consultar [GUIA_RAPIDO.md](GUIA_RAPIDO.md) quando necessário

### ✅ Manutenção Semanal
- [ ] Limpeza: `python utils.py cleanup`
- [ ] Verificar posts: `python utils.py posts`
- [ ] Revisar [MANUAL_OPERACAO.md - Manutenção](MANUAL_OPERACAO.md#-manutenção)

### ✅ Atualização Mensal
- [ ] Atualizar `trends.py` com novas tecnologias
- [ ] Revisar `config.py` se necessário
- [ ] Consultar [ethical_guidelines.md](ethical_guidelines.md) para novidades

---

## 🆘 Suporte Rápido

### 🔍 Problema Específico?
1. **Consulte primeiro**: [GUIA_RAPIDO.md - Troubleshooting](GUIA_RAPIDO.md#-troubleshooting-rápido)
2. **Se não resolver**: [MANUAL_OPERACAO.md - Troubleshooting](MANUAL_OPERACAO.md#-troubleshooting)
3. **Para desenvolvimento**: [system_overview.md](system_overview.md)

### 📞 Precisa de Ajuda?
- **Comandos básicos**: [GUIA_RAPIDO.md](GUIA_RAPIDO.md)
- **Referência completa**: [MANUAL_OPERACAO.md](MANUAL_OPERACAO.md)
- **Princípios éticos**: [ethical_guidelines.md](ethical_guidelines.md)

---

## 📊 Status da Documentação

| Documento | Status | Última Atualização |
|-----------|--------|-------------------|
| MANUAL_OPERACAO.md | ✅ Completo | Setembro 2025 |
| GUIA_RAPIDO.md | ✅ Completo | Setembro 2025 |
| README_autopost.md | ✅ Atualizado | Setembro 2025 |
| ethical_guidelines.md | ✅ Completo | Setembro 2025 |
| system_overview.md | ✅ Completo | Setembro 2025 |
| DOCUMENTACAO_INDICE.md | ✅ Atual | Setembro 2025 |

---

**📚 Documentação mantida e atualizada regularmente**
**🔄 Versão do sistema: 2.0 (Ética)**