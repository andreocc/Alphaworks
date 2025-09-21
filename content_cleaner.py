"""
Módulo para limpeza e correção de conteúdo mal formatado.
"""

import re
from typing import List

def clean_content_completely(content: str) -> str:
    """Remove completamente problemas de formatação e melhora a estrutura."""
    
    # Remove transições problemáticas
    problematic_phrases = [
        r'Para compreender o impacto completo.*?é necessário analisar:',
        r'Os dados revelam aspectos importantes:',
        r'A análise técnica mostra que:',
        r'Aqui é onde as coisas ficam interessantes:',
        r'E aqui está o plot twist:',
        r'Mas isso é apenas o começo da história',
    ]
    
    for phrase in problematic_phrases:
        content = re.sub(phrase, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove separadores excessivos
    content = re.sub(r'\n---\n+', '\n\n', content)
    content = re.sub(r'---\n+---', '', content)
    
    # Limpa títulos problemáticos
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove linhas vazias excessivas
        if not line.strip():
            if not cleaned_lines or cleaned_lines[-1].strip():
                cleaned_lines.append('')
            continue
        
        # Corrige títulos
        if line.startswith('## '):
            # Remove emojis e caracteres especiais
            clean_title = re.sub(r'[🔍⚙️🛡️⚡🚀🏗️🏢💻🔄☁️📊🔌📱🌐🤖🧠⛓️🎯➡️📚📋⚠️💡✅❌]', '', line)
            clean_title = re.sub(r'## +', '## ', clean_title).strip()
            
            # Se muito longo, mantém mas limita a 100 caracteres
            if len(clean_title) > 100:
                words = clean_title[3:].split()[:10]  # Mais palavras
                clean_title = '## ' + ' '.join(words)
            
            # Se válido, adiciona
            if len(clean_title) > 5 and not re.match(r'## [^a-zA-Z]*$', clean_title):
                cleaned_lines.append(clean_title)
        
        # Remove linhas que são só símbolos
        elif re.match(r'^[🔍⚙️🛡️⚡🚀🏗️🏢💻🔄☁️📊🔌📱🌐🤖🧠⛓️🎯➡️📚📋⚠️💡✅❌\s\-#]+$', line):
            continue
        
        # Remove linhas problemáticas específicas
        elif any(problem in line for problem in ['dicam', 'DebuCg', '> **💡', '> **⚠️']):
            continue
            
        else:
            cleaned_lines.append(line)
    
    # Reconstrói o conteúdo
    content = '\n'.join(cleaned_lines)
    
    # Remove espaços múltiplos
    content = re.sub(r' +', ' ', content)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    return content.strip()


def create_simple_structure(content: str, title: str) -> str:
    """Cria uma estrutura simples e limpa para o artigo."""
    
    # Extrai parágrafos válidos
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
    
    if not paragraphs:
        return content
    
    # Estrutura simples
    structured_content = []
    
    # Primeiro parágrafo como introdução
    if paragraphs:
        structured_content.append(paragraphs[0])
        structured_content.append('')
    
    # Agrupa parágrafos restantes em seções
    remaining_paragraphs = paragraphs[1:]
    
    if len(remaining_paragraphs) >= 2:
        structured_content.append('## Detalhes')
        structured_content.append('')
        for i, para in enumerate(remaining_paragraphs[:3]):
            structured_content.append(para)
            if i < 2:
                structured_content.append('')
    
    if len(remaining_paragraphs) >= 4:
        structured_content.append('')
        structured_content.append('## Impacto')
        structured_content.append('')
        for para in remaining_paragraphs[3:5]:
            structured_content.append(para)
            structured_content.append('')
    
    if len(remaining_paragraphs) >= 6:
        structured_content.append('## Conclusão')
        structured_content.append('')
        structured_content.append(remaining_paragraphs[-1])
    
    return '\n'.join(structured_content)