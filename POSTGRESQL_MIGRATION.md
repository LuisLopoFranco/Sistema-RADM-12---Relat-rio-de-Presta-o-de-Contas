# Guia de Migração para PostgreSQL

## Por que usar PostgreSQL?

O PostgreSQL é recomendado para ambientes de produção por oferecer:
- **Melhor performance** em ambientes com múltiplos usuários
- **Maior segurança** e controle de acesso
- **Suporte a transações** mais robustas
- **Escalabilidade** para grandes volumes de dados
- **Recursos avançados** de backup e recuperação

## Pré-requisitos

### 1. Instalar PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
- Baixe o instalador em: https://www.postgresql.org/download/windows/
- Execute o instalador e siga as instruções
- Anote a senha do usuário `postgres`

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### 2. Instalar o adaptador Python

O `psycopg2-binary` já está no `requirements.txt`, mas você pode instalá-lo separadamente:
```bash
pip install psycopg2-binary
```

## Configuração do PostgreSQL

### 1. Criar o Banco de Dados

Acesse o PostgreSQL:
```bash
# Linux/Mac
sudo -u postgres psql

# Windows (no PowerShell)
psql -U postgres
```

No console do PostgreSQL, execute:
```sql
-- Criar banco de dados
CREATE DATABASE travel_system;

-- Criar usuário (opcional, mas recomendado)
CREATE USER travel_admin WITH PASSWORD 'sua_senha_forte_aqui';

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE travel_system TO travel_admin;

-- Sair
\q
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (ou configure as variáveis no sistema):

```bash
# .env
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=travel_system
DATABASE_USER=travel_admin
DATABASE_PASSWORD=sua_senha_forte_aqui
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**IMPORTANTE:** Adicione `.env` ao `.gitignore` para não commitar senhas!

### 3. Instalar python-decouple (opcional)

Para carregar as variáveis do arquivo `.env` automaticamente:

```bash
pip install python-decouple
```

Depois, atualize o `settings.py`:
```python
from decouple import config

DATABASE_ENGINE = config('DATABASE_ENGINE', default='django.db.backends.sqlite3')
```

## Migração de Dados

### Opção 1: Banco Novo (Recomendado para Desenvolvimento)

Se você está começando ou em desenvolvimento, basta executar:

```bash
cd travel_system

# Executar migrações
python ../manage.py migrate

# Criar superusuário
python ../manage.py createsuperuser
```

### Opção 2: Migrar Dados Existentes do SQLite

Se você já tem dados no SQLite e quer migrar para PostgreSQL:

#### Passo 1: Fazer dump dos dados do SQLite
```bash
cd travel_system

# Exportar dados
python ../manage.py dumpdata --natural-foreign --natural-primary \
  --exclude auth.permission --exclude contenttypes \
  --indent 2 > data_backup.json
```

#### Passo 2: Configurar PostgreSQL
Configure as variáveis de ambiente conforme descrito acima.

#### Passo 3: Executar migrações no PostgreSQL
```bash
python ../manage.py migrate
```

#### Passo 4: Importar dados
```bash
python ../manage.py loaddata data_backup.json
```

### Opção 3: Usar ferramentas de migração

Para grandes volumes de dados, considere usar:
- **pgLoader**: https://pgloader.io/ (converte SQLite → PostgreSQL)
- **Django Database Backup**: Módulos como `django-dbbackup`

## Configuração Avançada do PostgreSQL

### 1. Otimizar Conexões

Para produção, adicione ao `settings.py`:

```python
if DATABASE_ENGINE == 'django.db.backends.postgresql':
    DATABASES['default']['CONN_MAX_AGE'] = 600  # Conexões persistentes (10 min)
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
    }
```

### 2. Configurar pg_hba.conf (Acesso Remoto)

Se precisar acessar o PostgreSQL remotamente, edite o arquivo `pg_hba.conf`:

**Linux:** `/etc/postgresql/[versão]/main/pg_hba.conf`

Adicione:
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    travel_system   travel_admin    0.0.0.0/0              md5
```

E em `postgresql.conf`, configure:
```
listen_addresses = '*'
```

Reinicie o PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 3. Backup Automatizado

Crie um script de backup:

```bash
#!/bin/bash
# backup_postgres.sh

