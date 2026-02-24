from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class User(AbstractUser):
    """
    Modelo customizado de usuário com perfis específicos:
    - SOLICITANTE: pode criar requisições de viagem
    - APROVADOR: pode aprovar/reprovar viagens
    - ADMINISTRADOR: tem acesso total e pode gerar relatórios
    """
    USER_TYPES = [
        ('SOLICITANTE', 'Solicitante'),
        ('APROVADOR', 'Aprovador'),
        ('ADMINISTRADOR', 'Administrador'),
    ]

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPES,
        default='SOLICITANTE',
        verbose_name='Tipo de Usuário'
    )
    cargo = models.CharField(max_length=200, verbose_name='Cargo')
    telefone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')

    # Dados bancários para reembolso
    conta_corrente = models.CharField(max_length=20, blank=True, verbose_name='Conta Corrente')
    agencia = models.CharField(max_length=10, blank=True, verbose_name='Agência')
    banco = models.CharField(max_length=10, blank=True, verbose_name='Código do Banco')

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_user_type_display()}"


class CostCenter(models.Model):
    """Centro de Custo para alocação de despesas"""
    codigo = models.CharField(max_length=50, unique=True, verbose_name='Código')
    nome = models.CharField(max_length=200, verbose_name='Nome')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Centro de Custo'
        verbose_name_plural = 'Centros de Custo'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class TravelRequest(models.Model):
    """
    Requisição/Relatório de Viagem
    Representa o cabeçalho do relatório de prestação de contas
    """
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('PENDENTE', 'Pendente de Aprovação'),
        ('APROVADA', 'Aprovada'),
        ('REPROVADA', 'Reprovada'),
        ('FINALIZADA', 'Finalizada'),
    ]

    MOTIVO_CLASSIFICACAO = [
        ('SERVICO', 'A serviço da Cooperativa'),
        ('TREINAMENTO', 'Treinamento/Curso'),
        ('OUTRO', 'Outro'),
    ]

    # Informações do solicitante
    solicitante = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='viagens_solicitadas',
        verbose_name='Solicitante'
    )

    # Informações da viagem
    centro_custo = models.ForeignKey(
        CostCenter,
        on_delete=models.PROTECT,
        verbose_name='Centro de Custo'
    )
    trecho_original = models.CharField(max_length=500, verbose_name='Trecho Original')
    trecho_alterado = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Trecho Alterado',
        help_text='Preencher apenas se houver alteração de rota'
    )
    destino = models.CharField(max_length=200, verbose_name='Destino')
    motivo = models.TextField(verbose_name='Motivo/Finalidade da Viagem')
    classificacao_motivo = models.CharField(
        max_length=20,
        choices=MOTIVO_CLASSIFICACAO,
        verbose_name='Classificação do Motivo'
    )
    outro_motivo_descricao = models.TextField(
        blank=True,
        verbose_name='Descrição do Outro Motivo',
        help_text='Obrigatório se classificação for "Outro"'
    )

    # Datas
    data_autorizacao = models.DateField(verbose_name='Data da Autorização')
    data_saida = models.DateField(verbose_name='Data da Saída')
    data_chegada = models.DateField(verbose_name='Data da Chegada')

    # Aprovação
    aprovador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='viagens_para_aprovar',
        limit_choices_to={'user_type': 'APROVADOR'},
        verbose_name='Aprovador'
    )

    # Financeiro
    adiantamento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Adiantamento (R$)'
    )

    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name='Status'
    )

    # Auditoria
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Requisição de Viagem'
        verbose_name_plural = 'Requisições de Viagem'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.solicitante.get_full_name()} - {self.destino} ({self.data_saida})"

    def clean(self):
        """Validações de negócio"""
        # Validar datas
        if self.data_autorizacao and self.data_saida and self.data_autorizacao > self.data_saida:
            raise ValidationError('Data de autorização deve ser anterior à data de saída')

        if self.data_saida and self.data_chegada and self.data_saida > self.data_chegada:
            raise ValidationError('Data de saída deve ser anterior à data de chegada')

        # Validar descrição se classificação for "OUTRO"
        if self.classificacao_motivo == 'OUTRO' and not self.outro_motivo_descricao:
            raise ValidationError('Descrição é obrigatória quando classificação for "Outro"')

    def calcular_total_despesas(self):
        """Calcula o total de todas as despesas da viagem"""
        total_expenses = self.despesas.aggregate(
            total=models.Sum('valor')
        )['total'] or Decimal('0.00')

        total_vehicle = self.viagens_veiculo.aggregate(
            total=models.Sum('custo_calculado')
        )['total'] or Decimal('0.00')

        return total_expenses + total_vehicle

    def calcular_saldo(self):
        """Calcula o saldo: total_despesas - adiantamento"""
        return self.calcular_total_despesas() - self.adiantamento

    def calcular_reembolso(self):
        """Valor a ser reembolsado ao usuário (se saldo > 0)"""
        saldo = self.calcular_saldo()
        return saldo if saldo > 0 else Decimal('0.00')

    def calcular_restituicao(self):
        """Valor a ser restituído à cooperativa (se saldo < 0)"""
        saldo = self.calcular_saldo()
        return abs(saldo) if saldo < 0 else Decimal('0.00')


