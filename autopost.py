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

# --- Configurações ---
POSTS_DIR = Path("content/posts")
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
TOPICS_CACHE = CACHE_DIR / "topics_cache.json"

def setup_api():
    """Carrega variáveis de ambiente e configura a API do Gemini."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERRO: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        print("Certifique-se de que o arquivo .env está na raiz do projeto e contém sua chave.")
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"❌ ERRO ao configurar a API do Gemini: {e}")
        return False

def call_gemini_api(prompt: str, safety_settings=None, max_retries=MAX_API_RETRIES) -> str:
    """
    Chama a API do Gemini com um prompt e configurações de segurança opcionais.
    Retorna a resposta em texto ou lança uma exceção em caso de erro.
    """
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt, safety_settings=safety_settings)
            if response.text:
                return response.text
            else:
                print(f"⚠️ Tentativa {attempt + 1}: Resposta vazia da API")
        except Exception as e:
            print(f"⚠️ Tentativa {attempt + 1} falhou: {e}")
            if attempt == max_retries - 1:
                raise e
    
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

def generate_new_topic() -> str:
    """Usa a IA para gerar um novo tópico de post, evitando duplicatas."""
    print("🧠 Gerando um novo tópico de notícia recente...")
    
    cache_data = load_topics_cache()
    used_topics = cache_data.get("used_topics", [])
    
    today = datetime.now()
    current_date_str = today.strftime("%d de %B de %Y")
    temporal_context = get_current_tech_context()
    
    # Obtém tendências atuais do mercado
    market_trends = get_market_trends()
    
    # Seleciona uma categoria aleatória e pega algumas tendências
    category = random.choice(list(market_trends.keys()))
    category_trends = market_trends[category]
    
    max_attempts = MAX_TOPIC_ATTEMPTS
    for attempt in range(max_attempts):
        # Seleciona 2-3 tendências da categoria escolhida
        selected_trends = random.sample(category_trends, min(3, len(category_trends)))
        
        # Adiciona algumas tendências de outras categorias para contexto
        other_categories = [k for k in market_trends.keys() if k != category]
        if other_categories:
            other_category = random.choice(other_categories)
            selected_trends.extend(random.sample(market_trends[other_category], 1))
        
        # Seleciona elementos específicos das tendências
        hot_company = random.choice(HOT_COMPANIES)
        trending_product = random.choice(TRENDING_PRODUCTS)
        emerging_tech = random.choice(EMERGING_TECH)
        recent_event = random.choice(RECENT_EVENTS)
        urgency_word = random.choice(URGENCY_KEYWORDS)
        temporal_context_specific = random.choice(TEMPORAL_CONTEXTS)
        
        prompt = (
            f"🚨 NEWSROOM ALERT - {current_date_str} {temporal_context_specific}\n\n"
            f"Você é editor-chefe de tecnologia gerando um título URGENTE para breaking news.\n\n"
            f"ELEMENTOS PARA O TÍTULO (use 1-2 destes):\n"
            f"• Empresa: {hot_company}\n"
            f"• Produto: {trending_product}\n"
            f"• Tecnologia: {emerging_tech}\n"
            f"• Evento: {recent_event}\n"
            f"• Urgência: {urgency_word}\n"
            f"• Timing: {temporal_context_specific}\n\n"
            f"FÓRMULAS DE TÍTULO EFICAZES:\n"
            f"• '[URGÊNCIA] [Empresa] [evento] [produto/tecnologia]'\n"
            f"• '[Empresa] [evento] [produto]: [impacto/número]'\n"
            f"• '[Produto] da [Empresa] [evento] com [tecnologia]'\n"
            f"• 'VAZOU: [Empresa] prepara [produto] com [tecnologia]'\n\n"
            f"EXEMPLOS DE ESTILO:\n"
            f"• 'CONFIRMADO: OpenAI lança GPT-5 com 10x mais poder'\n"
            f"• 'Apple anuncia iPhone 17 com tela holográfica para 2026'\n"
            f"• 'EXCLUSIVO: Meta adquire startup de IA por US$ 15 bilhões'\n"
            f"• 'Google revela Gemini 2.0 que supera humanos em programação'\n\n"
            f"REQUISITOS:\n"
            f"• Máximo 80 caracteres\n"
            f"• Inclua números/dados específicos quando possível\n"
            f"• Use palavras de impacto: revoluciona, supera, anuncia, confirma\n"
            f"• Foque no BENEFÍCIO/IMPACTO para o usuário\n\n"
            f"EVITE (já cobertos): {', '.join(used_topics[-5:]) if used_topics else 'nenhum'}\n\n"
            f"Gere UM título que pareça ter saído agora de uma redação tech!\n"
            f"APENAS O TÍTULO, sem explicações:"
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

def generate_realistic_data() -> Dict[str, str]:
    """Gera dados realistas para tornar as notícias mais específicas."""
    today = datetime.now()
    
    return {
        "version_numbers": random.choice(["2.1", "3.0", "4.5", "15.2", "24H2", "v6.1"]),
        "percentages": f"{random.randint(15, 85)}%",
        "user_numbers": f"{random.randint(100, 500)} milhões",
        "price_range": f"US$ {random.randint(99, 999)}",
        "release_timeframe": random.choice([
            "nas próximas semanas", "ainda este mês", "no primeiro trimestre de 2026",
            "até o final do ano", "na próxima atualização"
        ]),
        "market_impact": f"{random.randint(5, 25)} bilhões de dólares",
        "performance_gain": f"{random.randint(20, 300)}% mais rápido",
        "current_date": today.strftime("%d de %B"),
        "this_week": f"esta semana de {today.strftime('%d de %B')}"
    }

def generate_references(title: str) -> List[str]:
    """Gera fontes de referência realistas para o artigo."""
    print("📚 Gerando fontes de referência...")
    
    prompt = (
        f"Para um artigo sobre '{title}', gere 3-5 fontes de referência realistas e credíveis. "
        "Use sites reais de tecnologia como: TechCrunch, The Verge, Ars Technica, Wired, "
        "Tecmundo, Olhar Digital, Canaltech, sites oficiais de empresas, blogs de desenvolvedores conhecidos. "
        "Formato: uma fonte por linha, apenas o nome do site/fonte (ex: 'TechCrunch', 'Site oficial da Microsoft'). "
        "NÃO inclua URLs completas, apenas os nomes das fontes."
    )
    
    try:
        references_text = call_gemini_api(prompt).strip()
        references = [ref.strip() for ref in references_text.split('\n') if ref.strip()]
        print(f"✅ {len(references)} fontes geradas")
        return references[:5]  # Máximo 5 fontes
    except Exception as e:
        print(f"⚠️ Erro ao gerar referências: {e}")
        return DEFAULT_REFERENCES[:3]  # Fallback

def write_article(title: str) -> str:
    """Gera o conteúdo do artigo com base no título, incluindo fontes."""
    print(f'✍️ Escrevendo artigo sobre: "{title}"...')
    
    # Gera as referências e dados realistas
    references = generate_references(title)
    references_text = ", ".join(references)
    realistic_data = generate_realistic_data()
    
    today = datetime.now()
    current_date = today.strftime("%d de %B de %Y")
    
    prompt = (
        f"BREAKING NEWS - {current_date}\n\n"
        f"Você é um jornalista tech da {random.choice(['Tecmundo', 'The Verge', 'TechCrunch'])} "
        f"escrevendo uma matéria EXCLUSIVA sobre: '{title}'\n\n"
        f"CONTEXTO TEMPORAL: Esta notícia acabou de ser confirmada {realistic_data['this_week']}.\n\n"
        f"FONTES VERIFICADAS: {references_text}\n\n"
        f"DADOS PARA INCLUIR (use alguns destes números realistas):\n"
        f"- Versão/Build: {realistic_data['version_numbers']}\n"
        f"- Impacto: {realistic_data['percentages']} dos usuários\n"
        f"- Base de usuários: {realistic_data['user_numbers']}\n"
        f"- Preço estimado: {realistic_data['price_range']}\n"
        f"- Timeline: {realistic_data['release_timeframe']}\n"
        f"- Mercado: {realistic_data['market_impact']}\n"
        f"- Performance: {realistic_data['performance_gain']}\n\n"
        f"ESTRUTURA JORNALÍSTICA:\n"
        f"1. LEAD: Responda QUEM, O QUE, QUANDO, ONDE nos primeiros 2 parágrafos\n"
        f"2. ## Detalhes da Novidade (inclua números específicos)\n"
        f"3. ## Impacto no Mercado (compare com concorrentes)\n"
        f"4. ## Reação da Comunidade Tech\n"
        f"5. ## Próximos Passos (roadmap, expectativas)\n\n"
        f"REQUISITOS:\n"
        f"- {ARTICLE_MIN_WORDS}-{ARTICLE_MAX_WORDS} palavras\n"
        f"- Tom de URGÊNCIA jornalística (use 'acabou de', 'confirmou hoje', 'anunciou agora')\n"
        f"- Citações de executivos (invente nomes realistas)\n"
        f"- Dados técnicos específicos\n"
        f"- Menção ao impacto no Brasil\n"
        f"- Linguagem técnica mas acessível\n\n"
        f"IMPORTANTE:\n"
        f"- Escreva como se fosse FATO REAL que aconteceu hoje\n"
        f"- Use números e dados específicos fornecidos acima\n"
        f"- Inclua timestamps realistas ('nesta manhã', 'há poucas horas')\n"
        f"- Compare com produtos/serviços similares\n"
        f"- NÃO mencione que é conteúdo gerado por IA\n"
        f"- NÃO inclua seção de referências no final\n\n"
        f"Trate como uma EXCLUSIVA que você acabou de confirmar com suas fontes!"
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
            # Adiciona seção de referências ao final
            article += "\n\n## Fontes\n\n"
            for i, ref in enumerate(references, 1):
                article += f"{i}. {ref}\n"
            
            print("✅ Artigo gerado com sucesso (incluindo fontes).")
            return article
        else:
            print("❌ A IA não retornou um artigo válido.")
            return ""
    except Exception as e:
        print(f"❌ Erro ao gerar o artigo com a IA: {e}")
        return ""

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
    """Cria e salva o arquivo .md para o Hugo com metadados aprimorados."""
    print("📝 Formatando e salvando o post para o Hugo...")
    try:
        now = datetime.now()
        tz_offset = timezone(timedelta(hours=TIMEZONE_OFFSET))
        iso_timestamp = now.astimezone(tz_offset).isoformat()
        
        # Gera tags automaticamente
        tags = generate_tags(title, content)
        
        # Limpa o título para usar no nome do arquivo
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[\s_]+', '-', slug)
        filename = POSTS_DIR / f"{now.strftime('%Y-%m-%d')}-{slug[:50]}.md"

        # Gera um resumo do artigo
        summary_lines = content.split('\n')[:3]
        summary = ' '.join(summary_lines).replace('#', '').strip()[:150] + "..."
        
        escaped_title = title.replace('"', '\\"')
        escaped_summary = summary.replace('"', '\\"')
        tags_yaml = '\n  - '.join([''] + tags)
        
        frontmatter = f"""---
