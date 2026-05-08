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
