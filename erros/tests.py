import platform
import sys
from django.test import TestCase, Client, override_settings
from django.urls import reverse
import BarberProject.settings as project_settings


class ErrosViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_preview_400(self):
        response = self.client.get(reverse("erros:erro_400"))
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "400", status_code=400)
        self.assertContains(response, "Requisição Inválida", status_code=400)
        self.assertContains(response, "Delacruz Barber", status_code=400)

    def test_preview_403(self):
        response = self.client.get(reverse("erros:erro_403"))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "403", status_code=403)
        self.assertContains(response, "Acesso Não Autorizado", status_code=403)
        self.assertContains(response, "Delacruz Barber", status_code=403)

    def test_preview_404(self):
        response = self.client.get(reverse("erros:erro_404"))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Página Não Encontrada", status_code=404)
        self.assertContains(response, "Delacruz Barber", status_code=404)

    def test_preview_500(self):
        response = self.client.get(reverse("erros:erro_500"))
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "500", status_code=500)
        self.assertContains(response, "Instabilidade", status_code=500)
        self.assertContains(response, "Delacruz Barber", status_code=500)

    @override_settings(DEBUG=False)
    def test_handler404_when_debug_false(self):
        response = self.client.get("/uma-rota-que-certamente-nao-existe-404/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Página Não Encontrada", status_code=404)
        self.assertContains(response, "Voltar ao Início", status_code=404)
        self.assertContains(response, "Agendar Horário", status_code=404)


class DebugConfigTestCase(TestCase):
    def test_debug_is_boolean(self):
        self.assertIsInstance(project_settings.DEBUG, bool)

    def test_windows_environment_debug_behavior(self):
        # Em ambiente Windows nativo sem GAE, DEBUG deve ser booleano
        is_windows = sys.platform.startswith("win") or platform.system() == "Windows"
        if is_windows:
            self.assertTrue(project_settings.IS_WINDOWS)
