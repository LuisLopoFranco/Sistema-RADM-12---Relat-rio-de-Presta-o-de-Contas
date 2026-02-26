from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import (
    User, TravelRequest, Expense, VehicleTrip,
    VehicleLog, Approval, Attachment, CostCenter
)


class LoginForm(AuthenticationForm):
    """Formulário de Login customizado"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuário'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Formulário de registro de usuário"""
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'user_type', 'cargo', 'telefone',
            'conta_corrente', 'agencia', 'banco'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'conta_corrente': forms.TextInput(attrs={'class': 'form-control'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TravelRequestForm(forms.ModelForm):
    """Formulário para criar/editar requisição de viagem"""

    class Meta:
        model = TravelRequest
        fields = [
            'centro_custo', 'trecho_original', 'trecho_alterado', 'destino',
            'motivo', 'classificacao_motivo', 'outro_motivo_descricao',
            'data_autorizacao', 'data_saida', 'data_chegada',
            'aprovador', 'adiantamento'
        ]
        widgets = {
            'centro_custo': forms.Select(attrs={'class': 'form-control'}),
            'trecho_original': forms.TextInput(attrs={'class': 'form-control'}),
            'trecho_alterado': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'classificacao_motivo': forms.Select(attrs={'class': 'form-control'}),
            'outro_motivo_descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'data_autorizacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_saida': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_chegada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'aprovador': forms.Select(attrs={'class': 'form-control'}),
            'adiantamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Listar todos os aprovadores disponíveis
        self.fields['aprovador'].queryset = User.objects.filter(
            user_type='APROVADOR'
        )

    def clean(self):
        cleaned_data = super().clean()
        data_autorizacao = cleaned_data.get('data_autorizacao')
        data_saida = cleaned_data.get('data_saida')
        data_chegada = cleaned_data.get('data_chegada')

        # Validar datas
        if data_autorizacao and data_saida and data_autorizacao > data_saida:
            raise ValidationError('Data de autorização deve ser anterior à data de saída')

        if data_saida and data_chegada and data_saida > data_chegada:
            raise ValidationError('Data de saída deve ser anterior à data de chegada')

        # Validar descrição se classificação for "OUTRO"
        classificacao = cleaned_data.get('classificacao_motivo')
        outro_motivo = cleaned_data.get('outro_motivo_descricao')
        if classificacao == 'OUTRO' and not outro_motivo:
            raise ValidationError('Descrição é obrigatória quando classificação for "Outro"')

        return cleaned_data


class ExpenseForm(forms.ModelForm):
    """Formulário para adicionar despesas"""

    class Meta:
        model = Expense
        fields = ['categoria', 'descricao', 'valor', 'data_despesa']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'data_despesa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Se nenhum campo foi preenchido, pular validação (formulário extra vazio)
        if not any(cleaned_data.get(f) for f in ['categoria', 'descricao', 'valor', 'data_despesa']):
            return cleaned_data

        categoria = cleaned_data.get('categoria')
        descricao = cleaned_data.get('descricao')

        if categoria == 'OUTRAS' and not descricao:
            raise ValidationError('Descrição é obrigatória para categoria "Outras"')

        return cleaned_data


class VehicleTripForm(forms.ModelForm):
    """Formulário para adicionar viagem com veículo próprio"""

    class Meta:
        model = VehicleTrip
        fields = ['tipo_veiculo', 'placa', 'modelo', 'km_rodado', 'valor_litro']
        widgets = {
            'tipo_veiculo': forms.Select(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ABC-1234'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'km_rodado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valor_litro': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Se nenhum campo foi preenchido, pular validação (formulário extra vazio)
        if not any(cleaned_data.get(f) for f in ['tipo_veiculo', 'placa', 'modelo', 'km_rodado', 'valor_litro']):
            return cleaned_data
        return cleaned_data


class VehicleLogForm(forms.ModelForm):
    """Formulário para log de uso do veículo"""

    class Meta:
        model = VehicleLog
        fields = [
            'data', 'hora_saida', 'hora_chegada',
            'hodometro_saida', 'hodometro_chegada',
            'roteiro', 'objetivo', 'condutor', 'visto'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_saida': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_chegada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hodometro_saida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'hodometro_chegada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'roteiro': forms.TextInput(attrs={'class': 'form-control'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'condutor': forms.TextInput(attrs={'class': 'form-control'}),
            'visto': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ApprovalForm(forms.ModelForm):
    """Formulário para aprovação/reprovação de viagem"""

    class Meta:
        model = Approval
        fields = ['status', 'parecer', 'autoriza_debito_credito']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'parecer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'autoriza_debito_credito': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AttachmentForm(forms.ModelForm):
    """Formulário para upload de anexos/comprovantes"""

    class Meta:
        model = Attachment
        fields = ['tipo', 'arquivo', 'descricao']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CostCenterForm(forms.ModelForm):
    """Formulário para centros de custo"""

    class Meta:
        model = CostCenter
        fields = ['codigo', 'nome', 'descricao', 'ativo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Formsets para adicionar múltiplas despesas/anexos de uma vez
from django.forms import inlineformset_factory

ExpenseFormSet = inlineformset_factory(
    TravelRequest,
    Expense,
    form=ExpenseForm,
    extra=3,
    can_delete=True
)

VehicleTripFormSet = inlineformset_factory(
    TravelRequest,
    VehicleTrip,
    form=VehicleTripForm,
    extra=1,
    can_delete=True
)

AttachmentFormSet = inlineformset_factory(
    TravelRequest,
    Attachment,
    form=AttachmentForm,
    extra=3,
    can_delete=True
)