BACKUP_DIR="/var/backups/travel_system"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/travel_system_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -U travel_admin -h localhost travel_system > $BACKUP_FILE

# Manter apenas backups dos últimos 7 dias
find $BACKUP_DIR -name "travel_system_*.sql" -mtime +7 -delete

echo "Backup concluído: $BACKUP_FILE"
```

Configure no cron para executar diariamente:
```bash
# Executar todos os dias às 2h da manhã
0 2 * * * /caminho/para/backup_postgres.sh
```

## Verificação da Instalação

### 1. Verificar Conexão

```bash
cd travel_system
python ../manage.py dbshell
```

Você deve entrar no console do PostgreSQL. Digite `\dt` para ver as tabelas.

### 2. Verificar Migrações

```bash
python ../manage.py showmigrations
```

Todas devem estar marcadas com `[X]`.

### 3. Testar CRUD

```bash
python ../manage.py shell
```

No shell do Django:
```python
from travels.models import User, CostCenter

# Criar centro de custo
centro = CostCenter.objects.create(
    codigo='TEST001',
    nome='Centro de Teste',
    ativo=True
)
print(centro)

# Listar usuários
users = User.objects.all()
print(users)
```

## Solução de Problemas

### Erro: "fe_sendauth: no password supplied"

**Solução:** Certifique-se de que a variável `DATABASE_PASSWORD` está configurada.

### Erro: "FATAL: database 'travel_system' does not exist"

**Solução:** Crie o banco de dados no PostgreSQL (veja seção "Criar o Banco de Dados").

### Erro: "could not connect to server"

**Solução:** Verifique se o PostgreSQL está rodando:
```bash
sudo systemctl status postgresql  # Linux
brew services list                # macOS
```

### Erro: "Peer authentication failed"

**Solução:** Edite `pg_hba.conf` e mude o método de autenticação de `peer` para `md5`:
```
# Antes
local   all   all   peer

# Depois
local   all   all   md5
```

Reinicie o PostgreSQL.

### Performance Lenta

1. **Criar índices:** O Django já cria índices automaticamente, mas você pode adicionar mais se necessário
2. **Aumentar shared_buffers:** No `postgresql.conf`, ajuste:
   ```
   shared_buffers = 256MB  # Ajuste conforme RAM disponível
   ```
3. **Analisar queries lentas:** Ative o log de queries:
   ```
   log_min_duration_statement = 1000  # Log queries > 1 segundo
   ```

## Reverter para SQLite

Se precisar voltar para SQLite:

1. Remova ou comente as variáveis de ambiente do PostgreSQL
2. Ou configure explicitamente:
   ```bash
   export DATABASE_ENGINE=django.db.backends.sqlite3
   ```
3. Execute as migrações novamente:
   ```bash
   python manage.py migrate
   ```

## Ambientes Diferentes

### Desenvolvimento: SQLite
```bash
# Não configure variáveis de ambiente
# O sistema usará SQLite por padrão
python manage.py runserver
```

### Produção: PostgreSQL
```bash
export DATABASE_ENGINE=django.db.backends.postgresql
export DATABASE_NAME=travel_system
export DATABASE_USER=travel_admin
export DATABASE_PASSWORD=sua_senha
export DATABASE_HOST=localhost
export DATABASE_PORT=5432

python manage.py migrate
gunicorn travel_system.wsgi:application
```

## Checklist de Migração

- [ ] PostgreSQL instalado e rodando
- [ ] Banco de dados `travel_system` criado
- [ ] Usuário `travel_admin` criado (opcional)
- [ ] Variáveis de ambiente configuradas
- [ ] `psycopg2-binary` instalado
- [ ] Migrações executadas (`python manage.py migrate`)
- [ ] Dados migrados (se aplicável)
- [ ] Superusuário criado
- [ ] Teste de conexão realizado
- [ ] Backup configurado (produção)

## Recursos Adicionais

- **Documentação Django:** https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes
- **Documentação PostgreSQL:** https://www.postgresql.org/docs/
- **Tutorial pgAdmin:** https://www.pgadmin.org/docs/

---

**Versão:** 1.0
**Data:** 2025
**Mantido por:** Sistema de Gestão de Viagens
