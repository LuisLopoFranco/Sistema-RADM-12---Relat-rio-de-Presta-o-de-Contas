# Sistema de Gestão de Viagens e Prestação de Contas (RADM-12)

Sistema web completo em Python/Django para gerenciamento de viagens corporativas e prestação de contas, seguindo o padrão RADM-12.

## Funcionalidades Principais

### Três Tipos de Usuário:

1. **Solicitante**: Realiza requisições de viagens e gerencia suas despesas
2. **Aprovador**: Aprova ou reprova requisições de viagem
3. **Administrador**: Acesso completo ao sistema e geração de relatórios detalhados

### Recursos do Sistema:

- Cadastro completo de viagens com todas as informações do formulário RADM-12
- Gestão de despesas por categoria (Diárias, Refeições, Passagens, Táxi, Telefonemas, Outras)
- Controle de uso de veículo próprio com cálculo automático de combustível
  - Carro: 6 Km/L
  - Moto: 15 Km/L
- Upload de comprovantes (PDFs, imagens)
- Workflow de aprovação com parecer do superior
- Cálculo automático de adiantamento, reembolso e restituição
- Relatórios detalhados e exportação para CSV
- Impressão de relatório formatado para prestação de contas
- Dashboard personalizado por tipo de usuário

## Requisitos

- Python 3.8 a 3.13 com Django 4.2.x
- Python 3.14+ com Django 5.1+
- Navegador web moderno

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd Sistema-RADM-12---Relat-rio-de-Presta-o-de-Contas
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# No Windows:
venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

```bash
cd travel_system
python ../manage.py makemigrations
python ../manage.py migrate
```

### 5. Crie um superusuário (Administrador)

```bash
python ../manage.py createsuperuser
```

Siga as instruções na tela para criar o primeiro usuário administrador.

### 6. Execute o servidor

```bash
python ../manage.py runserver
```

O sistema estará disponível em: http://127.0.0.1:8000/

## Primeiro Acesso

1. Acesse http://127.0.0.1:8000/admin/
2. Faça login com o superusuário criado
3. Acesse "Usuários" e edite seu usuário para definir:
   - Tipo de Usuário: ADMINISTRADOR
   - Cargo
   - Dados bancários (se necessário)

### Criando Usuários

No Django Admin, você pode criar usuários de três tipos:

1. **Solicitante**: Para colaboradores que farão requisições de viagem
2. **Aprovador**: Para gestores que aprovarão viagens
3. **Administrador**: Para administração do sistema

### Criando Centros de Custo

Antes de criar viagens, cadastre os Centros de Custo em:
- Django Admin → Centros de Custo → Adicionar

## Uso do Sistema

### Para Solicitantes:

1. Acesse o sistema com suas credenciais
2. Vá em "Nova Viagem"
3. Preencha todos os dados da viagem:
   - Informações básicas (destino, trecho, motivo)
   - Datas (autorização, saída, chegada)
   - Aprovador e adiantamento
4. Clique em "Salvar e Continuar"
5. Adicione as despesas realizadas
6. Se utilizou veículo próprio, registre os dados
7. Faça upload dos comprovantes
8. Submeta para aprovação

### Para Aprovadores:

1. Acesse "Aprovar Viagens" no menu
2. Visualize as viagens pendentes
3. Clique em "Ver" para analisar os detalhes
4. Clique em "Aprovar" para dar o parecer
5. Escolha entre APROVADA ou REPROVADA
6. Escreva um parecer
7. Autorize ou não o débito/crédito
8. Confirme a decisão

### Para Administradores:

1. Acesse "Relatórios" para ver estatísticas gerais
2. Acesse "Relatório Detalhado" para filtrar e exportar
3. Use os filtros por data, status e centro de custo
4. Exporte para CSV quando necessário
5. Acesse o Django Admin para gestão completa

## Estrutura de Cálculos

### Despesas com Veículos:

```python
# Carro (6 Km/L)
custo_carro = (km_rodado / 6) * valor_litro

# Moto (15 Km/L)
custo_moto = (km_rodado / 15) * valor_litro
```

### Acerto Financeiro:

```python
total_despesas = soma_despesas + custo_veiculos
saldo = total_despesas - adiantamento

# Se saldo > 0: Reembolso ao usuário
# Se saldo < 0: Restituição à cooperativa (Cód. 261)
```

## Validações Implementadas

- Data de autorização ≤ Data de saída ≤ Data de chegada
- Obrigatoriedade de campos conforme regras de negócio
- Descrição obrigatória para categoria "Outras" em despesas
- Descrição obrigatória se classificação do motivo for "Outro"
- Validação de hodômetro (saída < chegada)
- Cálculo automático de KM rodado

## Tecnologias Utilizadas

- **Backend**: Python 3.x + Django 4.2
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Banco de Dados**: SQLite (padrão) - facilmente migável para PostgreSQL/MySQL
- **Autenticação**: Django Auth com modelo customizado de usuário

## Estrutura do Projeto

```
travel_system/
├── manage.py
├── travel_system/          # Configurações do projeto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── travels/                # App principal
    ├── models.py          # Models (User, TravelRequest, Expense, etc.)
    ├── views.py           # Views e lógica de negócio
    ├── forms.py           # Formulários
    ├── urls.py            # URLs do app
    ├── admin.py           # Configuração do Django Admin
    └── templates/         # Templates HTML
        └── travels/
```

## Models Principais

- **User**: Usuários do sistema com perfis
- **CostCenter**: Centros de custo
- **TravelRequest**: Requisições/Relatórios de viagem
- **Expense**: Despesas da viagem
- **VehicleTrip**: Viagens com veículo próprio
- **VehicleLog**: Logs detalhados de uso do veículo
- **Approval**: Aprovações das viagens
- **Attachment**: Comprovantes e anexos

## Relatórios Disponíveis

1. **Dashboard**: Visão geral por tipo de usuário
2. **Relatórios Estatísticos**: Despesas por categoria, uso de veículos, etc.
3. **Relatório Detalhado**: Com filtros e exportação CSV
4. **Impressão Individual**: Relatório formatado para impressão/PDF

## Segurança

- Autenticação obrigatória para todas as páginas
- Controle de permissões por tipo de usuário
- Validações no frontend e backend
- Proteção CSRF em todos os formulários
- Upload seguro de arquivos

## Suporte e Desenvolvimento

Sistema desenvolvido seguindo as melhores práticas do Django e padrões de desenvolvimento Python.

Para personalização ou desenvolvimento adicional, consulte a documentação oficial do Django: https://docs.djangoproject.com/

## Licença

Sistema proprietário - Todos os direitos reservados

---

**Versão**: 1.0
**Data**: 2025
**Framework**: Django 4.2+
**Python**: 3.8+
