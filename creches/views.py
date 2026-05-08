from django.shortcuts import render, redirect, get_object_or_404
from creches.forms import CriancaForm, EnderecoForm, FamiliaForm, UnidadeForm
from django.views.generic import ListView
from .models import Crianca, Endereco, Familia, Unidade
from .models import SugestaoCreche, Distrib_Vagas
from django.contrib import messages
from django.db import transaction
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from .utils import atualizar_sugestoes_proximidade
from django.db.models import Q
from .models import RankingProximidade
from django.utils import timezone
from .models import Crianca
from .models import Unidade, RankingProximidade

# página de início
def home(request):
    return render(request, "home.html")

#listagem das crianças
class Listagem(ListView):
    model = Crianca
    template_name = "listagem.html"
    context_object_name = "criancas"

    def get_queryset(self):
        # 1. Começamos com todos os objetos
        queryset = Crianca.objects.all()

        # 2. Recuperamos TODOS os parâmetros do GET (Filtros + Ordenação)
        nome = self.request.GET.get('nome')
        etapa = self.request.GET.get('etapa')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        ordenar_por = self.request.GET.get('ordenar', 'nome') # Padrão: nome

        # 3. Aplicamos os Filtros (se existirem)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if etapa and etapa != "":
            queryset = queryset.filter(etapa=etapa)
        if data_inicio:
            queryset = queryset.filter(data_nascimento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_nascimento__lte=data_fim)

        # 4. Aplicamos a Ordenação por último
        # Isso garante que os dados filtrados sejam exibidos na ordem escolhida
        return queryset.order_by(ordenar_por)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # O total deve respeitar os filtros aplicados
        context['total'] = self.get_queryset().count()
        return context    
    

def listagem_criancas(request):
    queryset = Crianca.objects.all().order_by('nome')
    
    nome_pesquisa = request.GET.get('nome')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    etapa_pesquisa = request.GET.get('etapa')

    # Filtros - O Django vai acumulando as queries
    if nome_pesquisa:
        queryset = queryset.filter(nome__icontains=nome_pesquisa)

    if etapa_pesquisa:
        queryset = queryset.filter(etapa=etapa_pesquisa)

    if data_inicio:
        queryset = queryset.filter(data_nascimento__gte=data_inicio)

    if data_fim:
        queryset = queryset.filter(data_nascimento__lte=data_fim)

    # Contagem para o feedback do usuário
    total_encontrado = queryset.count()

    return render(request, 'listagem.html', {
        'object_list': queryset, 
        'total': total_encontrado
    })

def atualiza(request, pk):

    # 1. Busca as instâncias existentes no banco
    crianca = get_object_or_404(Crianca, pk=pk)
    familia = crianca.familia
    endereco = crianca.endereco

    data = request.POST if request.method == "POST" else None

    form_crianca = CriancaForm(data, instance=crianca)
    form_familia = FamiliaForm(data, instance=familia)
    form_endereco = EnderecoForm(data, instance=endereco)

    if request.method == "POST":
        # O botão 'Salvar' dispara este bloco
        if (
            form_crianca.is_valid()
            and form_familia.is_valid()
            and form_endereco.is_valid()
        ):

            try:
                with transaction.atomic():
                    # Tudo aqui dentro ou acontece junto, ou nada acontece
                    f = form_familia.save()
                    e = form_endereco.save()

                    c = form_crianca.save(commit=False)
                    c.familia = f
                    c.endereco = e
                    c.save()

                    messages.success(request, "Dados gravados com sucesso")
                    return redirect("listagem")

            except Exception as err:
                # Caso ocorra algum erro inesperado no banco, você pode tratar aqui
                print(f"Erro ao salvar: {err}")

    return render(
    request,
    "update.html",
    {
        "form_crianca": form_crianca,
        "form_familia": form_familia,
        "form_endereco": form_endereco,
        "crianca": crianca,
    },
)


class UnidadeListView(ListView):
    model = Unidade
    template_name = "unidade_list.html"


def unidade_atualizar(request, pk):
    # 1. Busca as instâncias existentes no banco
    unidade = get_object_or_404(Unidade, pk=pk)
    endereco = unidade.endereco

    if request.method == "POST":
        form_unidade = UnidadeForm(request.POST, instance=unidade)
        form_endereco = EnderecoForm(request.POST, instance=endereco)

        if form_unidade.is_valid() and form_endereco.is_valid():
            form_unidade.save()
            form_endereco.save()

            messages.success(request, "Dados gravados com sucesso")
            return redirect("unidade_list")  # ou o nome da sua URL de sucesso
    else:
        # Carrega os formulários já preenchidos com os dados do banco
        form_unidade = UnidadeForm(instance=unidade)
        form_endereco = EnderecoForm(instance=endereco)

    return render(
        request,
        "unidade_atualiza.html",
        {
            "form_unidade": form_unidade,
            "form_endereco": form_endereco,
            "unidade": unidade,
        },
    )


def sucesso(request):
    return render(request, "sucesso")


