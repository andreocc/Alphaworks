@echo off
setlocal enabledelayedexpansion

REM === Configurações e Diretórios ===
set "POSTS_DIR=content\posts"
set "TEMP_FILE=temp_post_content.txt"

REM === Garante que o diretório de posts exista ===
if not exist "%POSTS_DIR%\" mkdir "%POSTS_DIR%"

REM === Data e Hora ===
REM Pega a data de forma robusta, independente da localidade
for /f "tokens=1-3 delims=/-" %%a in ("%date%") do (
    set "YYYY=%%c"
    set "MM=%%b"
    set "DD=%%a"
)
set "CURRENT_DATE=%YYYY%-%MM%-%DD%"
set "ISO_TIMESTAMP=%CURRENT_DATE%T12:00:00-03:00"

REM === Lista de temas clickbait ===
set "TOPICS[0]=10 truques de produtividade que os CEOs não querem que você saiba"
set "TOPICS[1]=Como ganhar dinheiro dormindo: a verdade sobre renda passiva"
set "TOPICS[2]=Por que 90%% das pessoas falham em seus objetivos (e como evitar isso)"
set "TOPICS[3]=O segredo obscuro da automação que está mudando carreiras"
set "TOPICS[4]=Como transformar seu hobby em uma máquina de renda online"
set "TOPICS[5]=Você está usando IA errado: descubra a forma certa"
set "TOPICS[6]=3 passos simples para dobrar sua criatividade em uma semana"
set "TOPICS[7]=O mito do equilíbrio entre vida e trabalho: a verdade chocante"
set "TOPICS[8]=Ferramentas gratuitas que podem substituir softwares caros"
set "TOPICS[9]=O futuro do trabalho: o que ninguém está te contando"
set "TOPIC_COUNT=10"

REM === Seleciona um tema aleatório ===
set /a "RAND_INDEX=(%RANDOM% %% %TOPIC_COUNT%)"
call set "SELECTED_TITLE=%%TOPICS[!RAND_INDEX!]%%"

echo.

echo Tema escolhido: !SELECTED_TITLE!

echo.

REM === Confirmação do usuário ===
choice /c SN /n /m "Deseja gerar um post com este tema? (S/N) "
if errorlevel 2 (
    echo.
    echo Operação cancelada pelo usuário.
    goto :eof
)
echo.

REM === Nome do arquivo final ===
set "FILENAME=%POSTS_DIR%\post-%CURRENT_DATE%-%RANDOM%.md"

REM === Prompt aprimorado para o Gemini ===
set "PROMPT=Escreva um artigo de blog com aproximadamente 600 palavras sobre o tema '!SELECTED_TITLE!'. O artigo deve ter um tom envolvente e provocativo, típico de conteúdo 'clickbait', mas com informações úteis e acionáveis. Estruture o conteúdo da seguinte forma: uma introdução cativante que fisgue o leitor; pelo menos 3 subtítulos claros usando markdown (##); uso de listas (bullet points) para facilitar a leitura; exemplos práticos ou cenários hipotéticos para ilustrar os pontos; e uma conclusão forte e inspiradora que incentive o leitor a agir. Importante: Não inclua o título principal no corpo do artigo, pois ele será adicionado ao frontmatter do Hugo."

REM === Chama o Gemini-CLI para gerar o conteúdo ===
echo Gerando conteúdo com o Gemini-CLI...
gemini.cmd --prompt "!PROMPT!" > %TEMP_FILE% 2> gemini_error.log

REM === Verifica se o conteúdo foi gerado ===
if errorlevel 1 (
    echo.
    echo ❌ ERRO: O comando 'gemini.cmd' falhou com o código de erro %errorlevel%.
    if exist gemini_error.log (
        echo.
        echo --- Detalhes do Erro ---
        type gemini_error.log
        del gemini_error.log
        echo -----------------------
    )
    goto :cleanup
)
if exist gemini_error.log del gemini_error.log

if not exist %TEMP_FILE% (
    echo.
    echo ERRO: O arquivo de conteúdo temporário (%TEMP_FILE%) não foi criado.
    echo Verifique se o comando 'gemini.cmd' está funcionando corretamente.
    goto :cleanup
)
for %%A in (%TEMP_FILE%) do if %%~zA equ 0 (
    echo.
    echo ERRO: O arquivo de conteúdo gerado está vazio.
    echo A chamada para 'gemini.cmd' pode ter falhado.
    goto :cleanup
)

REM === Cria o post com o frontmatter do Hugo (em UTF-8) ===
chcp 65001 > nul
(
    echo ---
    echo title: "!SELECTED_TITLE!"
    echo date: %ISO_TIMESTAMP%
    echo draft: false
    echo ---
    echo.
    type %TEMP_FILE%
) > "%FILENAME%"

REM === Limpeza e Mensagem Final ===
:cleanup
if exist %TEMP_FILE% del %TEMP_FILE%

if exist "%FILENAME%" (
    echo.
    echo ✅ Post criado com sucesso em: %FILENAME%
    echo.
    echo Para visualizar, rode: hugo server -D
) else (
    echo.
    echo ❌ Falha ao criar o post.
)

echo.
pause