title: "{escaped_title}"
date: {iso_timestamp}
draft: false
summary: "{escaped_summary}"
tags:{tags_yaml}
categories:
  - {HUGO_CATEGORY}
author: "{HUGO_AUTHOR}"
---

"""

        filename.write_text(frontmatter + content, encoding="utf-8")
        print(f"✅ Post salvo em: {filename}")
        print(f"📊 Tags geradas: {', '.join(tags)}")
        return filename
    except Exception as e:
        print(f"❌ Erro ao criar o arquivo do post: {e}")
        return None

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

def validate_post_quality(title: str, content: str) -> bool:
    """Valida a qualidade básica do post gerado."""
    if len(title) < 10 or len(content) < 500:
        print("❌ Post muito curto, regenerando...")
        return False
    
    if content.count('##') < 2:
        print("⚠️ Post com poucos subtítulos, mas continuando...")
    
    return True

def main():
    """Função principal que orquestra todo o processo com melhorias."""
    print("🚀 Iniciando geração automatizada de post...")
    print(f"📅 Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    if not setup_api():
        sys.exit(1)

    # Gera tópico com retry em caso de duplicata
    topic = generate_new_topic()
    if not topic:
        print("❌ Falha ao gerar tópico único.")
        sys.exit(1)

    # Gera artigo com validação de qualidade
    max_article_attempts = MAX_ARTICLE_ATTEMPTS
    article = ""
    
    for attempt in range(max_article_attempts):
        print(f"📝 Tentativa {attempt + 1} de geração do artigo...")
        article = write_article(topic)
        
        if article and validate_post_quality(topic, article):
            break
        elif attempt < max_article_attempts - 1:
            print("🔄 Regenerando artigo...")
    
    if not article:
        print("❌ Falha ao gerar artigo de qualidade.")
        sys.exit(1)

    # Cria o post com metadados aprimorados
    post_path = create_hugo_post(topic, article)
    if not post_path:
        sys.exit(1)

    # Commit e push
    commit_new_post(post_path, topic)

    print(f"\n✨ Post '{topic}' publicado com sucesso! ✨")
    print(f"📄 Arquivo: {post_path.name}")
    print(f"📊 Tamanho: {len(article)} caracteres")
    print(f"🕒 Processo concluído em: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()