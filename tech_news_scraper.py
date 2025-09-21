#!/usr/bin/env python3
"""
Tech News Scraper - Múltiplas fontes de notícias de tecnologia
Faz scraping de várias fontes confiáveis de notícias tech
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse
import hashlib
import random

class TechNewsScraper:
    def __init__(self):
        self.cache_dir = Path(".cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "tech_news.json"
        self.session = requests.Session()
        
        # Headers para parecer um navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Fontes de notícias tech (RSS feeds e páginas)
        self.news_sources = {
            'TechCrunch': {
                'rss': 'https://techcrunch.com/feed/',
                'url': 'https://techcrunch.com/',
                'selectors': {
                    'title': 'h2.post-block__title a, h1.article__title, .post-title',
                    'link': 'h2.post-block__title a, h1.article__title a, .post-title a',
                    'description': '.post-block__content, .article-content p:first-of-type'
                }
            },
            'The Verge': {
                'rss': 'https://www.theverge.com/rss/index.xml',
                'url': 'https://www.theverge.com/tech',
                'selectors': {
                    'title': 'h2 a, h1 a, .c-entry-box--compact__title a',
                    'link': 'h2 a, h1 a, .c-entry-box--compact__title a',
                    'description': '.c-entry-summary, .c-entry-content p:first-of-type'
                }
            },
            'Ars Technica': {
                'rss': 'https://feeds.arstechnica.com/arstechnica/index',
                'url': 'https://arstechnica.com/',
                'selectors': {
                    'title': 'h2 a, h1 a, .listing-title a',
                    'link': 'h2 a, h1 a, .listing-title a',
                    'description': '.excerpt, .listing-excerpt'
                }
            },
            'Wired': {
                'url': 'https://www.wired.com/category/business/tech/',
                'selectors': {
                    'title': 'h3 a, h2 a, .card-component__title a',
                    'link': 'h3 a, h2 a, .card-component__title a',
                    'description': '.card-component__dek, .summary'
                }
            },
            'Engadget': {
                'rss': 'https://www.engadget.com/rss.xml',
                'url': 'https://www.engadget.com/',
                'selectors': {
                    'title': 'h2 a, h1 a, .o-hit__title a',
                    'link': 'h2 a, h1 a, .o-hit__title a',
                    'description': '.o-hit__description, .summary'
                }
            }
        }

    def get_tech_news(self, max_articles: int = 20) -> List[Dict]:
        """
        Obtém notícias de tecnologia de múltiplas fontes
        """
        print("🔍 Coletando notícias de tecnologia de múltiplas fontes...")
        
        # Tenta carregar do cache primeiro
        cached_news = self.load_cache()
        if cached_news and self.is_cache_fresh():
            print(f"📋 Usando {len(cached_news)} notícias do cache")
            return cached_news[:max_articles]
        
        all_articles = []
        
        # Coleta de cada fonte
        for source_name, source_config in self.news_sources.items():
            try:
                print(f"📰 Coletando de {source_name}...")
                articles = self.scrape_source(source_name, source_config)
                
                if articles:
                    all_articles.extend(articles)
                    print(f"✅ {len(articles)} artigos de {source_name}")
                else:
                    print(f"⚠️ Nenhum artigo encontrado em {source_name}")
                
                # Pausa entre requests
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Erro ao coletar de {source_name}: {e}")
                continue
        
        # Remove duplicatas e ordena por relevância
        unique_articles = self.remove_duplicates(all_articles)
        relevant_articles = [a for a in unique_articles if self.is_tech_relevant(a)]
        
        # Ordena por data (mais recentes primeiro)
        relevant_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        # Salva no cache
        if relevant_articles:
            self.save_cache(relevant_articles)
            print(f"💾 {len(relevant_articles)} artigos únicos salvos no cache")
        
        return relevant_articles[:max_articles]

    def scrape_source(self, source_name: str, config: Dict) -> List[Dict]:
        """
        Faz scraping de uma fonte específica
        """
        articles = []
        
        try:
            # Tenta RSS primeiro se disponível
            if 'rss' in config:
                articles = self.scrape_rss(source_name, config['rss'])
                if articles:
                    return articles
            
            # Fallback para scraping HTML
            if 'url' in config:
                articles = self.scrape_html(source_name, config)
            
        except Exception as e:
            print(f"⚠️ Erro no scraping de {source_name}: {e}")
        
        return articles

    def scrape_rss(self, source_name: str, rss_url: str) -> List[Dict]:
        """
        Faz scraping de feed RSS
        """
        try:
            response = self.session.get(rss_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            articles = []
            
            # Procura por items do RSS
            items = soup.find_all('item')[:10]  # Máximo 10 por fonte
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    desc_elem = item.find('description')
                    date_elem = item.find('pubDate')
                    
                    if not title_elem or not title_elem.text.strip():
                        continue
                    
                    title = title_elem.text.strip()
                    link = link_elem.text.strip() if link_elem else ""
                    description = desc_elem.text.strip() if desc_elem else ""
                    pub_date = date_elem.text.strip() if date_elem else datetime.now().isoformat()
                    
                    # Limpa HTML da descrição
                    if description:
                        desc_soup = BeautifulSoup(description, 'html.parser')
                        description = desc_soup.get_text(strip=True)[:300]
                    
                    article = {
                        'id': hashlib.md5(title.encode()).hexdigest()[:12],
                        'title': title,
                        'description': description,
                        'url': link,
                        'published_at': pub_date,
                        'source': source_name,
                        'keywords': self.extract_keywords(title),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️ Erro ao processar item RSS: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"⚠️ Erro no RSS de {source_name}: {e}")
            return []

    def scrape_html(self, source_name: str, config: Dict) -> List[Dict]:
        """
        Faz scraping HTML de uma página
        """
        try:
            response = self.session.get(config['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            selectors = config.get('selectors', {})
            title_selector = selectors.get('title', 'h2 a, h3 a')
            
            # Encontra elementos de título
            title_elements = soup.select(title_selector)[:15]  # Máximo 15 por fonte
            
            for elem in title_elements:
                try:
                    title = elem.get_text(strip=True)
                    if len(title) < 10 or len(title) > 200:
                        continue
                    
                    # Obtém link
                    link = elem.get('href', '')
                    if not link.startswith('http'):
                        link = urljoin(config['url'], link)
                    
                    # Tenta encontrar descrição próxima
                    description = ""
                    parent = elem.find_parent()
                    if parent:
                        desc_elem = parent.find('p') or parent.find(class_=re.compile(r'(summary|excerpt|description)'))
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)[:300]
                    
                    article = {
                        'id': hashlib.md5(title.encode()).hexdigest()[:12],
                        'title': title,
                        'description': description,
                        'url': link,
                        'published_at': datetime.now().isoformat(),
                        'source': source_name,
                        'keywords': self.extract_keywords(title),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"⚠️ Erro ao processar elemento HTML: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"⚠️ Erro no HTML scraping de {source_name}: {e}")
            return []

    def extract_keywords(self, title: str) -> List[str]:
        """
        Extrai palavras-chave relevantes do título
        """
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'blockchain', 'cryptocurrency', 'bitcoin', 'ethereum',
            'cloud', 'aws', 'azure', 'google cloud',
            'cybersecurity', 'security', 'privacy', 'data breach',
            'startup', 'funding', 'ipo', 'acquisition',
            'apple', 'google', 'microsoft', 'meta', 'amazon', 'tesla',
            'iphone', 'android', 'windows', 'linux',
            'software', 'hardware', 'chip', 'processor',
            'quantum', 'robotics', 'automation', 'iot',
            '5g', 'wifi', 'internet', 'web', 'mobile',
            'vr', 'ar', 'virtual reality', 'augmented reality'
        ]
        
        title_lower = title.lower()
        found_keywords = []
        
        for keyword in tech_keywords:
            if keyword in title_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5]

    def is_tech_relevant(self, article: Dict) -> bool:
        """
        Verifica se o artigo é relevante para tecnologia
        """
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        text = f"{title} {description}"
        
        # Palavras-chave que indicam relevância tech
        tech_indicators = [
            'technology', 'tech', 'ai', 'artificial intelligence', 'machine learning',
            'software', 'hardware', 'app', 'platform', 'digital', 'cyber',
            'data', 'cloud', 'startup', 'innovation', 'algorithm', 'code',
            'programming', 'development', 'computer', 'internet', 'web',
            'mobile', 'smartphone', 'tablet', 'laptop', 'chip', 'processor',
            'quantum', 'robotics', 'automation', 'iot', '5g', 'wifi'
        ]
        
        # Empresas de tech
        tech_companies = [
            'apple', 'google', 'microsoft', 'amazon', 'meta', 'facebook',
            'tesla', 'nvidia', 'intel', 'amd', 'openai', 'anthropic',
            'uber', 'airbnb', 'netflix', 'spotify', 'zoom', 'slack'
        ]
        
        # Verifica relevância
        has_tech_keyword = any(keyword in text for keyword in tech_indicators)
        has_tech_company = any(company in text for company in tech_companies)
        has_keywords = len(article.get('keywords', [])) > 0
        
        return has_tech_keyword or has_tech_company or has_keywords

    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        Remove artigos duplicados baseado no título
        """
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_clean = re.sub(r'[^\w\s]', '', article['title'].lower()).strip()
            title_hash = hashlib.md5(title_clean.encode()).hexdigest()
            
            if title_hash not in seen_titles:
                seen_titles.add(title_hash)
                unique_articles.append(article)
        
        return unique_articles

    def load_cache(self) -> Optional[List[Dict]]:
        """
        Carrega notícias do cache
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('articles', [])
        except Exception as e:
            print(f"⚠️ Erro ao carregar cache: {e}")
        return None

    def save_cache(self, articles: List[Dict]):
        """
        Salva notícias no cache
        """
        try:
            cache_data = {
                'articles': articles,
                'cached_at': datetime.now().isoformat(),
                'source': 'multiple_tech_sources'
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")

    def is_cache_fresh(self, max_age_hours: int = 2) -> bool:
        """
        Verifica se o cache ainda está fresco
        """
        try:
            if not self.cache_file.exists():
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cached_at = datetime.fromisoformat(data.get('cached_at', ''))
                age = datetime.now() - cached_at
                return age.total_seconds() < (max_age_hours * 3600)
                
        except Exception:
            return False

    def get_article_content(self, url: str) -> Optional[str]:
        """
        Obtém conteúdo completo de um artigo
        """
        try:
            if not url or not url.startswith('http'):
                return None
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove elementos desnecessários
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()
            
            # Procura pelo conteúdo principal
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '[role="main"]',
                '.story-body'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # Se não encontrou, pega parágrafos do body
            if not content:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs[:10]])
            
            # Limpa o conteúdo
            if content:
                lines = [line.strip() for line in content.split('\n') if len(line.strip()) > 20]
                content = '\n'.join(lines)
                
                # Limita o tamanho
                if len(content) > 3000:
                    content = content[:3000] + "..."
            
            return content if len(content) > 100 else None
            
        except Exception as e:
            print(f"⚠️ Erro ao obter conteúdo do artigo {url}: {e}")
            return None


def main():
    """
    Função principal para testar o scraper
    """
    scraper = TechNewsScraper()
    
    print("🚀 Testando Tech News Scraper...")
    articles = scraper.get_tech_news(max_articles=15)
    
    if articles:
        print(f"\n✅ {len(articles)} artigos encontrados:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Fonte: {article['source']}")
            print(f"   URL: {article['url']}")
            print(f"   Keywords: {', '.join(article['keywords'])}")
            if article['description']:
                print(f"   Descrição: {article['description'][:100]}...")
    else:
        print("❌ Nenhum artigo encontrado")


if __name__ == "__main__":
    main()