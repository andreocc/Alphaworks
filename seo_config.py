# Configurações SEO para Google Ads e Monetização

# Meta tags e estrutura
SEO_SITE_NAME = "Alphaworks Tech Blog"
SEO_SITE_DESCRIPTION = "Conteúdo técnico sobre tecnologia, programação e inovação"
SEO_DEFAULT_IMAGE = "/images/og-default.jpg"
SEO_TWITTER_HANDLE = "@alphaworks"

# Configurações de conteúdo para monetização
MONETIZATION_FOCUS = {
    "min_word_count": 1200,  # Mínimo para bom desempenho de ads
    "optimal_word_count": 1500,  # Ideal para engagement e ads
    "max_word_count": 2000,  # Máximo antes de perder leitores
    "min_reading_time": 5,  # Minutos mínimos para boa monetização
    "optimal_reading_time": 8  # Tempo ideal para maximizar ads
}

# Palavras-chave de alta conversão para ads
HIGH_VALUE_KEYWORDS = {
    "desenvolvimento": {
        "primary": ["programação", "desenvolvimento web", "javascript", "python"],
        "long_tail": ["como aprender programação", "melhores linguagens programação 2025", "tutorial javascript iniciantes"],
        "commercial": ["curso programação", "bootcamp desenvolvimento", "certificação programador"]
    },
    "business": {
        "primary": ["startup", "empreendedorismo", "negócios digitais", "inovação"],
        "long_tail": ["como criar startup sucesso", "ideias negócios digitais 2025", "investimento startup brasil"],
        "commercial": ["consultoria startup", "aceleradora empresas", "investidor anjo"]
    },
    "technology": {
        "primary": ["inteligência artificial", "machine learning", "automação", "cloud computing"],
        "long_tail": ["como implementar IA empresa", "benefícios automação processos", "migração cloud computing"],
        "commercial": ["serviços IA", "consultoria cloud", "software automação"]
    }
}

# Templates de título otimizados para CTR
HIGH_CTR_TITLE_TEMPLATES = [
    "Como {keyword} pode aumentar sua produtividade em {percentage}%",
    "{number} segredos de {keyword} que os especialistas não contam",
    "Guia definitivo: {keyword} do zero ao profissional em {timeframe}",
    "Por que {keyword} é essencial para {target_audience} em 2025",
    "{keyword}: {number} erros que custam caro (e como evitar)",
    "Descoberta: {keyword} revoluciona {industry} - veja como",
    "{number} ferramentas de {keyword} que todo {professional} deveria conhecer",
    "Análise completa: {keyword} vs {alternative} - qual escolher?",
    "Tutorial prático: implementando {keyword} em {context} passo a passo",
    "Tendência 2025: como {keyword} está transformando {sector}"
]

# Estruturas de conteúdo para maximizar tempo na página
ENGAGEMENT_STRUCTURES = {
    "tutorial_completo": {
        "sections": [
            "Introdução e contexto",
            "Pré-requisitos e preparação", 
            "Passo a passo detalhado",
            "Exemplos práticos reais",
            "Problemas comuns e soluções",
            "Dicas avançadas",
            "Próximos passos",
            "Recursos adicionais"
        ],
        "min_words_per_section": 150
    },
    "guia_comparativo": {
        "sections": [
            "Visão geral do problema",
            "Opções disponíveis",
            "Critérios de avaliação",
            "Comparação detalhada",
            "Casos de uso específicos",
            "Recomendações por perfil",
            "Conclusão e próximos passos"
        ],
        "min_words_per_section": 180
    },
    "analise_tendencia": {
        "sections": [
            "Contexto atual do mercado",
            "Principais tendências identificadas",
            "Impacto nas empresas",
            "Oportunidades e desafios",
            "Como se preparar",
            "Previsões para o futuro",
            "Ação recomendada"
        ],
        "min_words_per_section": 200
    }
}

# Call-to-actions otimizados para conversão
CTA_TEMPLATES = {
    "newsletter": [
        "📧 Receba conteúdos exclusivos sobre {topic} direto no seu email",
        "🚀 Quer dominar {topic}? Assine nossa newsletter especializada",
        "💡 Mantenha-se atualizado com as últimas tendências em {topic}"
    ],
    "social": [
        "📱 Compartilhe este guia com sua rede profissional",
        "💬 O que você achou deste conteúdo? Comente suas experiências",
        "🔄 Ajude outros profissionais: compartilhe este artigo"
    ],
    "engagement": [
        "❓ Tem dúvidas sobre {topic}? Deixe nos comentários",
        "🎯 Qual sua experiência com {topic}? Conte para a comunidade",
        "📊 Este conteúdo foi útil? Avalie e compartilhe sua opinião"
    ]
}

# Configurações de schema markup para SEO
SCHEMA_MARKUP_TEMPLATES = {
    "article": {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{title}",
        "description": "{description}",
        "author": {
            "@type": "Person",
            "name": "{author}"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Alphaworks",
            "logo": {
                "@type": "ImageObject",
                "url": "{site_logo}"
            }
        },
        "datePublished": "{date_published}",
        "dateModified": "{date_modified}",
        "wordCount": "{word_count}",
        "timeRequired": "PT{reading_time}M"
    },
    "howto": {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "{title}",
        "description": "{description}",
        "totalTime": "PT{total_time}M",
        "estimatedCost": {
            "@type": "MonetaryAmount",
            "currency": "BRL",
            "value": "0"
        }
    }
}

# Métricas de qualidade para monetização
QUALITY_METRICS = {
    "bounce_rate_target": 60,  # % máximo aceitável
    "time_on_page_target": 300,  # segundos mínimos
    "pages_per_session_target": 2.5,  # páginas por sessão
    "ctr_target": 2.0,  # % mínimo de CTR
    "ad_viewability_target": 70  # % mínimo de viewability dos ads
}