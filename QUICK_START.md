# Guia Rápido de Início

## Setup em 5 Minutos

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados
```bash
cd travel_system
python ../manage.py migrate
```

### 3. Criar Superusuário
```bash
python ../manage.py createsuperuser
```

Preencha:
- Username: admin
- Email: admin@exemplo.com
- Password: (sua senha)

### 4. Iniciar Servidor
```bash
python ../manage.py runserver
```

### 5. Acessar o Sistema

**Interface Principal:**
- URL: http://127.0.0.1:8000/
- Login: Use o usuário criado no passo 3

**Django Admin (Configuração):**
- URL: http://127.0.0.1:8000/admin/
- Login: Mesmo usuário do passo 3

## Configuração Inicial Essencial

### 1. Configurar seu Usuário Administrador

1. Acesse http://127.0.0.1:8000/admin/
2. Vá em "Usuários" → Clique no seu usuário
3. Configure:
   - **Tipo de Usuário**: ADMINISTRADOR
   - **Nome**: Seu nome completo
   - **Cargo**: Seu cargo
   - **Dados bancários**: (opcional, para reembolsos)

### 2. Criar Centros de Custo

1. No Django Admin, vá em "Centros de Custo"
2. Clique em "Adicionar Centro de Custo"
3. Preencha:
   - Código: Ex: CC001
   - Nome: Ex: Administrativo
   - Ativo: ✓

Crie pelo menos 2-3 centros de custo para testes.

### 3. Criar Usuários de Teste

**Criar um Solicitante:**
1. Django Admin → Usuários → Adicionar
2. Preencha:
   - Username: solicitante1
   - Password: (defina uma senha)
   - Nome: João Silva
   - Email: joao@empresa.com
   - Tipo de Usuário: SOLICITANTE
   - Cargo: Analista

**Criar um Aprovador:**
1. Django Admin → Usuários → Adicionar
2. Preencha:
   - Username: aprovador1
   - Password: (defina uma senha)
   - Nome: Maria Santos
   - Email: maria@empresa.com
   - Tipo de Usuário: APROVADOR
   - Cargo: Gerente

## Testando o Sistema

### Fluxo Completo de Teste:

1. **Como Solicitante:**
   - Faça logout do admin
   - Login como solicitante1
   - Clique em "Nova Viagem"
   - Preencha todos os dados
   - Adicione despesas
   - Submeta para aprovação

2. **Como Aprovador:**
   - Faça logout
   - Login como aprovador1
   - Veja a viagem em "Aprovar Viagens"
   - Analise e aprove

3. **Como Administrador:**
   - Login como admin
   - Acesse "Relatórios"
   - Veja estatísticas e exporte dados

## Estrutura de Diretórios Após Setup

```
Sistema-RADM-12/
├── travel_system/
│   ├── manage.py
│   ├── db.sqlite3          # Criado após migrate
│   ├── travel_system/
│   └── travels/
├── media/                   # Criado automaticamente para uploads
│   ├── comprovantes/
│   └── relatorios/
├── requirements.txt
└── README.md
```

## Solução de Problemas Comuns

### Erro: "No module named 'django'"
```bash
pip install -r requirements.txt
```

### Erro: "Table doesn't exist"
```bash
python manage.py migrate
```

### Erro: "CSRF verification failed"
- Limpe o cache do navegador
- Verifique se está em http://127.0.0.1:8000 (não localhost)

### Erro ao fazer upload de arquivos
```bash
# Crie os diretórios manualmente:
mkdir -p media/comprovantes
mkdir -p media/relatorios
```

## Dados de Exemplo para Teste

### Exemplo de Viagem:
- **Destino**: São Paulo
- **Trecho**: Belo Horizonte → São Paulo
- **Motivo**: Reunião com cliente
- **Classificação**: A serviço da Cooperativa
- **Data Saída**: Hoje
- **Data Chegada**: Hoje + 2 dias
- **Adiantamento**: R$ 500,00

### Exemplo de Despesas:
- **Diárias**: R$ 200,00 (Hotel)
- **Refeições**: R$ 150,00 (Almoços e jantares)
- **Passagens**: R$ 300,00 (Ônibus ida e volta)
- **Táxi**: R$ 80,00 (Deslocamentos locais)

### Exemplo de Veículo:
- **Tipo**: Carro
- **Placa**: ABC-1234
- **Modelo**: Fiat Uno
- **KM Rodado**: 400 km
- **Valor Litro**: R$ 5,50
- **Custo Calculado**: (400 / 6) × 5,50 = R$ 366,67

## Comandos Úteis Django

```bash
# Criar migrações após alterar models
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos (produção)
python manage.py collectstatic

# Abrir shell Django
python manage.py shell

# Verificar problemas
python manage.py check
```

## Próximos Passos

1. Configure os centros de custo da sua organização
2. Crie usuários reais no sistema
3. Customize o SECRET_KEY em production (settings.py)
4. Configure um banco de dados mais robusto (PostgreSQL) se necessário
5. Configure email para notificações (opcional)

## Suporte

Para mais detalhes, consulte o arquivo README.md completo.

---
Sistema de Gestão de Viagens - RADM-12
