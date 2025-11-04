@echo off
chcp 65001 > nul

echo ==========================================
echo Sistema de Gestão de Viagens - RADM-12
echo Setup Automático
echo ==========================================
echo.

REM 1. Instalar dependências
echo 📦 Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo ✅ Dependências instaladas com sucesso
echo.

REM 2. Configurar banco de dados
echo 🗄️  Configurando banco de dados...
cd travel_system

python ..\manage.py makemigrations
python ..\manage.py migrate

if errorlevel 1 (
    echo ❌ Erro ao configurar banco de dados
    pause
    exit /b 1
)

echo ✅ Banco de dados configurado
echo.

REM 3. Criar diretórios para media
echo 📁 Criando diretórios para uploads...
if not exist "media\comprovantes" mkdir media\comprovantes
if not exist "media\relatorios" mkdir media\relatorios
if not exist "staticfiles" mkdir staticfiles

echo ✅ Diretórios criados
echo.

REM 4. Coletar arquivos estáticos
echo 📋 Coletando arquivos estáticos...
python ..\manage.py collectstatic --noinput

echo.
echo ==========================================
echo ✅ Setup concluído com sucesso!
echo ==========================================
echo.
echo Próximos passos:
echo 1. Crie um superusuário: python manage.py createsuperuser
echo 2. Inicie o servidor: python manage.py runserver
echo 3. Acesse: http://127.0.0.1:8000/
echo.
echo Consulte QUICK_START.md para mais detalhes
echo.
pause
