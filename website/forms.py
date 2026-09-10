import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    PerfilUsuario, Servico, Barbeiro, Cliente,
    HorarioDisponivel, Agendamento, MensagemContato,
    Feedback, FotoTrabalho, CupomDesconto, Produto,
    VendaProduto, BloqueioHorarioBarbeiro, FichaCliente,
    FilaEspera, PlanoAssinatura, AssinaturaCliente
)

def clean_telefone_campo(telefone):
    numeros = "".join(filter(str.isdigit, telefone))
    if len(numeros) not in [10, 11]:
        raise ValidationError("Informe um telefone válido no formato (44) 99999-9999.")
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"


class CadastroUsuarioForm(forms.Form):
    nome = forms.CharField(
        label="Nome",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Seu nome", "class": "form-control"})
    )
    sobrenome = forms.CharField(
        label="Sobrenome",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Seu sobrenome", "class": "form-control"})
    )
    usuario = forms.CharField(
        label="Usuário",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Nome de usuário", "class": "form-control"})
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"placeholder": "seu.email@exemplo.com", "class": "form-control"})
    )
    telefone = forms.CharField(
        label="Telefone / WhatsApp",
        max_length=15,
        widget=forms.TextInput(attrs={
            "class": "form-control phone-mask",
            "placeholder": "(44) 99999-9999",
            "maxlength": "15",
            "autocomplete": "tel",
        })
    )
    senha = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Sua senha", "class": "form-control"})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Repita a senha", "class": "form-control"})
    )

    def clean_usuario(self):
        usuario = self.cleaned_data.get("usuario")
        if User.objects.filter(username=usuario).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return usuario

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean_telefone(self):
        telefone = self.cleaned_data.get("telefone", "")
        return clean_telefone_campo(telefone)

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")
        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error("confirmar_senha", "As senhas não coincidem.")
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(
            username=cleaned_data["usuario"],
            email=cleaned_data["email"],
            password=cleaned_data["senha"],
            first_name=cleaned_data["nome"],
            last_name=cleaned_data["sobrenome"],
        )
        from django.contrib.auth.models import Group
        grupo_cliente, _ = Group.objects.get_or_create(name="Clientes")
        user.groups.add(grupo_cliente)
        
        PerfilUsuario.objects.create(
            usuario=user,
            tipo_usuario="cliente",
            telefone=cleaned_data["telefone"],
        )
        
        Cliente.objects.create(
            usuario=user,
            nome=f"{cleaned_data['nome']} {cleaned_data['sobrenome']}",
            telefone=cleaned_data["telefone"],
            email=cleaned_data["email"],
        )
        return user


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ["telefone", "foto_perfil"]
        widgets = {
            "telefone": forms.TextInput(attrs={
                "class": "form-control phone-mask",
                "placeholder": "(44) 99999-9999",
                "maxlength": "15"
            }),
            "foto_perfil": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_telefone(self):
        return clean_telefone_campo(self.cleaned_data.get("telefone", ""))


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["nome", "descricao", "preco", "duracao_minutos", "categoria", "icone", "ativo", "destaque", "ordem"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "preco": forms.NumberInput(attrs={"class": "form-control"}),
            "duracao_minutos": forms.NumberInput(attrs={"class": "form-control"}),
            "categoria": forms.TextInput(attrs={"class": "form-control"}),
            "icone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: scissors"}),
            "ordem": forms.NumberInput(attrs={"class": "form-control"}),
        }


class BarbeiroForm(forms.ModelForm):
    class Meta:
        model = Barbeiro
        fields = ["nome", "cargo", "especialidade", "descricao_curta", "imagem_url", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "especialidade": forms.TextInput(attrs={"class": "form-control"}),
            "descricao_curta": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "imagem_url": forms.TextInput(attrs={"class": "form-control", "placeholder": "Caminho da imagem ou URL"}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email", "observacoes"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={
                "class": "form-control phone-mask",
                "placeholder": "(44) 99999-9999",
                "maxlength": "15"
            }),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "observacoes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def clean_telefone(self):
        return clean_telefone_campo(self.cleaned_data.get("telefone", ""))


class HorarioDisponivelForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponivel
        fields = ["barbeiro", "horario", "ativo", "observacao"]
        widgets = {
            "barbeiro": forms.Select(attrs={"class": "form-select"}),
            "horario": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "observacao": forms.TextInput(attrs={"class": "form-control"}),
        }


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ["cliente", "servico", "barbeiro", "data", "horario", "status", "observacoes"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "servico": forms.Select(attrs={"class": "form-select"}),
            "barbeiro": forms.Select(attrs={"class": "form-select"}),
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "horario": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "observacoes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def clean_data(self):
        data = self.cleaned_data.get("data")
        from datetime import date
        if data < date.today():
            raise ValidationError("Não é possível agendar em datas passadas.")
        return data


class AgendamentoPublicoForm(forms.Form):
    servico = forms.ModelChoiceField(
        queryset=Servico.objects.filter(ativo=True),
        label="Serviço",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    barbeiro = forms.ModelChoiceField(
        queryset=Barbeiro.objects.filter(ativo=True),
        label="Barbeiro",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    data = forms.DateField(
        label="Data",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    horario = forms.TimeField(
        label="Horário Escolhido",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control fw-bold text-center", "id": "id_horario_input"})
    )
    nome = forms.CharField(
        label="Nome Completo",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Seu nome completo", "class": "form-control"})
    )
    telefone = forms.CharField(
        label="Telefone / WhatsApp",
        max_length=15,
        widget=forms.TextInput(attrs={
            "class": "form-control phone-mask",
            "placeholder": "(44) 99999-9999",
            "maxlength": "15",
            "autocomplete": "tel",
        })
    )
    email = forms.EmailField(
        label="E-mail para Confirmação",
        widget=forms.EmailInput(attrs={"placeholder": "seu.email@exemplo.com", "class": "form-control"})
    )
    metodo_pagamento = forms.ChoiceField(
        label="Forma de Pagamento",
        choices=[
            ("pix", "PIX"),
            ("cartao", "Cartão"),
            ("dinheiro", "Dinheiro"),
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    cupom_codigo = forms.CharField(
        label="Cupom de Desconto / Código de Amigo",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ex: DELACRUZ10 ou código do amigo", "class": "form-control"})
    )
    observacoes = forms.CharField(
        label="Observações Adicionais",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Algum detalhe ou preferência...", "class": "form-control"})
    )

    def clean_telefone(self):
        return clean_telefone_campo(self.cleaned_data.get("telefone", ""))

    def clean_data(self):
        data = self.cleaned_data.get("data")
        from datetime import date
        if data < date.today():
            raise ValidationError("Não é possível agendar em datas passadas.")
        return data


class MensagemContatoForm(forms.ModelForm):
    class Meta:
        model = MensagemContato
        fields = ["nome", "email", "telefone", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Seu nome"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Seu e-mail"}),
            "telefone": forms.TextInput(attrs={
                "class": "form-control phone-mask",
                "placeholder": "(44) 99999-9999",
                "maxlength": "15"
            }),
            "mensagem": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Sua mensagem..."}),
        }

    def clean_telefone(self):
        return clean_telefone_campo(self.cleaned_data.get("telefone", ""))


class FeedbackForm(forms.ModelForm):
    nota = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Nota (1 a 5)"
    )
    class Meta:
        model = Feedback
        fields = ["nota", "comentario"]
        widgets = {
            "comentario": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Escreva seu comentário sobre o atendimento..."
            }),
        }


class FotoTrabalhoForm(forms.ModelForm):
    class Meta:
        model = FotoTrabalho
        fields = ["barbeiro", "titulo", "descricao", "imagem", "categoria", "publicado"]
        widgets = {
            "barbeiro": forms.Select(attrs={"class": "form-select"}),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "imagem": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
        }


class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email", "observacoes"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={
                "class": "form-control phone-mask",
                "placeholder": "(44) 99999-9999",
                "maxlength": "15"
            }),
            "email": forms.EmailInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "observacoes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def clean_telefone(self):
        return clean_telefone_campo(self.cleaned_data.get("telefone", ""))


class BloqueioHorarioForm(forms.ModelForm):
    class Meta:
        model = BloqueioHorarioBarbeiro
        fields = ["data", "horario", "dia_inteiro", "motivo"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "horario": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "dia_inteiro": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "motivo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Almoço, Consulta médica, Folga"}),
        }


class FichaClienteForm(forms.ModelForm):
    class Meta:
        model = FichaCliente
        fields = ["estilo_corte", "produtos_preferidos", "observacoes_tecnicas"]
        widgets = {
            "estilo_corte": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Degradê navalhado alto, tesoura em cima"}),
            "produtos_preferidos": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Pomada matte, óleo de barba amadeirado"}),
            "observacoes_tecnicas": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Ex: Pele sensível na gola, redemoinho frontal..."}),
        }


class FilaEsperaForm(forms.ModelForm):
    class Meta:
        model = FilaEspera
        fields = ["barbeiro", "data_desejada", "turno", "observacoes"]
        widgets = {
            "barbeiro": forms.Select(attrs={"class": "form-select"}),
            "data_desejada": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "turno": forms.Select(attrs={"class": "form-select"}),
            "observacoes": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Preferências de horário ou detalhes..."}),
        }


class VendaProdutoRapidaForm(forms.Form):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True, estoque__gt=0),
        label="Selecione o Produto",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    quantidade = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Quantidade",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1})
    )


class CupomDescontoForm(forms.ModelForm):
    class Meta:
        model = CupomDesconto
        fields = ["codigo", "tipo", "valor", "limite_uso", "ativo", "validade"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "EX: DELACRUZ10"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "limite_uso": forms.NumberInput(attrs={"class": "form-control"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "validade": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class PlanoAssinaturaForm(forms.ModelForm):
    class Meta:
        model = PlanoAssinatura
        fields = ["nome", "descricao", "preco_mensal", "cortes_por_mes", "inclui_barba", "destaque", "ativo", "ordem"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "preco_mensal": forms.NumberInput(attrs={"class": "form-control"}),
            "cortes_por_mes": forms.NumberInput(attrs={"class": "form-control"}),
            "inclui_barba": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "destaque": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ordem": forms.NumberInput(attrs={"class": "form-control"}),
        }

