from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, CostCenter, TravelRequest, Expense,
    VehicleType, VehicleTrip, VehicleLog, Approval, Attachment
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administração de usuários customizada"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'cargo', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'cargo']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('user_type', 'cargo', 'telefone')
        }),
        ('Dados Bancários', {
            'fields': ('conta_corrente', 'agencia', 'banco')
        }),
    )


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    """Administração de Centros de Custo"""
    list_display = ['codigo', 'nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['codigo', 'nome']


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    """Administração de Tipos de Veículo"""
    list_display = ['nome', 'consumo_km_litro', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    fieldsets = (
        (None, {
            'fields': ('nome', 'consumo_km_litro', 'ativo')
        }),
        ('Informações Adicionais', {
            'fields': ('descricao',),
            'classes': ('collapse',)
        }),
    )


class ExpenseInline(admin.TabularInline):
    """Inline para despesas na viagem"""
    model = Expense
    extra = 1
    fields = ['categoria', 'descricao', 'valor', 'data_despesa']


class VehicleTripInline(admin.TabularInline):
    """Inline para viagens de veículo"""
    model = VehicleTrip
    extra = 0
    fields = ['tipo_veiculo', 'placa', 'km_rodado', 'valor_litro', 'custo_calculado']
    readonly_fields = ['custo_calculado']


class AttachmentInline(admin.TabularInline):
    """Inline para anexos"""
    model = Attachment
    extra = 1
    fields = ['tipo', 'arquivo', 'descricao']


@admin.register(TravelRequest)
class TravelRequestAdmin(admin.ModelAdmin):
    """Administração de Requisições de Viagem"""
    list_display = [
        'solicitante', 'destino', 'data_saida', 'data_chegada',
        'status', 'aprovador', 'criado_em'
    ]
    list_filter = ['status', 'classificacao_motivo', 'data_saida', 'centro_custo']
    search_fields = ['solicitante__first_name', 'solicitante__last_name', 'destino', 'motivo']
    date_hierarchy = 'data_saida'

    fieldsets = (
        ('Solicitante', {
            'fields': ('solicitante', 'centro_custo')
        }),
        ('Informações da Viagem', {
            'fields': (
                'trecho_original', 'trecho_alterado', 'destino',
                'motivo', 'classificacao_motivo', 'outro_motivo_descricao'
            )
        }),
        ('Datas', {
            'fields': ('data_autorizacao', 'data_saida', 'data_chegada')
        }),
        ('Aprovação e Financeiro', {
            'fields': ('aprovador', 'adiantamento', 'status')
        }),
    )

    inlines = [ExpenseInline, VehicleTripInline, AttachmentInline]

    def get_readonly_fields(self, request, obj=None):
        """Não permitir editar status se já foi aprovada/reprovada"""
        if obj and obj.status in ['APROVADA', 'REPROVADA']:
            return ['status']
        return []


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Administração de Despesas"""
    list_display = ['viagem', 'categoria', 'descricao', 'valor', 'data_despesa']
    list_filter = ['categoria', 'data_despesa']
    search_fields = ['viagem__solicitante__first_name', 'descricao']
    date_hierarchy = 'data_despesa'


class VehicleLogInline(admin.TabularInline):
    """Inline para logs de veículo"""
    model = VehicleLog
    extra = 1
    fields = [
        'data', 'hora_saida', 'hora_chegada',
        'hodometro_saida', 'hodometro_chegada', 'km_rodado',
        'roteiro', 'condutor'
    ]
    readonly_fields = ['km_rodado']


@admin.register(VehicleTrip)
class VehicleTripAdmin(admin.ModelAdmin):
    """Administração de Viagens com Veículo"""
    list_display = ['viagem', 'tipo_veiculo', 'placa', 'km_rodado', 'custo_calculado']
    list_filter = ['tipo_veiculo']
    search_fields = ['viagem__solicitante__first_name', 'placa', 'modelo']

    readonly_fields = ['custo_calculado']
    inlines = [VehicleLogInline]


@admin.register(VehicleLog)
class VehicleLogAdmin(admin.ModelAdmin):
    """Administração de Logs de Veículo"""
    list_display = [
        'viagem_veiculo', 'data', 'hora_saida', 'hora_chegada',
        'km_rodado', 'condutor'
    ]
    list_filter = ['data']
    search_fields = ['roteiro', 'condutor']
    date_hierarchy = 'data'

    readonly_fields = ['km_rodado']


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    """Administração de Aprovações"""
    list_display = ['viagem', 'aprovador', 'status', 'data_aprovacao', 'autoriza_debito_credito']
    list_filter = ['status', 'data_aprovacao']
    search_fields = ['viagem__solicitante__first_name', 'parecer']
    date_hierarchy = 'data_aprovacao'

    readonly_fields = ['data_aprovacao']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Administração de Anexos"""
    list_display = ['viagem', 'despesa', 'tipo', 'arquivo', 'enviado_em']
    list_filter = ['tipo', 'enviado_em']
    search_fields = ['viagem__solicitante__first_name', 'descricao']
    date_hierarchy = 'enviado_em'
