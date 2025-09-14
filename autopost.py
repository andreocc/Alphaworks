import os
import sys
import re
import random
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai
from config import *
from trends import *
from news_api_improved import get_current_news, get_news_context
from content_formatting import format_content
from content_cleaner import clean_content_completely, create_simple_structure

# --- Configurações ---
POSTS_DIR = Path("content/posts")
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
TOPICS_CACHE = CACHE_DIR / "topics_cache.json"

def setup_api():
    """Carrega variáveis de ambiente e configura a API do Gemini."""
    load_dotenv()
    # Tenta múltiplas variáveis de ambiente para compatibilidade
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("❌ ERRO: Nenhuma chave de API encontrada.")
        print("Configure uma das seguintes variáveis no arquivo .env:")
        print("  - GEMINI_API_KEY=sua_chave_aqui")
        print("  - GOOGLE_API_KEY=sua_chave_aqui")
        print("  - GOOGLE_GENERATIVE_AI_API_KEY=sua_chave_aqui")
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"❌ ERRO ao configurar a API do Gemini: {e}")
        return False

def call_gemini_api(prompt: str, safety_settings=None, max_retries=MAX_API_RETRIES, timeout=None) -> str:
    """
    Chama a API do Gemini com fallback automático para modelos mais simples.
    Retorna a resposta em texto ou lança uma exceção em caso de erro.
    """
    import time
    
    # Lista de modelos em ordem de preferência (melhor para pior)
    model_fallback = [
        {
            'name': 'models/gemini-1.5-flash-latest',
            'description': 'Modelo principal (mais completo)',
            'max_tokens': 1500,
            'temperature': 0.7
        },
        {
            'name': 'models/gemini-1.5-flash',
            'description': 'Modelo estável (fallback 1)',
            'max_tokens': 1200,
            'temperature': 0.6
        },
        {
            'name': 'models/gemini-1.5-flash-8b',
            'description': 'Modelo básico (fallback 2)',
            'max_tokens': 1000,
            'temperature': 0.5
        }
    ]
    
    if timeout is None:
        timeout = API_TIMEOUT_SECONDS
    
    # Tenta cada modelo na ordem de fallback
    for model_idx, model_config in enumerate(model_fallback):
        model = genai.GenerativeModel(model_config['name'])
        
        if model_idx > 0:
            print(f"🔄 Tentando fallback: {model_config['description']}")
        
        for attempt in range(max_retries):
            try:
                if model_idx == 0:
                    print(f"🔄 API call {attempt + 1}/{max_retries}")
                else:
                    print(f"🔄 Fallback call {attempt + 1}/{max_retries}")
                
                # Configura timeout baseado no tamanho do prompt
                prompt_size = len(prompt)
                if prompt_size > 5000:
                    current_timeout = timeout * 2
                    print(f"📏 Prompt longo ({prompt_size} chars) - Timeout: {current_timeout}s")
                else:
                    current_timeout = timeout
                    print(f"📏 Prompt: {prompt_size} chars - Timeout: {current_timeout}s")
                
                start_time = time.time()
                
                # Configuração otimizada baseada no modelo
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=model_config['max_tokens'],
                    temperature=model_config['temperature'],
                    top_p=0.9,
                    top_k=40
                )
                
                response = model.generate_content(
                    prompt, 
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                
                elapsed_time = time.time() - start_time
                print(f"✅ API respondeu em {elapsed_time:.1f}s")
                
                if response.text:
                    if model_idx > 0:
                        print(f"✅ Sucesso com fallback: {model_config['description']}")
                    return response.text
                else:
                    print(f"⚠️ Tentativa {attempt + 1}: Resposta vazia")
                
            except Exception as e:
                elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
                error_str = str(e).lower()
                
                # Detecta erro de quota - força fallback para próximo modelo
                if "quota" in error_str or "429" in error_str or "exceeded" in error_str:
                    print(f"� Quotia excedida no modelo {model_config['description']}")
                    if model_idx < len(model_fallback) - 1:
                        print(f"🔄 Tentando próximo modelo...")
                        break  # Sai do loop de tentativas e vai para próximo modelo
                    else:
                        print(f"❌ Todos os modelos esgotaram quota")
                        raise e
                
                # Detecta timeout
                elif "timeout" in error_str or "504" in error_str or elapsed_time > current_timeout:
                    print(f"⏰ Timeout detectado ({elapsed_time:.1f}s)")
                    if attempt < max_retries - 1:
                        print("🔄 Reduzindo prompt para próxima tentativa...")
                        # Reduz prompt se muito longo
                        if len(prompt) > 3000:
                            prompt = prompt[:2500] + "\n\nIMPORTANTE: Responda de forma concisa e direta."
                
                # Outros erros
                else:
                    print(f"❌ Erro: {str(e)[:100]}...")
                
                # Se é a última tentativa deste modelo, tenta próximo modelo
                if attempt == max_retries - 1:
                    if model_idx < len(model_fallback) - 1:
                        print(f"🔄 Modelo {model_config['description']} falhou, tentando próximo...")
                        break  # Vai para próximo modelo
                    else:
                        raise e
                
                # Espera progressiva apenas se não for erro de quota
                if "quota" not in error_str and "429" not in error_str:
                    wait_time = (attempt + 1) * 2
                    print(f"⏳ Aguardando {wait_time}s...")
                    time.sleep(wait_time)
    
    raise Exception("Falha em todas as tentativas de chamada da API")

def load_topics_cache() -> Dict:
    """Carrega o cache de tópicos já utilizados."""
    if TOPICS_CACHE.exists():
        try:
            with open(TOPICS_CACHE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"used_topics": [], "last_update": ""}
    return {"used_topics": [], "last_update": ""}

def save_topics_cache(cache_data: Dict):
    """Salva o cache de tópicos."""
    with open(TOPICS_CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def is_topic_duplicate(topic: str, used_topics: List[str]) -> bool:
    """Verifica se o tópico é muito similar aos já utilizados."""
    topic_hash = hashlib.md5(topic.lower().encode()).hexdigest()
    for used_topic in used_topics:
        used_hash = hashlib.md5(used_topic.lower().encode()).hexdigest()
        # Verifica similaridade básica
        if topic_hash == used_hash or topic.lower() in used_topic.lower() or used_topic.lower() in topic.lower():
            return True
    return False

def get_current_tech_context() -> str:
    """Gera contexto temporal específico para notícias atuais."""
    today = datetime.now()
    current_date = today.strftime("%d de %B de %Y")
    current_month = today.strftime("%B de %Y")
    week_day = today.strftime("%A")
    
    # Contextos específicos baseados na data
    contexts = [
        f"Esta semana ({current_date})",
        f"Neste mês de {current_month}",
        f"Nos últimos 7 dias",
        f"Esta {week_day}",
        "Recentemente anunciado",
        "Lançado hoje",
        "Trending agora"
    ]
    
    return random.choice(contexts)

def get_market_trends() -> Dict[str, List[str]]:
    """Retorna tendências atuais do mercado tech por categoria."""
    return {
        "ai_ml": [
            "GPT-4 Turbo", "Claude 3.5", "Gemini Ultra", "Llama 3", "Midjourney v6",
            "Sora (OpenAI)", "Runway ML", "Anthropic Constitutional AI", "Meta AI Studio",
            "Google AI Studio", "Microsoft Copilot Pro", "GitHub Copilot X"
        ],
        "mobile": [
            "iPhone 16 Pro", "Samsung Galaxy S25", "Google Pixel 9", "OnePlus 13",
            "iOS 18", "Android 15", "One UI 7", "MIUI 15", "ColorOS 15",
            "5G SA", "eSIM", "satellite connectivity", "foldable displays"
        ],
        "software": [
            "Windows 11 24H2", "macOS Sequoia", "Ubuntu 24.04", "Chrome 130",
            "Firefox 131", "VS Code updates", "Docker Desktop", "Kubernetes 1.31",
            "React 19", "Next.js 15", "Vue 3.5", "Angular 18"
        ],
        "security": [
            "zero-day exploits", "ransomware-as-a-service", "supply chain attacks",
            "quantum-resistant encryption", "passwordless authentication", "FIDO2",
            "WebAuthn", "biometric security", "AI-powered threats", "deepfake detection"
        ],
        "cloud": [
            "AWS re:Invent", "Google Cloud Next", "Microsoft Build", "serverless computing",
            "edge computing", "multi-cloud", "hybrid cloud", "container orchestration",
            "microservices", "API-first architecture", "cloud-native security"
        ],
        "hardware": [
            "Apple M4", "Intel Core Ultra", "AMD Ryzen 8000", "NVIDIA RTX 50 series",
            "Qualcomm Snapdragon X", "ARM Cortex-X5", "DDR5 memory", "PCIe 5.0",
            "USB4 v2", "Thunderbolt 5", "Wi-Fi 7", "Bluetooth 6.0"
        ]
    }

def generate_news_technical_analysis() -> str:
    """Gera análise técnica baseada em notícia real do Google News style."""
    print("📰 Gerando análise técnica de notícia real...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    try:
        # Obtém notícias atuais
        news_articles = get_current_news("technology")
        
        if news_articles:
            selected_news = random.choice(news_articles)
            news_title = selected_news["title"]
            news_source = selected_news["source"]
            
            # Limpa o título da notícia para usar nos templates
            clean_title = news_title.replace('"', '').replace("'", "")
            
            # Templates de análise técnica baseados na notícia
            analysis_templates = [
                f"Análise técnica: {clean_title} - impactos na infraestrutura",
                f"Deep dive: por trás de '{clean_title}' - arquitetura e implementação",
                f"Tech breakdown: {clean_title} - o que profissionais precisam saber",
                f"Security review: {clean_title} - vulnerabilidades e mitigações",
                f"Performance analysis: {clean_title} - benchmarks e otimizações", 
                f"DevOps perspective: {clean_title} - deployment e monitoring",
                f"Enterprise impact: {clean_title} - ROI e adoção corporativa",
                f"Infrastructure implications: {clean_title} - scaling e recursos",
                f"Implementation guide: lições técnicas de '{clean_title}'",
                f"Case study técnico: análise completa de {clean_title}"
            ]
            
            # Define tamanho mínimo flexível
            min_length = max(30, SEO_TITLE_MIN_LENGTH - 20)  # Mais flexível
            
            # Testa títulos até encontrar um válido
            for template in analysis_templates:
                original_template = template
                
                # Verifica tamanho mas não trunca automaticamente
                if len(template) > SEO_TITLE_MAX_LENGTH:
                    # Pula este template se muito longo
                    continue
                
                if len(template) >= min_length and not is_topic_duplicate(template, used_topics):
                    print(f"✅ Análise técnica baseada em notícia: {template}")
                    print(f"📰 Notícia fonte: {news_source} - {clean_title}")
                    
                    # Atualiza cache com informações da notícia
                    used_topics.append(template)
                    cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
                    cache_data["last_update"] = datetime.now().isoformat()
                    cache_data["news_source"] = {
                        "title": news_title,
                        "source": news_source,
                        "url": selected_news.get("url", ""),
                        "published_at": selected_news.get("published_at", ""),
                        "analysis_type": "technical"
                    }
                    save_topics_cache(cache_data)
                    
                    return template
            
            # Se nenhum template funcionou, tenta versões mais curtas
            # Se chegou aqui, usa título mais direto sem truncar
            short_templates = [
                f"Análise técnica: {clean_title}",
                f"Deep dive: {clean_title}",
                f"Tech breakdown: {clean_title}",
                f"Análise: {clean_title}"
            ]
            
            for template in short_templates:
                if len(template) >= min_length and not is_topic_duplicate(template, used_topics):
                    print(f"✅ Análise técnica (versão curta): {template}")
                    print(f"📰 Notícia fonte: {news_source} - {clean_title}")
                    
                    # Atualiza cache
                    used_topics.append(template)
                    cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
                    cache_data["last_update"] = datetime.now().isoformat()
                    cache_data["news_source"] = {
                        "title": news_title,
                        "source": news_source,
                        "url": selected_news.get("url", ""),
                        "published_at": selected_news.get("published_at", ""),
                        "analysis_type": "technical"
                    }
                    save_topics_cache(cache_data)
                    
                    return template
        
        # Se chegou aqui, não conseguiu gerar da notícia
        print("⚠️ Não conseguiu gerar análise da notícia, tentando abordagem alternativa...")
        
        # Tenta uma abordagem mais simples
        if news_articles:
            simple_news = random.choice(news_articles)
            simple_title = f"Análise técnica: {simple_news['title']}"
            if not is_topic_duplicate(simple_title, used_topics):
                print(f"✅ Análise simples: {simple_title}")
                return simple_title
        
        # Último fallback
        print("⚠️ Fallback para tópico técnico...")
        return generate_technical_seo_topic()
        
    except Exception as e:
        print(f"❌ Erro ao gerar análise técnica: {e}")
        print("⚠️ Fallback para tópico técnico SEO...")
        return generate_technical_seo_topic()

def generate_it_professional_topic() -> str:
    """Gera tópico técnico focado em profissionais de TI."""
    print("💻 Gerando tópico técnico para profissionais de TI...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    # Obtém notícias atuais
    try:
        news_articles = get_current_news("technology")
        
        if news_articles:
            selected_news = random.choice(news_articles)
            news_title = selected_news["title"]
            news_keywords = selected_news.get("keywords", [])
            
            # Templates técnicos específicos para IT
            it_templates = [
                f"Technical analysis: {news_title.lower()} - infrastructure implications",
                f"DevOps impact: how {news_title.lower()} affects deployment pipelines", 
                f"Security assessment: {news_title.lower()} vulnerabilities and mitigations",
                f"Performance review: {news_title.lower()} benchmarks and optimization",
                f"Architecture deep dive: {news_title.lower()} system design patterns",
                f"Enterprise perspective: {news_title.lower()} adoption challenges",
                f"Implementation guide: deploying solutions from {news_title.lower()}",
                f"Monitoring and observability: tracking {news_title.lower()} in production"
            ]
            
            # Se há palavras-chave técnicas, cria títulos mais específicos
            if news_keywords:
                tech_keyword = news_keywords[0]
                specific_templates = [
                    f"Deep dive: {tech_keyword} architecture revealed by {news_title.lower()}",
                    f"Performance analysis: {tech_keyword} scalability insights from {news_title.lower()}",
                    f"Security review: {tech_keyword} vulnerabilities exposed in {news_title.lower()}",
                    f"DevOps guide: {tech_keyword} deployment lessons from {news_title.lower()}",
                    f"Infrastructure impact: {tech_keyword} requirements after {news_title.lower()}"
                ]
                it_templates.extend(specific_templates)
            
            # Testa títulos técnicos
            for template in it_templates:
                if len(template) <= SEO_TITLE_MAX_LENGTH and not is_topic_duplicate(template, used_topics):
                    print(f"✅ Título técnico: {template}")
                    print(f"📰 Base: {selected_news['source']} - {news_title}")
                    
                    # Atualiza cache
                    used_topics.append(template)
                    cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
                    cache_data["last_update"] = datetime.now().isoformat()
                    cache_data["news_source"] = {
                        "title": news_title,
                        "source": selected_news["source"],
                        "url": selected_news.get("url", ""),
                        "published_at": selected_news.get("published_at", "")
                    }
                    save_topics_cache(cache_data)
                    
                    return template
        
        # Fallback: gera título técnico sem notícia específica
        return generate_technical_seo_topic()
        
    except Exception as e:
        print(f"❌ Erro ao gerar tópico técnico: {e}")
        return generate_technical_seo_topic()

def generate_technical_seo_topic() -> str:
    """Gera tópico técnico SEO para profissionais de TI."""
    print("🔧 Gerando tópico técnico SEO...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    # Seleciona elementos técnicos
    tech_template = random.choice(IT_PROFESSIONAL_TITLE_TEMPLATES)
    tech_keyword = random.choice(IT_TECHNICAL_KEYWORDS)
    tech_area = random.choice(TRENDING_PRODUCTS + EMERGING_TECH)
    sector = random.choice(APPLICATION_SECTORS)
    
    # Gera variações técnicas
    technical_variations = [
        tech_template.format(tecnologia=tech_keyword, alternativa=random.choice(IT_TECHNICAL_KEYWORDS), setor=sector),
        f"Performance benchmarks: {tech_keyword} vs {random.choice(IT_TECHNICAL_KEYWORDS)}",
        f"Production deployment: {tech_keyword} best practices and pitfalls",
        f"Scalability analysis: {tech_keyword} under high load conditions",
        f"Security hardening: {tech_keyword} configuration and monitoring",
        f"DevOps integration: {tech_keyword} in CI/CD pipelines",
        f"Infrastructure as Code: {tech_keyword} automation strategies",
        f"Monitoring and alerting: {tech_keyword} observability patterns"
    ]
    
    # Seleciona título válido
    for title in technical_variations:
        if SEO_TITLE_MIN_LENGTH <= len(title) <= SEO_TITLE_MAX_LENGTH and not is_topic_duplicate(title, used_topics):
            print(f"✅ Título técnico SEO: {title}")
            
            # Atualiza cache
            used_topics.append(title)
            cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
            cache_data["last_update"] = datetime.now().isoformat()
            save_topics_cache(cache_data)
            
            return title
    
    # Fallback final
    return generate_seo_optimized_topic()

def generate_news_based_topic() -> str:
    """Gera tópico baseado em notícias reais atuais."""
    print("📰 Gerando tópico baseado em notícias atuais...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    # Obtém notícias atuais
    try:
        news_articles = get_current_news("technology")
        
        if not news_articles:
            print("⚠️ Nenhuma notícia encontrada, usando geração SEO...")
            return generate_seo_optimized_topic()
        
        # Seleciona notícia aleatória
        selected_news = random.choice(news_articles)
        
        # Gera variações de título baseadas na notícia
        news_title = selected_news["title"]
        news_keywords = selected_news.get("keywords", [])
        
        # Templates para transformar notícia em conteúdo
        news_templates = [
            f"Análise: O que {news_title.lower()} significa para o mercado",
            f"Entendendo: Como {news_title.lower()} impacta empresas brasileiras", 
            f"Contexto: Por que {news_title.lower()} é importante",
            f"Guia: O que aprender com {news_title.lower()}",
            f"Impacto: Como {news_title.lower()} muda o cenário tech",
            f"Análise completa: {news_title} e suas implicações"
        ]
        
        # Gera títulos mais específicos se há palavras-chave
        if news_keywords:
            keyword = news_keywords[0]
            specific_templates = [
                f"Como {keyword} está transformando o mercado após {news_title.lower()}",
                f"Guia completo: {keyword} no contexto de {news_title.lower()}",
                f"Análise: Impacto de {keyword} revelado por {news_title.lower()}",
                f"O que {news_title.lower()} ensina sobre {keyword}",
                f"Tendências em {keyword}: lições de {news_title.lower()}"
            ]
            news_templates.extend(specific_templates)
        
        # Testa títulos até encontrar um válido
        for template in news_templates:
            # Pula templates muito longos
            if len(template) > SEO_TITLE_MAX_LENGTH:
                continue
            
            if len(template) >= SEO_TITLE_MIN_LENGTH and not is_topic_duplicate(template, used_topics):
                print(f"✅ Título baseado em notícia: {template}")
                print(f"📰 Notícia fonte: {selected_news['source']} - {news_title}")
                
                # Atualiza cache
                used_topics.append(template)
                cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
                cache_data["last_update"] = datetime.now().isoformat()
                cache_data["news_source"] = {
                    "title": news_title,
                    "source": selected_news["source"],
                    "url": selected_news.get("url", ""),
                    "published_at": selected_news.get("published_at", "")
                }
                save_topics_cache(cache_data)
                
                return template
        
        print("⚠️ Nenhum título válido gerado da notícia, usando SEO...")
        return generate_seo_optimized_topic()
        
    except Exception as e:
        print(f"❌ Erro ao obter notícias: {e}")
        print("⚠️ Fallback para geração SEO...")
        return generate_seo_optimized_topic()

def generate_seo_optimized_topic() -> str:
    """Gera um tópico otimizado para SEO e Google Ads."""
    print("🎯 Gerando tópico SEO-otimizado...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    today = datetime.now()
    current_year = today.year
    
    # Seleciona categoria SEO e palavras-chave
    seo_category = random.choice(list(SEO_KEYWORDS.keys()))
    keywords = SEO_KEYWORDS[seo_category]
    primary_keyword = random.choice(keywords)
    
    # Seleciona template SEO
    template = random.choice(SEO_TITLE_TEMPLATES)
    
    # Preenche o template com dados relevantes
    tech_area = random.choice(TRENDING_PRODUCTS + EMERGING_TECH)
    sector = random.choice(APPLICATION_SECTORS)
    audience = random.choice(["desenvolvedores", "empresas", "iniciantes", "profissionais"])
    number = random.choice(["5", "7", "10", "15"])
    
    # Gera título baseado no template
    title_variations = []
    
    try:
        title = template.format(
            tecnologia=primary_keyword,
            setor=sector,
            público=audience,
            número=number,
            ano=current_year,
            alternativa=random.choice(keywords),
            contexto=sector
        )
        title_variations.append(title)
    except KeyError:
        pass  # Template não compatível, pula
    
    # Adiciona variações manuais SEO-friendly
    manual_variations = [
        f"Como usar {primary_keyword} para melhorar {sector}",
        f"Guia completo de {primary_keyword} para {audience}",
        f"{number} dicas de {primary_keyword} que funcionam em {current_year}",
        f"Tutorial: {primary_keyword} na prática para {sector}",
        f"Análise: impacto de {primary_keyword} no Brasil"
    ]
    
    title_variations.extend(manual_variations)
    
    # Seleciona título que não seja duplicata
    for title in title_variations:
        if not is_topic_duplicate(title, used_topics):
            # Valida tamanho SEO
            if SEO_TITLE_MIN_LENGTH <= len(title) <= SEO_TITLE_MAX_LENGTH:
                print(f"✅ Título SEO gerado: {title}")
                print(f"📊 Palavra-chave principal: {primary_keyword}")
                print(f"🎯 Categoria: {seo_category}")
                
                # Atualiza cache
                used_topics.append(title)
                cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
                cache_data["last_update"] = datetime.now().isoformat()
                save_topics_cache(cache_data)
                
                return title
    
    # Fallback para geração com IA se necessário
    print("⚠️ Nenhum título SEO válido encontrado, usando geração com IA...")
    return generate_new_topic()

def generate_new_topic() -> str:
    """Usa a IA para gerar um novo tópico educativo e analítico sobre tecnologia."""
    print("🧠 Gerando tópico educativo sobre tecnologia...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    today = datetime.now()
    current_date_str = today.strftime("%d de %B de %Y")
    current_year = today.year
    
    # Obtém tendências atuais do mercado
    market_trends = get_market_trends()
    
    # Seleciona uma categoria aleatória e pega algumas tendências
    category = random.choice(list(market_trends.keys()))
    category_trends = market_trends[category]
    
    max_attempts = MAX_TOPIC_ATTEMPTS
    for attempt in range(max_attempts):
        # Seleciona 2-3 tendências da categoria escolhida
        selected_trends = random.sample(category_trends, min(3, len(category_trends)))
        
        # Decide se será conteúdo puramente educativo ou híbrido (70% educativo, 30% híbrido)
        is_hybrid = random.random() < 0.3
        
        if is_hybrid:
            # Conteúdo híbrido: educativo + contexto de notícias
            content_type = random.choice(HYBRID_CONTENT_TYPES)
            hybrid_keyword = random.choice(HYBRID_KEYWORDS)
            news_context = random.choice(NEWS_CONTEXTS)
            tech_theme = random.choice(list(TECH_NEWS_THEMES.keys()))
            theme_topics = TECH_NEWS_THEMES[tech_theme]
            news_topic = random.choice(theme_topics)
            print(f"🔄 Modo híbrido: {content_type} sobre {news_topic}")
        else:
            # Conteúdo puramente educativo
            content_type = random.choice(EDUCATIONAL_CONTENT_TYPES)
            educational_keyword = random.choice(EDUCATIONAL_KEYWORDS)
            print(f"📚 Modo educativo: {content_type}")
        
        tech_area = random.choice(selected_trends)
        application_sector = random.choice(APPLICATION_SECTORS)
        technical_concept = random.choice(TECHNICAL_CONCEPTS)
        
        if is_hybrid:
            # Prompt para conteúdo híbrido (educativo + contexto de notícias)
            prompt = (
                f"Você é um analista técnico criando conteúdo educativo contextualizado para {current_year}.\n\n"
                f"Gere um título que EDUQUE sobre tecnologia usando contexto de tendências atuais:\n\n"
                f"ELEMENTOS PARA O TÍTULO:\n"
                f"• Tipo de análise: {content_type}\n"
                f"• Contexto atual: {news_context} {news_topic}\n"
                f"• Área técnica: {tech_area}\n"
                f"• Setor de aplicação: {application_sector}\n"
                f"• Conceito técnico: {technical_concept}\n\n"
                f"FÓRMULAS HÍBRIDAS:\n"
                f"• '{content_type}: {news_topic} e o impacto em [setor]'\n"
                f"• 'O que {news_topic} ensina sobre [conceito técnico]'\n"
                f"• '{hybrid_keyword}: Como {news_topic} afeta [setor]'\n"
                f"• 'Lições de {news_topic} para [aplicação prática]'\n\n"
                f"EXEMPLOS HÍBRIDOS:\n"
                f"• 'Análise: O que os avanços em IA generativa significam para startups'\n"
                f"• 'Contexto: Por que investimentos em IA estão transformando a saúde'\n"
                f"• 'Entendendo o impacto de novos modelos de linguagem no desenvolvimento'\n"
                f"• 'Lições dos recentes desenvolvimentos em cibersegurança para PMEs'\n\n"
                f"DIRETRIZES HÍBRIDAS:\n"
                f"• Use contexto de tendências SEM inventar fatos específicos\n"
                f"• Foque no APRENDIZADO que o contexto oferece\n"
                f"• Mantenha tom educativo, não noticioso\n"
                f"• Máximo 100 caracteres\n"
                f"• Evite datas específicas ou eventos inventados\n\n"
                f"EVITE (já cobertos): {', '.join(used_topics[-5:]) if used_topics else 'nenhum'}\n\n"
                f"Gere um título que ENSINE usando contexto atual:\n"
                f"APENAS O TÍTULO:"
            )
        else:
            # Prompt para conteúdo puramente educativo
            prompt = (
                f"Você é um especialista técnico criando conteúdo educativo para {current_year}.\n\n"
                f"Gere um título EDUCATIVO sobre tecnologia usando estes elementos:\n\n"
                f"ELEMENTOS DISPONÍVEIS:\n"
                f"• Tipo de conteúdo: {content_type}\n"
                f"• Área técnica: {tech_area}\n"
                f"• Palavra-chave educativa: {educational_keyword}\n"
                f"• Setor de aplicação: {application_sector}\n"
                f"• Conceito técnico: {technical_concept}\n\n"
                f"FÓRMULAS EDUCATIVAS:\n"
                f"• '{educational_keyword} [tecnologia]: [conceito] para [setor]'\n"
                f"• '{content_type}: [tecnologia] em [setor] - [conceito]'\n"
                f"• 'Como [tecnologia] melhora [conceito] no [setor]'\n"
                f"• '{content_type} de [tecnologia]: [conceito] na prática'\n\n"
                f"EXEMPLOS DE QUALIDADE:\n"
                f"• 'Guia completo: Implementando IA generativa em startups'\n"
                f"• 'Análise: Como edge computing melhora performance em saúde'\n"
                f"• 'Entendendo blockchain: Segurança de dados no setor financeiro'\n"
                f"• 'Comparativo: Arquiteturas de software para escalabilidade'\n\n"
                f"DIRETRIZES:\n"
                f"• Foque em VALOR EDUCATIVO real\n"
                f"• Use linguagem técnica mas acessível\n"
                f"• Seja específico sobre aplicação prática\n"
                f"• Máximo 100 caracteres\n"
                f"• Evite sensacionalismo\n\n"
                f"EVITE (já cobertos): {', '.join(used_topics[-5:]) if used_topics else 'nenhum'}\n\n"
                f"Gere UM título educativo que ensine algo valioso:\n"
                f"APENAS O TÍTULO:"
            )
        
        try:
            topic = call_gemini_api(prompt).strip()
            if topic and not is_topic_duplicate(topic, used_topics):
                print(f"✅ Tópico gerado (tentativa {attempt + 1}): {topic}")
                
                # Atualiza o cache
                used_topics.append(topic)
                cache_data["used_topics"] = used_topics[-MAX_CACHED_TOPICS:]
                cache_data["last_update"] = datetime.now().isoformat()
                save_topics_cache(cache_data)
                
                return topic
            else:
                print(f"⚠️ Tópico duplicado ou inválido (tentativa {attempt + 1})")
        except Exception as e:
            print(f"❌ Erro na tentativa {attempt + 1}: {e}")
    
    print("❌ Não foi possível gerar um tópico único após várias tentativas.")
    return ""

def get_educational_context(title: str) -> Dict[str, str]:
    """Gera contexto educativo baseado no título do artigo."""
    today = datetime.now()
    current_year = today.year
    
    # Identifica o tipo de conteúdo baseado no título
    if any(word in title.lower() for word in ["como", "guia", "entendendo"]):
        content_focus = "explicativo"
    elif any(word in title.lower() for word in ["análise", "comparativo", "vs"]):
        content_focus = "analítico"
    elif any(word in title.lower() for word in ["futuro", "tendências", "evolução"]):
        content_focus = "prospectivo"
    else:
        content_focus = "informativo"
    
    return {
        "current_year": str(current_year),
        "content_focus": content_focus,
        "educational_approach": random.choice([
            "didático e acessível", "técnico mas compreensível", 
            "prático e aplicado", "analítico e detalhado"
        ])
    }

def generate_references(title: str) -> List[str]:
    """Gera fontes de referência realistas para o artigo."""
    print("📚 Selecionando fontes credíveis...")
    
    # Seleciona fontes baseadas no tipo de notícia
    references = []
    
    # Sempre inclui uma fonte brasileira
    references.append(random.choice(CREDIBLE_SOURCES["brazilian"]))
    
    # Adiciona fontes internacionais baseadas no título
    if any(company in title.lower() for company in ["apple", "google", "microsoft", "meta", "openai"]):
        references.append(random.choice(CREDIBLE_SOURCES["official"]))
    
    # Adiciona fontes de tech news
    references.extend(random.sample(CREDIBLE_SOURCES["tech_news"], 2))
    
    # Se menciona investimento/negócios, adiciona fonte business
    if any(word in title.lower() for word in ["bilhões", "aquisição", "investimento", "ipo"]):
        references.append(random.choice(CREDIBLE_SOURCES["business"]))
    
    # Remove duplicatas e limita a 5 fontes
    references = list(dict.fromkeys(references))[:5]
    
    print(f"✅ {len(references)} fontes selecionadas: {', '.join(references)}")
    return references

def write_article_chunked(title: str) -> str:
    """Gera artigo em partes menores para evitar timeout."""
    print("🔧 Gerando artigo em chunks para evitar timeout...")
    
    # Gera estrutura primeiro
    structure_prompt = (
        f"Crie apenas a ESTRUTURA de um artigo técnico sobre: '{title}'\n\n"
        f"Retorne apenas os títulos das seções em markdown (##), sem conteúdo.\n"
        f"Exemplo:\n"
        f"## Resumo da Notícia\n"
        f"## Análise Técnica\n"
        f"## Impactos na Infraestrutura\n"
        f"## Conclusão\n\n"
        f"Máximo 6 seções."
    )
    
    try:
        structure = call_gemini_api(structure_prompt, timeout=15)
        sections = [s.strip() for s in structure.split('\n') if s.strip().startswith('##')]
        
        if not sections:
            print("⚠️ Fallback para geração normal...")
            return write_article(title)
        
        print(f"📋 Estrutura criada: {len(sections)} seções")
        
        # Gera cada seção separadamente
        full_article = ""
        
        for i, section in enumerate(sections):
            print(f"✍️ Gerando seção {i+1}/{len(sections)}: {section}")
            
            section_prompt = (
                f"Escreva APENAS o conteúdo para a seção '{section}' de um artigo sobre: '{title}'\n\n"
                f"Contexto: Análise técnica para profissionais de TI.\n"
                f"Tamanho: 150-250 palavras.\n"
                f"Tom: Técnico e informativo.\n\n"
                f"Retorne apenas o conteúdo da seção, sem o título."
            )
            
            try:
                section_content = call_gemini_api(section_prompt, timeout=20)
                full_article += f"{section}\n\n{section_content}\n\n"
                print(f"✅ Seção {i+1} concluída")
            except Exception as e:
                print(f"⚠️ Erro na seção {i+1}: {e}")
                # Continua com as outras seções
                full_article += f"{section}\n\n[Conteúdo da seção em desenvolvimento]\n\n"
        
        return full_article
        
    except Exception as e:
        print(f"❌ Erro na geração chunked: {e}")
        print("⚠️ Fallback para geração normal...")
        return write_article(title)

def write_article(title: str) -> str:
    """Gera o conteúdo do artigo baseado em notícias reais ou educativo."""
    
    # Detecta se é conteúdo baseado em notícias
    is_news_based = any(word in title.lower() for word in [
        "análise", "contexto:", "o que", "lições", "por trás", 
        "significam", "impacto de", "entendendo", "como", "após",
        "deep dive:", "tech breakdown:", "security review:"
    ])
    
    # Obtém contexto de notícia se disponível
    news_context = None
    if is_news_based:
        # Primeiro tenta obter do cache (notícia usada para gerar o título)
        cache_data = load_topics_cache()
        cached_news = cache_data.get("news_source")
        
        if cached_news and cached_news.get("title"):
            news_context = cached_news
            print(f"📰 Usando notícia do cache: {cached_news['title']}")

        else:
            # Fallback: busca notícia relevante
            title_keywords = []
            for category_keywords in SEO_KEYWORDS.values():
                for keyword in category_keywords:
                    if keyword.lower() in title.lower():
                        title_keywords.append(keyword)
            
            news_context = get_news_context(title_keywords)
    


    print(f"� DebuCg final - is_news_analysis: {is_news_analysis if 'is_news_analysis' in locals() else 'não definido ainda'}")
    
    if news_context:
        print(f'✍️ Escrevendo artigo baseado em notícia real: "{title}"...')
        print(f'📰 Contexto: {news_context["source"]} - {news_context["title"]}')
    elif is_news_based:
        print(f'✍️ Escrevendo artigo híbrido (educativo + contexto): "{title}"...')
    else:
        print(f'✍️ Escrevendo artigo educativo sobre: "{title}"...')
    
    # Gera as referências credíveis e contexto educativo
    references = generate_references(title)
    references_text = ", ".join(references)
    edu_context = get_educational_context(title)
    
    today = datetime.now()
    current_date = today.strftime("%d de %B de %Y")
    
    # Detecta se é análise técnica de notícia
    is_news_analysis = any(word in title.lower() for word in [
        "análise técnica:", "deep dive:", "tech breakdown:", "security review:",
        "performance analysis:", "devops perspective:", "enterprise impact:",
        "infrastructure implications:", "implementation guide:", "case study técnico:"
    ])
    
    # Detecta se é conteúdo técnico geral
    is_technical_content = any(word in title.lower() for word in [
        "technical", "deep dive", "performance", "security", "devops", 
        "architecture", "infrastructure", "deployment", "monitoring", "benchmarks"
    ])
    
    if news_context and is_news_analysis:
        # Prompt para conteúdo técnico baseado em notícia
        news_title = news_context["title"]
        news_source = news_context["source"]
        news_description = news_context.get("description", "")
        
        prompt = (
            f"ANÁLISE TÉCNICA DE NOTÍCIA REAL - {current_date}\n\n"
            f"Você é um tech lead sênior fazendo uma análise técnica profunda da notícia: '{news_title}'\n"
            f"Seu artigo tem o título: '{title}'\n\n"
            f"NOTÍCIA ORIGINAL:\n"
            f"- Título: {news_title}\n"
            f"- Fonte: {news_source}\n"
            f"- Contexto: {news_description}\n\n"
            f"FONTES TÉCNICAS ADICIONAIS: {references_text}\n\n"
            f"OBJETIVO: Fazer um 'refactoring' técnico da notícia, explicando:\n"
            f"- O que realmente aconteceu tecnicamente\n"
            f"- Por que isso importa para profissionais de TI\n"
            f"- Quais são as implicações práticas\n"
            f"- Como isso afeta infraestrutura e operações\n\n"
            f"ESTRUTURA JORNALÍSTICA PROFISSIONAL:\n"
            f"1. ## Lead Jornalístico\n"
            f"   - Parágrafo de abertura com os 5 W's (O que, Quem, Quando, Onde, Por que)\n"
            f"   - Impacto imediato e relevância para o leitor\n"
            f"   - Dados quantitativos quando disponíveis\n\n"
            f"2. ## Contexto e Background\n"
            f"   - Histórico da tecnologia/empresa/situação\n"
            f"   - Desenvolvimentos anteriores relevantes\n"
            f"   - Posicionamento no mercado atual\n\n"
            f"3. ## Análise Técnica Aprofundada\n"
            f"   - Especificações técnicas detalhadas\n"
            f"   - Comparação com concorrentes/alternativas\n"
            f"   - Arquitetura e componentes envolvidos\n\n"
            f"4. ## Impactos e Implicações\n"
            f"   - Efeitos na indústria e mercado\n"
            f"   - Mudanças para desenvolvedores e empresas\n"
            f"   - Considerações de adoção e migração\n\n"
            f"5. ## Perspectiva de Especialistas\n"
            f"   - Análise de tendências do setor\n"
            f"   - Desafios e oportunidades identificados\n"
            f"   - Previsões baseadas em dados\n\n"
            f"6. ## Implementação Prática\n"
            f"   - Guia passo-a-passo para adoção\n"
            f"   - Custos, recursos e timeline realistas\n"
            f"   - Métricas de sucesso e KPIs\n\n"
            f"7. ## Conclusão Editorial\n"
            f"   - Síntese dos pontos principais\n"
            f"   - Recomendações baseadas na análise\n"
            f"   - Próximos desenvolvimentos a acompanhar\n\n"
            f"PADRÕES DE QUALIDADE JORNALÍSTICA:\n"
            f"- {SEO_ARTICLE_MIN_WORDS}-{SEO_ARTICLE_MAX_WORDS} palavras com densidade informacional alta\n"
            f"- LEAD jornalístico: responda O QUE, QUEM, QUANDO, ONDE, POR QUE nos primeiros parágrafos\n"
            f"- Estrutura de pirâmide invertida: informações mais importantes primeiro\n"
            f"- Fontes credíveis e citações específicas (não genéricas)\n"
            f"- Dados concretos, estatísticas e números verificáveis\n"
            f"- Contexto histórico e comparações relevantes\n"
            f"- Linguagem precisa, objetiva e sem redundâncias\n"
            f"- Transições lógicas entre parágrafos\n"
            f"- Evite clichês e frases feitas\n"
            f"- Cada parágrafo deve ter uma ideia central clara\n"
            f"- Conclusões baseadas em evidências apresentadas\n\n"
            f"ELEMENTOS OBRIGATÓRIOS:\n"
            f"✅ Lead jornalístico com os 5 W's nos primeiros parágrafos\n"
            f"✅ Dados específicos: números, percentuais, versões, datas\n"
            f"✅ Citações de fontes credíveis e especialistas\n"
            f"✅ Análise técnica que vai além da notícia superficial\n"
            f"✅ Comparações com concorrentes e alternativas\n"
            f"✅ Contexto histórico e posicionamento no mercado\n"
            f"✅ Impactos práticos para desenvolvedores e empresas\n"
            f"✅ Conclusões baseadas em evidências apresentadas\n\n"
            f"QUALIDADE EDITORIAL OBRIGATÓRIA:\n"
            f"🎯 Cada parágrafo = uma ideia central (3-5 frases)\n"
            f"🎯 Transições lógicas entre parágrafos e seções\n"
            f"🎯 Linguagem precisa, sem redundâncias ou clichês\n"
            f"🎯 Verbos no tempo correto (presente/passado)\n"
            f"🎯 Estrutura de pirâmide invertida (mais importante primeiro)\n\n"
            f"INSTRUÇÕES CRÍTICAS PARA QUALIDADE JORNALÍSTICA:\n"
            f"• PRIMEIRO PARÁGRAFO deve responder: O QUE aconteceu, QUEM está envolvido, QUANDO\n"
            f"• Use conectores lógicos: 'Além disso', 'Por outro lado', 'Consequentemente'\n"
            f"• Parágrafos de 3-5 frases cada, máximo 100 palavras\n"
            f"• Dados específicos: números, percentuais, versões, datas\n"
            f"• Linguagem precisa e objetiva, sem exageros ou clichês\n"
            f"• Estrutura de pirâmide invertida: mais importante primeiro\n\n"
            f"Escreva uma ANÁLISE JORNALÍSTICA TÉCNICA que profissionais de TI respeitarão!"
        )
    elif news_context:
        # Prompt para conteúdo baseado em notícia real (menos técnico)
        news_title = news_context["title"]
        news_source = news_context["source"]
        news_description = news_context.get("description", "")
        
        prompt = (
            f"ANÁLISE INFORMATIVA PARA PROFISSIONAIS DE TI - {current_date}\n\n"
            f"Você é um tech lead experiente escrevendo para profissionais de TI sobre: '{title}'\n\n"
            f"NOTÍCIA DE REFERÊNCIA:\n"
            f"- Título: {news_title}\n"
            f"- Fonte: {news_source}\n"
            f"- Contexto: {news_description}\n\n"
            f"FONTES ADICIONAIS: {references_text}\n\n"
            f"ESTRUTURA INFORMATIVA:\n"
            f"1. RESUMO EXECUTIVO: Key takeaways para profissionais ocupados\n"
            f"2. ## Contexto Técnico (o que mudou e por que importa)\n"
            f"3. ## Análise de Impacto (como afeta stacks e workflows atuais)\n"
            f"4. ## Implicações para Equipes (skills, processos, ferramentas)\n"
            f"5. ## Considerações de Adoção (quando e como implementar)\n"
            f"6. ## Competitive Landscape (alternativas e comparações)\n"
            f"7. ## Roadmap e Próximos Passos (planejamento estratégico)\n\n"
            f"DIRETRIZES PROFISSIONAIS:\n"
            f"- {SEO_ARTICLE_MIN_WORDS}-{SEO_ARTICLE_MAX_WORDS} palavras\n"
            f"- Tom profissional, direto ao ponto\n"
            f"- Foque em implicações práticas para o dia a dia\n"
            f"- Inclua considerações de budget, timeline, recursos\n"
            f"- Aborde riscos e benefícios de forma equilibrada\n"
            f"- Contextualize para realidade de empresas brasileiras\n\n"
            f"IMPORTANTE:\n"
            f"✅ Informação acionável para tomada de decisão\n"
            f"✅ Análise crítica, não apenas hype\n"
            f"✅ Considerações práticas de implementação\n"
            f"✅ Impacto em workflows e processos existentes\n"
            f"❌ NÃO seja apenas descritivo\n"
            f"❌ NÃO ignore limitações e desafios\n\n"
            f"Escreva para PROFISSIONAIS que precisam tomar DECISÕES TÉCNICAS!"
        )
    elif is_news_based:
        # Prompt para conteúdo híbrido (educativo + contexto de tendências)
        prompt = (
            f"ARTIGO EDUCATIVO CONTEXTUALIZADO - {current_date}\n\n"
            f"Você é um analista técnico escrevendo um artigo EDUCATIVO que usa contexto de tendências: '{title}'\n\n"
            f"CONTEXTO EDUCATIVO:\n"
            f"- Ano de referência: {edu_context['current_year']}\n"
            f"- Foco do conteúdo: {edu_context['content_focus']}\n"
            f"- Abordagem: {edu_context['educational_approach']}\n\n"
            f"FONTES DE REFERÊNCIA: {references_text}\n\n"
            f"ESTRUTURA HÍBRIDA:\n"
            f"1. INTRODUÇÃO: Contextualize a tendência e sua relevância educativa\n"
            f"2. ## Contexto Atual (tendências gerais, sem fatos específicos)\n"
            f"3. ## Conceitos Técnicos Envolvidos (explicação educativa)\n"
            f"4. ## Análise do Impacto (o que isso significa tecnicamente)\n"
            f"5. ## Lições e Aprendizados (insights educativos)\n"
            f"6. ## Aplicações Práticas (como aplicar o conhecimento)\n"
            f"7. ## Conclusão (síntese educativa)\n\n"
            f"DIRETRIZES HÍBRIDAS:\n"
            f"- {SEO_ARTICLE_MIN_WORDS}-{SEO_ARTICLE_MAX_WORDS} palavras (otimizado para SEO)\n"
            f"- Use contexto de tendências para EDUCAR, não para noticiar\n"
            f"- Foque no APRENDIZADO que as tendências oferecem\n"
            f"- Explique conceitos técnicos por trás das tendências\n"
            f"- Mantenha tom educativo, nunca jornalístico urgente\n"
            f"- Contextualize para profissionais brasileiros\n\n"
            f"PROIBIÇÕES ABSOLUTAS:\n"
            f"❌ NÃO invente eventos específicos ou datas\n"
            f"❌ NÃO crie notícias falsas ou fatos específicos\n"
            f"❌ NÃO use linguagem de urgência jornalística\n"
            f"❌ NÃO afirme acontecimentos específicos não verificáveis\n"
            f"❌ NÃO crie citações ou declarações falsas\n\n"
            f"FOQUE EM EDUCAÇÃO CONTEXTUALIZADA:\n"
            f"✅ Use tendências gerais como contexto educativo\n"
            f"✅ Explique conceitos técnicos por trás das tendências\n"
            f"✅ Analise implicações e aprendizados\n"
            f"✅ Forneça insights práticos e aplicáveis\n"
            f"✅ Eduque sobre como se preparar para mudanças\n\n"
            f"Escreva um artigo que EDUQUE usando contexto de tendências atuais!"
        )
    else:
        # Prompt para conteúdo puramente educativo
        prompt = (
            f"ARTIGO TÉCNICO EDUCATIVO - {current_date}\n\n"
            f"Você é um especialista técnico escrevendo um artigo EDUCATIVO sobre: '{title}'\n\n"
            f"CONTEXTO EDUCATIVO:\n"
            f"- Ano de referência: {edu_context['current_year']}\n"
            f"- Foco do conteúdo: {edu_context['content_focus']}\n"
            f"- Abordagem: {edu_context['educational_approach']}\n\n"
            f"FONTES DE REFERÊNCIA: {references_text}\n\n"
            f"ESTRUTURA EDUCATIVA:\n"
            f"1. INTRODUÇÃO: Apresente o tema e sua relevância\n"
            f"2. ## Conceitos e Definições (fundamentos técnicos)\n"
            f"3. ## Como Funciona (aspectos técnicos explicados)\n"
            f"4. ## Aplicações e Casos de Uso (exemplos reais)\n"
            f"5. ## Vantagens e Desvantagens (análise equilibrada)\n"
            f"6. ## Considerações para Implementação (aspectos práticos)\n"
            f"7. ## Conclusão (síntese e recomendações)\n\n"
            f"DIRETRIZES RIGOROSAS:\n"
            f"- {SEO_ARTICLE_MIN_WORDS}-{SEO_ARTICLE_MAX_WORDS} palavras (otimizado para SEO)\n"
            f"- Tom EDUCATIVO e TÉCNICO, nunca sensacionalista\n"
            f"- Base-se em conhecimento geral estabelecido\n"
            f"- Explique conceitos complexos de forma clara\n"
            f"- Use exemplos práticos e aplicáveis\n"
            f"- Seja honesto sobre limitações e desafios\n"
            f"- Contextualize para desenvolvedores/profissionais brasileiros\n\n"
            f"PROIBIÇÕES ABSOLUTAS:\n"
            f"❌ NÃO invente notícias, lançamentos ou eventos específicos\n"
            f"❌ NÃO use linguagem de urgência ('breaking', 'exclusivo')\n"
            f"❌ NÃO crie citações ou declarações falsas\n"
            f"❌ NÃO afirme fatos específicos não verificáveis\n"
            f"❌ NÃO use datas específicas recentes ('ontem', 'esta semana')\n"
            f"❌ NÃO invente números ou estatísticas\n\n"
            f"FOQUE EM VALOR EDUCATIVO:\n"
            f"✅ Explique conceitos e funcionamento\n"
            f"✅ Analise prós e contras de forma equilibrada\n"
            f"✅ Forneça orientações práticas\n"
            f"✅ Compare diferentes abordagens/tecnologias\n"
            f"✅ Eduque sobre melhores práticas\n"
            f"✅ Contextualize tendências gerais do setor\n\n"
            f"Escreva um artigo que seja uma REFERÊNCIA TÉCNICA confiável e educativa!"
        )
    
    try:
        safety_settings = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
        
        article = call_gemini_api(prompt, safety_settings=safety_settings)
        
        if article:
            # Aplica limpeza completa e formatação
            article = clean_content_completely(article)
            article = create_simple_structure(article, title)
            article = improve_journalistic_language(article)
            article = format_content(article)
            
            # Adiciona seção de referências formatada
            article += "\n\n---\n\n## 📚 Fontes e Referências\n\n"
            for i, ref in enumerate(references, 1):
                article += f"{i}. **{ref}**\n"
            
            # CTA engajante já foi aplicado pela função add_engaging_cta
            
            print("✅ Artigo gerado e formatado com sucesso.")
            return article
        else:
            print("❌ A IA não retornou um artigo válido.")
            return ""
    except Exception as e:
        print(f"❌ Erro ao gerar o artigo: {e}")
        return ""

def generate_seo_description(title: str, content: str) -> str:
    """Gera meta description otimizada para SEO."""
    print("📝 Gerando meta description SEO...")
    
    # Extrai primeira frase do conteúdo
    first_paragraph = content.split('\n')[0:3]
    clean_text = ' '.join(first_paragraph).replace('#', '').strip()
    
    # Identifica palavra-chave principal do título
    title_lower = title.lower()
    primary_keyword = ""
    
    for category, keywords in SEO_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                primary_keyword = keyword
                break
        if primary_keyword:
            break
    
    # Templates de meta description SEO
    templates = [
        f"Descubra como {primary_keyword} pode transformar seu negócio. Guia completo com dicas práticas e exemplos reais.",
        f"Tudo sobre {primary_keyword}: conceitos, implementação e melhores práticas. Leia nosso guia completo.",
        f"Aprenda {primary_keyword} do zero ao avançado. Tutorial completo com exemplos práticos e dicas de especialistas.",
        f"Guia definitivo de {primary_keyword}: como implementar, vantagens e casos de sucesso no Brasil.",
        f"{primary_keyword} explicado: conceitos, aplicações e como começar. Guia prático para iniciantes e profissionais."
    ]
    
    if primary_keyword:
        description = random.choice(templates)
    else:
        # Fallback baseado no conteúdo
        description = clean_text[:SEO_DESCRIPTION_MAX_LENGTH-3] + "..."
    
    # Ajusta tamanho para SEO
    if len(description) > SEO_DESCRIPTION_MAX_LENGTH:
        description = description[:SEO_DESCRIPTION_MAX_LENGTH-3] + "..."
    elif len(description) < SEO_DESCRIPTION_MIN_LENGTH:
        description += f" Leia mais sobre {primary_keyword} e suas aplicações práticas."
    
    print(f"✅ Meta description gerada ({len(description)} chars)")
    return description

def extract_seo_keywords(title: str, content: str) -> List[str]:
    """Extrai palavras-chave SEO do título e conteúdo."""
    keywords = []
    title_lower = title.lower()
    content_lower = content.lower()
    
    # Identifica palavras-chave principais
    for category, keyword_list in SEO_KEYWORDS.items():
        for keyword in keyword_list:
            if keyword in title_lower or keyword in content_lower:
                keywords.append(keyword)
    
    # Remove duplicatas e limita
    keywords = list(dict.fromkeys(keywords))[:SEO_KEYWORDS_PER_POST]
    
    return keywords

def generate_tags(title: str, content: str) -> List[str]:
    """Gera tags relevantes para o post baseado no título e conteúdo."""
    print("🏷️ Gerando tags para o post...")
    
    prompt = (
        f"Baseado no título '{title}' e no conteúdo do artigo, gere 3-6 tags relevantes em português. "
        "Use tags comuns de tecnologia como: inteligencia-artificial, startups, ciberseguranca, "
        "inovacao, big-tech, software, hardware, mobile, web, dados, etc. "
        "Retorne apenas as tags separadas por vírgula, em minúsculas e com hífens no lugar de espaços."
    )
    
    try:
        tags_text = call_gemini_api(prompt).strip()
        tags = [tag.strip().lower().replace(' ', '-') for tag in tags_text.split(',')]
        return [tag for tag in tags if tag and len(tag) > 2][:MAX_TAGS]
    except Exception as e:
        print(f"⚠️ Erro ao gerar tags: {e}")
        return ["tecnologia", "inovacao"]

def create_hugo_post(title: str, content: str) -> Optional[Path]:
    """Cria e salva o arquivo .md para o Hugo com otimizações SEO completas."""
    print("📝 Formatando e salvando o post SEO-otimizado...")
    try:
        now = datetime.now()
        tz_offset = timezone(timedelta(hours=TIMEZONE_OFFSET))
        iso_timestamp = now.astimezone(tz_offset).isoformat()
        
        # Gera elementos SEO
        tags = generate_tags(title, content)
        seo_description = generate_seo_description(title, content)
        seo_keywords = extract_seo_keywords(title, content)
        
        # Calcula reading time (palavras / 200 palavras por minuto)
        word_count = len(content.split())
        reading_time = max(1, round(word_count / 200))
        
        # Limpa o título para usar no nome do arquivo
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[\s_]+', '-', slug)
        filename = POSTS_DIR / f"{now.strftime('%Y-%m-%d')}-{slug[:80]}.md"

        # Escapa caracteres especiais
        escaped_title = title.replace('"', '\\"')
        escaped_description = seo_description.replace('"', '\\"')
        
        # Formata arrays YAML
        tags_yaml = '\n  - '.join([''] + tags)
        keywords_yaml = '\n  - '.join([''] + seo_keywords) if seo_keywords else ''
        
        # Frontmatter SEO-otimizado
        frontmatter = f"""---
title: "{escaped_title}"
date: {iso_timestamp}
draft: false
description: "{escaped_description}"
summary: "{escaped_description}"
tags:{tags_yaml}
keywords:{keywords_yaml}
categories:
  - {HUGO_CATEGORY}
author: "{HUGO_AUTHOR}"
readingTime: {reading_time}
wordCount: {word_count}
seo:
  title: "{escaped_title}"
  description: "{escaped_description}"
  canonical: ""
  noindex: false
---

"""

        # Adiciona CTA engajante e estrutura SEO ao conteúdo
        content_with_cta = add_engaging_cta(content, title)
        seo_content = add_seo_structure(content_with_cta, seo_keywords)
        
        filename.write_text(frontmatter + seo_content, encoding="utf-8")
        
        print(f"✅ Post SEO salvo em: {filename}")
        print(f"📊 Tags: {', '.join(tags)}")
        print(f"🎯 Keywords SEO: {', '.join(seo_keywords)}")
        print(f"📖 Tempo de leitura: {reading_time} min")
        print(f"📝 Palavras: {word_count}")
        
        return filename
    except Exception as e:
        print(f"❌ Erro ao criar o arquivo do post: {e}")
        return None

def add_storytelling_elements(content: str) -> str:
    """Adiciona elementos de storytelling para melhor engajamento."""
    
    # Adiciona hook de abertura se não existir
    lines = content.split('\n')
    first_paragraph = lines[0] if lines else ""
    
    # Remove hooks não-jornalísticos - o lead deve ser direto e informativo
    # Em jornalismo técnico, a abertura deve ser factual, não especulativa
    pass
    
    # Adiciona transições jornalísticas profissionais entre seções
    sections = content.split('##')
    if len(sections) > 2:
        transitions = [
            "\n\nPara compreender o impacto completo, é necessário analisar:\n\n",
            "\n\nOs dados revelam aspectos importantes:\n\n", 
            "\n\nA análise técnica mostra que:\n\n",
            "\n\nEspecialistas do setor apontam:\n\n",
            "\n\nAs implicações práticas incluem:\n\n"
        ]
        
        for i in range(1, min(len(sections), 4)):
            if i < len(transitions):
                sections[i] = transitions[i-1] + "##" + sections[i]
        
        content = "##".join(sections)
    
    return content


def improve_journalistic_language(content: str) -> str:
    """Melhora a linguagem para padrões jornalísticos profissionais."""
    
    # Substitui linguagem marketeira por jornalística
    replacements = [
        # Remove linguagem especulativa
        (r'Imagine que', 'Considere que'),
        (r'E se eu te dissesse', 'Os dados indicam'),
        (r'Você já se perguntou', 'Analistas questionam'),
        (r'incrível', 'significativo'),
        (r'fantástico', 'notável'),
        (r'revolucionário', 'inovador'),
        
        # Melhora conectores
        (r'Mas isso não é tudo', 'Além disso'),
        (r'E tem mais', 'Adicionalmente'),
        (r'Aqui está o ponto', 'O aspecto central é'),
        
        # Linguagem mais precisa
        (r'muitas empresas', 'diversas organizações'),
        (r'a maioria dos', 'grande parte dos'),
        (r'praticamente todos', 'a maior parte dos'),
        
        # Remove exageros
        (r'extremamente', 'altamente'),
        (r'incrivelmente', 'notavelmente'),
        (r'absolutamente', 'completamente'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Melhora estrutura de frases
    # Evita frases muito longas
    sentences = re.split(r'(?<=[.!?])\s+', content)
    improved_sentences = []
    
    for sentence in sentences:
        words = sentence.split()
        # Se a frase tem mais de 25 palavras, sugere quebra
        if len(words) > 25 and ',' in sentence:
            # Tenta quebrar na primeira vírgula após a 15ª palavra
            comma_positions = [i for i, word in enumerate(words) if ',' in word]
            if comma_positions and comma_positions[0] > 10:
                break_point = comma_positions[0] + 1
                first_part = ' '.join(words[:break_point]).rstrip(',') + '.'
                second_part = ' '.join(words[break_point:])
                improved_sentences.extend([first_part, second_part])
            else:
                improved_sentences.append(sentence)
        else:
            improved_sentences.append(sentence)
    
    return ' '.join(improved_sentences)


def improve_headings_structure(content: str) -> str:
    """Melhora a estrutura dos subtítulos com emojis consistentes."""
    
    # Mapeia palavras-chave para emojis apropriados
    emoji_map = {
        'análise': '🔍',
        'técnica': '⚙️', 
        'segurança': '🛡️',
        'performance': '⚡',
        'implementação': '🚀',
        'arquitetura': '🏗️',
        'infraestrutura': '🏢',
        'desenvolvimento': '💻',
        'devops': '🔄',
        'cloud': '☁️',
        'dados': '📊',
        'api': '🔌',
        'mobile': '📱',
        'web': '🌐',
        'ia': '🤖',
        'machine learning': '🧠',
        'blockchain': '⛓️',
        'conclusão': '🎯',
        'próximos passos': '➡️',
        'recursos': '📚'
    }
    
    lines = content.split('\n')
    improved_lines = []
    
    for line in lines:
        if line.startswith('## ') and not line.startswith('### '):
            # Remove emojis existentes
            clean_line = re.sub(r'[^\w\s\-:]', '', line[3:]).strip()
            
            # Encontra emoji apropriado
            emoji = '📋'  # emoji padrão
            for keyword, emoji_char in emoji_map.items():
                if keyword.lower() in clean_line.lower():
                    emoji = emoji_char
                    break
            
            # Reconstrói o título
            improved_line = f"## {emoji} {clean_line}"
            improved_lines.append(improved_line)
        else:
            improved_lines.append(line)
    
    return '\n'.join(improved_lines)


def add_visual_elements(content: str) -> str:
    """Adiciona elementos visuais para melhorar a experiência de leitura."""
    
    # Adiciona separadores visuais entre seções principais
    content = re.sub(r'\n(## [^#])', r'\n---\n\n\1', content)
    
    # Destaca informações importantes com callouts
    important_patterns = [
        (r'(É importante notar que|Vale destacar que|Importante:|Atenção:)', r'> **💡 Destaque:** \1'),
        (r'(Cuidado|Atenção|Aviso)', r'> **⚠️ Atenção:** \1'),
        (r'(Dica|Pro tip|Sugestão)', r'> **💡 Dica:** \1'),
        (r'(Exemplo|Por exemplo)', r'> **📝 Exemplo:** \1')
    ]
    
    for pattern, replacement in important_patterns:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Adiciona ícones para listas quando apropriado
    content = re.sub(r'^- (Vantagem|Benefício)', r'✅ \1', content, flags=re.MULTILINE)
    content = re.sub(r'^- (Desvantagem|Limitação|Problema)', r'❌ \1', content, flags=re.MULTILINE)
    content = re.sub(r'^- (Requisito|Necessário)', r'📋 \1', content, flags=re.MULTILINE)
    content = re.sub(r'^- (Ferramenta|Tool)', r'🛠️ \1', content, flags=re.MULTILINE)
    
    return content


def add_engaging_cta(content: str, title: str) -> str:
    """Adiciona call-to-actions mais engajantes ao final do conteúdo."""
    
    # Remove CTAs genéricos existentes
    content = re.sub(r'\*\*Gostou do conteúdo\?\*\*.*?$', '', content, flags=re.MULTILINE | re.DOTALL)
    content = re.sub(r'### 💬 Discussão.*?$', '', content, flags=re.MULTILINE | re.DOTALL)
    content = re.sub(r'## Conclusão\n\nEste guia oferece.*?$', '', content, flags=re.MULTILINE | re.DOTALL)
    
    # CTAs específicos baseados no tipo de conteúdo
    if any(word in title.lower() for word in ['análise', 'deep dive', 'breakdown']):
        cta = """
## 💬 Vamos Continuar a Conversa

**Qual sua experiência com essa tecnologia?** Compartilhe nos comentários:
- Já implementou algo similar na sua empresa?
- Quais desafios enfrentou durante a adoção?
- Que outras análises técnicas gostaria de ver?

**📧 Quer receber mais conteúdo técnico como este?** 
Conecte-se comigo no LinkedIn para discussões sobre arquitetura, DevOps e inovação.

**🔄 Achou útil?** Compartilhe com sua equipe - conhecimento técnico é melhor quando compartilhado!
"""
    elif any(word in title.lower() for word in ['security', 'segurança', 'vulnerabilidade']):
        cta = """
## 🛡️ Sua Infraestrutura Está Preparada?

**Avalie sua postura de segurança:**
- Sua equipe conhece essas vulnerabilidades?
- Seus sistemas estão atualizados com as últimas práticas?
- Tem um plano de resposta a incidentes?

**💡 Precisa de uma segunda opinião?** 
Compartilhe este artigo com seu time de segurança e discutam as implicações.

**🚀 Próximo passo:** Implemente pelo menos uma das recomendações desta semana.
"""
    else:
        cta = """
## 🚀 Próximos Passos

**Para implementar essas ideias:**
1. Discuta com sua equipe os pontos mais relevantes
2. Identifique quick wins que podem ser implementados rapidamente  
3. Planeje um piloto para testar os conceitos

**💭 Sua opinião importa:** Que outros tópicos técnicos gostaria de ver explorados?

**🔗 Mantenha-se atualizado:** Siga para mais análises técnicas e insights do mercado.
"""
    
    content += cta
    return content


def add_seo_structure(content: str, keywords: List[str]) -> str:
    """Adiciona estrutura SEO ao conteúdo do artigo."""
    
    # Adiciona índice se o artigo for longo
    lines = content.split('\n')
    headers = [line for line in lines if line.startswith('##')]
    
    if len(headers) >= 3:
        toc = "\n## Índice\n\n"
        for header in headers:
            clean_header = header.replace('##', '').strip()
            anchor = clean_header.lower().replace(' ', '-').replace(',', '').replace(':', '')
            toc += f"- [{clean_header}](#{anchor})\n"
        
        # Insere índice após a introdução
        intro_end = content.find('\n##')
        if intro_end > 0:
            content = content[:intro_end] + toc + content[intro_end:]
    
    # Adiciona FAQ section se houver palavras-chave
    if keywords:
        faq_section = f"\n\n## Perguntas Frequentes\n\n"
        
        for keyword in keywords[:3]:  # Máximo 3 FAQs
            faq_section += f"### O que é {keyword}?\n\n"
            faq_section += f"{keyword.capitalize()} é uma tecnologia/conceito importante que permite [explicação breve baseada no contexto do artigo].\n\n"
        
        content += faq_section
    
    # CTA engajante já foi aplicado anteriormente
    
    return content

def commit_new_post(file_path: Path, title: str):
    """Adiciona, commita e faz push do novo post no Git."""
    print("🚀 Fazendo commit do novo post...")
    try:
        # Adiciona o arquivo ao stage
        subprocess.run(["git", "add", str(file_path)], check=True)
        
        # Cria a mensagem de commit
        commit_message = f'feat: Add post "{title[:100]}"'
        
        # Faz o commit
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("✅ Commit local realizado com sucesso!")

        # Faz o push para o repositório remoto
        print("📡 Enviando para o repositório remoto (git push)...")
        subprocess.run(["git", "push"], check=True)
        print("✅ Push realizado com sucesso!")
        
        print(f"\nResumo:\n  {commit_message}")

    except subprocess.CalledProcessError as e:
        print(f"❌ ERRO ao executar comando git: {e}")
        print("Verifique se o git está instalado, configurado (user.name, user.email) e se suas credenciais para o GitHub estão corretas (ex: via Personal Access Token).")
    except FileNotFoundError:
        print("❌ ERRO: O comando 'git' não foi encontrado. O arquivo foi criado mas não commitado.")

def validate_journalistic_quality(title: str, content: str) -> bool:
    """Valida se o conteúdo atende aos padrões de qualidade jornalística."""
    
    issues = []
    
    # Verifica se tem lead jornalístico (primeiros 2 parágrafos)
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
    if len(paragraphs) >= 2:
        first_two = ' '.join(paragraphs[:2]).lower()
        # Verifica se responde aos 5 W's básicos (mais flexível)
        has_what = any(word in first_two for word in ['anunciou', 'lançou', 'revelou', 'apresentou', 'desenvolveu', 'criou', 'introduziu', 'implementou', 'oferece', 'disponibiliza'])
        has_who = any(word in first_two for word in ['empresa', 'companhia', 'organização', 'equipe', 'google', 'microsoft', 'amazon', 'meta', 'nvidia', 'apple', 'tecnologia', 'plataforma'])
        
        # Relaxa critério - só precisa de O QUE e QUEM
        if not (has_what or has_who):
            issues.append("Lead precisa ser mais informativo sobre o que aconteceu e quem está envolvido")
    
    # Verifica densidade de dados específicos
    data_indicators = len(re.findall(r'\d+[%\w]*', content))  # números, percentuais
    word_count = len(content.split())
    data_density = data_indicators / word_count if word_count > 0 else 0
    
    if data_density < 0.01:  # Menos de 1% de dados específicos
        issues.append("Baixa densidade de dados específicos (números, percentuais)")
    
    # Verifica se tem parágrafos muito longos (mais flexível)
    long_paragraphs = [p for p in paragraphs if len(p.split()) > 150]
    if len(long_paragraphs) > 3:
        issues.append("Parágrafos excessivamente longos (>150 palavras)")
    
    # Verifica redundâncias comuns
    redundant_phrases = [
        'é importante notar que', 'vale destacar que', 'cabe ressaltar que',
        'como mencionado anteriormente', 'conforme já dito'
    ]
    redundancy_count = sum(content.lower().count(phrase) for phrase in redundant_phrases)
    if redundancy_count > 3:
        issues.append("Muitas frases redundantes ou clichês")
    
    # Verifica se tem conectores lógicos (mais abrangente)
    logical_connectors = ['portanto', 'consequentemente', 'assim', 'dessa forma', 'logo', 'além disso', 'por outro lado', 'entretanto', 'contudo', 'no entanto', 'adicionalmente', 'por sua vez', 'desta forma']
    connector_count = sum(1 for connector in logical_connectors if connector in content.lower())
    if connector_count < 2:
        issues.append("Poucos conectores lógicos para melhor fluxo textual")
    
    if issues:
        print(f"❌ Problemas de qualidade jornalística encontrados:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    print("✅ Conteúdo aprovado na validação de qualidade jornalística")
    return True


def validate_ethical_guidelines(title: str, content: str) -> bool:
    """Valida se o conteúdo segue as diretrizes éticas."""
    
    # Palavras proibidas (sensacionalistas)
    forbidden_words = [
        "breaking", "exclusivo", "confirmado", "vazou", "oficial",
        "acabou de", "nesta manhã", "hoje cedo", "há poucas horas"
    ]
    
    title_lower = title.lower()
    content_lower = content.lower()
    
    # Verifica palavras proibidas no título
    for word in forbidden_words:
        if word in title_lower:
            print(f"❌ Título contém palavra sensacionalista: '{word}'")
            return False
    
    # Verifica se é educativo ou híbrido válido
    educational_indicators = [
        "como", "guia", "análise", "comparativo", "entendendo",
        "explicado", "fundamentos", "conceitos", "práticas"
    ]
    
    hybrid_indicators = [
        "análise:", "contexto:", "o que", "lições", "por trás",
        "significam", "impacto de", "implicações"
    ]
    
    has_educational_indicator = any(word in title_lower for word in educational_indicators)
    has_hybrid_indicator = any(word in title_lower for word in hybrid_indicators)
    
    if not (has_educational_indicator or has_hybrid_indicator):
        print("❌ Título não parece educativo nem híbrido válido")
        return False
    
    # Verifica timestamps específicos no conteúdo
    temporal_flags = [
        "hoje", "ontem", "esta manhã", "nesta tarde", "há poucas horas",
        "acabou de ser anunciado", "confirmou hoje", "nesta semana"
    ]
    
    for flag in temporal_flags:
        if flag in content_lower:
            print(f"❌ Conteúdo contém timestamp específico: '{flag}'")
            return False
    
    return True

def validate_seo_quality(title: str, content: str) -> bool:
    """Valida qualidade SEO do post gerado."""
    
    # Validação de título SEO
    if len(title) < SEO_TITLE_MIN_LENGTH:
        print(f"❌ Título muito curto para SEO ({len(title)} < {SEO_TITLE_MIN_LENGTH})")
        return False
    
    if len(title) > SEO_TITLE_MAX_LENGTH:
        print(f"❌ Título muito longo para SEO ({len(title)} > {SEO_TITLE_MAX_LENGTH})")
        return False
    
    # Validação de conteúdo SEO
    word_count = len(content.split())
    if word_count < SEO_ARTICLE_MIN_WORDS:
        print(f"❌ Artigo muito curto para SEO ({word_count} < {SEO_ARTICLE_MIN_WORDS} palavras)")
        return False
    
    if word_count > SEO_ARTICLE_MAX_WORDS:
        print(f"⚠️ Artigo muito longo ({word_count} > {SEO_ARTICLE_MAX_WORDS} palavras), mas continuando...")
    
    # Validação de estrutura SEO
    headers = content.count('##')
    if headers < 3:
        print(f"⚠️ Poucos subtítulos para SEO ({headers} < 3), mas continuando...")
    
    # Verifica presença de palavras-chave SEO
    has_seo_keywords = False
    title_lower = title.lower()
    content_lower = content.lower()
    
    for keywords in SEO_KEYWORDS.values():
        for keyword in keywords:
            if keyword in title_lower or keyword in content_lower:
                has_seo_keywords = True
                break
        if has_seo_keywords:
            break
    
    if not has_seo_keywords:
        print("⚠️ Nenhuma palavra-chave SEO identificada, mas continuando...")
    
    print(f"✅ Post aprovado na validação SEO ({word_count} palavras, {headers} subtítulos)")
    return True

def validate_post_quality(title: str, content: str) -> bool:
    """Valida a qualidade básica, ética e SEO do post gerado."""
    
    # Validação de qualidade jornalística
    if not validate_journalistic_quality(title, content):
        print("❌ Post não atende aos padrões de qualidade jornalística, regenerando...")
        return False
    
    # Validação ética
    if not validate_ethical_guidelines(title, content):
        print("❌ Post não atende às diretrizes éticas, regenerando...")
        return False
    
    # Validação SEO
    if not validate_seo_quality(title, content):
        print("❌ Post não atende aos critérios SEO, regenerando...")
        return False
    
    print("✅ Post aprovado em todas as validações (ética + SEO)")
    return True

def load_ethical_guidelines() -> bool:
    """Carrega e valida se as diretrizes éticas estão disponíveis."""
    guidelines_file = Path("ethical_guidelines.md")
    if guidelines_file.exists():
        print("✅ Diretrizes éticas carregadas")
        return True
    else:
        print("⚠️ Arquivo de diretrizes éticas não encontrado")
        return False

def show_progress(step: int, total: int, description: str):
    """Mostra indicador de progresso."""
    if PROGRESS_INDICATORS:
        percentage = (step / total) * 100
        bar_length = 20
        filled_length = int(bar_length * step // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f"📊 [{bar}] {percentage:.0f}% - {description}")

def main():
    """Função principal que orquestra todo o processo de análise técnica."""
    total_steps = 6
    current_step = 0
    
    print("📰 Iniciando geração de análise técnica de notícias...")
    print(f"📅 Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🎯 Foco: 80% análise de notícias, 15% técnico SEO, 5% técnico geral")
    print("⚡ Otimizado para evitar timeouts")
    print()
    
    current_step += 1
    show_progress(current_step, total_steps, "Configurando API...")
    
    if not setup_api():
        sys.exit(1)

    current_step += 1
    show_progress(current_step, total_steps, "Gerando tópico...")
    
    # Decide o tipo de geração focado em análise técnica de notícias
    rand = random.random()
    
    print(f"🎲 Sorteio: {rand:.2f}")
    
    if rand < 0.8:
        print("📰 Selecionado: Análise técnica de notícia")
        topic = generate_news_technical_analysis()
    elif rand < 0.95:
        print("🔧 Selecionado: Conteúdo técnico SEO")
        topic = generate_technical_seo_topic()
    else:
        print("💻 Selecionado: Conteúdo técnico geral")
        topic = generate_it_professional_topic()
    
    if not topic:
        print("❌ Falha ao gerar tópico único.")
        sys.exit(1)
    
    current_step += 1
    show_progress(current_step, total_steps, f"Tópico: {topic}")

    current_step += 1
    show_progress(current_step, total_steps, "Gerando artigo...")
    
    # Gera artigo com timeout otimizado
    max_article_attempts = MAX_ARTICLE_ATTEMPTS
    article = ""
    
    for attempt in range(max_article_attempts):
        print(f"📝 Tentativa {attempt + 1}/{max_article_attempts} - Gerando artigo...")
        try:
            article = write_article(topic)
            
            if article and validate_post_quality(topic, article):
                print(f"✅ Artigo gerado com sucesso ({len(article)} chars)")
                break
            elif attempt < max_article_attempts - 1:
                print("🔄 Regenerando artigo...")
        except Exception as e:
            if "timeout" in str(e).lower() or "504" in str(e):
                print(f"⏰ Timeout na geração do artigo (tentativa {attempt + 1})")
                if attempt < max_article_attempts - 1:
                    print("🔄 Tentando com prompt mais simples...")
            else:
                print(f"❌ Erro na geração: {str(e)[:100]}...")
    
    if not article:
        print("❌ Falha ao gerar artigo de qualidade.")
        sys.exit(1)
    
    current_step += 1
    show_progress(current_step, total_steps, f"Artigo: {len(article)} caracteres")

    current_step += 1
    show_progress(current_step, total_steps, "Criando post Hugo...")
    
    # Cria o post com metadados aprimorados
    post_path = create_hugo_post(topic, article)
    if not post_path:
        sys.exit(1)

    current_step += 1
    show_progress(current_step, total_steps, "Fazendo commit...")
    
    # Commit e push
    commit_new_post(post_path, topic)

    show_progress(total_steps, total_steps, "Processo concluído!")
    
    print(f"\n✨ Análise técnica '{topic}' publicada com sucesso! ✨")
    print(f"� TArquivo: {post_path.name}")
    print(f"�  Tamanho: {len(article)} caracteres")
    print(f"📰 Tipo: Análise técnica de notícia")
    print(f"🕒 Processo concluído em: {datetime.now().strftime('%H:%M:%S')}")
    print(f"⚡ Sem timeouts detectados!")

if __name__ == "__main__":
    # Verifica diretrizes éticas antes de executar
    guidelines_file = Path("ethical_guidelines.md")
    if guidelines_file.exists():
        print("✅ Diretrizes éticas carregadas")
    else:
        print("⚠️ Arquivo de diretrizes éticas não encontrado")
    
    main()