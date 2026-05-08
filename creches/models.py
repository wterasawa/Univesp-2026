from django.db import models


class Endereco(models.Model):
    logradouro = models.CharField(
        max_length=100, verbose_name="Logradouro (rua, avenida, etc.)"
    )
    numero = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="Número"
    )
    complemento = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Complemento"
    )
    bairro = models.CharField(
        blank=True, null=True, max_length=50, verbose_name="Bairro"
    )
    cep = models.CharField(blank=True, null=True, max_length=9, verbose_name="CEP")
    cidade = models.CharField(max_length=50, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.bairro}, {self.cep}"


class Familia(models.Model):
    mae = models.CharField(max_length=100)
    mae = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Nome da Mãe"
    )
    pai = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Nome do Pai"
    )
    renda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Renda Mensal Familiar",
    )
    telefone_1 = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone 1"
    )
    telefone_2 = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Telefone 2"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    auxilio = models.BooleanField(
        blank=True, null=True, default=False, verbose_name="Recebe Auxílio?"
    )  # Indica se a família recebe algum tipo de auxílio
    trabalha = models.BooleanField(
        blank=True, null=True, default=False, verbose_name="Trabalha?"
    )  # Indica se pelo menos um dos responsáveis trabalha
    nis = models.IntegerField(
        unique=True, blank=True, null=True, verbose_name="Número do NIS"
    )  # Número de Identificação Social, importante para programas sociais

    def __str__(self):
        return f"Família de {self.mae or self.pai}"


class Unidade(models.Model):
    nome_unidade = models.CharField(
        max_length=100, verbose_name="Nome da Unidade de Ensino"
    )
    endereco = models.ForeignKey(
        Endereco, on_delete=models.CASCADE, related_name="unidade"
    )

    def __str__(self):
        return self.nome_unidade


class Crianca(models.Model):
    ETAPAS_CHOICES = [
        ("B1", "Berçário 1"),
        ("B2", "Berçário 2"),
        ("M1", "Maternal 1"),
        ("M2", "Maternal 2"),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome Completo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    sexo = models.CharField(
        max_length=1,
        blank=False,
        null=False,
        choices=[("M", "Masculino"), ("F", "Feminino")],
        verbose_name="Sexo",
    )
    cpf = models.CharField(
        max_length=14, unique=True, blank=True, null=True, verbose_name="CPF"
    )
    cert_nascimento = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Certidão de Nascimento"
    )
    data_cadastro = models.DateField(auto_now_add=True, verbose_name="Data de Cadastro")
    etapa = models.CharField(
        blank=False,
        null=False,
        max_length=2,
        choices=ETAPAS_CHOICES,
        verbose_name="Etapa",
    )

    # Relacionamentos
    endereco = models.ForeignKey(
        Endereco, on_delete=models.SET_NULL, null=True, related_name="crianca"
    )
    familia = models.ForeignKey(
        Familia, on_delete=models.CASCADE, related_name="membros"
    )

    def __str__(self):
        return self.nome


class RankingProximidade(models.Model):
    crianca = models.ForeignKey(Crianca, on_delete=models.CASCADE)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    distancia_km = models.FloatField()
    posicao = models.IntegerField() # 1, 2 ou 3


class SugestaoCreche(models.Model):
    crianca = models.ForeignKey(
        "Crianca", on_delete=models.CASCADE, related_name="sugestoes"
    )
    unidade = models.ForeignKey("Unidade", on_delete=models.CASCADE)
    distancia = models.FloatField(help_text="Distância em quilômetros")
    data_calculo = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["distancia"]
        verbose_name = "Sugestão de Creche"

class Distrib_Vagas(models.Model):
    ultima_rev = models.DateTimeField(auto_now=True, verbose_name="Última Revisão")
    
    class Meta:
        verbose_name = "Distribuição de Vaga"
        verbose_name_plural = "Distribuição de Vagas"
