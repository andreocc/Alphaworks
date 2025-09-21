#!/usr/bin/env python3
"""
News Publisher - Sistema de publicação baseado em scraping
Pega notícias reais do Perplexity AI e cria artigos jornalísticos
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timezone, timedelta
import subprocess
from dotenv import load_dotenv

from tech_news_scraper import TechNewsScraper

# Configurações
POSTS_DIR = Path("content/posts")
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
PUBLISHED_CACHE = CACHE_DIR / "published_articles.json"

# Configurações do Hugo
HUGO_AUTHOR = "Alphaworks"
HUGO_CATEGORY = "Tecnologia"
TIMEZONE_OFFSET = -3  # Brasília (UTC-3)

class NewsPublisher:
    def __init__(self):
        self.scraper = TechNewsScraper()
        self.published_articles = self.load_published_cache()
        
        # Mapeamento de fontes com links
        self.source_links = {
            'Perplexity AI': 'https://www.perplexity.ai/',
            'TechCrunch': 'https://techcrunch.com/',
            'The Verge': 'https://www.theverge.com/',
            'Ars Technica': 'https://arstechnica.com/',
            'Wired': 'https://www.wired.com/',
            'Engadget': 'https://www.engadget.com/',
            'Tecmundo': 'https://www.tecmundo.com.br/',
            'Olhar Digital': 'https://olhardigital.com.br/',
            'Canaltech': 'https://canaltech.com.br/',
            'Tecnoblog': 'https://tecnoblog.net/',
        }

    def get_fresh_news(self) -> Optional[Dict]:
        """
        Obtém uma notícia ainda não publicada
        """
        print("📰 Buscando notícias não publicadas...")
        
        articles = self.scraper.get_tech_news(max_articles=20)
        
        if not articles:
            print("❌ Nenhuma notícia encontrada")
            return None
        
        # Filtra artigos já publicados
        for article in articles:
            article_id = self.generate_article_id(article['title'])
            
            if article_id not in self.published_articles:
                print(f"✅ Nova notícia encontrada: {article['title'][:60]}...")
                return article
        
        print("⚠️ Todas as notícias já foram publicadas")
        return None

    def generate_article_id(self, title: str) -> str:
        """
        Gera ID único para o artigo baseado no título
        """
        clean_title = re.sub(r'[^\w\s]', '', title.lower()).strip()
        return hashlib.md5(clean_title.encode()).hexdigest()[:12]

    def create_journalistic_article(self, news_data: Dict) -> str:
        """
        Cria um artigo jornalístico baseado na notícia real
        """
        title = news_data['title']
        description = news_data.get('description', '')
        url = news_data.get('url', '')
        keywords = news_data.get('keywords', [])
        
        print(f"✍️ Criando artigo jornalístico para: {title}")
        
        # Tenta obter conteúdo completo se há URL
        full_content = ""
        if url:
            print("📖 Obtendo conteúdo completo...")
            full_content = self.scraper.get_article_content(url)
        
        # Cria o artigo jornalístico
        article_content = self.write_journalistic_content(
            title=title,
            description=description,
            full_content=full_content,
            keywords=keywords,
            source_url=url
        )
        
        return article_content

    def write_journalistic_content(self, title: str, description: str, 
                                 full_content: str, keywords: List[str], 
                                 source_url: str) -> str:
        """
        Escreve conteúdo jornalístico baseado nas informações reais
        """
        # Análise do conteúdo para extrair informações
        main_topic = self.identify_main_topic(title, keywords)
        companies = self.extract_companies(title, description)
        tech_areas = self.extract_tech_areas(title, description, keywords)
        
        # Estrutura do artigo jornalístico
        article = f"""A {main_topic} está em destaque no cenário tecnológico atual. """
        
        if companies:
            article += f"Empresas como {', '.join(companies)} estão na vanguarda deste desenvolvimento. "
        
        article += f"{description}\n\n"
        
        # Seção de contexto
        article += "## Contexto e Relevância\n\n"
        article += self.generate_context_section(main_topic, tech_areas, companies)
        
        # Seção de análise técnica
        article += "\n## Análise Técnica\n\n"
        article += self.generate_technical_analysis(main_topic, tech_areas, keywords)
        
        # Seção de impacto no mercado
        article += "\n## Impacto no Mercado\n\n"
        article += self.generate_market_impact(main_topic, companies, tech_areas)
        
        # Seção de perspectivas futuras
        article += "\n## Perspectivas Futuras\n\n"
        article += self.generate_future_perspectives(main_topic, tech_areas)
        
        # Se há conteúdo completo, adiciona insights adicionais
        if full_content and len(full_content) > 200:
            article += "\n## Detalhes Adicionais\n\n"
            article += self.extract_key_insights(full_content)
        
        return article

    def identify_main_topic(self, title: str, keywords: List[str]) -> str:
        """
        Identifica o tópico principal da notícia
        """
        title_lower = title.lower()
        
        topic_mapping = {
            'inteligência artificial': ['ai', 'artificial intelligence', 'machine learning', 'deep learning'],
            'cibersegurança': ['security', 'cybersecurity', 'privacy', 'breach', 'hack'],
            'blockchain': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'crypto'],
            'computação em nuvem': ['cloud', 'aws', 'azure', 'google cloud'],
            'dispositivos móveis': ['iphone', 'android', 'smartphone', 'mobile', 'app'],
            'startups': ['startup', 'funding', 'investment', 'ipo', 'acquisition'],
            'big tech': ['apple', 'google', 'microsoft', 'meta', 'amazon', 'tesla'],
            'software': ['software', 'programming', 'development', 'code'],
            'hardware': ['hardware', 'chip', 'processor', 'semiconductor'],
            'inovação tecnológica': ['innovation', 'technology', 'tech', 'digital']
        }
        
        for topic, indicators in topic_mapping.items():
            if any(indicator in title_lower for indicator in indicators):
                return topic
        
        # Se não encontrou, usa palavras-chave
        if keywords:
            return keywords[0].replace('_', ' ').title()
        
        return "tecnologia"

    def extract_companies(self, title: str, description: str) -> List[str]:
        """
        Extrai nomes de empresas mencionadas
        """
        text = f"{title} {description}".lower()
        
        companies = [
            'Apple', 'Google', 'Microsoft', 'Amazon', 'Meta', 'Tesla',
            'NVIDIA', 'Intel', 'AMD', 'IBM', 'Oracle', 'Salesforce',
            'OpenAI', 'Anthropic', 'SpaceX', 'Netflix', 'Uber', 'Airbnb'
        ]
        
        found_companies = []
        for company in companies:
            if company.lower() in text:
                found_companies.append(company)
        
        return found_companies[:3]  # Máximo 3 empresas

    def extract_tech_areas(self, title: str, description: str, keywords: List[str]) -> List[str]:
        """
        Extrai áreas tecnológicas relevantes
        """
        text = f"{title} {description} {' '.join(keywords)}".lower()
        
        tech_areas = [
            'inteligência artificial', 'machine learning', 'blockchain',
            'computação em nuvem', 'cibersegurança', 'internet das coisas',
            'realidade virtual', 'realidade aumentada', 'automação',
            'robótica', 'computação quântica', 'biotecnologia'
        ]
        
        found_areas = []
        for area in tech_areas:
            if any(word in text for word in area.split()):
                found_areas.append(area)
        
        return found_areas[:3]  # Máximo 3 áreas

    def generate_context_section(self, main_topic: str, tech_areas: List[str], companies: List[str]) -> str:
        """
        Gera seção de contexto
        """
        context = f"O desenvolvimento em {main_topic} representa uma tendência significativa no mercado tecnológico atual. "
        
        if tech_areas:
            context += f"Esta evolução está conectada com avanços em {', '.join(tech_areas)}, "
            context += "demonstrando a interconexão entre diferentes áreas da tecnologia.\n\n"
        
        if companies:
            context += f"A participação de empresas estabelecidas como {', '.join(companies)} "
            context += "indica a importância estratégica deste desenvolvimento para o setor.\n\n"
        
        context += "Para o mercado brasileiro, essas inovações podem representar novas oportunidades "
        context += "de crescimento e modernização tecnológica."
        
        return context

    def generate_technical_analysis(self, main_topic: str, tech_areas: List[str], keywords: List[str]) -> str:
        """
        Gera análise técnica
        """
        analysis = f"Do ponto de vista técnico, os avanços em {main_topic} envolvem "
        analysis += "múltiplas camadas de inovação tecnológica.\n\n"
        
        if 'ai' in keywords or 'artificial intelligence' in keywords:
            analysis += "Os algoritmos de inteligência artificial estão se tornando mais "
            analysis += "sofisticados, permitindo aplicações mais precisas e eficientes. "
        
        if 'cloud' in keywords:
            analysis += "A integração com plataformas de computação em nuvem oferece "
            analysis += "escalabilidade e acessibilidade ampliadas. "
        
        if 'security' in keywords or 'cybersecurity' in keywords:
            analysis += "Aspectos de segurança são fundamentais, exigindo implementação "
            analysis += "de protocolos robustos de proteção de dados. "
        
        analysis += "\n\nA implementação dessas tecnologias requer consideração cuidadosa "
        analysis += "de fatores como infraestrutura, custos operacionais e capacitação técnica."
        
        return analysis

    def generate_market_impact(self, main_topic: str, companies: List[str], tech_areas: List[str]) -> str:
        """
        Gera análise de impacto no mercado
        """
        impact = f"O impacto no mercado de {main_topic} pode ser observado em diferentes dimensões.\n\n"
        
        impact += "**Competitividade Empresarial**: Empresas que adotam essas tecnologias "
        impact += "tendem a obter vantagens competitivas significativas, melhorando "
        impact += "eficiência operacional e capacidade de inovação.\n\n"
        
        impact += "**Transformação Setorial**: Diversos setores da economia podem ser "
        impact += "impactados, desde serviços financeiros até manufatura e saúde.\n\n"
        
        impact += "**Oportunidades de Investimento**: O desenvolvimento cria novas "
        impact += "oportunidades para investidores e empreendedores interessados "
        impact += "em tecnologias emergentes.\n\n"
        
        if companies:
            impact += f"A participação de empresas como {', '.join(companies)} "
            impact += "demonstra o potencial de mercado e a viabilidade comercial "
            impact += "dessas inovações."
        
        return impact

    def generate_future_perspectives(self, main_topic: str, tech_areas: List[str]) -> str:
        """
        Gera perspectivas futuras
        """
        perspectives = f"As perspectivas futuras para {main_topic} são promissoras, "
        perspectives += "com potencial para transformações significativas.\n\n"
        
        perspectives += "**Evolução Tecnológica**: Espera-se continuidade no desenvolvimento "
        perspectives += "de soluções mais avançadas e acessíveis.\n\n"
        
        perspectives += "**Adoção Ampliada**: A tendência é de maior adoção por empresas "
        perspectives += "de diferentes portes e setores.\n\n"
        
        perspectives += "**Regulamentação**: Desenvolvimento de frameworks regulatórios "
        perspectives += "adequados para acompanhar a evolução tecnológica.\n\n"
        
        perspectives += "**Capacitação**: Crescente necessidade de capacitação profissional "
        perspectives += "especializada para aproveitar essas oportunidades."
        
        return perspectives

    def extract_key_insights(self, full_content: str) -> str:
        """
        Extrai insights principais do conteúdo completo
        """
        # Pega os primeiros parágrafos mais informativos
        paragraphs = [p.strip() for p in full_content.split('\n') if len(p.strip()) > 50]
        
        insights = "Com base nas informações disponíveis:\n\n"
        
        # Pega até 3 parágrafos mais relevantes
        for i, paragraph in enumerate(paragraphs[:3]):
            if len(paragraph) > 100:
                insights += f"• {paragraph[:200]}...\n\n"
        
        return insights

    def generate_tags(self, title: str, keywords: List[str], companies: List[str]) -> List[str]:
        """
        Gera tags relevantes para o post
        """
        tags = set()
        
        # Tags baseadas em keywords
        keyword_mapping = {
            'ai': 'inteligencia-artificial',
            'artificial intelligence': 'inteligencia-artificial',
            'machine learning': 'machine-learning',
            'blockchain': 'blockchain',
            'cloud': 'cloud-computing',
            'security': 'ciberseguranca',
            'cybersecurity': 'ciberseguranca',
            'startup': 'startups',
            'mobile': 'mobile',
            'software': 'software',
            'hardware': 'hardware'
        }
        
        for keyword in keywords:
            if keyword in keyword_mapping:
                tags.add(keyword_mapping[keyword])
        
        # Tags baseadas em empresas
        company_tags = {
            'Apple': 'apple',
            'Google': 'google',
            'Microsoft': 'microsoft',
            'Amazon': 'amazon',
            'Meta': 'meta',
            'Tesla': 'tesla',
            'NVIDIA': 'nvidia'
        }
        
        for company in companies:
            if company in company_tags:
                tags.add(company_tags[company])
        
        # Tags genéricas sempre incluídas
        tags.update(['tecnologia', 'inovacao'])
        
        return list(tags)[:6]  # Máximo 6 tags

    def create_hugo_post(self, news_data: Dict, article_content: str) -> Optional[Path]:
        """
        Cria arquivo Hugo com o artigo
        """
        print("📝 Criando post Hugo...")
        
        title = news_data['title']
        keywords = news_data.get('keywords', [])
        companies = self.extract_companies(title, news_data.get('description', ''))
        
        # Gera metadados
        tags = self.generate_tags(title, keywords, companies)
        
        # Calcula tempo de leitura
        word_count = len(article_content.split())
        reading_time = max(1, round(word_count / 200))
        
        # Gera slug para o arquivo
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[\s_]+', '-', slug)
        
        now = datetime.now()
        tz_offset = timezone(timedelta(hours=TIMEZONE_OFFSET))
        iso_timestamp = now.astimezone(tz_offset).isoformat()
        
        filename = POSTS_DIR / f"{now.strftime('%Y-%m-%d')}-{slug[:80]}.md"
        
        # Gera descrição
        description = news_data.get('description', '')
        if not description:
            # Usa primeiras frases do artigo
            sentences = article_content.split('.')[:2]
            description = '. '.join(sentences) + '.'
        
        # Limita descrição
        if len(description) > 160:
            description = description[:157] + "..."
        
        # Cria tags YAML
        tags_yaml = '\n'.join([f"  - {tag}" for tag in tags])
        keywords_yaml = '\n'.join([f"  - {kw}" for kw in keywords[:5]])
        
        # Escapa caracteres especiais
        escaped_title = title.replace('"', '\\"')
        escaped_description = description.replace('"', '\\"')
        
        # Frontmatter
        frontmatter = f"""---
