from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Avg, Count
from datetime import date, datetime, timedelta
from django.db.models import Q

from .models import (
    PerfilUsuario, Servico, Barbeiro, Cliente,
    HorarioDisponivel, Agendamento, MensagemContato,
    Feedback, FotoTrabalho
)
from .forms import (
    CadastroUsuarioForm, PerfilUsuarioForm, ServicoForm,
    BarbeiroForm, ClienteForm, HorarioDisponivelForm,
    AgendamentoForm, AgendamentoPublicoForm, MensagemContatoForm,
    FeedbackForm, FotoTrabalhoForm, PerfilClienteForm
)

# --- SECURITY MIXINS ---

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

class ClienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated and 
            hasattr(self.request.user, "perfil") and 
            self.request.user.perfil.tipo_usuario == "cliente"
        )

class BarbeiroRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated and 
            hasattr(self.request.user, "perfil") and 
            self.request.user.perfil.tipo_usuario == "barbeiro"
        )


# --- PUBLIC VIEWS ---

class IndexView(TemplateView):
    template_name = "website/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["servicos_destaque"] = Servico.objects.filter(ativo=True, destaque=True).order_by("ordem")
        context["barbeiros"] = Barbeiro.objects.filter(ativo=True)
        context["fotos_trabalho"] = FotoTrabalho.objects.filter(publicado=True).order_by("-criado_em")
        return context


class ServicosPublicView(ListView):
    model = Servico
    template_name = "website/servicos.html"
    context_object_name = "servicos"

    def get_queryset(self):
        return Servico.objects.filter(ativo=True).order_by("ordem")


class BarbeirosPublicView(ListView):
    model = Barbeiro
    template_name = "website/barbeiros.html"
    context_object_name = "barbeiros"

    def get_queryset(self):
        return Barbeiro.objects.filter(ativo=True)


class SobreView(TemplateView):
    template_name = "website/sobre.html"


class ContatoCreateView(CreateView):
    model = MensagemContato
    form_class = MensagemContatoForm
    template_name = "website/contato.html"
    success_url = reverse_lazy("contato")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.usuario = self.request.user
        messages.success(self.request, "Sua mensagem foi enviada com sucesso! Entraremos em contato em breve. ✅")
        return super().form_valid(form)


class AgendamentoPublicoView(FormView):
    template_name = "website/agendamento.html"
    form_class = AgendamentoPublicoForm
    success_url = reverse_lazy("agendamento")

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            try:
                cliente = Cliente.objects.get(usuario=self.request.user)
                initial.update({
                    "nome": cliente.nome,
                    "telefone": cliente.telefone,
                    "email": cliente.email,
                })
            except Cliente.DoesNotExist:
                initial.update({
                    "nome": f"{self.request.user.first_name} {self.request.user.last_name}",
                    "email": self.request.user.email,
                })
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["servicos"] = Servico.objects.filter(ativo=True).order_by("ordem")
        context["barbeiros"] = Barbeiro.objects.filter(ativo=True)
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        email = cleaned_data["email"]
        telefone = cleaned_data["telefone"]
        nome = cleaned_data["nome"]
        
        cliente = None
        if self.request.user.is_authenticated:
            cliente = Cliente.objects.filter(usuario=self.request.user).first()
            
        if not cliente:
            cliente = Cliente.objects.filter(email=email).first()
        if not cliente:
            cliente = Cliente.objects.filter(telefone=telefone).first()
            
        if not cliente:
            cliente = Cliente.objects.create(
                usuario=self.request.user if self.request.user.is_authenticated else None,
                nome=nome,
                telefone=telefone,
                email=email,
            )
        else:
            if not cliente.usuario and self.request.user.is_authenticated:
                cliente.usuario = self.request.user
            cliente.nome = nome
            cliente.telefone = telefone
            cliente.save()
            
        barbeiro = cleaned_data["barbeiro"]
        data = cleaned_data["data"]
        horario = cleaned_data["horario"]
        
        # Double check availability on backend
        if Agendamento.objects.filter(barbeiro=barbeiro, data=data, horario=horario).exclude(status="cancelado").exists():
            form.add_error("horario", "Este horário já está reservado para este barbeiro.")
            return self.form_invalid(form)
            
        Agendamento.objects.create(
            usuario=self.request.user if self.request.user.is_authenticated else None,
            cliente=cliente,
            servico=cleaned_data["servico"],
            barbeiro=barbeiro,
            data=data,
            horario=horario,
            status="pendente",
            observacoes=cleaned_data["observacoes"],
        )
        
        messages.success(self.request, "Seu agendamento foi solicitado com sucesso! Acompanhe em sua área. ✅")
        return super().form_valid(form)