def cadastrar_crianca(request):
    if request.method == "POST":
        form_crianca = CriancaForm(request.POST)
        form_familia = FamiliaForm(request.POST)
        form_endereco = EnderecoForm(request.POST)

        if (
            form_crianca.is_valid()
            and form_endereco.is_valid()
            and form_familia.is_valid()
        ):
            endereco = form_endereco.save()
            familia = form_familia.save()

            crianca = form_crianca.save(commit=False)
            crianca.endereco = endereco
            crianca.familia = familia
            crianca.save()

            messages.success(request, "Dados gravados com sucesso")
            return redirect("home")

    else:
        form_crianca = CriancaForm()
        form_endereco = EnderecoForm()
        form_familia = FamiliaForm()

    return render(
        request,
        "cadastro.html",
        {
            "form_crianca": form_crianca,
            "form_endereco": form_endereco,
            "form_familia": form_familia,
        },
    )

def unidade_cadastrar(request):
    if request.method == "POST":
        form_unidade = UnidadeForm(request.POST)
        form_endereco = EnderecoForm(request.POST)

        if form_unidade.is_valid() and form_endereco.is_valid():
            # 1. Cria a instância do endereço sem salvar no banco ainda
            endereco = form_endereco.save(commit=False)

            # 2. Lógica de Geocodificação
            try:
                geolocator = Nominatim(user_agent="meu_app_django")
                # Monta a string de busca baseada nos campos do seu model Endereco
                # Exemplo: "Rua X, Número, Cidade, Estado, Brasil"
                endereco_completo = f"{endereco.logradouro}, {endereco.numero}, {endereco.bairro}, {endereco.cep}, {endereco.cidade}, {endereco.estado}, Brasil"

                location = geolocator.geocode(endereco_completo)

                if location:
                    endereco.latitude = location.latitude
                    endereco.longitude = location.longitude
            except Exception as e:
                # É boa prática tratar erros de conexão ou timeout da API
                print(f"Erro na geocodificação: {e}")

            # 3. Agora salva o endereço com as coordenadas (se encontradas)
            endereco.save()

            unidade = form_unidade.save(commit=False)
            unidade.endereco = endereco
            unidade.save()

            messages.success(request, "Dados gravados com sucesso")
            return redirect(home)

    else:
        form_unidade = UnidadeForm()
        form_endereco = EnderecoForm()

    return render(
        request,
        "unidade_cadastro.html",
        {
            "form_unidade": form_unidade,
            "form_endereco": form_endereco,
        },
    )


def confirmar_exclusao_crianca(request, pk):
    crianca = get_object_or_404(Crianca, pk=pk)

    if request.method == "POST":
        crianca.delete()
        return redirect("listagem")  # Redireciona após excluir

    return render(request, "confirmar_delete.html", {"crianca": crianca})


def confirmar_exclusao_unidade(request, pk):
    unidade = get_object_or_404(Unidade, pk=pk)

    if request.method == "POST":
        unidade.delete()
        return redirect("unidade_list")  # Redireciona após excluir

    return render(request, "unidade_confirmar_delete.html", {"unidade": unidade})


def listavagas(request):
    # Lógica para buscar as vagas ou sugestões
    sugestoes = SugestaoCreche.objects.all()
    return render(request, "distrib_vagas.html", {"sugestoes": sugestoes})



def calcular_vagas_manual(request, pk):
    crianca = get_object_or_404(Crianca, pk=pk)
    # Chama a sua função de cálculo que corrigimos antes
    atualizar_sugestoes_proximidade(crianca)
    return redirect("distr_vagas")  # Redireciona para a lista de vagas


def processar_ranking_manual(request):
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                # 1. Limpa o ranking atual
                RankingProximidade.objects.all().delete()
                # Busca o primeiro registro ou cria um novo se não existir
                obj_tuple = Distrib_Vagas.objects.get_or_create(id=1)
                ultima_rev = obj_tuple[0]
                created = obj_tuple[1]

                ultima_rev.ultima_rev = timezone.now()
                ultima_rev.save()
                
                # 2. Otimiza a busca com select_related (evita o problema de N+1 consultas)
                criancas = Crianca.objects.select_related('endereco').exclude(
                    endereco__latitude__isnull=True,
                    endereco__longitude__isnull=True
                )
                unidades = Unidade.objects.select_related('endereco').all()
                
                count_criancas = 0

                for crianca in criancas:
                    distancias = []
                    # Pega coordenadas da criança
                    coord_c = (crianca.endereco.latitude, crianca.endereco.longitude)

                    for unidade in unidades:
                        coord_u = (unidade.endereco.latitude, unidade.endereco.longitude)
                        
                        # Cálculo via GeoPy
                        dist = geodesic(coord_c, coord_u).km
                        distancias.append((dist, unidade))

                    # Ordena e pega as 3 mais próximas
                    distancias.sort(key=lambda x: x[0])
                    top_3 = distancias[:3]

                    # Grava os resultados
                    for i, (distancia, unidade) in enumerate(top_3, start=1):
                        RankingProximidade.objects.create(
                            crianca=crianca,
                            unidade=unidade,
                            distancia_km=round(distancia, 2),
                            posicao=i
                        )
                    count_criancas += 1
                messages.success(request, f"Sucesso! {count_criancas} crianças foram processadas.")
        
        except Exception as e:
            messages.error(request, f"Erro ao processar: {e}")
            
        return redirect('home')
    
    rankings = RankingProximidade.objects.select_related('crianca', 'unidade').all()[:50]
    
    # Busca a data para exibir no banner azul
    info_revisao = Distrib_Vagas.objects.first() 

    return render(request, 'criancas_vagas.html', {
        'rankings': rankings,
        'ultima_distribuicao': info_revisao
    })
    

