# Guia de Atualização para Versão 1.1.0

Este guia ajudará você a atualizar seu sistema da versão 1.0 para 1.1.0.

## O que há de novo na versão 1.1.0?

- ✅ **25 categorias de despesas** (antes: 6)
- ✅ **Tipos de veículos configuráveis** (antes: hardcoded)
- ✅ **Suporte a PostgreSQL** (antes: apenas SQLite)

## Passos para Atualização

### Passo 1: Backup dos Dados

**IMPORTANTE:** Sempre faça backup antes de atualizar!

```bash
cd travel_system

# Backup completo do banco
python ../manage.py dumpdata > backup_v1.0_$(date +%Y%m%d).json

# Backup específico de viagens com veículos (se houver)
python ../manage.py dumpdata travels.VehicleTrip > vehicle_trips_backup.json
```

### Passo 2: Atualizar o Código

```bash
# Volte para o diretório raiz do projeto
cd ..

# Obtenha as últimas alterações
git pull origin claude/python-web-system-011CUnvy6V18t2okhcMagtMQ
```

### Passo 3: Instalar Dependências (se necessário)

Se você planeja usar PostgreSQL:

```bash
pip install psycopg2-binary
```

Caso contrário, as dependências não mudaram.

### Passo 4: Aplicar Migrações

```bash
cd travel_system

# Criar as novas migrações
python ../manage.py makemigrations

# Aplicar as migrações
python ../manage.py migrate
```

### Passo 5: Carregar Tipos de Veículos Padrão

```bash
# Carregar os 10 tipos de veículos pré-configurados
python ../manage.py loaddata vehicle_types
```

Isso criará:
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

### Passo 6: Migrar Viagens com Veículos Existentes (se houver)

**ATENÇÃO:** Se você já tem viagens com veículos cadastradas, precisará recriá-las manualmente ou com script customizado, pois o campo `tipo_veiculo` mudou de CharField para ForeignKey.

#### Opção A: Poucas Viagens (Manual)

1. Acesse o Django Admin: http://127.0.0.1:8000/admin/
2. Vá em "Viagens com Veículo Próprio"
3. Para cada viagem:
   - Anote os dados (placa, modelo, km, valor litro)
   - Delete a viagem antiga
   - Crie uma nova selecionando o tipo correto
   - Preencha os dados anotados

#### Opção B: Muitas Viagens (Script)

Crie um script de migração customizado. Exemplo:

```python
# migration_script.py
from travels.models import VehicleTrip, VehicleType

# Mapeamento de tipos antigos para novos
mapping = {
    'CARRO': VehicleType.objects.get(nome='Carro Popular'),
    'MOTO': VehicleType.objects.get(nome='Moto 160cc a 300cc'),
}

# Implemente a lógica de conversão aqui
# Este é apenas um exemplo - adapte conforme sua necessidade
```

Execute:
```bash
python manage.py shell < migration_script.py
```

### Passo 7: Verificar a Atualização

```bash
# Verificar migrações aplicadas
python ../manage.py showmigrations

# Testar o servidor
python ../manage.py runserver
```

Acesse:
1. http://127.0.0.1:8000/admin/
2. Verifique "Tipos de Veículo" - deve ter 10 tipos
3. Crie uma nova viagem de teste
4. Adicione despesas com as novas categorias

### Passo 8: (Opcional) Migrar para PostgreSQL

Se desejar migrar para PostgreSQL, siga o guia completo:
```bash
# Ver documentação completa
cat ../POSTGRESQL_MIGRATION.md
```

Ou acesse: [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md)

## Novas Categorias de Despesas

Agora você tem 25 categorias:

**Hospedagem:**
- Diárias e Extras de Hotel
- Hospedagem

**Refeições:**
- Refeições/Lanches
- Café da Manhã
- Almoço
- Jantar

**Passagens:**
- Passagens Aéreas
- Passagens Rodoviárias
- Passagens (Outras)

**Transporte:**
- Táxi
- Uber/App de Transporte
- Ônibus
- Metrô/Trem
- Estacionamento
- Pedágio
- Combustível

**Comunicação:**
- Telefonemas
- Internet/Dados Móveis

**Outros:**
- Correio/Sedex
- Material de Escritório
- Inscrição em Evento/Curso
- Documentação/Taxas
- Lavanderia
- Gorjetas
- Outras Despesas

## Configuração de Tipos de Veículos Personalizados

Para adicionar seus próprios tipos de veículos:

1. Acesse: http://127.0.0.1:8000/admin/
2. Vá em "Tipos de Veículo"
3. Clique em "Adicionar Tipo de Veículo"
4. Preencha:
   - Nome: Ex: "Carro Elétrico"
   - Consumo (Km/L): Ex: "25.00" (ou equivalente energético)
   - Ativo: Marque
   - Descrição: Ex: "Veículos 100% elétricos"
5. Salve

## Solução de Problemas

### Erro: "django.db.utils.OperationalError: no such table"

**Solução:**
```bash
python manage.py migrate --run-syncdb
```

### Erro: "django.core.exceptions.ObjectDoesNotExist: VehicleType matching query does not exist"

**Solução:** Você não carregou os tipos de veículos. Execute:
```bash
python manage.py loaddata vehicle_types
```

### Erro ao migrar viagens com veículos existentes

**Solução:** Siga o Passo 6 deste guia para migrar manualmente ou com script.

### Viagens antigas com veículos não aparecem

**Causa:** O campo `tipo_veiculo` mudou de CharField para ForeignKey.

**Solução:** Recrie as viagens com veículos usando os novos tipos (veja Passo 6).

## Reversão para Versão 1.0 (Rollback)

Se precisar voltar para a versão 1.0:

```bash
# 1. Restaurar backup
cd travel_system
python ../manage.py loaddata backup_v1.0_YYYYMMDD.json

# 2. Reverter código
cd ..
git checkout <hash-do-commit-1.0>

# 3. Reverter migrações
cd travel_system
python ../manage.py migrate travels <numero-da-migracao-anterior>
```

## Recursos Adicionais

- [CHANGELOG.md](CHANGELOG.md) - Histórico completo de mudanças
- [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md) - Guia de migração para PostgreSQL
- [README.md](README.md) - Documentação geral do sistema

## Checklist de Atualização

- [ ] Backup dos dados realizado
- [ ] Código atualizado (git pull)
- [ ] Dependências instaladas (se necessário)
- [ ] Migrações aplicadas
- [ ] Tipos de veículos carregados (loaddata)
- [ ] Viagens com veículos existentes migradas (se aplicável)
- [ ] Servidor testado e funcionando
- [ ] Django Admin acessível
- [ ] Novos tipos de veículos visíveis no admin
- [ ] Novas categorias de despesas disponíveis
- [ ] Teste de criação de viagem com novas funcionalidades

## Dúvidas?

Consulte a documentação completa ou abra uma issue no repositório.

---

**Atualizado em:** 2025
**Versão:** 1.1.0
