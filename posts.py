import os
import sys
import re
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import google.generativeai as genai

# --- Configurações ---
POSTS_DIR = Path("content/posts")

# --- Temas Estáticos (Fallback) ---
STATIC_TOPICS = [
    "10 truques de produtividade que os CEOs não querem que você saiba",
    "Como ganhar dinheiro dormindo: a verdade sobre renda passiva",
    "Por que 90% das pessoas falham em seus objetivos (e como evitar isso)",
    "O segredo obscuro da automação que está mudando carreiras",
    "Como transformar seu hobby em uma máquina de renda online",
]

def call_gemini_api(prompt: str) -> str:
    """
    Chama a API do Gemini e retorna a resposta em texto.
    Lança exceções em caso de erro.
    """
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    return response.text

def get_dynamic_topics() -> list[str]:
    """
    Usa a API do Gemini para gerar uma lista de temas em alta.
    Retorna uma lista de strings ou uma lista vazia em caso de falha.
    """
    print("Buscando temas em alta com a API do Gemini...")
    prompt = (
        "Liste 10 títulos de artigos de blog que estão em alta no Brasil, com um estilo 'clickbait' atraente. "
        "Os temas devem ser sobre tecnologia, produtividade, inovação e carreira. "
        "Responda APENAS com a lista numerada. Não adicione introdução, conclusão ou qualquer outro texto."
    )
    try:
        response_text = call_gemini_api(prompt)
        # Extrai os tópicos da saída, removendo números e limpando espaços
        topics = re.findall(r'^\s*\d+\.\s*(.*)', response_text, re.MULTILINE)
        
        if topics:
            print("✅ Temas encontrados!")
            return [topic.strip() for topic in topics]
        else:
            print("⚠️  Não foi possível extrair os temas da resposta da API.")
            return []
    except Exception as e:
        print(f"⚠️  Erro ao buscar temas dinâmicos: {e}")
        return []

def main():
    """
    Script principal para gerar um post de blog com Hugo e Gemini.
    """
    # --- Carrega variáveis de ambiente e configura a API ---
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERRO: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
        print("Certifique-se de que o arquivo .env está na raiz do projeto e contém sua chave.")
        sys.exit(1)
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"❌ ERRO ao configurar a API do Gemini: {e}")
        sys.exit(1)

    POSTS_DIR.mkdir(exist_ok=True)

    topics = get_dynamic_topics()
    if not topics:
        print("Usando lista de temas estática como fallback.")
        topics = STATIC_TOPICS

    print("\n--- Escolha um tema para o post ---\n")
    for i, title in enumerate(topics):
        print(f"  {i + 1}: {title}")
    
    selected_index = -1
    while True:
        try:
            choice = input(f"\nDigite o número do tema (1-{len(topics)}): ")
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(topics):
                break
            else:
                print(f"❌ Escolha inválida. Por favor, digite um número entre 1 e {len(topics)}.")
        except ValueError:
            print("❌ Entrada inválida. Por favor, digite um número.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperação cancelada.")
            sys.exit(1)
            
    selected_title = topics[selected_index]
    print(f'\nTema escolhido: "{selected_title}"\n')

    # --- Confirmação do usuário ---
    try:
        confirm = input("Deseja gerar um post com este tema? (S/N) ").strip().upper()
        if confirm != 'S':
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperação cancelada.")
        sys.exit(1)

    print("\nGerando o artigo com a API do Gemini...")
    
    # --- Prompt para o Gemini (geração do artigo) ---
    article_prompt = (
        f"Escreva um artigo de blog com aproximadamente 600 palavras sobre o tema '{selected_title}'. "
        "O artigo deve ter um tom envolvente e provocativo, típico de conteúdo 'clickbait', mas com informações úteis e acionáveis. "
        "Estruture o conteúdo da seguinte forma: uma introdução cativante que fisgue o leitor; "
        "pelo menos 3 subtítulos claros usando markdown (##); "
        "uso de listas (bullet points) para facilitar a leitura; "
        "exemplos práticos ou cenários hipotéticos para ilustrar os pontos; "
        "e uma conclusão forte e inspiradora que incentive o leitor a agir. "
        "Importante: Não inclua o título principal no corpo do artigo, pois ele será adicionado ao frontmatter do Hugo."
    )

    try:
        article_content = call_gemini_api(article_prompt)

        # --- Data e Hora ---
        now = datetime.now()
        tz_offset = timezone(timedelta(hours=-3)) # Fuso horário de Brasília
        iso_timestamp = now.astimezone(tz_offset).isoformat()
        current_date_str = now.strftime("%Y-%m-%d")

        # --- Nome do arquivo final ---
        filename = POSTS_DIR / f"post-{current_date_str}-{random.randint(1000, 9999)}.md"

        # --- Cria o post com o frontmatter do Hugo ---
        escaped_title = selected_title.replace('"', '\"')
        frontmatter = f"""
---
title: \"{escaped_title}\"
date: {iso_timestamp}
draft: false
---

"""

        filename.write_text(frontmatter + article_content, encoding="utf-8")

        print(f"\n✅ Post criado com sucesso em: {filename}")
        print("\nPara visualizar, rode: hugo server -D")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado ao gerar o artigo: {e}")

if __name__ == "__main__":
    main()
    try:
        input("\nPressione Enter para sair...")
    except (KeyboardInterrupt, EOFError):
        print()