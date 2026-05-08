from django.apps import AppConfig


class CrechesConfig(AppConfig):
    name = "creches"

    default_auto_field = "django.db.models.BigAutoField"
    name = "creches"  # Nome do seu app

    def ready(self):
        """
        Este método é executado quando o Django inicia.
        Importar o arquivo de signals aqui garante que os gatilhos
        sejam registrados corretamente no sistema.
        """
        import creches.signals  # Importação vital