class CadastroUsuarioView(FormView):
    template_name = "website/cadastro.html"
    form_class = CadastroUsuarioForm
    success_url = reverse_lazy("area_cliente")

    def form_valid(self, form):
        user = form.save()
        from django.contrib.auth import login
        login(self.request, user)
        messages.success(self.request, "Cadastro realizado com sucesso! Bem-vindo(a) à sua área exclusiva. 🎉")
        return super().form_valid(form)


class RedirecionarUsuarioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return redirect("dashboard")
        
        perfil = getattr(request.user, "perfil", None)
        if perfil:
            if perfil.tipo_usuario == "barbeiro":
                return redirect("area_barbeiro")
            elif perfil.tipo_usuario == "administrador":
                return redirect("dashboard")
        
        return redirect("area_cliente")


# --- AUTH VIEWS ---

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = "pagina_inicial"

class CustomPasswordChangeView(PasswordChangeView):
    template_name = "registration/alterar_senha.html"
    success_url = reverse_lazy("redirecionar_usuario")

    def form_valid(self, form):
        messages.success(self.request, "Senha alterada com sucesso! ✅")
        return super().form_valid(form)


# --- HELPER FOR AVAILABLE TIMES ---

class HorariosDisponiveisView(View):
    def get(self, request, *args, **kwargs):
        barbeiro_id = request.GET.get("barbeiro")
        data_str = request.GET.get("data")
        
        if not barbeiro_id or not data_str:
            return JsonResponse({"error": "Parâmetros 'barbeiro' e 'data' são obrigatórios."}, status=400)
            
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Formato de data inválido. Use YYYY-MM-DD."}, status=400)
            
        default_times = [
            "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
            "20:00", "20:30", "21:00"
        ]
        
        barbeiro = Barbeiro.objects.filter(id=barbeiro_id, ativo=True).first()
        if not barbeiro:
            return JsonResponse({"error": "Barbeiro não encontrado."}, status=404)
            
        horarios_disp = HorarioDisponivel.objects.filter(barbeiro=barbeiro, ativo=True)
        if horarios_disp.exists():
            active_times = [h.horario.strftime("%H:%M") for h in horarios_disp]
        else:
            active_times = default_times
            
        blocked_times = Agendamento.objects.filter(
            barbeiro=barbeiro,
            data=data,
        ).exclude(status="cancelado").values_list("horario", flat=True)
        blocked_times_str = [t.strftime("%H:%M") for t in blocked_times]
        
        response_data = []
        for t_str in default_times:
            if t_str in active_times:
                is_available = t_str not in blocked_times_str
                if data == date.today():
                    now_time_str = datetime.now().strftime("%H:%M")
                    if t_str <= now_time_str:
                        is_available = False
                response_data.append({
                    "time": t_str,
                    "available": is_available
                })
            else:
                response_data.append({
                    "time": t_str,
                    "available": False
                })
                
        return JsonResponse({"times": response_data})


# --- CLIENT VIEWS ---

class AreaClienteView(ClienteRequiredMixin, TemplateView):
    template_name = "website/cliente/area_cliente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = Cliente.objects.filter(usuario=self.request.user).first()
        if cliente:
            context["cliente"] = cliente
            context["proximos_agendamentos"] = Agendamento.objects.filter(
                cliente=cliente,
                status__in=["pendente", "confirmado"]
            ).order_by("data", "horario")
            context["ultimo_agendamento"] = Agendamento.objects.filter(
                cliente=cliente,
                status="concluido"
            ).order_by("-data", "-horario").first()
        return context


class HistoricoClienteView(ClienteRequiredMixin, ListView):
    model = Agendamento
    template_name = "website/cliente/historico_cliente.html"
    context_object_name = "agendamentos"

    def get_queryset(self):
        cliente = Cliente.objects.filter(usuario=self.request.user).first()
        if cliente:
            return Agendamento.objects.filter(cliente=cliente).order_by("-data", "-horario")
        return Agendamento.objects.none()