title: "{escaped_title}"
date: {iso_timestamp}
draft: false
description: "{escaped_description}"
summary: "{escaped_description}"
tags:
{tags_yaml}
keywords:
{keywords_yaml}
categories:
  - {HUGO_CATEGORY}
author: "{HUGO_AUTHOR}"
readingTime: {reading_time}
wordCount: {word_count}
source_url: "{news_data.get('url', '')}"
seo:
  title: "{escaped_title}"
  description: "{escaped_description}"
  canonical: ""
  noindex: false
---

"""
        
        # Conteúdo completo
        full_content = frontmatter + article_content
        
        # Adiciona seção de fontes
        full_content += "\n\n---\n\n## 📚 Fontes e Referências\n\n"
        full_content += f"1. **[Perplexity AI](https://www.perplexity.ai/)**\n"
        
        if news_data.get('url'):
            domain = news_data['url'].split('/')[2] if '/' in news_data['url'] else 'Fonte Original'
            full_content += f"2. **[{domain}]({news_data['url']})**\n"
        
        # Salva arquivo
        try:
            filename.write_text(full_content, encoding="utf-8")
            print(f"✅ Post salvo: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Erro ao salvar post: {e}")
            return None

    def commit_and_push(self, filename: Path, title: str):
        """
        Faz commit e push do novo post
        """
        try:
            print("🚀 Fazendo commit do novo post...")
            
            # Git add
            subprocess.run(['git', 'add', str(filename)], check=True)
            
            # Git commit
            commit_message = f'feat: Add news article "{title[:50]}..."'
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            print("✅ Commit local realizado!")
            
            # Git push
            print("📡 Enviando para repositório remoto...")
            subprocess.run(['git', 'push'], check=True)
            
            print("✅ Push realizado com sucesso!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro no git: {e}")
        except FileNotFoundError:
            print("❌ Git não encontrado. Post criado mas não commitado.")

    def load_published_cache(self) -> set:
        """
        Carrega cache de artigos já publicados
        """
        try:
            if PUBLISHED_CACHE.exists():
                with open(PUBLISHED_CACHE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('published_ids', []))
        except Exception as e:
            print(f"⚠️ Erro ao carregar cache de publicados: {e}")
        
        return set()

    def save_published_cache(self, article_id: str, title: str):
        """
        Salva ID do artigo publicado no cache
        """
        try:
            self.published_articles.add(article_id)
            
            cache_data = {
                'published_ids': list(self.published_articles),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(PUBLISHED_CACHE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")

    def publish_news_article(self) -> bool:
        """
        Processo principal: busca notícia e publica artigo
        """
        print("🚀 Iniciando publicação de artigo baseado em notícias reais...")
        
        # Busca notícia não publicada
        news_data = self.get_fresh_news()
        if not news_data:
            return False
        
        # Cria artigo jornalístico
        article_content = self.create_journalistic_article(news_data)
        
        # Cria post Hugo
        filename = self.create_hugo_post(news_data, article_content)
        if not filename:
            return False
        
        # Marca como publicado
        article_id = self.generate_article_id(news_data['title'])
        self.save_published_cache(article_id, news_data['title'])
        
        # Commit e push
        self.commit_and_push(filename, news_data['title'])
        
        print(f"✅ Artigo publicado com sucesso: {news_data['title']}")
        return True


def main():
    """
    Função principal
    """
    publisher = NewsPublisher()
    
    success = publisher.publish_news_article()
    
    if success:
        print("🎉 Processo concluído com sucesso!")
    else:
        print("❌ Não foi possível publicar artigo")
        sys.exit(1)


if __name__ == "__main__":
    main()