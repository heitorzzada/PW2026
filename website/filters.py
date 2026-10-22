import django_filters
from django import forms
from .models import Agendamento, Cliente, Servico, Barbeiro


class AgendamentoFilter(django_filters.FilterSet):
    data = django_filters.DateFilter(
        field_name="data",
        label="Data",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-white border-secondary"})
    )
    data_inicio = django_filters.DateFilter(
        field_name="data",
        lookup_expr="gte",
        label="A partir de",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-white border-secondary"})
    )
    data_fim = django_filters.DateFilter(
        field_name="data",
        lookup_expr="lte",
        label="Até",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control bg-dark text-white border-secondary"})
    )
    status = django_filters.ChoiceFilter(
        choices=Agendamento.STATUS_CHOICES,
        label="Status",
        empty_label="Todos os Status",
        widget=forms.Select(attrs={"class": "form-select bg-dark text-white border-secondary"})
    )
    barbeiro = django_filters.ModelChoiceFilter(
        queryset=Barbeiro.objects.filter(ativo=True),
        label="Barbeiro",
        empty_label="Todos os Barbeiros",
        widget=forms.Select(attrs={"class": "form-select bg-dark text-white border-secondary"})
    )
    cliente_nome = django_filters.CharFilter(
        field_name="cliente__nome",
        lookup_expr="icontains",
        label="Nome do Cliente",
        widget=forms.TextInput(attrs={"placeholder": "Filtrar por nome...", "class": "form-control bg-dark text-white border-secondary"})
    )

    class Meta:
        model = Agendamento
        fields = ["data_inicio", "data_fim", "status", "barbeiro", "cliente_nome"]


class ServicoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Nome do Serviço",
        widget=forms.TextInput(attrs={"placeholder": "Buscar por nome...", "class": "form-control bg-dark text-white border-secondary"})
    )
    categoria = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Categoria",
        widget=forms.TextInput(attrs={"placeholder": "Buscar por categoria...", "class": "form-control bg-dark text-white border-secondary"})
    )
    ativo = django_filters.BooleanFilter(
        label="Ativo",
        widget=forms.Select(choices=[("", "Todos"), (True, "Ativos"), (False, "Inativos")], attrs={"class": "form-select bg-dark text-white border-secondary"})
    )

    class Meta:
        model = Servico
        fields = ["nome", "categoria", "ativo"]


class ClienteFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Nome",
        widget=forms.TextInput(attrs={"placeholder": "Filtrar por nome...", "class": "form-control bg-dark text-white border-secondary"})
    )
    telefone = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Telefone",
        widget=forms.TextInput(attrs={"placeholder": "Filtrar por telefone...", "class": "form-control bg-dark text-white border-secondary"})
    )
    email = django_filters.CharFilter(
        lookup_expr="icontains",
        label="E-mail",
        widget=forms.TextInput(attrs={"placeholder": "Filtrar por e-mail...", "class": "form-control bg-dark text-white border-secondary"})
    )

    class Meta:
        model = Cliente
        fields = ["nome", "telefone", "email"]
