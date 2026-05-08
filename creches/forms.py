from django import forms
from .models import Crianca, Endereco, Familia, Unidade
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


class UnidadeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("nome_unidade")

    class Meta:
        model = Unidade
        fields = ["nome_unidade"]


class FamiliaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "mae",
            "pai",
            "email",
            Row(
                Column("telefone_1", css_class="form-group col-md-6 mb-0"),
                Column("telefone_2", css_class="form-group col-md-6 mb-0"),
            ),
            Row(
                Column("auxilio", css_class="form-group col-md-3 mb-0"),
                Column("trabalha", css_class="form-group col-md-3 mb-0"),
                Column("renda", css_class="form-group col-md-3 mb-0"),
                Column("nis", css_class="form-group col-md-3 mb-0"),
            ),
        )

    class Meta:
        model = Familia
        fields = [
            "mae",
            "pai",
            "renda",
            "telefone_1",
            "telefone_2",
            "email",
            "auxilio",
            "nis",
            "trabalha",
        ]


class CriancaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # Nome completo ocupando a linha toda (opcional)
            "nome",
            # Campos na mesma linha
            Row(
                Column("data_nascimento", css_class="form-group col-md-4 mb-0"),
                Column("sexo", css_class="form-group col-md-4 mb-0"),
                Column("etapa", css_class="form-group col-md-4 mb-0"),
            ),
            Row(
                Column("cert_nascimento", css_class="form-group col-md-6 mb-0"),
                Column("cpf", css_class="form-group col-md-6 mb-0"),
            ),
        )

    class Meta:
        model = Crianca
        fields = ["nome", "data_nascimento", "sexo", "etapa", "cert_nascimento", "cpf"]
        widgets = {
            "data_nascimento": forms.TextInput(
                attrs={"placeholder": "DD/MM/AAAA", "class": "form-control"}
            ),
        }


class EnderecoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = (
            False  # Importante: para não criar uma tag <form> duplicada
        )
        self.helper.layout = Layout(
            Row(
                Column("cep", css_class="form-group col-md-4 mb-0"),
                Column("estado", css_class="form-group col-md-2 mb-0"),
                Column("cidade", css_class="form-group col-md-6 mb-0"),
            ),
            Row(
                Column("logradouro", css_class="form-group col-md-8 mb-0"),
                Column("numero", css_class="form-group col-md-4 mb-0"),
            ),
            Row(
                Column("complemento", css_class="form-group col-md-6 mb-0"),
                Column("bairro", css_class="form-group col-md-6 mb-0"),
            ),
            Row(
                Column("latitude", css_class="form-group col-md-6 mb-0"),
                Column("longitude", css_class="form-group col-md-6 mb-0"),
            ),
        )

    class Meta:
        model = Endereco
        fields = [
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "estado",
            "latitude",
            "longitude",
        ]
        widgets = {
            "cep": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "00000-000",
                    "onblur": "buscarCEP(this.value)",  # Você pode chamar sua função de busca aqui
                }
            ),
            "logradouro": forms.TextInput(
                attrs={"id": "id_logradouro", "class": "form-control"}
            ),
            "numero": forms.TextInput(
                attrs={"id": "id_numero", "class": "form-control"}
            ),
            "bairro": forms.TextInput(
                attrs={"id": "id_bairro", "class": "form-control"}
            ),
            "cidade": forms.TextInput(
                attrs={"id": "id_cidade", "class": "form-control"}
            ),
            "estado": forms.TextInput(
                attrs={"id": "id_estado", "class": "form-control"}
            ),
            "complemento": forms.TextInput(
                attrs={"id": "id_complemento", "class": "form-control"}
            ),
        }
