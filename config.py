# Configurações do AutoPost

# Configurações de conteúdo
ARTICLE_MIN_WORDS = 700
ARTICLE_MAX_WORDS = 900
MIN_SUBTITLES = 2
MAX_TAGS = 6

# Configurações de cache
MAX_CACHED_TOPICS = 50
CACHE_RETENTION_DAYS = 30

# Configurações de retry
MAX_API_RETRIES = 3
MAX_TOPIC_ATTEMPTS = 5
MAX_ARTICLE_ATTEMPTS = 3

# Fontes de referência padrão (fallback)
DEFAULT_REFERENCES = [
    "TechCrunch",
    "The Verge", 
    "Tecmundo",
    "Olhar Digital",
    "Ars Technica"
]

# Categorias e tags comuns
COMMON_TECH_TAGS = [
    "inteligencia-artificial",
    "startups", 
    "ciberseguranca",
    "inovacao",
    "big-tech",
    "software",
    "hardware", 
    "mobile",
    "web",
    "dados",
    "blockchain",
    "cloud",
    "iot",
    "5g",
    "realidade-virtual"
]

# Configurações do Hugo
HUGO_AUTHOR = "Alphaworks"
HUGO_CATEGORY = "Tecnologia"
TIMEZONE_OFFSET = -3  # Brasília (UTC-3)

# Configurações de SEO
SEO_TITLE_MIN_LENGTH = 50
SEO_TITLE_MAX_LENGTH = 100
SEO_DESCRIPTION_MIN_LENGTH = 150
SEO_DESCRIPTION_MAX_LENGTH = 160
SEO_ARTICLE_MIN_WORDS = 1200  # Melhor para Google Ads
SEO_ARTICLE_MAX_WORDS = 1800
SEO_KEYWORDS_PER_POST = 3  # Palavras-chave principais por post

# Configurações de Notícias
NEWS_API_ENABLED = True
NEWS_CACHE_HOURS = 1  # Cache de notícias por 1 hora
NEWS_SOURCES_PRIORITY = [
    "TechCrunch", "The Verge", "Ars Technica", "Wired", 
    "Tecmundo", "Olhar Digital", "Reuters", "Bloomberg"
]
NEWS_CATEGORIES = ["technology", "startup", "ai", "cybersecurity"]
MAX_NEWS_AGE_HOURS = 48  # Máximo 48 horas de idade das notícias

# Configurações para Profissionais de TI
IT_PROFESSIONAL_FOCUS = True
TECHNICAL_DEPTH_LEVEL = "advanced"  # basic, intermediate, advanced
TARGET_AUDIENCE = "it_professionals"  # developers, sysadmins, it_professionals, tech_enthusiasts

# Configurações de Performance e Timeout
API_TIMEOUT_SECONDS = 30  # Timeout para chamadas da API
ARTICLE_GENERATION_TIMEOUT = 60  # Timeout específico para geração de artigos
PROGRESS_INDICATORS = True  # Mostrar indicadores de progresso
CHUNK_ARTICLE_GENERATION = True  # Gerar artigo em partes para evitar timeout