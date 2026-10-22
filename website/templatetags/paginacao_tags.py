from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Substitui ou adiciona parâmetros na URL mantendo todos os outros filtros do GET.
    Essencial para paginação correta em conjunto com a biblioteca Django Filter.
    Uso:
        <a href="?{% param_replace page=page_obj.next_page_number %}">Próxima</a>
    """
    request = context.get("request")
    if not request:
        return ""
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None and value != "":
            params[key] = str(value)
        elif key in params:
            del params[key]
    return params.urlencode()


@register.filter(name="add_class")
def add_class(value, arg):
    """
    Filtro para adicionar classe CSS aos campos de formulários, incluindo os do Django Filter.
    Uso: {{ form.campo|add_class:"form-control bg-dark text-white" }}
    """
    if hasattr(value, "as_widget"):
        return value.as_widget(attrs={"class": arg})
    return value
