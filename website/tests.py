from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, time
from website.models import (
    PerfilUsuario, Servico, Barbeiro, Cliente, HorarioDisponivel,
    Agendamento, MensagemContato, Feedback, FotoTrabalho,
    PlanoAssinatura, AssinaturaCliente, Produto, ItemAgendamento
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


class DelacruzCatalogAndSeedTestCase(TestCase):
    def test_seed_delacruz_real_catalog_and_idempotency(self):
        from django.core.management import call_command
        from website.models import Servico, Produto, PlanoAssinatura

        # 1. Executa seed primeira vez
        call_command("seed_delacruz_real")

        # Verifica 4 serviços ativos
        servicos_ativos = Servico.objects.filter(ativo=True).order_by("ordem")
        self.assertEqual(servicos_ativos.count(), 4)
        nomes_servicos = [s.nome for s in servicos_ativos]
        self.assertListEqual(nomes_servicos, ["Cabelo", "Barba", "Cavanhaque", "Sobrancelha"])

        cabelo = Servico.objects.get(nome="Cabelo")
        self.assertEqual(cabelo.preco, Decimal("30.00"))
        self.assertEqual(cabelo.duracao_minutos, 30)

        sobrancelha = Servico.objects.get(nome="Sobrancelha")
        self.assertEqual(sobrancelha.preco, Decimal("5.00"))
        self.assertEqual(sobrancelha.duracao_minutos, 10)

        # Verifica 3 produtos ativos com estoque 0
        produtos_ativos = Produto.objects.filter(ativo=True)
        self.assertEqual(produtos_ativos.count(), 3)
        for p in produtos_ativos:
            self.assertEqual(p.estoque, 0)
        nomes_produtos = set(produtos_ativos.values_list("nome", flat=True))
        self.assertEqual(nomes_produtos, {"Pomada Fox", "Pomada em pó", "Shampoo anticaspa"})

        # Verifica 3 planos de assinatura ativos
        planos_ativos = PlanoAssinatura.objects.filter(ativo=True).order_by("ordem")
        self.assertEqual(planos_ativos.count(), 3)

        p_normal = PlanoAssinatura.objects.get(codigo="plano-normal")
        self.assertEqual(p_normal.preco_mensal, Decimal("80.00"))
        self.assertEqual(p_normal.modalidade, "limitado")
        self.assertEqual(p_normal.limite_mensal, 4)
        self.assertEqual(set(p_normal.servicos_inclusos.values_list("nome", flat=True)), {"Cabelo", "Sobrancelha"})

        p_barba = PlanoAssinatura.objects.get(codigo="plano-com-barba")
        self.assertEqual(p_barba.preco_mensal, Decimal("120.00"))
        self.assertEqual(p_barba.modalidade, "limitado")
        self.assertEqual(p_barba.limite_mensal, 4)
        self.assertEqual(set(p_barba.servicos_inclusos.values_list("nome", flat=True)), {"Cabelo", "Sobrancelha", "Barba"})

        p_infinito = PlanoAssinatura.objects.get(codigo="plano-cortes-infinitos")
        self.assertEqual(p_infinito.preco_mensal, Decimal("100.00"))
        self.assertEqual(p_infinito.modalidade, "ilimitado")
        self.assertIsNone(p_infinito.limite_mensal)
        self.assertEqual(set(p_infinito.servicos_inclusos.values_list("nome", flat=True)), {"Cabelo", "Sobrancelha"})

        # 2. Executa seed pela segunda vez (Idempotência)
        call_command("seed_delacruz_real")
        self.assertEqual(Servico.objects.filter(ativo=True).count(), 4)
        self.assertEqual(Produto.objects.filter(ativo=True).count(), 3)
        self.assertEqual(PlanoAssinatura.objects.filter(ativo=True).count(), 3)


class SchedulingBufferAndCollisionTestCase(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_delacruz_real")
        self.barbeiro = Barbeiro.objects.create(
            nome="Barbeiro Teste",
            cargo="Barbeiro Oficial",
            especialidade="Cabelo e Barba",
            descricao_curta="Especialista",
            ativo=True
        )
        self.servico_cabelo = Servico.objects.get(nome="Cabelo")
        self.cliente = Cliente.objects.create(
            nome="Cliente Teste",
            telefone="(44) 99999-0000",
            email="cliente@teste.com"
        )
        self.data_teste = date(2026, 10, 15)

    def test_horarios_disponiveis_api_boundary_8_and_2130(self):
        client = Client()
        url = reverse("horarios_disponiveis")
        resp = client.get(url, {
            "barbeiro": self.barbeiro.id,
            "data": self.data_teste.strftime("%Y-%m-%d"),
            "servico": self.servico_cabelo.id,
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        times_map = {item["time"]: item["available"] for item in data["times"]}

        # 08:00 e 21:30 devem estar presentes e disponíveis em dia livre
        self.assertIn("08:00", times_map)
        self.assertTrue(times_map["08:00"])
        self.assertIn("21:30", times_map)
        self.assertTrue(times_map["21:30"])

    def test_semi_open_collision_with_5min_buffer(self):
        # Cria agendamento existente às 08:00 com Cabelo (30m + 5m buffer = ocupa até 08:35)
        Agendamento.objects.create(
            cliente=self.cliente,
            barbeiro=self.barbeiro,
            servico=self.servico_cabelo,
            data=self.data_teste,
            horario=time(8, 0),
            duracao_total_minutos=30,
            status="confirmado"
        )

        client = Client()
        url = reverse("horarios_disponiveis")
        resp = client.get(url, {
            "barbeiro": self.barbeiro.id,
            "data": self.data_teste.strftime("%Y-%m-%d"),
            "servico": self.servico_cabelo.id,
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        times_map = {item["time"]: item["available"] for item in data["times"]}

        # 08:00 colide -> Indisponível
        self.assertFalse(times_map["08:00"])
        # 08:30 colide com término 08:35 -> Indisponível
        self.assertFalse(times_map["08:30"])
        # 09:00 está livre -> Disponível
        self.assertTrue(times_map["09:00"])

    def test_reverse_order_collision(self):
        # Existindo agendamento às 09:00 (30m + 5m = ocupa 09:00 às 09:35)
        Agendamento.objects.create(
            cliente=self.cliente,
            barbeiro=self.barbeiro,
            servico=self.servico_cabelo,
            data=self.data_teste,
            horario=time(9, 0),
            duracao_total_minutos=30,
            status="confirmado"
        )

        client = Client()
        url = reverse("horarios_disponiveis")
        resp = client.get(url, {
            "barbeiro": self.barbeiro.id,
            "data": self.data_teste.strftime("%Y-%m-%d"),
            "servico": self.servico_cabelo.id,
        })
        times_map = {item["time"]: item["available"] for item in resp.json()["times"]}

        # Candidato às 08:30 com 35m de ocupação ocuparia até 09:05, colidindo com 09:00 -> Recusado
        self.assertFalse(times_map["08:30"])
        # 08:00 ocupa até 08:35 (não colide com 09:00) -> Disponível
        self.assertTrue(times_map["08:00"])


class SubscriptionPlanLogicTestCase(TestCase):
    def setUp(self):
        from django.core.management import call_command
        call_command("seed_delacruz_real")
        self.cliente = Cliente.objects.create(
            nome="Cliente VIP",
            telefone="(44) 99999-1111",
            email="vip@teste.com"
        )
        self.plano_normal = PlanoAssinatura.objects.get(codigo="plano-normal")
        self.plano_infinito = PlanoAssinatura.objects.get(codigo="plano-cortes-infinitos")

    def test_plano_limitado_usage_limit(self):
        from website.models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.create(
            cliente=self.cliente,
            plano=self.plano_normal,
            status="ativa",
            cortes_usados_mes=3
        )
        # 3 de 4 usados -> Tem cortes disponíveis
        self.assertTrue(assinatura.tem_cortes_disponiveis())

        # 4 de 4 usados -> Esgotado
        assinatura.cortes_usados_mes = 4
        assinatura.save()
        self.assertFalse(assinatura.tem_cortes_disponiveis())

    def test_plano_ilimitado_always_available(self):
        from website.models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.create(
            cliente=self.cliente,
            plano=self.plano_infinito,
            status="ativa",
            cortes_usados_mes=15  # Mesmo com 15 cortes usados, continua disponível
        )
        self.assertTrue(assinatura.tem_cortes_disponiveis())

        # Se cancelada -> Indisponível
        assinatura.status = "cancelada"
        assinatura.save()
        self.assertFalse(assinatura.tem_cortes_disponiveis())