class FeedbackCreateView(ClienteRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = "website/cliente/feedback.html"
    success_url = reverse_lazy("area_cliente")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agendamento = Agendamento.objects.get(pk=self.kwargs["pk"])
        context["agendamento"] = agendamento
        return context

    def form_valid(self, form):
        agendamento = Agendamento.objects.get(pk=self.kwargs["pk"])
        cliente = Cliente.objects.filter(usuario=self.request.user).first()
        
        if agendamento.cliente != cliente:
            messages.error(self.request, "Você só pode avaliar seus próprios agendamentos.")
            return redirect("area_cliente")
        if agendamento.status != "concluido":
            messages.error(self.request, "Você só pode avaliar agendamentos concluídos.")
            return redirect("area_cliente")
        if Feedback.objects.filter(agendamento=agendamento).exists():
            messages.error(self.request, "Você já enviou feedback para este agendamento.")
            return redirect("area_cliente")

        form.instance.usuario = self.request.user
        form.instance.cliente = cliente
        form.instance.barbeiro = agendamento.barbeiro
        form.instance.agendamento = agendamento
        messages.success(self.request, "Feedback enviado com sucesso! Obrigado. ✅")
        return super().form_valid(form)


class PerfilClienteUpdateView(ClienteRequiredMixin, UpdateView):
    model = Cliente
    form_class = PerfilClienteForm
    template_name = "website/cliente/perfil_cliente.html"
    success_url = reverse_lazy("area_cliente")

    def get_object(self, queryset=None):
        return Cliente.objects.filter(usuario=self.request.user).first()

    def form_valid(self, form):
        messages.success(self.request, "Seus dados de perfil foram atualizados! ✅")
        return super().form_valid(form)


class AgendamentoClienteCancelView(ClienteRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        cliente = Cliente.objects.filter(usuario=request.user).first()
        agendamento = Agendamento.objects.filter(id=pk, cliente=cliente, status="pendente").first()
        if agendamento:
            agendamento.status = "cancelado"
            agendamento.save()
            messages.success(request, "Agendamento cancelado com sucesso. ✅")
        else:
            messages.error(request, "Não foi possível cancelar o agendamento.")
        return redirect("area_cliente")


# --- BARBER VIEWS ---

class AreaBarbeiroView(BarbeiroRequiredMixin, TemplateView):
    template_name = "website/barbeiro/area_barbeiro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            context["barbeiro"] = barbeiro
            context["proximos_agendamentos"] = Agendamento.objects.filter(
                barbeiro=barbeiro,
                status__in=["pendente", "confirmado"]
            ).order_by("data", "horario")[:5]
            context["feedbacks"] = Feedback.objects.filter(barbeiro=barbeiro).order_by("-criado_em")[:5]
            context["fotos"] = FotoTrabalho.objects.filter(barbeiro=barbeiro).order_by("-criado_em")[:4]
        return context


class AgendamentosBarbeiroView(BarbeiroRequiredMixin, TemplateView):
    template_name = "website/barbeiro/agendamentos_barbeiro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            context["agendamentos"] = Agendamento.objects.filter(
                barbeiro=barbeiro
            ).order_by("data", "horario")
        return context

    def post(self, request, *args, **kwargs):
        agendamento_id = request.POST.get("agendamento_id")
        novo_status = request.POST.get("status")
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        
        if agendamento_id and novo_status in ["confirmado", "concluido", "cancelado"]:
            agendamento = Agendamento.objects.filter(id=agendamento_id, barbeiro=barbeiro).first()
            if agendamento:
                agendamento.status = novo_status
                agendamento.save()
                messages.success(request, f"Status do agendamento atualizado para {agendamento.get_status_display()}! ✅")
            else:
                messages.error(request, "Agendamento não encontrado.")
        return redirect("agendamentos_barbeiro")


class HistoricoBarbeiroView(BarbeiroRequiredMixin, ListView):
    model = Agendamento
    template_name = "website/barbeiro/historico_barbeiro.html"
    context_object_name = "agendamentos"

    def get_queryset(self):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            return Agendamento.objects.filter(barbeiro=barbeiro, status="concluido").order_by("-data", "-horario")
        return Agendamento.objects.none()


class RelatoriosBarbeiroView(BarbeiroRequiredMixin, TemplateView):
    template_name = "website/barbeiro/relatorios_barbeiro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            today = date.today()
            thirty_days_ago = today - timedelta(days=30)
            
            agendamentos_hoje = Agendamento.objects.filter(
                barbeiro=barbeiro, status="concluido", data=today
            )
            faturamento_hoje = agendamentos_hoje.aggregate(total=Sum("servico__preco"))["total"] or 0
            
            agendamentos_30 = Agendamento.objects.filter(
                barbeiro=barbeiro, status="concluido", data__gte=thirty_days_ago
            )
            faturamento_30 = agendamentos_30.aggregate(total=Sum("servico__preco"))["total"] or 0
            
            total_hoje = agendamentos_hoje.count()
            total_30 = agendamentos_30.count()
            
            feedbacks = Feedback.objects.filter(barbeiro=barbeiro)
            media_nota = feedbacks.aggregate(media=Avg("nota"))["media"] or 0
            
            servicos_populares = Agendamento.objects.filter(
                barbeiro=barbeiro, status="concluido"
            ).values("servico__nome").annotate(total=Count("id")).order_by("-total")[:3]
            
            clientes_atendidos = Agendamento.objects.filter(
                barbeiro=barbeiro, status="concluido"
            ).values("cliente").distinct().count()

            context.update({
                "faturamento_hoje": faturamento_hoje,
                "faturamento_30_dias": faturamento_30,
                "agendamentos_hoje_count": total_hoje,
                "agendamentos_30_dias_count": total_30,
                "media_nota": round(media_nota, 1),
                "servicos_populares": servicos_populares,
                "clientes_atendidos": clientes_atendidos,
            })
        return context


class FotosBarbeiroListView(BarbeiroRequiredMixin, ListView):
    model = FotoTrabalho
    template_name = "website/barbeiro/fotos_barbeiro.html"
    context_object_name = "fotos"

    def get_queryset(self):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            return FotoTrabalho.objects.filter(barbeiro=barbeiro).order_by("-criado_em")
        return FotoTrabalho.objects.none()


class FotoTrabalhoCreateView(BarbeiroRequiredMixin, CreateView):
    model = FotoTrabalho
    form_class = FotoTrabalhoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("fotos_barbeiro")
    extra_context = {
        "titulo": "Cadastrar Foto de Trabalho",
        "botao": "Enviar Foto"
    }

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user)
        form.fields["barbeiro"].queryset = barbeiro
        form.fields["barbeiro"].initial = barbeiro.first()
        return form

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Foto cadastrada com sucesso! ✅")
        return super().form_valid(form)


