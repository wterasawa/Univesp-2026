from geopy.distance import geodesic
from .models import Crianca, Unidade, SugestaoCreche


def atualizar_sugestoes_proximidade(crianca):
    # Inicializa a lista antes para evitar erros
    lista_calculada = []

    # Check if the endereco exists before accessing its attributes
    if not hasattr(crianca, "endereco") or crianca.endereco is None:
        # Handle the case where there is no address (e.g., return early or log it)
        return

    # Now it's safe to check coordinates
    if not crianca.endereco.latitude or not crianca.endereco.longitude:
        return

    # Verifica se o crianca tem coordenadas. Se não tiver, para aqui.
    if not crianca.endereco.latitude or not crianca.endereco.longitude:
        return

    SugestaoCreche.objects.filter(crianca=crianca).delete()
    ponto_crianca = (crianca.endereco.latitude, crianca.endereco.longitude)

    # 2. Filtra apenas unidades que POSSUEM latitude e longitude (exclui as nulas)
    # .   Filtra acessando o campo através do relacionamento 'endereco'
    todas_unidades = Unidade.objects.exclude(endereco__latitude__isnull=True).exclude(
        endereco__longitude__isnull=True
    )

    for unidade in todas_unidades:
        # Busca as coordenadas dentro do objeto de endereço da unidade
        ponto_unidade = (unidade.endereco.latitude, unidade.endereco.longitude)
        dist = geodesic(ponto_crianca, ponto_unidade).km
        lista_calculada.append({"obj": unidade, "dist": dist})

    # 3. Limpar sugestões anteriores deste crianca
    SugestaoCreche.objects.filter(crianca=crianca).delete()

    # 4. Localização do crianca
    ponto_crianca = (crianca.endereco.latitude, crianca.endereco.longitude)

    # 5. Calcular distâncias para todas as unidades
    todas_unidades = Unidade.objects.all()
    lista_calculada = []

    for unidade in todas_unidades:
        if unidade.endereco.latitude and unidade.endereco.longitude:
            ponto_unidade = (unidade.endereco.latitude, unidade.endereco.longitude)
            dist = geodesic(ponto_crianca, ponto_unidade).km
            lista_calculada.append({"obj": unidade, "dist": dist})

    # 6. Ordenar e pegar as 3 menores
    top_3 = sorted(lista_calculada, key=lambda x: x["dist"])[:3]

    # 5. Gravar na nova tabela
    for item in top_3:
        SugestaoCreche.objects.create(
            crianca=crianca, unidade=item["obj"], distancia=item["dist"]
        )


"""


from django.db.models.signals import post_save
from django.dispatch import receiver
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from .models import Crianca
from .utils import atualizar_sugestoes_proximidade


@receiver(post_save, sender='creches.Endereco')
def preencher_latitude_longitude(sender, instance, created, **kwargs):

    from .models import Endereco

    # Verifica se latitude ou longitude estão vazios
    if not instance.latitude or not instance.longitude:
        
        # 1. Configura o geocodificador
        geolocator = Nominatim(user_agent="django_auto_geocoder")
        
        # 2. Monta o endereço (mesmo padrão do exemplo anterior)
        endereco_completo = f"{instance.logradouro}, {instance.numero}, {instance.bairro}, {instance.cidade} - {instance.estado}, {instance.cep}, Brazil"
        
        try:
            location = geolocator.geocode(endereco_completo)
            
            if location:
                # 3. Atualiza usando .update() para evitar o loop infinito do post_save
                Endereco.objects.filter(pk=instance.pk).update(
                    latitude=location.latitude,
                    longitude=location.longitude
                )
        except Exception as e:
            print(f"Erro na geocodificação automática: {e}")







esta rotina veio do signals.py


@receiver(post_save, sender=Crianca)

def ao_salvar_crianca(sender, instance, **kwargs):

    from .models import Endereco

    geolocator = Nominatim(user_agent="django_auto_geocoder")

    atualizar_sugestoes_proximidade(instance)

    # Verifique se a criança possui um endereço vinculado antes de acessar
    if instance.endereco:
        endereco = instance.endereco
        endereco_completo = f"{endereco.logradouro or ''}, {endereco.numero or ''}, {endereco.bairro or ''}, {endereco.cidade or ''}"
    
    # ... resto da sua lógica de geocodificação ...
    try:
            location = geolocator.geocode(endereco_completo)
            if location:
                # Só atualiza se o geocoder retornar algo válido
                Endereco.objects.filter(pk=instance.pk).update(
                    latitude=location.latitude,
                    longitude=location.longitude
                )
    except Exception as e:
            print(f"Erro na geocodificação: {e}")
"""
