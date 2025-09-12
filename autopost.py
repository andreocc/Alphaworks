import os
import sys
import re
import random
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone, timedelta
import subprocess
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configurações ---
POSTS_DIR = Path("content/posts")

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

def call_gemini_api(prompt: str, safety_settings=None) -> str:
    """
    Chama a API do Gemini com um prompt e configurações de segurança opcionais.
    Retorna a resposta em texto ou lança uma exceção em caso de erro.
    """
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    response = model.generate_content(prompt, safety_settings=safety_settings)
    return response.text

def generate_new_topic() -> str:
    """Usa a IA para gerar um novo tópico de post."""
    print("🧠 Gerando um novo tópico de notícia...")
    current_year = datetime.now().year
    prompt = (
        f"Estamos em {current_year}. Gere um título para um post de blog sobre um tópico de tecnologia que seja notícia ou uma tendência QUENTE e ATUAL. "
        "O tópico deve ser relevante para o público brasileiro neste ano. "
        "O estilo deve ser informativo e interessante, como nos portais Tecmundo e Meiobit. "
        "Evite tópicos que eram populares no ano passado. "
        "Retorne APENAS o título, sem aspas ou qualquer outro texto."
    )
    try:
        topic = call_gemini_api(prompt).strip()
        if topic:
            print(f"✅ Tópico gerado: {topic}")
            return topic
        else:
            print("❌ A IA não retornou um tópico válido.")
            return ""
    except Exception as e:
        print(f"❌ Erro ao gerar novo tópico com a IA: {e}")
        return ""

def write_article(title: str) -> str:
    """Gera o conteúdo do artigo com base no título."""
    print(f'✍️ Escrevendo artigo sobre: "{title}"...')
    prompt = (
        f"Escreva um artigo de blog informativo e bem pesquisado com cerca de 700 palavras sobre o tema: '{title}'. "
        "O tom deve ser jornalístico e analítico, no estilo de um grande portal de tecnologia como Tecmundo ou Meiobit. "
        "Estruture o artigo com uma introdução clara, vários subtítulos (usando markdown ##) para organizar as ideias, "
        "e uma conclusão que resuma os pontos principais. Garanta que o conteúdo seja factual, detalhado e agregue valor ao leitor."
    )
    try:
        # Configurações de segurança mais permissivas para evitar bloqueios por temas de "notícia"
        safety_settings = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
        article = call_gemini_api(prompt, safety_settings=safety_settings)
        if article:
            print("✅ Artigo gerado com sucesso.")
            return article
        else:
            print("❌ A IA não retornou um artigo válido.")
            return ""
    except Exception as e:
        print(f"❌ Erro ao gerar o artigo com a IA: {e}")
        return ""

def create_hugo_post(title: str, content: str) -> Optional[Path]:
    """Cria e salva o arquivo .md para o Hugo."""
    print("📝 Formatando e salvando o post para o Hugo...")
    try:
        now = datetime.now()
        tz_offset = timezone(timedelta(hours=-3)) # Fuso horário de Brasília
        iso_timestamp = now.astimezone(tz_offset).isoformat()
        # Limpa o título para usar no nome do arquivo
        slug = re.sub(r'[^\w\s-]', '', title.lower()).strip()
        slug = re.sub(r'[\s_]+', '-', slug)
        filename = POSTS_DIR / f"{now.strftime('%Y-%m-%d')}-{slug[:50]}.md"

        escaped_title = title.replace('"', '\"')
        frontmatter = f"""
---
title: \"{escaped_title}\"\ndate: {iso_timestamp}\ndraft: false
---

"""

        filename.write_text(frontmatter + content, encoding="utf-8")
        print(f"✅ Post salvo em: {filename}")
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

def main():
    """Função principal que orquestra todo o processo."""
    if not setup_api():
        sys.exit(1)

    topic = generate_new_topic()
    if not topic:
        sys.exit(1)

    article = write_article(topic)
    if not article:
        sys.exit(1)

    post_path = create_hugo_post(topic, article)
    if not post_path:
        sys.exit(1)

    commit_new_post(post_path, topic)

    print("\n✨ Processo de autopublicação concluído! ✨")

if __name__ == "__main__":
    main()