class FotoTrabalhoUpdateView(BarbeiroRequiredMixin, UpdateView):
    model = FotoTrabalho
    form_class = FotoTrabalhoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("fotos_barbeiro")
    extra_context = {
        "titulo": "Editar Foto de Trabalho",
        "botao": "Salvar Alterações"
    }

    def get_queryset(self):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        return FotoTrabalho.objects.filter(barbeiro=barbeiro)

    def form_valid(self, form):
        messages.success(self.request, "Foto atualizada com sucesso! ✅")
        return super().form_valid(form)


class FotoTrabalhoDeleteView(BarbeiroRequiredMixin, DeleteView):
    model = FotoTrabalho
    template_name = "website/excluir.html"
    success_url = reverse_lazy("fotos_barbeiro")
    extra_context = {
        "titulo": "Excluir Foto de Trabalho",
        "botao": "Excluir"
    }

    def get_queryset(self):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        return FotoTrabalho.objects.filter(barbeiro=barbeiro)

    def form_valid(self, form):
        messages.success(self.request, "Foto excluída com sucesso! ✅")
        return super().form_valid(form)


# --- ADMIN DASHBOARD ---

class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = "website/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        agendamentos_hoje = Agendamento.objects.filter(data=today)
        
        context.update({
            "agendamentos_hoje": agendamentos_hoje.count(),
            "pendentes": Agendamento.objects.filter(status="pendente").count(),
            "confirmados": Agendamento.objects.filter(status="confirmado").count(),
            "concluidos": Agendamento.objects.filter(status="concluido").count(),
            "faturamento_estimado": Agendamento.objects.filter(
                data=today, status__in=["confirmado", "concluido"]
            ).aggregate(total=Sum("servico__preco"))["total"] or 0,
            "ultimos_agendamentos": Agendamento.objects.all().order_by("-criado_em")[:10],
        })
        return context


# --- ADMIN CRUD VIEWS ---

