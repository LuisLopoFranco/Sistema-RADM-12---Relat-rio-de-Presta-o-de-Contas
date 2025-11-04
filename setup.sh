#!/bin/bash

# Script de configuração automática do Sistema de Viagens RADM-12

echo "=========================================="
echo "Sistema de Gestão de Viagens - RADM-12"
echo "Setup Automático"
echo "=========================================="
echo ""

# 1. Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo "✅ Dependências instaladas com sucesso"
echo ""

# 2. Configurar banco de dados
echo "🗄️  Configurando banco de dados..."
cd travel_system

python ../manage.py makemigrations
python ../manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Erro ao configurar banco de dados"
    exit 1
fi

echo "✅ Banco de dados configurado"
echo ""

# 3. Criar diretórios para media
echo "📁 Criando diretórios para uploads..."
mkdir -p media/comprovantes
mkdir -p media/relatorios
mkdir -p staticfiles

echo "✅ Diretórios criados"
echo ""

# 4. Coletar arquivos estáticos
echo "📋 Coletando arquivos estáticos..."
python ../manage.py collectstatic --noinput

echo ""
echo "=========================================="
echo "✅ Setup concluído com sucesso!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Crie um superusuário: python manage.py createsuperuser"
echo "2. Inicie o servidor: python manage.py runserver"
echo "3. Acesse: http://127.0.0.1:8000/"
echo ""
echo "Consulte QUICK_START.md para mais detalhes"
echo ""
