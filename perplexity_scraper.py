#!/usr/bin/env python3
"""
Perplexity AI Tech News Scraper
Faz scraping das notícias de tecnologia do Perplexity AI Discover
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

class PerplexityTechScraper:
    def __init__(self):
        self.base_url = "https://www.perplexity.ai"
        self.tech_url = "https://www.perplexity.ai/discover/tech"
        self.cache_dir = Path(".cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "perplexity_news.json"
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

    def get_tech_news(self, max_articles: int = 20) -> List[Dict]:
        """
        Faz scraping das notícias de tecnologia do Perplexity AI
        """
        print("🔍 Fazendo scraping do Perplexity AI Tech...")
        
        try:
            # Primeiro, tenta carregar do cache se for recente
            cached_news = self.load_cache()
            if cached_news and self.is_cache_fresh():
                print(f"📋 Usando {len(cached_news)} notícias do cache")
                return cached_news[:max_articles]
            
            # Faz o scraping da página principal
            response = self.session.get(self.tech_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # Procura por diferentes padrões de artigos na página
            article_selectors = [
                'article',
                '[data-testid*="article"]',
                '.article',
                '.news-item',
                '.story',
                '.post',
                'div[class*="article"]',
                'div[class*="story"]',
                'div[class*="news"]'
            ]
            
            found_articles = []
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    found_articles.extend(elements)
                    print(f"✅ Encontrados {len(elements)} elementos com seletor: {selector}")
            
            # Se não encontrou com seletores específicos, procura por links e títulos
            if not found_articles:
                print("🔍 Tentando abordagem alternativa...")
                # Procura por links que parecem ser artigos
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Filtra links que parecem ser artigos de tech
                    if (len(text) > 20 and 
                        any(word in text.lower() for word in ['tech', 'ai', 'software', 'data', 'cloud', 'cyber', 'digital']) and
                        not any(skip in href.lower() for skip in ['login', 'signup', 'profile', 'settings'])):
                        found_articles.append(link)
            
            print(f"📰 Total de elementos encontrados: {len(found_articles)}")
            
            # Processa cada artigo encontrado
            for i, element in enumerate(found_articles[:max_articles * 2]):  # Pega mais para filtrar
                try:
                    article_data = self.extract_article_data(element, soup)
                    if article_data and self.is_tech_relevant(article_data):
                        articles.append(article_data)
                        print(f"✅ Artigo {len(articles)}: {article_data['title'][:60]}...")
                        
                        if len(articles) >= max_articles:
                            break
                            
                except Exception as e:
                    print(f"⚠️ Erro ao processar artigo {i}: {e}")
                    continue
            
            # Se ainda não tem artigos suficientes, tenta uma abordagem mais ampla
            if len(articles) < 5:
                print("🔍 Tentando extração mais ampla...")
                articles.extend(self.fallback_extraction(soup, max_articles - len(articles)))
            
            # Salva no cache
            if articles:
                self.save_cache(articles)
                print(f"💾 {len(articles)} artigos salvos no cache")
            
            return articles
            
        except requests.RequestException as e:
            print(f"❌ Erro de rede ao acessar Perplexity: {e}")
            # Tenta usar cache antigo se disponível
            cached_news = self.load_cache()
            if cached_news:
                print("📋 Usando cache antigo como fallback")
                return cached_news[:max_articles]
            return []
            
        except Exception as e:
            print(f"❌ Erro inesperado no scraping: {e}")
            return []

    def extract_article_data(self, element, soup) -> Optional[Dict]:
        """
        Extrai dados de um elemento de artigo
        """
        try:
            # Tenta extrair título
            title = ""
            title_selectors = ['h1', 'h2', 'h3', '.title', '[class*="title"]', '[class*="headline"]']
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Se não encontrou título no elemento, usa o próprio texto
            if not title:
                title = element.get_text(strip=True)
            
            # Limpa e valida título
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) < 10 or len(title) > 200:
                return None
            
            # Tenta extrair link
            link = ""
            if element.name == 'a':
                link = element.get('href', '')
            else:
                link_elem = element.find('a', href=True)
                if link_elem:
                    link = link_elem.get('href', '')
            
            # Converte link relativo para absoluto
            if link and not link.startswith('http'):
                link = urljoin(self.base_url, link)
            
            # Tenta extrair descrição/resumo
            description = ""
            desc_selectors = ['.description', '.summary', '.excerpt', 'p', '.content']
            
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    desc_text = desc_elem.get_text(strip=True)
                    if len(desc_text) > 20 and desc_text != title:
                        description = desc_text[:300]
                        break
            
            # Tenta extrair data
            published_at = self.extract_date(element)
            
            # Gera ID único baseado no título
            article_id = hashlib.md5(title.encode()).hexdigest()[:12]
            
            # Extrai palavras-chave do título
            keywords = self.extract_keywords(title)
            
            return {
                'id': article_id,
                'title': title,
                'description': description,
                'url': link,
                'published_at': published_at,
                'source': 'Perplexity AI',
                'keywords': keywords,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair dados do artigo: {e}")
            return None

    def extract_date(self, element) -> str:
        """
        Tenta extrair data de publicação do elemento
        """
        try:
            # Procura por elementos com data
            date_selectors = [
                'time',
                '[datetime]',
                '.date',
                '.published',
                '[class*="date"]',
                '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_elem = element.select_one(selector)
                if date_elem:
                    # Tenta pegar do atributo datetime
                    datetime_attr = date_elem.get('datetime')
                    if datetime_attr:
                        return datetime_attr
                    
                    # Tenta pegar do texto
                    date_text = date_elem.get_text(strip=True)
                    if date_text:
                        return date_text
            
            # Se não encontrou, usa data atual
            return datetime.now().isoformat()
            
        except:
            return datetime.now().isoformat()

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
            'quantum', 'robotics', 'automation', 'iot'
        ]
        
        title_lower = title.lower()
        found_keywords = []
        
        for keyword in tech_keywords:
            if keyword in title_lower:
                found_keywords.append(keyword)
        
        return found_keywords[:5]  # Máximo 5 keywords

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
            'mobile', 'smartphone', 'tablet', 'laptop', 'chip', 'processor'
        ]
        
        # Empresas de tech
        tech_companies = [
            'apple', 'google', 'microsoft', 'amazon', 'meta', 'facebook',
            'tesla', 'nvidia', 'intel', 'amd', 'openai', 'anthropic'
        ]
        
        # Verifica se tem pelo menos uma palavra-chave relevante
        has_tech_keyword = any(keyword in text for keyword in tech_indicators)
        has_tech_company = any(company in text for company in tech_companies)
        
        return has_tech_keyword or has_tech_company

    def fallback_extraction(self, soup, max_articles: int) -> List[Dict]:
        """
        Método de fallback para extrair artigos quando os seletores principais falham
        """
        articles = []
        
        try:
            # Procura por todos os links na página
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                if len(articles) >= max_articles:
                    break
                
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Filtra links que parecem ser títulos de artigos
                if (len(text) > 15 and len(text) < 150 and
                    not any(skip in href.lower() for skip in ['login', 'signup', 'profile', 'settings', 'about']) and
                    not text.lower().startswith(('click', 'read more', 'see more', 'learn more'))):
                    
                    # Cria artigo básico
                    article = {
                        'id': hashlib.md5(text.encode()).hexdigest()[:12],
                        'title': text,
                        'description': '',
                        'url': urljoin(self.base_url, href) if not href.startswith('http') else href,
                        'published_at': datetime.now().isoformat(),
                        'source': 'Perplexity AI',
                        'keywords': self.extract_keywords(text),
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    if self.is_tech_relevant(article):
                        articles.append(article)
                        print(f"📰 Fallback - Artigo: {text[:50]}...")
            
        except Exception as e:
            print(f"⚠️ Erro no fallback extraction: {e}")
        
        return articles

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
                'source': 'perplexity_ai_tech'
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
        Faz scraping do conteúdo completo de um artigo
        """
        try:
            if not url or not url.startswith('http'):
                return None
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove elementos desnecessários
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Procura pelo conteúdo principal
            content_selectors = [
                'article',
                '.content',
                '.article-content',
                '.post-content',
                '.entry-content',
                'main',
                '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # Se não encontrou, pega o body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator='\n', strip=True)
            
            # Limpa o conteúdo
            if content:
                # Remove linhas muito curtas e vazias
                lines = [line.strip() for line in content.split('\n') if len(line.strip()) > 10]
                content = '\n'.join(lines)
                
                # Limita o tamanho
                if len(content) > 5000:
                    content = content[:5000] + "..."
            
            return content if len(content) > 100 else None
            
        except Exception as e:
            print(f"⚠️ Erro ao obter conteúdo do artigo {url}: {e}")
            return None


def main():
    """
    Função principal para testar o scraper
    """
    scraper = PerplexityTechScraper()
    
    print("🚀 Testando Perplexity AI Tech Scraper...")
    articles = scraper.get_tech_news(max_articles=10)
    
    if articles:
        print(f"\n✅ {len(articles)} artigos encontrados:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   URL: {article['url']}")
            print(f"   Keywords: {', '.join(article['keywords'])}")
            if article['description']:
                print(f"   Descrição: {article['description'][:100]}...")
    else:
        print("❌ Nenhum artigo encontrado")


if __name__ == "__main__":
    main()