class Expense(models.Model):
    """
    Despesas realizadas durante a viagem
    Cada item deve ter comprovante anexado
    """
    CATEGORIA_CHOICES = [
        ('DIARIAS', 'Diárias e Extras de Hotel'),
        ('HOSPEDAGEM', 'Hospedagem'),
        ('REFEICOES', 'Refeições/Lanches'),
        ('CAFE_MANHA', 'Café da Manhã'),
        ('ALMOCO', 'Almoço'),
        ('JANTAR', 'Jantar'),
        ('PASSAGENS_AEREAS', 'Passagens Aéreas'),
        ('PASSAGENS_RODOVIARIAS', 'Passagens Rodoviárias'),
        ('PASSAGENS', 'Passagens (Outras)'),
        ('TAXI', 'Táxi'),
        ('UBER_APP', 'Uber/App de Transporte'),
        ('ONIBUS', 'Ônibus'),
        ('METRO_TREM', 'Metrô/Trem'),
        ('ESTACIONAMENTO', 'Estacionamento'),
        ('PEDAGIO', 'Pedágio'),
        ('COMBUSTIVEL', 'Combustível'),
        ('TELEFONEMAS', 'Telefonemas'),
        ('INTERNET', 'Internet/Dados Móveis'),
        ('CORREIO', 'Correio/Sedex'),
        ('MATERIAL_ESCRITORIO', 'Material de Escritório'),
        ('INSCRICAO_EVENTO', 'Inscrição em Evento/Curso'),
        ('DOCUMENTACAO', 'Documentação/Taxas'),
        ('LAVANDERIA', 'Lavanderia'),
        ('GORJETAS', 'Gorjetas'),
        ('OUTRAS', 'Outras Despesas'),
    ]

    viagem = models.ForeignKey(
        TravelRequest,
        on_delete=models.CASCADE,
        related_name='despesas',
        verbose_name='Viagem'
    )
    categoria = models.CharField(
        max_length=32,
        choices=CATEGORIA_CHOICES,
        verbose_name='Categoria'
    )
    descricao = models.TextField(verbose_name='Descrição')
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor (R$)'
    )
    data_despesa = models.DateField(verbose_name='Data da Despesa')

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['data_despesa']

    def __str__(self):
        return f"{self.get_categoria_display()} - R$ {self.valor}"

    def clean(self):
        """Validações de negócio"""
        if self.categoria == 'OUTRAS' and not self.descricao:
            raise ValidationError('Descrição é obrigatória para categoria "Outras"')


