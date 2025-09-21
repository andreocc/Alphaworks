#!/usr/bin/env python3
"""
Utilitários para o AutoPost - gerenciamento de cache e estatísticas
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

CACHE_DIR = Path(".cache")
TOPICS_CACHE = CACHE_DIR / "topics_cache.json"
POSTS_DIR = Path("content/posts")

def load_cache() -> Dict:
    """Carrega o cache de tópicos."""
    if TOPICS_CACHE.exists():
        try:
            with open(TOPICS_CACHE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"used_topics": [], "last_update": ""}
    return {"used_topics": [], "last_update": ""}

def show_cache_stats():
    """Mostra estatísticas do cache."""
    cache_data = load_cache()
    used_topics = cache_data.get("used_topics", [])
    last_update = cache_data.get("last_update", "")
    
    print("📊 Estatísticas do Cache")
    print("=" * 40)
    print(f"Tópicos em cache: {len(used_topics)}")
    print(f"Última atualização: {last_update}")
    
    if used_topics:
        print("\n📝 Últimos 10 tópicos:")
        for i, topic in enumerate(used_topics[-10:], 1):
            print(f"  {i:2d}. {topic}")

def clear_cache():
    """Limpa o cache de tópicos."""
    if TOPICS_CACHE.exists():
        TOPICS_CACHE.unlink()
        print("✅ Cache limpo com sucesso!")
    else:
        print("ℹ️ Cache já estava vazio.")

def show_posts_stats():
    """Mostra estatísticas dos posts gerados."""
    if not POSTS_DIR.exists():
        print("❌ Diretório de posts não encontrado.")
        return
    
    posts = list(POSTS_DIR.glob("*.md"))
    
    print("📈 Estatísticas dos Posts")
    print("=" * 40)
    print(f"Total de posts: {len(posts)}")
    
    if posts:
        # Posts por mês
        monthly_counts = {}
        for post in posts:
            try:
                date_str = post.name[:10]  # YYYY-MM-DD
                month = date_str[:7]  # YYYY-MM
                monthly_counts[month] = monthly_counts.get(month, 0) + 1
            except:
                continue
        
        print("\n📅 Posts por mês:")
        for month in sorted(monthly_counts.keys(), reverse=True)[:6]:
            print(f"  {month}: {monthly_counts[month]} posts")
        
        # Post mais recente
        latest_post = max(posts, key=lambda p: p.stat().st_mtime)
        mod_time = datetime.fromtimestamp(latest_post.stat().st_mtime)
        print(f"\n📄 Post mais recente: {latest_post.name}")
        print(f"   Modificado em: {mod_time.strftime('%d/%m/%Y %H:%M')}")

def cleanup_old_cache(days: int = 30):
    """Remove entradas antigas do cache."""
    cache_data = load_cache()
    
    if not cache_data.get("last_update"):
        print("ℹ️ Cache vazio, nada para limpar.")
        return
    
    try:
        last_update = datetime.fromisoformat(cache_data["last_update"])
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if last_update < cutoff_date:
            clear_cache()
            print(f"✅ Cache antigo (>{days} dias) removido.")
        else:
            print(f"ℹ️ Cache ainda é recente (<{days} dias).")
    except:
        print("⚠️ Erro ao verificar data do cache, limpando...")
        clear_cache()

def test_news_integration():
    """Testa a integração com APIs de notícias."""
    try:
        from news_api_improved import get_current_news, get_news_context
        
        print("🧪 Testando integração de notícias...")
        
        # Testa obtenção de notícias
        news = get_current_news("technology")
        print(f"📰 {len(news)} notícias obtidas")
        
        if news:
            print("\n📋 Últimas notícias:")
            for i, article in enumerate(news[:3], 1):
                print(f"{i}. {article['title']}")
                print(f"   Fonte: {article['source']}")
                print(f"   Palavras-chave: {', '.join(article.get('keywords', []))}")
                print()
            
            # Testa contexto de notícia
            test_keywords = ["IA", "startup", "tecnologia"]
            context = get_news_context(test_keywords)
            
            if context:
                print(f"🎯 Contexto encontrado para {test_keywords}:")
                print(f"   {context['title'][:60]}...")
                print(f"   Fonte: {context['source']}")
            else:
                print("⚠️ Nenhum contexto específico encontrado")
        else:
            print("❌ Nenhuma notícia obtida")
            
    except ImportError:
        print("❌ Módulo news_api não encontrado")
    except Exception as e:
        print(f"❌ Erro ao testar notícias: {e}")

def main():
    """Interface de linha de comando para utilitários."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python utils.py [comando]")
        print("\nComandos disponíveis:")
        print("  stats     - Mostra estatísticas do cache e posts")
        print("  clear     - Limpa o cache de tópicos")
        print("  cleanup   - Remove cache antigo (>30 dias)")
        print("  cache     - Mostra apenas estatísticas do cache")
        print("  posts     - Mostra apenas estatísticas dos posts")
        print("  news      - Testa integração com APIs de notícias")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_cache_stats()
        print()
        show_posts_stats()
    elif command == "clear":
        clear_cache()
    elif command == "cleanup":
        cleanup_old_cache()
    elif command == "cache":
        show_cache_stats()
    elif command == "posts":
        show_posts_stats()
    elif command == "news":
        test_news_integration()
    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main()