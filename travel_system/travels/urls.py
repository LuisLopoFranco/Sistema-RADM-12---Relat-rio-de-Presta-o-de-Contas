from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Viagens - Solicitante
    path('viagens/', views.minhas_viagens, name='minhas_viagens'),
    path('viagens/criar/', views.criar_viagem, name='criar_viagem'),
    path('viagens/<int:pk>/', views.detalhe_viagem, name='detalhe_viagem'),
    path('viagens/<int:pk>/editar/', views.editar_viagem, name='editar_viagem'),
    path('viagens/<int:pk>/submeter/', views.submeter_viagem, name='submeter_viagem'),
    path('viagens/<int:viagem_pk>/upload/', views.upload_comprovante, name='upload_comprovante'),

    # Aprovações - Aprovador
    path('aprovar/', views.viagens_para_aprovar, name='viagens_para_aprovar'),
    path('aprovar/<int:pk>/', views.aprovar_viagem, name='aprovar_viagem'),

    # Relatórios - Administrador
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/detalhado/', views.relatorio_detalhado, name='relatorio_detalhado'),
    path('relatorios/exportar/', views.exportar_relatorio_csv, name='exportar_relatorio_csv'),
    path('relatorios/imprimir/<int:pk>/', views.imprimir_relatorio, name='imprimir_relatorio'),
]