# Servico CRUD
class ServicoCreateView(AdminRequiredMixin, CreateView):
    model = Servico
    form_class = ServicoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_servicos")
    extra_context = {"titulo": "Cadastrar Serviço", "botao": "Cadastrar"}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Serviço cadastrado com sucesso! ✅")
        return super().form_valid(form)

class ServicoUpdateView(AdminRequiredMixin, UpdateView):
    model = Servico
    form_class = ServicoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_servicos")
    extra_context = {"titulo": "Editar Serviço", "botao": "Salvar Alterações"}

    def form_valid(self, form):
        messages.success(self.request, "Serviço atualizado com sucesso! ✅")
        return super().form_valid(form)

class ServicoDeleteView(AdminRequiredMixin, DeleteView):
    model = Servico
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_servicos")
    extra_context = {"titulo": "Excluir Serviço", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Serviço excluído com sucesso! ✅")
        return super().form_valid(form)

class ServicoListView(AdminRequiredMixin, ListView):
    model = Servico
    template_name = "website/listas/servicos.html"
    context_object_name = "servicos"
    queryset = Servico.objects.all().order_by("ordem")

class ServicoDetailView(AdminRequiredMixin, DetailView):
    model = Servico
    template_name = "website/ver/servico.html"


# Barbeiro CRUD
class BarbeiroCreateView(AdminRequiredMixin, CreateView):
    model = Barbeiro
    form_class = BarbeiroForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_barbeiros")
    extra_context = {"titulo": "Cadastrar Barbeiro", "botao": "Cadastrar"}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Barbeiro cadastrado com sucesso! ✅")
        return super().form_valid(form)

class BarbeiroUpdateView(AdminRequiredMixin, UpdateView):
    model = Barbeiro
    form_class = BarbeiroForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_barbeiros")
    extra_context = {"titulo": "Editar Barbeiro", "botao": "Salvar Alterações"}

    def form_valid(self, form):
        messages.success(self.request, "Barbeiro atualizado com sucesso! ✅")
        return super().form_valid(form)

class BarbeiroDeleteView(AdminRequiredMixin, DeleteView):
    model = Barbeiro
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_barbeiros")
    extra_context = {"titulo": "Excluir Barbeiro", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Barbeiro excluído com sucesso! ✅")
        return super().form_valid(form)

class BarbeiroListView(AdminRequiredMixin, ListView):
    model = Barbeiro
    template_name = "website/listas/barbeiros.html"
    context_object_name = "barbeiros"

class BarbeiroDetailView(AdminRequiredMixin, DetailView):
    model = Barbeiro
    template_name = "website/ver/barbeiro.html"


# Cliente CRUD
class ClienteCreateView(AdminRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_clientes")
    extra_context = {"titulo": "Cadastrar Cliente", "botao": "Cadastrar"}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Cliente cadastrado com sucesso! ✅")
        return super().form_valid(form)

class ClienteUpdateView(AdminRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_clientes")
    extra_context = {"titulo": "Editar Cliente", "botao": "Salvar Alterações"}

    def form_valid(self, form):
        messages.success(self.request, "Cliente atualizado com sucesso! ✅")
        return super().form_valid(form)

class ClienteDeleteView(AdminRequiredMixin, DeleteView):
    model = Cliente
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_clientes")
    extra_context = {"titulo": "Excluir Cliente", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Cliente excluído com sucesso! ✅")
        return super().form_valid(form)

class ClienteListView(AdminRequiredMixin, ListView):
    model = Cliente
    template_name = "website/listas/clientes.html"
    context_object_name = "clientes"

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get("q")

        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) |
                Q(email__icontains=busca)
            )

        return queryset

class ClienteDetailView(AdminRequiredMixin, DetailView):
    model = Cliente
    template_name = "website/ver/cliente.html"


# HorarioDisponivel CRUD
class HorarioDisponivelCreateView(AdminRequiredMixin, CreateView):
    model = HorarioDisponivel
    form_class = HorarioDisponivelForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_horarios")
    extra_context = {"titulo": "Cadastrar Horário Disponível", "botao": "Cadastrar"}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Horário cadastrado com sucesso! ✅")
        return super().form_valid(form)

class HorarioDisponivelUpdateView(AdminRequiredMixin, UpdateView):
    model = HorarioDisponivel
    form_class = HorarioDisponivelForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_horarios")
    extra_context = {"titulo": "Editar Horário Disponível", "botao": "Salvar Alterações"}

    def form_valid(self, form):
        messages.success(self.request, "Horário atualizado com sucesso! ✅")
        return super().form_valid(form)

class HorarioDisponivelDeleteView(AdminRequiredMixin, DeleteView):
    model = HorarioDisponivel
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_horarios")
    extra_context = {"titulo": "Excluir Horário Disponível", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Horário excluído com sucesso! ✅")
        return super().form_valid(form)

class HorarioDisponivelListView(AdminRequiredMixin, ListView):
    model = HorarioDisponivel
    template_name = "website/listas/horarios.html"
    context_object_name = "horarios"

class HorarioDisponivelDetailView(AdminRequiredMixin, DetailView):
    model = HorarioDisponivel
    template_name = "website/ver/horario.html"


# Agendamento CRUD
class AgendamentoCreateView(AdminRequiredMixin, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_agendamentos")
    extra_context = {"titulo": "Cadastrar Agendamento", "botao": "Cadastrar"}

    def form_valid(self, form):
        # Prevent double booking for same barber, date, and time
        barbeiro = form.cleaned_data["barbeiro"]
        data = form.cleaned_data["data"]
        horario = form.cleaned_data["horario"]
        if Agendamento.objects.filter(barbeiro=barbeiro, data=data, horario=horario).exclude(status="cancelado").exists():
            form.add_error("horario", "Este horário já está reservado para este barbeiro.")
            return self.form_invalid(form)

        form.instance.usuario = self.request.user
        messages.success(self.request, "Agendamento realizado com sucesso! ✅")
        return super().form_valid(form)

class AgendamentoUpdateView(AdminRequiredMixin, UpdateView):
    model = Agendamento
    form_class = AgendamentoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_agendamentos")
    extra_context = {"titulo": "Editar Agendamento", "botao": "Salvar Alterações"}

    def form_valid(self, form):
        messages.success(self.request, "Agendamento atualizado com sucesso! ✅")
        return super().form_valid(form)

class AgendamentoDeleteView(AdminRequiredMixin, DeleteView):
    model = Agendamento
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_agendamentos")
    extra_context = {"titulo": "Excluir Agendamento", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Agendamento excluído com sucesso! ✅")
        return super().form_valid(form)

class AgendamentoListView(AdminRequiredMixin, ListView):
    model = Agendamento
    template_name = "website/listas/agendamentos.html"
    context_object_name = "agendamentos"
    queryset = Agendamento.objects.all().order_by("-data", "-horario")

class AgendamentoDetailView(AdminRequiredMixin, DetailView):
    model = Agendamento
    template_name = "website/ver/agendamento.html"


# MensagemContato CRUD
class MensagemContatoListView(AdminRequiredMixin, ListView):
    model = MensagemContato
    template_name = "website/listas/mensagens.html"
    context_object_name = "mensagens"
    queryset = MensagemContato.objects.all().order_by("-enviada_em")

class MensagemContatoDetailView(AdminRequiredMixin, DetailView):
    model = MensagemContato
    template_name = "website/ver/mensagem.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.lida:
            obj.lida = True
            obj.save()
        return obj

class MensagemContatoDeleteView(AdminRequiredMixin, DeleteView):
    model = MensagemContato
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_mensagens")
    extra_context = {"titulo": "Excluir Mensagem de Contato", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Mensagem excluída com sucesso! ✅")
        return super().form_valid(form)


# Feedback CRUD
class FeedbackListView(AdminRequiredMixin, ListView):
    model = Feedback
    template_name = "website/listas/feedbacks.html"
    context_object_name = "feedbacks"
    queryset = Feedback.objects.all().order_by("-criado_em")

class FeedbackDetailView(AdminRequiredMixin, DetailView):
    model = Feedback
    template_name = "website/ver/feedback.html"

class FeedbackDeleteView(AdminRequiredMixin, DeleteView):
    model = Feedback
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_feedbacks")
    extra_context = {"titulo": "Excluir Feedback", "botao": "Excluir"}

    def form_valid(self, form):
        messages.success(self.request, "Feedback excluído com sucesso! ✅")
        return super().form_valid(form)


# FotoTrabalho CRUD (Admin View)
class FotoTrabalhoListView(AdminRequiredMixin, ListView):
    model = FotoTrabalho
    template_name = "website/listas/fotos.html"
    context_object_name = "fotos"

class FotoTrabalhoDetailView(AdminRequiredMixin, DetailView):
    model = FotoTrabalho
    template_name = "website/ver/foto.html"