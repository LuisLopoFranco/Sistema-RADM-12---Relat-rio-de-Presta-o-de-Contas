from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime
import csv

from .models import (
    User, TravelRequest, Expense, VehicleTrip,
    VehicleLog, Approval, Attachment, CostCenter
)
from .forms import (
    LoginForm, TravelRequestForm, ExpenseForm,
    VehicleTripForm, VehicleLogForm, ApprovalForm,
    AttachmentForm, ExpenseFormSet, VehicleTripFormSet,
    AttachmentFormSet
)


# ==================== AUTENTICAÇÃO ====================

def user_login(request):
    """View de login"""
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'travels/login.html', {'form': form})


def user_logout(request):
    """View de logout"""
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Dashboard principal - adaptado ao tipo de usuário"""
    user = request.user
    context = {
        'user': user,
    }

    if user.user_type == 'SOLICITANTE':
        # Solicitante: suas próprias viagens
        context['minhas_viagens'] = TravelRequest.objects.filter(
            solicitante=user
        ).order_by('-criado_em')[:10]

        context['total_viagens'] = TravelRequest.objects.filter(solicitante=user).count()
        context['viagens_pendentes'] = TravelRequest.objects.filter(
            solicitante=user, status='PENDENTE'
        ).count()
        context['viagens_aprovadas'] = TravelRequest.objects.filter(
            solicitante=user, status='APROVADA'
        ).count()

    elif user.user_type == 'APROVADOR':
        # Aprovador: viagens pendentes de aprovação
        context['viagens_para_aprovar'] = TravelRequest.objects.filter(
            aprovador=user, status='PENDENTE'
        ).order_by('-criado_em')

        context['total_pendentes'] = context['viagens_para_aprovar'].count()
        context['total_aprovadas'] = TravelRequest.objects.filter(
            aprovador=user, status='APROVADA'
        ).count()
        context['total_reprovadas'] = TravelRequest.objects.filter(
            aprovador=user, status='REPROVADA'
        ).count()

    elif user.user_type == 'ADMINISTRADOR':
        # Administrador: visão geral do sistema
        context['total_viagens'] = TravelRequest.objects.count()
        context['viagens_pendentes'] = TravelRequest.objects.filter(status='PENDENTE').count()
        context['viagens_aprovadas'] = TravelRequest.objects.filter(status='APROVADA').count()
        context['total_usuarios'] = User.objects.count()

        # Últimas viagens
        context['ultimas_viagens'] = TravelRequest.objects.all().order_by('-criado_em')[:10]

        # Estatísticas financeiras
        total_despesas = TravelRequest.objects.filter(
            status__in=['APROVADA', 'FINALIZADA']
        ).aggregate(
            total=Sum('despesas__valor')
        )['total'] or 0
        context['total_despesas'] = total_despesas

    return render(request, 'travels/dashboard.html', context)


# ==================== VIAGENS - SOLICITANTE ====================

@login_required
def minhas_viagens(request):
    """Lista de viagens do solicitante"""
    viagens = TravelRequest.objects.filter(solicitante=request.user).order_by('-criado_em')
    return render(request, 'travels/minhas_viagens.html', {'viagens': viagens})


@login_required
def criar_viagem(request):
    """Criar nova requisição de viagem"""
    if request.method == 'POST':
        form = TravelRequestForm(request.POST)
        if form.is_valid():
            viagem = form.save(commit=False)
            viagem.solicitante = request.user
            viagem.save()
            messages.success(request, 'Viagem criada com sucesso!')
            return redirect('editar_viagem', pk=viagem.pk)
    else:
        form = TravelRequestForm()

    return render(request, 'travels/criar_viagem.html', {'form': form})


@login_required
def editar_viagem(request, pk):
    """Editar viagem e adicionar despesas/veículos/anexos"""
    viagem = get_object_or_404(TravelRequest, pk=pk)

    # Verificar permissão
    if viagem.solicitante != request.user and request.user.user_type != 'ADMINISTRADOR':
        messages.error(request, 'Você não tem permissão para editar esta viagem.')
        return redirect('dashboard')

    # Não permitir edição se já foi aprovada/reprovada
    if viagem.status in ['APROVADA', 'REPROVADA', 'FINALIZADA']:
        messages.warning(request, 'Esta viagem não pode mais ser editada.')
        return redirect('detalhe_viagem', pk=pk)

    if request.method == 'POST':
        form = TravelRequestForm(request.POST, instance=viagem)
        expense_formset = ExpenseFormSet(request.POST, instance=viagem)
        vehicle_formset = VehicleTripFormSet(request.POST, instance=viagem)

        if form.is_valid() and expense_formset.is_valid() and vehicle_formset.is_valid():
            form.save()
            expense_formset.save()
            vehicle_formset.save()
            messages.success(request, 'Viagem atualizada com sucesso!')
            return redirect('editar_viagem', pk=pk)
    else:
        form = TravelRequestForm(instance=viagem)
        expense_formset = ExpenseFormSet(instance=viagem)
        vehicle_formset = VehicleTripFormSet(instance=viagem)

    context = {
        'form': form,
        'expense_formset': expense_formset,
        'vehicle_formset': vehicle_formset,
        'viagem': viagem,
    }

    return render(request, 'travels/editar_viagem.html', context)


@login_required
def detalhe_viagem(request, pk):
    """Visualizar detalhes da viagem"""
    viagem = get_object_or_404(TravelRequest, pk=pk)

    # Verificar permissão
    pode_ver = (
        viagem.solicitante == request.user or
        viagem.aprovador == request.user or
        request.user.user_type == 'ADMINISTRADOR'
    )

    if not pode_ver:
        messages.error(request, 'Você não tem permissão para ver esta viagem.')
        return redirect('dashboard')

    context = {
        'viagem': viagem,
        'despesas': viagem.despesas.all(),
        'veiculos': viagem.viagens_veiculo.all(),
        'anexos': viagem.anexos.all(),
        'total_despesas': viagem.calcular_total_despesas(),
        'saldo': viagem.calcular_saldo(),
        'reembolso': viagem.calcular_reembolso(),
        'restituicao': viagem.calcular_restituicao(),
    }

    return render(request, 'travels/detalhe_viagem.html', context)


@login_required
def submeter_viagem(request, pk):
    """Submeter viagem para aprovação"""
    viagem = get_object_or_404(TravelRequest, pk=pk, solicitante=request.user)

    if viagem.status != 'RASCUNHO':
        messages.warning(request, 'Esta viagem já foi submetida.')
        return redirect('detalhe_viagem', pk=pk)

    # Validar se tem despesas
    if not viagem.despesas.exists():
        messages.error(request, 'Adicione pelo menos uma despesa antes de submeter.')
        return redirect('editar_viagem', pk=pk)

    viagem.status = 'PENDENTE'
    viagem.save()
    messages.success(request, 'Viagem submetida para aprovação!')

    return redirect('detalhe_viagem', pk=pk)


@login_required
def upload_comprovante(request, viagem_pk):
    """Upload de comprovantes para a viagem"""
    viagem = get_object_or_404(TravelRequest, pk=viagem_pk)

    # Verificar permissão
    if viagem.solicitante != request.user and request.user.user_type != 'ADMINISTRADOR':
        messages.error(request, 'Você não tem permissão para fazer upload.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.viagem = viagem
            anexo.save()
            messages.success(request, 'Comprovante enviado com sucesso!')
            return redirect('editar_viagem', pk=viagem_pk)
    else:
        form = AttachmentForm()

    return render(request, 'travels/upload_comprovante.html', {
        'form': form,
        'viagem': viagem
    })


# ==================== APROVAÇÕES - APROVADOR ====================

@login_required
def viagens_para_aprovar(request):
    """Lista de viagens pendentes de aprovação"""
    if request.user.user_type not in ['APROVADOR', 'ADMINISTRADOR']:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')

    viagens = TravelRequest.objects.filter(
        aprovador=request.user,
        status='PENDENTE'
    ).order_by('-criado_em')

    return render(request, 'travels/viagens_para_aprovar.html', {'viagens': viagens})


@login_required
def aprovar_viagem(request, pk):
    """Aprovar ou reprovar viagem"""
    viagem = get_object_or_404(TravelRequest, pk=pk)

    # Verificar permissão
    if viagem.aprovador != request.user and request.user.user_type != 'ADMINISTRADOR':
        messages.error(request, 'Você não tem permissão para aprovar esta viagem.')
        return redirect('dashboard')

    if viagem.status != 'PENDENTE':
        messages.warning(request, 'Esta viagem já foi processada.')
        return redirect('detalhe_viagem', pk=pk)

    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            aprovacao = form.save(commit=False)
            aprovacao.viagem = viagem
            aprovacao.aprovador = request.user
            aprovacao.save()

            # Atualizar status da viagem
            viagem.status = aprovacao.status
            viagem.save()

            messages.success(request, f'Viagem {aprovacao.get_status_display().lower()} com sucesso!')
            return redirect('viagens_para_aprovar')
    else:
        form = ApprovalForm()

    context = {
        'form': form,
        'viagem': viagem,
        'total_despesas': viagem.calcular_total_despesas(),
        'saldo': viagem.calcular_saldo(),
        'reembolso': viagem.calcular_reembolso(),
        'restituicao': viagem.calcular_restituicao(),
    }

    return render(request, 'travels/aprovar_viagem.html', context)


# ==================== RELATÓRIOS - ADMINISTRADOR ====================

@login_required
def relatorios(request):
    """Dashboard de relatórios para administradores"""
    if request.user.user_type != 'ADMINISTRADOR':
        messages.error(request, 'Você não tem permissão para acessar relatórios.')
        return redirect('dashboard')

    # Estatísticas gerais
    total_viagens = TravelRequest.objects.count()
    viagens_por_status = TravelRequest.objects.values('status').annotate(
        total=Count('id')
    )

    # Total de despesas por categoria
    despesas_por_categoria = Expense.objects.values('categoria').annotate(
        total=Sum('valor')
    ).order_by('-total')

    # Uso de veículos
    uso_veiculos = VehicleTrip.objects.values('tipo_veiculo').annotate(
        total_km=Sum('km_rodado'),
        total_custo=Sum('custo_calculado')
    )

    # Viagens por centro de custo
    viagens_por_centro = TravelRequest.objects.values(
        'centro_custo__nome'
    ).annotate(
        total=Count('id'),
        total_despesas=Sum('despesas__valor')
    ).order_by('-total')

    context = {
        'total_viagens': total_viagens,
        'viagens_por_status': viagens_por_status,
        'despesas_por_categoria': despesas_por_categoria,
        'uso_veiculos': uso_veiculos,
        'viagens_por_centro': viagens_por_centro,
    }

    return render(request, 'travels/relatorios.html', context)


@login_required
def relatorio_detalhado(request):
    """Relatório detalhado com filtros"""
    if request.user.user_type != 'ADMINISTRADOR':
        messages.error(request, 'Você não tem permissão para acessar relatórios.')
        return redirect('dashboard')

    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status')
    centro_custo = request.GET.get('centro_custo')

    viagens = TravelRequest.objects.all()

    if data_inicio:
        viagens = viagens.filter(data_saida__gte=data_inicio)
    if data_fim:
        viagens = viagens.filter(data_saida__lte=data_fim)
    if status:
        viagens = viagens.filter(status=status)
    if centro_custo:
        viagens = viagens.filter(centro_custo_id=centro_custo)

    viagens = viagens.order_by('-data_saida')

    # Calcular totais
    total_adiantamento = sum([v.adiantamento for v in viagens])
    total_despesas = sum([v.calcular_total_despesas() for v in viagens])
    total_reembolso = sum([v.calcular_reembolso() for v in viagens])
    total_restituicao = sum([v.calcular_restituicao() for v in viagens])

    context = {
        'viagens': viagens,
        'centros_custo': CostCenter.objects.filter(ativo=True),
        'total_adiantamento': total_adiantamento,
        'total_despesas': total_despesas,
        'total_reembolso': total_reembolso,
        'total_restituicao': total_restituicao,
        'filtros': {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'status': status,
            'centro_custo': centro_custo,
        }
    }

    return render(request, 'travels/relatorio_detalhado.html', context)


@login_required
def exportar_relatorio_csv(request):
    """Exportar relatório para CSV"""
    if request.user.user_type != 'ADMINISTRADOR':
        messages.error(request, 'Você não tem permissão para exportar relatórios.')
        return redirect('dashboard')

    # Obter filtros da query string
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    status = request.GET.get('status')
    centro_custo = request.GET.get('centro_custo')

    viagens = TravelRequest.objects.all()

    if data_inicio:
        viagens = viagens.filter(data_saida__gte=data_inicio)
    if data_fim:
        viagens = viagens.filter(data_saida__lte=data_fim)
    if status:
        viagens = viagens.filter(status=status)
    if centro_custo:
        viagens = viagens.filter(centro_custo_id=centro_custo)

    # Criar CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_viagens_{datetime.now().strftime("%Y%m%d")}.csv"'
    response.write('\ufeff')  # BOM para UTF-8

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Solicitante', 'Cargo', 'Centro de Custo', 'Destino',
        'Data Saída', 'Data Chegada', 'Motivo', 'Status',
        'Adiantamento', 'Total Despesas', 'Saldo', 'Reembolso', 'Restituição',
        'Aprovador', 'Data Aprovação'
    ])

    for viagem in viagens:
        aprovacao = getattr(viagem, 'aprovacao', None)
        writer.writerow([
            viagem.solicitante.get_full_name(),
            viagem.solicitante.cargo,
            str(viagem.centro_custo),
            viagem.destino,
            viagem.data_saida.strftime('%d/%m/%Y'),
            viagem.data_chegada.strftime('%d/%m/%Y'),
            viagem.get_classificacao_motivo_display(),
            viagem.get_status_display(),
            f'{viagem.adiantamento:.2f}'.replace('.', ','),
            f'{viagem.calcular_total_despesas():.2f}'.replace('.', ','),
            f'{viagem.calcular_saldo():.2f}'.replace('.', ','),
            f'{viagem.calcular_reembolso():.2f}'.replace('.', ','),
            f'{viagem.calcular_restituicao():.2f}'.replace('.', ','),
            viagem.aprovador.get_full_name(),
            aprovacao.data_aprovacao.strftime('%d/%m/%Y %H:%M') if aprovacao else ''
        ])

    return response


@login_required
def imprimir_relatorio(request, pk):
    """Gerar versão para impressão do relatório de viagem"""
    viagem = get_object_or_404(TravelRequest, pk=pk)

    # Verificar permissão
    pode_ver = (
        viagem.solicitante == request.user or
        viagem.aprovador == request.user or
        request.user.user_type == 'ADMINISTRADOR'
    )

    if not pode_ver:
        messages.error(request, 'Você não tem permissão para imprimir esta viagem.')
        return redirect('dashboard')

    context = {
        'viagem': viagem,
        'despesas': viagem.despesas.all(),
        'veiculos': viagem.viagens_veiculo.all(),
        'total_despesas': viagem.calcular_total_despesas(),
        'saldo': viagem.calcular_saldo(),
        'reembolso': viagem.calcular_reembolso(),
        'restituicao': viagem.calcular_restituicao(),
        'aprovacao': getattr(viagem, 'aprovacao', None),
    }

    return render(request, 'travels/imprimir_relatorio.html', context)
