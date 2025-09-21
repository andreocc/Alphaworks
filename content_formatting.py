#!/usr/bin/env python3
"""
Módulo para formatação avançada de conteúdo e melhoria de layout
"""

import re
from typing import List, Dict

class ContentFormatter:
    """Classe para formatação avançada de artigos."""
    
    def __init__(self):
        self.emoji_map = {
            "resumo": "📋",
            "análise": "🔍", 
            "técnica": "⚙️",
            "performance": "📊",
            "security": "🔒",
            "devops": "🚀",
            "infrastructure": "🏗️",
            "implementation": "💻",
            "conclusão": "✅",
            "próximos": "🎯",
            "importante": "⚠️",
            "dica": "💡",
            "exemplo": "📝",
            "código": "```",
            "lista": "•",
            "vantagem": "✅",
            "desvantagem": "❌"
        }
    
    def add_visual_elements(self, content: str) -> str:
        """Adiciona elementos visuais ao conteúdo."""
        
        # Adiciona emojis aos títulos baseado no conteúdo
        for keyword, emoji in self.emoji_map.items():
            pattern = rf"(##\s+)([^#\n]*{keyword}[^#\n]*)"
            replacement = rf"\1{emoji} \2"
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def add_callout_boxes(self, content: str) -> str:
        """Adiciona caixas de destaque para informações importantes."""
        
        # Identifica parágrafos importantes
        important_patterns = [
            r"(É importante notar que.*?\.)",
            r"(Vale destacar que.*?\.)",
            r"(Atenção:.*?\.)",
            r"(Importante:.*?\.)",
            r"(Cuidado:.*?\.)"
        ]
        
        for pattern in important_patterns:
            content = re.sub(
                pattern,
                r"> **💡 Destaque:** \1",
                content,
                flags=re.IGNORECASE | re.DOTALL
            )
        
        return content
    
    def add_code_blocks(self, content: str) -> str:
        """Adiciona blocos de código quando apropriado."""
        
        # Identifica menções a comandos ou código
        code_patterns = [
            (r"comando `([^`]+)`", r"```bash\n\1\n```"),
            (r"código `([^`]+)`", r"```\n\1\n```"),
            (r"script `([^`]+)`", r"```python\n\1\n```"),
            (r"configuração `([^`]+)`", r"```yaml\n\1\n```")
        ]
        
        for pattern, replacement in code_patterns:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def add_tables(self, content: str) -> str:
        """Adiciona tabelas quando há comparações."""
        
        # Procura por comparações e transforma em tabelas
        comparison_pattern = r"(\w+):\s*([^\.]+)\.\s*(\w+):\s*([^\.]+)\."
        
        def replace_with_table(match):
            item1, desc1, item2, desc2 = match.groups()
            return f"""
| Aspecto | {item1} | {item2} |
|---------|---------|---------|
| Características | {desc1} | {desc2} |
"""
        
        content = re.sub(comparison_pattern, replace_with_table, content)
        
        return content
    
    def add_lists_and_bullets(self, content: str) -> str:
        """Melhora formatação de listas."""
        
        # Transforma frases com "incluem" em listas
        list_patterns = [
            (r"incluem:?\s*([^\.]+)\.", self._convert_to_list),
            (r"são:?\s*([^\.]+)\.", self._convert_to_list),
            (r"principais.*?:?\s*([^\.]+)\.", self._convert_to_list)
        ]
        
        for pattern, converter in list_patterns:
            content = re.sub(pattern, converter, content, flags=re.IGNORECASE)
        
        return content
    
    def _convert_to_list(self, match):
        """Converte texto em lista formatada."""
        items_text = match.group(1)
        items = [item.strip() for item in re.split(r'[,;]', items_text) if item.strip()]
        
        if len(items) > 2:
            formatted_list = "\n\n"
            for item in items:
                formatted_list += f"- **{item.strip()}**\n"
            formatted_list += "\n"
            return formatted_list
        
        return match.group(0)  # Retorna original se não for lista válida
    
    def add_section_summaries(self, content: str) -> str:
        """Adiciona resumos no início de seções longas."""
        
        sections = content.split('\n## ')
        formatted_sections = []
        
        for i, section in enumerate(sections):
            if i == 0:  # Primeira seção (antes do primeiro ##)
                formatted_sections.append(section)
                continue
            
            lines = section.split('\n')
            section_title = lines[0] if lines else ""
            section_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            # Se a seção é muito longa, adiciona resumo
            if len(section_content) > 800:
                # Extrai primeira frase como resumo
                first_sentence = section_content.split('.')[0] + '.'
                summary = f"\n> **📋 Resumo:** {first_sentence}\n"
                section_content = summary + section_content
            
            formatted_sections.append(f"## {section_title}\n{section_content}")
        
        return '\n'.join(formatted_sections)
    
    def add_reading_aids(self, content: str) -> str:
        """Adiciona elementos que facilitam a leitura."""
        
        # Adiciona separadores visuais
        content = content.replace('\n\n## ', '\n\n---\n\n## ')
        
        # Adiciona ícones para diferentes tipos de informação
        content = re.sub(r'\*\*(Vantagem|Benefício|Prós?):\*\*', r'✅ **\1:**', content, flags=re.IGNORECASE)
        content = re.sub(r'\*\*(Desvantagem|Problema|Contras?):\*\*', r'❌ **\1:**', content, flags=re.IGNORECASE)
        content = re.sub(r'\*\*(Dica|Sugestão):\*\*', r'💡 **\1:**', content, flags=re.IGNORECASE)
        content = re.sub(r'\*\*(Atenção|Cuidado|Importante):\*\*', r'⚠️ **\1:**', content, flags=re.IGNORECASE)
        
        return content
    
    def format_article(self, content: str) -> str:
        """Aplica todas as formatações ao artigo."""
        
        print("🎨 Aplicando formatação avançada...")
        
        # Aplica todas as melhorias
        content = self.add_visual_elements(content)
        content = self.add_callout_boxes(content)
        content = self.add_code_blocks(content)
        content = self.add_tables(content)
        content = self.add_lists_and_bullets(content)
        content = self.add_section_summaries(content)
        content = self.add_reading_aids(content)
        
        # Adiciona espaçamento adequado
        content = re.sub(r'\n{3,}', '\n\n', content)  # Remove espaços excessivos
        content = re.sub(r'(\n## )', r'\n\n\1', content)  # Espaço antes de seções
        
        print("✅ Formatação aplicada com sucesso")
        return content

# Instância global
formatter = ContentFormatter()

def format_content(content: str) -> str:
    """Função helper para formatação de conteúdo."""
    return formatter.format_article(content)