class VehicleType(models.Model):
    """
    Tipo de Veículo configurável com consumo personalizado
    Permite ao administrador definir diferentes tipos de veículos
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome do Veículo')
    consumo_km_litro = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Consumo (Km/L)',
        help_text='Quantos quilômetros o veículo faz por litro'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    descricao = models.TextField(blank=True, verbose_name='Descrição')

    class Meta:
        verbose_name = 'Tipo de Veículo'
        verbose_name_plural = 'Tipos de Veículo'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.consumo_km_litro} Km/L)"


class VehicleTrip(models.Model):
    """
    Viagem realizada com veículo próprio
    Calcula automaticamente o custo baseado em km rodado e consumo configurado
    """
    viagem = models.ForeignKey(
        TravelRequest,
        on_delete=models.CASCADE,
        related_name='viagens_veiculo',
        verbose_name='Viagem'
    )
    tipo_veiculo = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Veículo',
        limit_choices_to={'ativo': True}
    )
    placa = models.CharField(max_length=10, verbose_name='Placa')
    modelo = models.CharField(max_length=100, verbose_name='Modelo')
    km_rodado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='KM Rodado'
    )
    valor_litro = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor do Litro (R$)'
    )
    custo_calculado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Custo Calculado (R$)'
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Viagem com Veículo Próprio'
        verbose_name_plural = 'Viagens com Veículo Próprio'

    def __str__(self):
        return f"{self.tipo_veiculo.nome} - {self.placa} - {self.km_rodado}km"

    def calcular_custo(self):
        """
        Calcula o custo do deslocamento:
        custo = (km_rodado / consumo) * valor_litro
        """
        consumo = self.tipo_veiculo.consumo_km_litro
        litros_gastos = self.km_rodado / consumo
        return litros_gastos * self.valor_litro

    def save(self, *args, **kwargs):
        """Calcula automaticamente o custo antes de salvar"""
        self.custo_calculado = self.calcular_custo()
        super().save(*args, **kwargs)


class VehicleLog(models.Model):
    """
    Log detalhado de uso do veículo (hodômetro)
    Controle linha-a-linha do veículo próprio
    """
    viagem_veiculo = models.ForeignKey(
        VehicleTrip,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Viagem Veículo'
    )
    data = models.DateField(verbose_name='Data')
    hora_saida = models.TimeField(verbose_name='Hora de Saída')
    hora_chegada = models.TimeField(verbose_name='Hora de Chegada')
    hodometro_saida = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0'))],
        verbose_name='Hodômetro Saída (km)'
    )
    hodometro_chegada = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0'))],
        verbose_name='Hodômetro Chegada (km)'
    )
    km_rodado = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        default=0,
        verbose_name='KM Rodado'
    )
    roteiro = models.CharField(max_length=500, verbose_name='Roteiro/Percurso')
    objetivo = models.TextField(verbose_name='Motivo/Objetivo')
    condutor = models.CharField(max_length=200, verbose_name='Condutor')
    visto = models.CharField(max_length=200, blank=True, verbose_name='Visto')

    class Meta:
        verbose_name = 'Log de Uso de Veículo'
        verbose_name_plural = 'Logs de Uso de Veículo'
        ordering = ['data', 'hora_saida']

    def __str__(self):
        return f"{self.data} - {self.roteiro} ({self.km_rodado}km)"

    def clean(self):
        """Validações de hodômetro"""
        if self.hodometro_chegada < self.hodometro_saida:
            raise ValidationError('Hodômetro de chegada deve ser maior que hodômetro de saída')

    def calcular_km(self):
        """Calcula KM rodado baseado no hodômetro"""
        return self.hodometro_chegada - self.hodometro_saida

    def save(self, *args, **kwargs):
        """Calcula automaticamente o KM antes de salvar"""
        self.km_rodado = self.calcular_km()
        super().save(*args, **kwargs)


class Approval(models.Model):
    """
    Parecer e aprovação do superior hierárquico
    """
    STATUS_CHOICES = [
        ('APROVADA', 'Aprovada'),
        ('REPROVADA', 'Reprovada'),
    ]

    viagem = models.OneToOneField(
        TravelRequest,
        on_delete=models.CASCADE,
        related_name='aprovacao',
        verbose_name='Viagem'
    )
    aprovador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'user_type__in': ['APROVADOR', 'ADMINISTRADOR']},
        verbose_name='Aprovador'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Status'
    )
    parecer = models.TextField(verbose_name='Parecer')
    data_aprovacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Aprovação')

    # Autorização de débito/crédito
    autoriza_debito_credito = models.BooleanField(
        default=False,
        verbose_name='Autoriza o débito/crédito conforme demonstrado'
    )

    class Meta:
        verbose_name = 'Aprovação'
        verbose_name_plural = 'Aprovações'

    def __str__(self):
        return f"{self.get_status_display()} - {self.viagem}"

    def save(self, *args, **kwargs):
        """Atualiza o status da viagem ao salvar a aprovação"""
        super().save(*args, **kwargs)
        self.viagem.status = self.status
        self.viagem.save()


class Attachment(models.Model):
    """
    Comprovantes anexados (fotos, PDFs, etc)
    Cada despesa deve ter pelo menos um comprovante
    """
    TIPO_CHOICES = [
        ('COMPROVANTE_DESPESA', 'Comprovante de Despesa'),
        ('DOCUMENTO_VIAGEM', 'Documento da Viagem'),
        ('OUTRO', 'Outro'),
    ]

    viagem = models.ForeignKey(
        TravelRequest,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name='Viagem'
    )
    despesa = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comprovantes',
        verbose_name='Despesa'
    )
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default='COMPROVANTE_DESPESA',
        verbose_name='Tipo'
    )
    arquivo = models.FileField(
        upload_to='comprovantes/%Y/%m/%d/',
        verbose_name='Arquivo'
    )
    descricao = models.CharField(max_length=200, blank=True, verbose_name='Descrição')
    enviado_em = models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')

    class Meta:
        verbose_name = 'Anexo/Comprovante'
        verbose_name_plural = 'Anexos/Comprovantes'
        ordering = ['-enviado_em']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.arquivo.name}"