def verificar_coordenadas_faltantes(request):

    todos_enderecos = Endereco.objects.all()

    for e in todos_enderecos:
        print(f"Rua: {e.logradouro} | Lat: {repr(e.latitude)} | Lon: {repr(e.longitude)}")
        
            # Filtra crianças cujo endereço associado tem lat ou lon null
        criancas_sem_coord = Crianca.objects.filter(
                Q(endereco__latitude__isnull=True) | 
                Q(endereco__longitude__isnull=True) |
                Q(endereco__latitude=0) | 
                Q(endereco__longitude=0)
            ).select_related('endereco')

            # Filtra unidades cujo endereço associado tem lat ou lon null
        unidades_sem_coord = Unidade.objects.filter(
                Q(endereco__latitude__isnull=True) | 
                Q(endereco__longitude__isnull=True) |
                Q(endereco__latitude=0) | 
                Q(endereco__longitude=0)
            ).select_related('endereco')

        context = {
                'criancas_erro': criancas_sem_coord,
                'unidades_erro': unidades_sem_coord,
                'total_erros': criancas_sem_coord.count() + unidades_sem_coord.count()
            }
        
        return render(request, 'coord_vazias.html', context)
        
    return

def pesquisar_ceps_faltantes(request):
    # Filtra endereços onde o CEP está nulo ou vazio
    enderecos_sem_cep = Endereco.objects.filter(cep__isnull=True) | Endereco.objects.filter(cep="")
    
    geolocator = Nominatim(user_agent="vagas_creches_app")
    sugestoes = []

    for endereco in enderecos_sem_cep:
        # Monta uma string de busca: "Logradouro, Numero, Cidade, Estado"
        query = f"{endereco.logradouro}, {endereco.numero}, {endereco.bairro}, {endereco.cidade}, Brazil"
        
        try:
            location = geolocator.geocode(query, addressdetails=True)
            if location and 'postcode' in location.raw['address']:
                cep_encontrado = location.raw['address']['postcode']
                # Remove o hífen se preferir salvar apenas números
                # cep_limpo = cep_encontrado.replace("-", "")
                
                sugestoes.append({
                    'id': endereco.pk,
                    'logradouro': endereco.logradouro,
                    'cidade': endereco.cidade,
                    'cep_sugerido': cep_encontrado  # cep_limpo
                })
        except Exception as e:
            print(f"Erro ao buscar CEP para {endereco.logradouro}: {e}")

    return render(request, 'pesquisar_ceps.html', {'sugestoes': sugestoes})

def confirmar_cep(request, pk):
    if request.method == "POST":
        cep_valor = request.POST.get('cep_sugerido')
        endereco = Endereco.objects.get(pk=pk)
        endereco.cep = cep_valor
        endereco.save()
        messages.success(request, f"CEP {cep_valor} atualizado para {endereco.logradouro}!")
    return redirect('pesquisar_ceps_faltantes')


def criancas_por_creche(request):
    unidades = Unidade.objects.all().order_by('nome_unidade')
    ranking_filtrado = None
    unidade_selecionada = None

    # Captura os dados enviados pelo formulário (GET)
    unidade_id = request.GET.get('unidade')
    etapa_selecionada = request.GET.get('etapa')

    if unidade_id:
        try:
            unidade_selecionada = Unidade.objects.get(id=unidade_id)
            
            # 1. Filtro base por unidade + segurança contra crianças apagadas
            queryset = RankingProximidade.objects.filter(
                unidade_id=unidade_id,
                crianca__isnull=False
            )
            
            # 2. Se o usuário escolheu uma etapa específica, aplicamos o filtro
            # Verifique se a etapa foi selecionada e se não é um valor vazio
            if etapa_selecionada and etapa_selecionada != "":
                queryset = queryset.filter(crianca__etapa=etapa_selecionada)

            # 3. Carregamos os dados relacionados (otimização de performance)
            ranking_filtrado = queryset.select_related('crianca', 'crianca__endereco').order_by('distancia_km')
            
        except Unidade.DoesNotExist:
            unidade_selecionada = None

    context = {
        'unidades': unidades,
        'ranking': ranking_filtrado,
        'unidade_selecionada': unidade_selecionada,
        'etapa_atual': etapa_selecionada,
    }
    return render(request, 'criancas_por_creche.html', context)
