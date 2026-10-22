"""
URLs para pré-visualização das telas de erro do app 'erros'.
Permite visualizar as telas 400, 403, 404 e 500 diretamente pelo navegador.
"""
from django.urls import path
from . import views

app_name = "erros"

urlpatterns = [
    path("400/", views.preview_400, name="erro_400"),
    path("403/", views.preview_403, name="erro_403"),
    path("404/", views.preview_404, name="erro_404"),
    path("500/", views.preview_500, name="erro_500"),
]
