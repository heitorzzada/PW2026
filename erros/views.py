"""
Views para tratamento e renderização de páginas de erro HTTP customizadas.
Ativado quando DEBUG = False no ambiente do Django ou via rotas de preview.
"""
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


def error_400(request, exception=None):
    """
    Handler para erro HTTP 400 (Bad Request).
    Renderiza template amigável e estilizado no padrão Delacruz Barber.
    """
    context = {
        "status_code": 400,
        "titulo": "Requisição Inválida",
        "mensagem": "A solicitação enviada contém parâmetros inválidos ou incompletos e não pôde ser processada pelo servidor.",
        "path": getattr(request, "path", ""),
        "exception": str(exception) if exception else None,
    }
    return render(request, "erros/400.html", context, status=400)


def error_403(request, exception=None):
    """
    Handler para erro HTTP 403 (Permission Denied).
    Renderiza template de acesso negado estilizado no padrão Delacruz Barber.
    """
    context = {
        "status_code": 403,
        "titulo": "Acesso Não Autorizado",
        "mensagem": "Você não possui permissão para acessar esta página ou recurso restrito. Se você for barbeiro ou administrador, verifique suas credenciais.",
        "path": getattr(request, "path", ""),
        "exception": str(exception) if exception else None,
    }
    return render(request, "erros/403.html", context, status=403)


def error_404(request, exception=None):
    """
    Handler para erro HTTP 404 (Page Not Found).
    Renderiza template de página não encontrada estilizado no padrão Delacruz Barber.
    """
    context = {
        "status_code": 404,
        "titulo": "Página Não Encontrada",
        "mensagem": "O endereço que você tentou acessar não existe, foi removido ou está temporariamente indisponível.",
        "path": getattr(request, "path", ""),
        "exception": str(exception) if exception else None,
    }
    return render(request, "erros/404.html", context, status=404)


@requires_csrf_token
def error_500(request):
    """
    Handler para erro HTTP 500 (Internal Server Error).
    Renderiza template de erro interno de servidor com fallback seguro.
    """
    context = {
        "status_code": 500,
        "titulo": "Instabilidade Temporária no Servidor",
        "mensagem": "Identificamos uma oscilação momentânea em nossos servidores. Fique tranquilo: seus dados e agendamentos estão preservados e nossa equipe técnica já foi acionada.",
        "path": getattr(request, "path", ""),
    }
    return render(request, "erros/500.html", context, status=500)


# Views para teste e pré-visualização das telas em ambiente de desenvolvimento
def preview_400(request):
    return error_400(request, exception="Parâmetro de requisição malformado ou ausente.")


def preview_403(request):
    return error_403(request, exception="Área restrita a barbeiros e administradores autorizados.")


def preview_404(request):
    return error_404(request, exception="A URL informada não foi localizada no catálogo de rotas do sistema.")


def preview_500(request):
    return error_500(request)
