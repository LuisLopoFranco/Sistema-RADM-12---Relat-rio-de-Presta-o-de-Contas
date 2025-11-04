# Changelog - Sistema de Gestão de Viagens

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.1.0] - 2025-01-XX

### ✨ Novidades

#### Categorias de Despesas Expandidas
- **25 categorias de despesas** disponíveis (antes eram 6)
- Novas categorias incluem:
  - Hospedagem separada de Diárias
  - Refeições detalhadas (Café da Manhã, Almoço, Jantar)
  - Passagens especificadas (Aéreas, Rodoviárias)
  - Transportes urbanos detalhados (Táxi, Uber/App, Ônibus, Metrô/Trem)
  - Despesas modernas (Internet/Dados Móveis, Apps de Transporte)
  - Despesas de viagem (Estacionamento, Pedágio, Combustível)
  - Outras categorias (Correio, Material de Escritório, Inscrição em Eventos, etc.)

#### Tipos de Veículos Configuráveis
- **Sistema totalmente configurável** de tipos de veículos via Django Admin
- Administradores podem criar/editar tipos de veículos personalizados
- Cada tipo tem **consumo (Km/L) configurável**
- **10 tipos de veículos pré-cadastrados:**
  - Carro Popular (12 Km/L)
  - Carro Médio (10 Km/L)
  - Carro SUV (8 Km/L)
  - Carro Flex - Gasolina (11 Km/L)
  - Carro Flex - Etanol (7.5 Km/L)
  - Moto até 160cc (35 Km/L)
  - Moto 160cc a 300cc (25 Km/L)
  - Moto acima de 300cc (18 Km/L)
  - Carro Híbrido (18 Km/L)
  - Caminhonete/Pickup (7 Km/L)
- Fixtures JSON para carregar tipos padrão automaticamente

#### Suporte a PostgreSQL
- **Sistema multi-banco**: Suporta SQLite (desenvolvimento) e PostgreSQL (produção)
- Configuração via **variáveis de ambiente**
- **Migração facilitada** de SQLite para PostgreSQL
- Documentação completa em `POSTGRESQL_MIGRATION.md`
- Instruções de backup e recuperação

### 🔧 Melhorias

#### Models
- Novo modelo `VehicleType` para configuração de veículos
- `VehicleTrip` agora usa ForeignKey para `VehicleType` (mais flexível)
- Cálculo de consumo agora é **dinâmico** baseado no tipo configurado
- Campo `categoria` do modelo `Expense` expandido com 25 opções

#### Admin
- Nova seção "Tipos de Veículo" no Django Admin
- Interface administrativa para gerenciar tipos e consumos
- Campos organizados com fieldsets colapsáveis

#### Configuração
- `settings.py` atualizado com suporte multi-banco
- `.env.example` atualizado com variáveis PostgreSQL
- Detecção automática do banco baseado em `DATABASE_ENGINE`

### 📚 Documentação

#### Novos Arquivos
- `POSTGRESQL_MIGRATION.md`: Guia completo de migração para PostgreSQL
  - Instalação do PostgreSQL em Linux, Windows e macOS
  - Configuração de usuários e permissões
  - Migração de dados do SQLite
  - Troubleshooting completo
  - Configurações avançadas de performance

- `CHANGELOG.md`: Histórico de mudanças do projeto

- `vehicle_types.json`: Fixture com 10 tipos de veículos pré-configurados

#### Arquivos Atualizados
- `.env.example`: Documentação de variáveis PostgreSQL
- `README.md`: Menção às novas funcionalidades

### 🔄 Migrações

#### Necessárias
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Carregar Tipos de Veículos (opcional, mas recomendado)
```bash
python manage.py loaddata vehicle_types
```

### ⚠️ Breaking Changes

#### VehicleTrip
- **IMPORTANTE:** O campo `tipo_veiculo` mudou de CharField para ForeignKey
- Sistemas existentes precisarão:
  1. Fazer backup dos dados
  2. Executar as novas migrações
  3. Recriar os registros de VehicleTrip com os novos tipos

#### Processo de Migração para Sistemas em Produção:
```bash
# 1. Backup
python manage.py dumpdata travels.VehicleTrip > vehicle_trips_backup.json

# 2. Executar migrações
python manage.py makemigrations
python manage.py migrate

# 3. Carregar tipos de veículos
python manage.py loaddata vehicle_types

# 4. Recriar viagens de veículos (se necessário)
# Pode ser necessário script customizado para converter dados antigos
```

### 🐛 Correções
- Nenhuma correção de bugs nesta versão (funcionalidades novas)

### 🔐 Segurança
- Variáveis de ambiente para senhas de banco (não mais hardcoded)
- `.env` adicionado ao `.gitignore`

### 📊 Estatísticas
- **6 → 25 categorias** de despesas (+317%)
- **2 → 10+ tipos** de veículos (configuráveis, +400%)
- **1 → 2 bancos** suportados (SQLite + PostgreSQL)
- **+1 modelo** novo (VehicleType)
- **+1000 linhas** de documentação

---

## [1.0.0] - 2025-01-XX

### 🎉 Lançamento Inicial

Sistema completo de gestão de viagens e prestação de contas (RADM-12).

#### Funcionalidades Principais
- 3 tipos de usuários (Solicitante, Aprovador, Administrador)
- Cadastro completo de viagens
- Gestão de despesas por categoria
- Controle de uso de veículo próprio
- Upload de comprovantes
- Workflow de aprovação
- Cálculos automáticos financeiros
- Relatórios e exportação CSV
- Dashboard personalizado
- Sistema de impressão

#### Tecnologias
- Django 4.2+
- Python 3.8+
- Bootstrap 5
- SQLite

---

## Versionamento

Este projeto segue [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.x.x): Mudanças incompatíveis na API
- **MINOR** (x.1.x): Novas funcionalidades compatíveis
- **PATCH** (x.x.1): Correções de bugs compatíveis

## Links

- [README](README.md)
- [Quick Start](QUICK_START.md)
- [PostgreSQL Migration](POSTGRESQL_MIGRATION.md)
