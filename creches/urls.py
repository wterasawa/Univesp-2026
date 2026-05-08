from django.urls import path
from . import views
import creches

urlpatterns = [
    path("", creches.views.home, name="home"),
    path("cadastro/", creches.views.cadastrar_crianca, name="cadastro"),
    path("listagem/", creches.views.Listagem.as_view(), name="listagem"),
    path("atualiza/<int:pk>", creches.views.atualiza, name="atualiza"),
    path("exclusao/<int:pk>", creches.views.confirmar_exclusao_crianca, name="delete"),
    path("unidade/list", creches.views.UnidadeListView.as_view(), name="unidade_list"),
    path("unidade/cadastro", creches.views.unidade_cadastrar, name="unidade_cadastro"),
    path("unidade/atualiza/<int:pk>", creches.views.unidade_atualizar, name="unidade_atualiza"),
    path("unidade/exclusao/<int:pk>", creches.views.confirmar_exclusao_unidade, name="unidade_delete"),
    path("distr_vagas/", creches.views.listavagas, name="distr_vagas"),
    path("calcular-vagas/<int:pk>/", views.calcular_vagas_manual, name="calcular_vagas_manual"),
    path("criancas_vagas/", creches.views.processar_ranking_manual, name="criancas_vagas"),
    path("coord_vazias/", creches.views.verificar_coordenadas_faltantes, name="coord_vazias"),
    path('pesquisar_ceps', views.pesquisar_ceps_faltantes, name='pesquisar_ceps_faltantes'),
    path('ceps/confirmar/<int:pk>/', views.confirmar_cep, name='confirmar_cep'),
    path('proximidade/por-creche/', views.criancas_por_creche, name='criancas_por_creche'),
    path("listagem_criancas", creches.views.listagem_criancas, name="listagem_criancas"),
#    path("sucesso/", creches.views.sucesso, name="sucesso"),
]
