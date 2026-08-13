from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, time
from website.models import (
    PerfilUsuario, Servico, Barbeiro, Cliente, HorarioDisponivel,
    Agendamento, MensagemContato, Feedback, FotoTrabalho
)

class SecurityAndUserIsolationTestCase(TestCase):
    def setUp(self):
        # User A (Admin A)
        self.user_a = User.objects.create_superuser(
            username="usera", email="usera@test.com", password="password123"
        )
        PerfilUsuario.objects.create(usuario=self.user_a, tipo_usuario="administrador")

        # User B (Admin B)
        self.user_b = User.objects.create_superuser(
            username="userb", email="userb@test.com", password="password123"
        )
        PerfilUsuario.objects.create(usuario=self.user_b, tipo_usuario="administrador")

        # Clients for HTTP requests
        self.client_a = Client()
        self.client_a.login(username="usera", password="password123")

        self.client_b = Client()
        self.client_b.login(username="userb", password="password123")

    def test_servico_user_isolation(self):
        # User A creates a Servico
        servico_a = Servico.objects.create(
            usuario=self.user_a,
            nome="Corte User A",
            preco=Decimal("50.00"),
            duracao_minutos=30,
            ordem=1
        )

        # User B tries to view list -> should not see User A's service
        resp_b_list = self.client_b.get(reverse("listar_servicos"))
        self.assertEqual(resp_b_list.status_code, 200)
        self.assertNotIn(servico_a, resp_b_list.context["servicos"])

        # User B tries to view detail -> should get 404
        resp_b_detail = self.client_b.get(reverse("ver_servico", args=[servico_a.pk]))
        self.assertEqual(resp_b_detail.status_code, 404)

        # User B tries to edit -> should get 404
        resp_b_edit = self.client_b.get(reverse("editar_servico", args=[servico_a.pk]))
        self.assertEqual(resp_b_edit.status_code, 404)

        # User B tries to delete -> should get 404
        resp_b_delete = self.client_b.post(reverse("excluir_servico", args=[servico_a.pk]))
        self.assertEqual(resp_b_delete.status_code, 404)

        # User A views list -> sees their service
        resp_a_list = self.client_a.get(reverse("listar_servicos"))
        self.assertEqual(resp_a_list.status_code, 200)
        self.assertIn(servico_a, resp_a_list.context["servicos"])

        # User A views detail -> 200
        resp_a_detail = self.client_a.get(reverse("ver_servico", args=[servico_a.pk]))
        self.assertEqual(resp_a_detail.status_code, 200)

        # User A edits -> 200
        resp_a_edit = self.client_a.get(reverse("editar_servico", args=[servico_a.pk]))
        self.assertEqual(resp_a_edit.status_code, 200)

        # User A deletes -> 302 redirect on success
        resp_a_delete = self.client_a.post(reverse("excluir_servico", args=[servico_a.pk]))
        self.assertEqual(resp_a_delete.status_code, 302)
        self.assertFalse(Servico.objects.filter(pk=servico_a.pk).exists())

    def test_barbeiro_user_isolation(self):
        barbeiro_a = Barbeiro.objects.create(
            usuario=self.user_a,
            nome="Barbeiro A",
            cargo="Barbeiro",
            especialidade="Cortes",
            descricao_curta="Teste"
        )

        # User B isolation check
        self.assertEqual(self.client_b.get(reverse("ver_barbeiro", args=[barbeiro_a.pk])).status_code, 404)
        self.assertEqual(self.client_b.get(reverse("editar_barbeiro", args=[barbeiro_a.pk])).status_code, 404)
        self.assertEqual(self.client_b.post(reverse("excluir_barbeiro", args=[barbeiro_a.pk])).status_code, 404)

        resp_b_list = self.client_b.get(reverse("listar_barbeiros"))
        self.assertNotIn(barbeiro_a, resp_b_list.context["barbeiros"])

        # User A access check
        resp_a_list = self.client_a.get(reverse("listar_barbeiros"))
        self.assertIn(barbeiro_a, resp_a_list.context["barbeiros"])
        self.assertEqual(self.client_a.get(reverse("ver_barbeiro", args=[barbeiro_a.pk])).status_code, 200)

    def test_auth_urls_exist(self):
        # Check login page
        resp_login = self.client.get(reverse("login"))
        self.assertEqual(resp_login.status_code, 200)

        # Check unauthenticated access to password change -> redirect to login
        resp_pw_unauth = self.client.get(reverse("alterar_senha"))
        self.assertEqual(resp_pw_unauth.status_code, 302)

        # Check authenticated access to password change -> 200
        resp_pw_auth = self.client_a.get(reverse("alterar_senha"))
        self.assertEqual(resp_pw_auth.status_code, 200)
