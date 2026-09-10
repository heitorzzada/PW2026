from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db.models import Sum, Avg, Count, Q
from datetime import date, datetime, timedelta

from .models import (
    PerfilUsuario, Servico, Barbeiro, Cliente,
    HorarioDisponivel, Agendamento, MensagemContato,
    Feedback, FotoTrabalho, CupomDesconto, Produto,
    VendaProduto, ComissaoBarbeiro, PagamentoPix,
    CartaoFidelidade, MovimentacaoFidelidade, NotificacaoLog,
    BloqueioHorarioBarbeiro, FichaCliente, FilaEspera,
    PlanoAssinatura, AssinaturaCliente, ItemAgendamento
)
from .forms import (
    CadastroUsuarioForm, PerfilUsuarioForm, ServicoForm,
    BarbeiroForm, ClienteForm, HorarioDisponivelForm,
    AgendamentoForm, AgendamentoPublicoForm, MensagemContatoForm,
    FeedbackForm, FotoTrabalhoForm, PerfilClienteForm,
    BloqueioHorarioForm, FichaClienteForm, FilaEsperaForm,
    VendaProdutoRapidaForm, CupomDescontoForm, PlanoAssinaturaForm
)
from .pix import gerar_payload_pix, gerar_url_qrcode_pix

# --- SECURITY MIXINS ---

class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    group_required = None

    def get_group_required(self):
        return self.group_required

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        groups = self.get_group_required()
        if groups:
            if isinstance(groups, str):
                groups = [groups]
            if self.request.user.groups.filter(name__in=groups).exists():
                return True
            perfil_tipo = getattr(getattr(self.request.user, "perfil", None), "tipo_usuario", None)
            if "Administradores" in groups and (self.request.user.is_staff or perfil_tipo == "administrador"):
                return True
            if "Barbeiros" in groups and perfil_tipo == "barbeiro":
                return True
            if "Clientes" in groups and perfil_tipo == "cliente":
                return True
            return False
        return True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Acesso não permitido para o seu perfil de usuário. 🛑")
        return redirect("redirecionar_usuario")


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        if hasattr(self.request.user, "perfil") and self.request.user.perfil.tipo_usuario == "administrador":
            return True
        return self.request.user.groups.filter(name="Administradores").exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Acesso exclusivo para administradores. 🛑")
        return redirect("redirecionar_usuario")


class ClienteRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        if hasattr(self.request.user, "perfil") and self.request.user.perfil.tipo_usuario in ["cliente", "administrador"]:
            return True
        return self.request.user.groups.filter(name="Clientes").exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Área restrita aos clientes. 🛑")
        return redirect("redirecionar_usuario")


class BarbeiroRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        if hasattr(self.request.user, "perfil") and self.request.user.perfil.tipo_usuario in ["barbeiro", "administrador"]:
            return True
        return self.request.user.groups.filter(name="Barbeiros").exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Área restrita aos barbeiros. 🛑")
        return redirect("redirecionar_usuario")



# --- PUBLIC VIEWS ---

class IndexView(TemplateView):
    template_name = "website/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["servicos_destaque"] = Servico.objects.filter(ativo=True, destaque=True).order_by("ordem")
        context["barbeiros"] = Barbeiro.objects.filter(ativo=True)
        context["fotos_trabalho"] = FotoTrabalho.objects.select_related("barbeiro").filter(publicado=True).order_by("-criado_em")
        return context


class ServicosPublicView(ListView):
    model = Servico
    template_name = "website/servicos.html"
    context_object_name = "servicos"
    paginate_by = 10

    def get_queryset(self):
        return Servico.objects.filter(ativo=True).order_by("ordem")


class BarbeirosPublicView(ListView):
    model = Barbeiro
    template_name = "website/barbeiros.html"
    context_object_name = "barbeiros"
    paginate_by = 10

    def get_queryset(self):
        return Barbeiro.objects.filter(ativo=True).order_by("nome")


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
        servico = cleaned_data["servico"]
        metodo_pagamento = cleaned_data.get("metodo_pagamento", "pix")
        cupom_codigo = cleaned_data.get("cupom_codigo", "").strip().upper()
        
        # Validação de disponibilidade com duração real e buffer de 5 minutos
        duracao_atendimento = servico.duracao_minutos or 30
        buffer_minutos = 5
        cand_inicio_dt = datetime.combine(data, horario)
        cand_fim_ocupado_dt = cand_inicio_dt + timedelta(minutes=duracao_atendimento + buffer_minutos)
        cand_horario_fim = (cand_inicio_dt + timedelta(minutes=duracao_atendimento)).time()

        if BloqueioHorarioBarbeiro.objects.filter(barbeiro=barbeiro, data=data, dia_inteiro=True).exists():
            form.add_error("data", "Este barbeiro está de folga nesta data.")
            return self.form_invalid(form)

        # Colisão de intervalos semiabertos contra agendamentos existentes
        agendamentos_existentes = Agendamento.objects.filter(
            barbeiro=barbeiro, data=data
        ).exclude(status="cancelado")

        for ag in agendamentos_existentes:
            dur_ag = ag.duracao_total_minutos or (ag.servico.duracao_minutos if ag.servico else 30)
            ag_inicio_dt = datetime.combine(data, ag.horario)
            ag_fim_ocupado_dt = ag_inicio_dt + timedelta(minutes=dur_ag + buffer_minutos)
            if cand_inicio_dt < ag_fim_ocupado_dt and cand_fim_ocupado_dt > ag_inicio_dt:
                form.add_error("horario", f"Este horário colide com outro agendamento (iniciado às {ag.horario.strftime('%H:%M')}).")
                return self.form_invalid(form)

        # Colisão com bloqueios pontuais do barbeiro
        bloqueios = BloqueioHorarioBarbeiro.objects.filter(
            barbeiro=barbeiro, data=data, dia_inteiro=False, horario__isnull=False
        )
        for bl in bloqueios:
            bl_inicio_dt = datetime.combine(data, bl.horario)
            bl_fim_ocupado_dt = bl_inicio_dt + timedelta(minutes=30 + buffer_minutos)
            if cand_inicio_dt < bl_fim_ocupado_dt and cand_fim_ocupado_dt > bl_inicio_dt:
                form.add_error("horario", f"Horário bloqueado pelo barbeiro ({bl.motivo}).")
                return self.form_invalid(form)

        preco_base = float(servico.preco)
        desconto = 0.0
        cupom_encontrado = None

        # 1. Verifica Assinatura Ativa (Clube Delacruz)
        assinatura = AssinaturaCliente.objects.filter(cliente=cliente, status="ativa").first()
        coberto_por_assinatura = False
        if assinatura and assinatura.tem_cortes_disponiveis():
            desconto = preco_base
            assinatura.cortes_usados_mes += 1
            assinatura.save()
            coberto_por_assinatura = True

        # 2. Verifica Cupom de Desconto ou Código de Amigo (se não coberto pela assinatura)
        elif cupom_codigo:
            cupom = CupomDesconto.objects.filter(codigo__iexact=cupom_codigo, ativo=True).first()
            if cupom and cupom.is_valido():
                desconto = float(cupom.calcular_desconto(preco_base))
                cupom.usado_vezes += 1
                cupom.save()
                cupom_encontrado = cupom
            else:
                # Código de Indicação de Amigo
                amigo = Cliente.objects.filter(codigo_indicacao__iexact=cupom_codigo).exclude(id=cliente.id).first()
                if amigo:
                    desconto = min(10.0, preco_base)
                    amigo.saldo_creditos = float(amigo.saldo_creditos) + 10.0
                    amigo.save()
                    messages.info(self.request, f"Código de indicação do(a) {amigo.nome} aplicado! R$ 10,00 de desconto. 🎁")

        valor_final = max(round(preco_base - desconto, 2), 0.0)

        agendamento = Agendamento.objects.create(
            usuario=self.request.user if self.request.user.is_authenticated else None,
            cliente=cliente,
            servico=servico,
            barbeiro=barbeiro,
            data=data,
            horario=horario,
            horario_fim=cand_horario_fim,
            duracao_total_minutos=duracao_atendimento,
            status="confirmado" if coberto_por_assinatura else "pendente",
            valor_total=preco_base,
            desconto_aplicado=desconto,
            cupom=cupom_encontrado,
            metodo_pagamento=metodo_pagamento,
            status_pagamento="pago" if coberto_por_assinatura else "pendente",
            observacoes=cleaned_data.get("observacoes"),
        )
        agendamento.servicos.add(servico)

        # Snapshot de ItemAgendamento
        ItemAgendamento.objects.create(
            agendamento=agendamento,
            servico=servico,
            preco_unitario=servico.preco,
            duracao_minutos=duracao_atendimento
        )

        # Se escolheu PIX e tem valor a pagar, gera dados de pagamento Pix
        if metodo_pagamento in ["pix", "pix_sinal", "pix_total"] and valor_final > 0:
            valor_pix = valor_final
            txid = f"DELA{agendamento.id}{int(datetime.now().timestamp()) % 10000}"
            payload_pix = gerar_payload_pix(
                chave_pix="delacruz@barber.com.br",
                nome_recebedor="Delacruz Barber",
                cidade_recebedor="Maringa",
                valor=valor_pix,
                txid=txid
            )
            PagamentoPix.objects.create(
                agendamento=agendamento,
                transacao_id=txid,
                valor=valor_pix,
                qr_code_payload=payload_pix,
                status="pendente"
            )
            messages.success(self.request, "Agendamento reservado! Efetue o pagamento via Pix para confirmação. 📱")
            return redirect("pix_pagamento", pk=agendamento.id)

        if coberto_por_assinatura:
            messages.success(self.request, "Agendamento confirmado com sucesso pelo seu Plano VIP Delacruz Club! 👑")
        else:
            messages.success(self.request, "Seu agendamento foi solicitado com sucesso! Acompanhe em sua área. ✅")
            
        if self.request.user.is_authenticated:
            return redirect("area_cliente")
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

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
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
        servico_id = request.GET.get("servico") or request.GET.get("servico_id")
        plano_id = request.GET.get("plano") or request.GET.get("plano_id")
        
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
            "20:00", "20:30", "21:00", "21:30"
        ]
        
        barbeiro = Barbeiro.objects.filter(id=barbeiro_id, ativo=True).first()
        if not barbeiro:
            return JsonResponse({"error": "Barbeiro não encontrado."}, status=404)
            
        # Determina a duração prevista do atendimento (em minutos)
        duracao_atendimento = 30
        if servico_id:
            serv = Servico.objects.filter(id=servico_id, ativo=True).first()
            if serv:
                duracao_atendimento = serv.duracao_minutos
        elif plano_id:
            plano = PlanoAssinatura.objects.filter(Q(id=plano_id) | Q(codigo=plano_id), ativo=True).first()
            if plano and plano.servicos_inclusos.exists():
                duracao_atendimento = sum(s.duracao_minutos for s in plano.servicos_inclusos.all())

        buffer_minutos = 5
        duracao_ocupada_candidato = duracao_atendimento + buffer_minutos

        # Verifica folga do dia (dia inteiro bloqueado)
        dia_todo_bloqueado = BloqueioHorarioBarbeiro.objects.filter(barbeiro=barbeiro, data=data, dia_inteiro=True).exists()
        if dia_todo_bloqueado:
            return JsonResponse({
                "times": [{"time": t, "available": False} for t in default_times],
                "dia_bloqueado": True,
                "duracao_atendimento": duracao_atendimento
            })

        # Coleta intervalos ocupados existentes (Agendamentos ativos)
        agendamentos = Agendamento.objects.filter(
            barbeiro=barbeiro,
            data=data
        ).exclude(status="cancelado")

        intervalos_ocupados = []
        for ag in agendamentos:
            dur_ag = ag.duracao_total_minutos or (ag.servico.duracao_minutos if ag.servico else 30)
            inicio_dt = datetime.combine(data, ag.horario)
            fim_ocupado_dt = inicio_dt + timedelta(minutes=dur_ag + buffer_minutos)
            intervalos_ocupados.append((inicio_dt, fim_ocupado_dt))

        # Coleta bloqueios pontuais do barbeiro
        bloqueios = BloqueioHorarioBarbeiro.objects.filter(
            barbeiro=barbeiro, data=data, dia_inteiro=False, horario__isnull=False
        )
        for bl in bloqueios:
            inicio_dt = datetime.combine(data, bl.horario)
            fim_ocupado_dt = inicio_dt + timedelta(minutes=30 + buffer_minutos)
            intervalos_ocupados.append((inicio_dt, fim_ocupado_dt))

        # Verifica quais horários estão ativos no cadastro do barbeiro
        horarios_disp = HorarioDisponivel.objects.filter(barbeiro=barbeiro, ativo=True)
        if horarios_disp.exists():
            active_times_set = set(h.horario.strftime("%H:%M") for h in horarios_disp)
        else:
            active_times_set = set(default_times)

        agora = datetime.now()
        response_data = []

        for t_str in default_times:
            if t_str not in active_times_set:
                response_data.append({
                    "time": t_str,
                    "available": False,
                    "duracao_minutos": duracao_atendimento
                })
                continue

            h_time = datetime.strptime(t_str, "%H:%M").time()
            cand_inicio_dt = datetime.combine(data, h_time)
            cand_fim_ocupado_dt = cand_inicio_dt + timedelta(minutes=duracao_ocupada_candidato)

            # Colisão de intervalos semiabertos: inicio_cand < fim_exist e fim_cand > inicio_exist
            colide = False
            for oc_inicio, oc_fim in intervalos_ocupados:
                if cand_inicio_dt < oc_fim and cand_fim_ocupado_dt > oc_inicio:
                    colide = True
                    break

            # Se for hoje, bloqueia horários no passado
            if not colide and data == date.today():
                if cand_inicio_dt <= agora:
                    colide = True

            response_data.append({
                "time": t_str,
                "available": not colide,
                "duracao_minutos": duracao_atendimento,
                "termino_previsto": (cand_inicio_dt + timedelta(minutes=duracao_atendimento)).strftime("%H:%M")
            })

        return JsonResponse({
            "times": response_data,
            "dia_bloqueado": False,
            "duracao_atendimento": duracao_atendimento,
            "buffer_minutos": buffer_minutos
        })


# --- CLIENT VIEWS ---

class AreaClienteView(ClienteRequiredMixin, TemplateView):
    template_name = "website/cliente/area_cliente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = Cliente.objects.filter(usuario=self.request.user).first()
        if cliente:
            context["cliente"] = cliente
            context["proximos_agendamentos"] = Agendamento.objects.select_related(
                "servico", "barbeiro"
            ).filter(
                cliente=cliente,
                status__in=["pendente", "confirmado"]
            ).order_by("data", "horario")
            context["ultimo_agendamento"] = Agendamento.objects.select_related(
                "servico", "barbeiro"
            ).filter(
                cliente=cliente,
                status="concluido"
            ).order_by("-data", "-horario").first()
            
            # 1. Carteirinha de Fidelidade Digital (10 selos)
            cartao, _ = CartaoFidelidade.objects.get_or_create(cliente=cliente)
            context["fidelidade"] = cartao
            context["selos_preenchidos"] = range(min(cartao.pontos_acumulados, 10))
            context["selos_restantes"] = range(max(10 - cartao.pontos_acumulados, 0))
            
            # 2. Clube de Assinatura VIP
            assinatura = AssinaturaCliente.objects.select_related("plano").filter(cliente=cliente, status="ativa").first()
            context["assinatura"] = assinatura
            
            # 3. Fila de espera ativa do cliente
            context["filas_ativas"] = FilaEspera.objects.filter(cliente=cliente, status="aguardando").order_by("data_desejada")
        return context


class HistoricoClienteView(ClienteRequiredMixin, ListView):
    model = Agendamento
    template_name = "website/cliente/historico_cliente.html"
    context_object_name = "agendamentos"
    paginate_by = 10

    def get_queryset(self):
        cliente = Cliente.objects.filter(usuario=self.request.user).first()
        if cliente:
            return Agendamento.objects.select_related(
                "servico", "barbeiro"
            ).filter(cliente=cliente).order_by("-data", "-horario")
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

    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)

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
            context["proximos_agendamentos"] = Agendamento.objects.select_related(
                "cliente", "servico"
            ).filter(
                barbeiro=barbeiro,
                status__in=["pendente", "confirmado"]
            ).order_by("data", "horario")[:5]
            context["feedbacks"] = Feedback.objects.select_related(
                "cliente"
            ).filter(barbeiro=barbeiro).order_by("-criado_em")[:5]
            context["fotos"] = FotoTrabalho.objects.select_related(
                "barbeiro"
            ).filter(barbeiro=barbeiro).order_by("-criado_em")[:4]
        return context


class AgendamentosBarbeiroView(BarbeiroRequiredMixin, TemplateView):
    template_name = "website/barbeiro/agendamentos_barbeiro.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            context["agendamentos"] = Agendamento.objects.select_related(
                "cliente", "servico"
            ).prefetch_related("vendas_produtos__produto").filter(
                barbeiro=barbeiro
            ).order_by("data", "horario")
            context["produtos_disponiveis"] = Produto.objects.filter(ativo=True).order_by("nome")
        return context

    def post(self, request, *args, **kwargs):
        agendamento_id = request.POST.get("agendamento_id")
        action = request.POST.get("action", "status")
        novo_status = request.POST.get("status")
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        
        if not agendamento_id or not barbeiro:
            messages.error(request, "Ação inválida.")
            return redirect("agendamentos_barbeiro")
            
        agendamento = Agendamento.objects.filter(id=agendamento_id, barbeiro=barbeiro).first()
        if not agendamento:
            messages.error(request, "Agendamento não encontrado.")
            return redirect("agendamentos_barbeiro")
            
        if action == "toggle_checkin":
            agendamento.checkin_realizado = not agendamento.checkin_realizado
            agendamento.save()
            estado = "confirmada" if agendamento.checkin_realizado else "desfeita"
            messages.success(request, f"Presença de {agendamento.cliente.nome} {estado}! 📍")
            return redirect("agendamentos_barbeiro")

        if action == "toggle_atendimento":
            agendamento.em_atendimento = not agendamento.em_atendimento
            agendamento.save()
            msg = "iniciado na cadeira" if agendamento.em_atendimento else "finalizado na cadeira"
            messages.info(request, f"Atendimento de {agendamento.cliente.nome} {msg}! 💈")
            return redirect("agendamentos_barbeiro")

        if action == "marcar_pago":
            agendamento.status_pagamento = "pago"
            agendamento.save()
            messages.success(request, f"Pagamento de {agendamento.cliente.nome} marcado como PAGO! 💵")
            return redirect("agendamentos_barbeiro")

        if novo_status in ["confirmado", "concluido", "cancelado"]:
            agendamento.status = novo_status
            if novo_status == "concluido":
                agendamento.em_atendimento = False
                agendamento.status_pagamento = "pago"
                
                # 1. Carimba selo na Carteirinha de Fidelidade
                cartao, _ = CartaoFidelidade.objects.get_or_create(cliente=agendamento.cliente)
                cartao.registrar_corte_concluido(agendamento)
                
                # 2. Registra comissão do barbeiro
                if float(barbeiro.percentual_comissao) > 0:
                    base_val = float(agendamento.servico.preco if agendamento.servico else agendamento.valor_total)
                    comissao_val = round((base_val * float(barbeiro.percentual_comissao)) / 100, 2)
                    ComissaoBarbeiro.objects.update_or_create(
                        agendamento=agendamento,
                        defaults={
                            "barbeiro": barbeiro,
                            "valor_total_servico": base_val,
                            "percentual_comissao": barbeiro.percentual_comissao,
                            "valor_comissao": comissao_val,
                        }
                    )
                messages.success(request, f"Corte de {agendamento.cliente.nome} concluído! Selo de fidelidade carimbado. ⭐")

            elif novo_status == "cancelado":
                # Fila de espera inteligente: busca quem estava aguardando vaga
                espera = FilaEspera.objects.filter(
                    data_desejada=agendamento.data,
                    status="aguardando"
                ).filter(Q(barbeiro=barbeiro) | Q(barbeiro__isnull=True)).first()
                if espera:
                    espera.status = "notificado"
                    espera.save()
                    messages.info(request, f"Vaga liberada! O cliente {espera.cliente.nome} da Fila de Espera foi prioritariamente notificado. 🔔")
                messages.warning(request, f"Agendamento de {agendamento.cliente.nome} cancelado.")
            else:
                messages.success(request, f"Agendamento confirmado com sucesso! ✅")
                
            agendamento.save()
            
        return redirect("agendamentos_barbeiro")


class HistoricoBarbeiroView(BarbeiroRequiredMixin, ListView):
    model = Agendamento
    template_name = "website/barbeiro/historico_barbeiro.html"
    context_object_name = "agendamentos"
    paginate_by = 10

    def get_queryset(self):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            return Agendamento.objects.select_related(
                "cliente", "servico"
            ).filter(barbeiro=barbeiro, status="concluido").order_by("-data", "-horario")
        return Agendamento.objects.none()


class RelatoriosBarbeiroView(GroupRequiredMixin, BarbeiroRequiredMixin, TemplateView):
    template_name = "website/barbeiro/relatorios_barbeiro.html"
    group_required = "Barbeiros"

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
                barbeiro=barbeiro
            ).exclude(status="cancelado").values("servico__nome").annotate(total=Count("id")).order_by("-total")[:3]
            
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
    paginate_by = 10

    def get_queryset(self):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        if barbeiro:
            return FotoTrabalho.objects.select_related(
                "barbeiro"
            ).filter(barbeiro=barbeiro).order_by("-criado_em")
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

class DashboardView(GroupRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "website/dashboard.html"
    group_required = "Administradores"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        agendamentos = Agendamento.objects.all()
        agendamentos_hoje = agendamentos.filter(data=today)
        
        faturamento_estimado = agendamentos_hoje.exclude(
            status="cancelado"
        ).aggregate(total=Sum("servico__preco"))["total"] or 0

        servicos_populares = agendamentos.exclude(
            status="cancelado"
        ).values("servico__nome").annotate(total=Count("id")).order_by("-total")[:5]

        media_satisfacao = Feedback.objects.aggregate(media=Avg("nota"))["media"] or 0


        ultimos_agendamentos = agendamentos.select_related(
            "cliente", "servico", "barbeiro"
        ).order_by("-criado_em")[:10]

        context.update({
            "agendamentos_hoje": agendamentos_hoje.count(),
            "pendentes": agendamentos.filter(status="pendente").count(),
            "confirmados": agendamentos.filter(status="confirmado").count(),
            "concluidos": agendamentos.filter(status="concluido").count(),
            "faturamento_estimado": faturamento_estimado,
            "servicos_populares": servicos_populares,
            "media_satisfacao": round(media_satisfacao, 1) if media_satisfacao else 0,
            "ultimos_agendamentos": ultimos_agendamentos,
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

    def get_queryset(self):
        return Servico.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Serviço atualizado com sucesso! ✅")
        return super().form_valid(form)

class ServicoDeleteView(AdminRequiredMixin, DeleteView):
    model = Servico
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_servicos")
    extra_context = {"titulo": "Excluir Serviço", "botao": "Excluir"}

    def get_queryset(self):
        return Servico.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Serviço excluído com sucesso! ✅")
        return super().form_valid(form)

class ServicoListView(AdminRequiredMixin, ListView):
    model = Servico
    template_name = "website/listas/servicos.html"
    context_object_name = "servicos"
    paginate_by = 10

    def get_queryset(self):
        return Servico.objects.filter(usuario=self.request.user).order_by("ordem")

class ServicoDetailView(AdminRequiredMixin, DetailView):
    model = Servico
    template_name = "website/ver/servico.html"

    def get_queryset(self):
        return Servico.objects.filter(usuario=self.request.user)


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

    def get_queryset(self):
        return Barbeiro.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Barbeiro atualizado com sucesso! ✅")
        return super().form_valid(form)

class BarbeiroDeleteView(AdminRequiredMixin, DeleteView):
    model = Barbeiro
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_barbeiros")
    extra_context = {"titulo": "Excluir Barbeiro", "botao": "Excluir"}

    def get_queryset(self):
        return Barbeiro.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Barbeiro excluído com sucesso! ✅")
        return super().form_valid(form)

class BarbeiroListView(AdminRequiredMixin, ListView):
    model = Barbeiro
    template_name = "website/listas/barbeiros.html"
    context_object_name = "barbeiros"
    paginate_by = 10

    def get_queryset(self):
        return Barbeiro.objects.filter(usuario=self.request.user).order_by("nome")

class BarbeiroDetailView(AdminRequiredMixin, DetailView):
    model = Barbeiro
    template_name = "website/ver/barbeiro.html"

    def get_queryset(self):
        return Barbeiro.objects.filter(usuario=self.request.user)


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

    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Cliente atualizado com sucesso! ✅")
        return super().form_valid(form)

class ClienteDeleteView(AdminRequiredMixin, DeleteView):
    model = Cliente
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_clientes")
    extra_context = {"titulo": "Excluir Cliente", "botao": "Excluir"}

    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Cliente excluído com sucesso! ✅")
        return super().form_valid(form)

class ClienteListView(AdminRequiredMixin, ListView):
    model = Cliente
    template_name = "website/listas/clientes.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        queryset = Cliente.objects.filter(usuario=self.request.user)
        busca = self.request.GET.get("q")

        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) |
                Q(email__icontains=busca)
            )

        return queryset.order_by("nome")

class ClienteDetailView(AdminRequiredMixin, DetailView):
    model = Cliente
    template_name = "website/ver/cliente.html"

    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)


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

    def get_queryset(self):
        return HorarioDisponivel.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Horário atualizado com sucesso! ✅")
        return super().form_valid(form)

class HorarioDisponivelDeleteView(AdminRequiredMixin, DeleteView):
    model = HorarioDisponivel
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_horarios")
    extra_context = {"titulo": "Excluir Horário Disponível", "botao": "Excluir"}

    def get_queryset(self):
        return HorarioDisponivel.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Horário excluído com sucesso! ✅")
        return super().form_valid(form)

class HorarioDisponivelListView(AdminRequiredMixin, ListView):
    model = HorarioDisponivel
    template_name = "website/listas/horarios.html"
    context_object_name = "horarios"
    paginate_by = 10

    def get_queryset(self):
        return HorarioDisponivel.objects.select_related("barbeiro").filter(usuario=self.request.user).order_by("barbeiro__nome", "horario")

class HorarioDisponivelDetailView(AdminRequiredMixin, DetailView):
    model = HorarioDisponivel
    template_name = "website/ver/horario.html"

    def get_queryset(self):
        return HorarioDisponivel.objects.filter(usuario=self.request.user)


# Agendamento CRUD
class AgendamentoCreateView(AdminRequiredMixin, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    template_name = "website/form.html"
    success_url = reverse_lazy("listar_agendamentos")
    extra_context = {"titulo": "Cadastrar Agendamento", "botao": "Cadastrar"}

    def form_valid(self, form):
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

    def get_queryset(self):
        return Agendamento.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Agendamento atualizado com sucesso! ✅")
        return super().form_valid(form)

class AgendamentoDeleteView(AdminRequiredMixin, DeleteView):
    model = Agendamento
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_agendamentos")
    extra_context = {"titulo": "Excluir Agendamento", "botao": "Excluir"}

    def get_queryset(self):
        return Agendamento.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Agendamento excluído com sucesso! ✅")
        return super().form_valid(form)

class AgendamentoListView(GroupRequiredMixin, AdminRequiredMixin, ListView):
    model = Agendamento
    template_name = "website/listas/agendamentos.html"
    context_object_name = "agendamentos"
    paginate_by = 10
    group_required = "Administradores"

    def get_queryset(self):
        return Agendamento.objects.select_related("cliente", "servico", "barbeiro").filter(usuario=self.request.user).order_by("-data", "-horario")

class AgendamentoDetailView(AdminRequiredMixin, DetailView):
    model = Agendamento
    template_name = "website/ver/agendamento.html"

    def get_queryset(self):
        return Agendamento.objects.filter(usuario=self.request.user)


# MensagemContato CRUD
class MensagemContatoListView(AdminRequiredMixin, ListView):
    model = MensagemContato
    template_name = "website/listas/mensagens.html"
    context_object_name = "mensagens"
    paginate_by = 10

    def get_queryset(self):
        return MensagemContato.objects.filter(usuario=self.request.user).order_by("-enviada_em")

class MensagemContatoDetailView(AdminRequiredMixin, DetailView):
    model = MensagemContato
    template_name = "website/ver/mensagem.html"

    def get_queryset(self):
        return MensagemContato.objects.filter(usuario=self.request.user)

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

    def get_queryset(self):
        return MensagemContato.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Mensagem excluída com sucesso! ✅")
        return super().form_valid(form)


# Feedback CRUD
class FeedbackListView(AdminRequiredMixin, ListView):
    model = Feedback
    template_name = "website/listas/feedbacks.html"
    context_object_name = "feedbacks"
    paginate_by = 10

    def get_queryset(self):
        return Feedback.objects.select_related("cliente", "barbeiro", "agendamento").filter(usuario=self.request.user).order_by("-criado_em")

class FeedbackDetailView(AdminRequiredMixin, DetailView):
    model = Feedback
    template_name = "website/ver/feedback.html"

    def get_queryset(self):
        return Feedback.objects.filter(usuario=self.request.user)

class FeedbackDeleteView(AdminRequiredMixin, DeleteView):
    model = Feedback
    template_name = "website/excluir.html"
    success_url = reverse_lazy("listar_feedbacks")
    extra_context = {"titulo": "Excluir Feedback", "botao": "Excluir"}

    def get_queryset(self):
        return Feedback.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Feedback excluído com sucesso! ✅")
        return super().form_valid(form)


# FotoTrabalho CRUD (Admin View)
class FotoTrabalhoListView(AdminRequiredMixin, ListView):
    model = FotoTrabalho
    template_name = "website/listas/fotos.html"
    context_object_name = "fotos"
    paginate_by = 10

    def get_queryset(self):
        return FotoTrabalho.objects.select_related("barbeiro").filter(usuario=self.request.user).order_by("-criado_em")

class FotoTrabalhoDetailView(AdminRequiredMixin, DetailView):
    model = FotoTrabalho
    template_name = "website/ver/foto.html"

    def get_queryset(self):
        return FotoTrabalho.objects.filter(usuario=self.request.user)


# =========================================================================
# NOVAS FUNCIONALIDADES: PIX, BLOQUEIOS, FICHA, COMANDA, FILA, TV, CLUBE
# =========================================================================

class PagamentoPixDetailView(DetailView):
    model = Agendamento
    template_name = "website/pix_pagamento.html"
    context_object_name = "agendamento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agendamento = self.get_object()
        pix = getattr(agendamento, "pagamento_pix", None)
        if pix:
            context["pix"] = pix
            context["qrcode_url"] = gerar_url_qrcode_pix(pix.qr_code_payload, tamanho=260)
        return context

    def post(self, request, *args, **kwargs):
        agendamento = self.get_object()
        pix = getattr(agendamento, "pagamento_pix", None)
        # Simula/Confirma o pagamento via Pix
        if pix:
            pix.status = "pago"
            pix.pago_em = datetime.now()
            pix.save()
            agendamento.status = "confirmado"
            agendamento.status_pagamento = "pago"
            agendamento.save()
            messages.success(request, "Pagamento PIX confirmado com sucesso! Seu horário está garantido. 🎉")
        if request.user.is_authenticated:
            return redirect("area_cliente")
        return redirect("pagina_inicial")


class BloqueiosBarbeiroView(BarbeiroRequiredMixin, TemplateView):
    template_name = "website/barbeiro/bloqueios.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        context["barbeiro"] = barbeiro
        context["bloqueios"] = BloqueioHorarioBarbeiro.objects.filter(barbeiro=barbeiro).order_by("-data")
        context["form"] = BloqueioHorarioForm()
        return context

    def post(self, request, *args, **kwargs):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        form = BloqueioHorarioForm(request.POST)
        if form.is_valid():
            bloqueio = form.save(commit=False)
            bloqueio.barbeiro = barbeiro
            bloqueio.save()
            messages.success(request, "Horário/Data bloqueado com sucesso! ✅")
        else:
            messages.error(request, "Erro ao registrar bloqueio. Verifique os dados.")
        return redirect("bloqueios_barbeiro")


class BloqueioBarbeiroDeleteView(BarbeiroRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        bloqueio = BloqueioHorarioBarbeiro.objects.filter(id=pk, barbeiro=barbeiro).first()
        if bloqueio:
            bloqueio.delete()
            messages.success(request, "Bloqueio removido! O horário voltou a ficar disponível. ✅")
        return redirect("bloqueios_barbeiro")


class FichaClienteView(BarbeiroRequiredMixin, View):
    def get(self, request, cliente_id, *args, **kwargs):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        cliente = Cliente.objects.filter(id=cliente_id).first()
        if not cliente:
            messages.error(request, "Cliente não encontrado.")
            return redirect("agendamentos_barbeiro")
        ficha, _ = FichaCliente.objects.get_or_create(cliente=cliente, barbeiro=barbeiro)
        form = FichaClienteForm(instance=ficha)
        return render(request, "website/barbeiro/ficha_cliente.html", {
            "cliente": cliente,
            "barbeiro": barbeiro,
            "ficha": ficha,
            "form": form,
        })

    def post(self, request, cliente_id, *args, **kwargs):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        cliente = Cliente.objects.filter(id=cliente_id).first()
        ficha, _ = FichaCliente.objects.get_or_create(cliente=cliente, barbeiro=barbeiro)
        form = FichaClienteForm(request.POST, instance=ficha)
        if form.is_valid():
            form.save()
            messages.success(request, f"Ficha técnica de {cliente.nome} atualizada com sucesso! 📝")
            return redirect("agendamentos_barbeiro")
        return render(request, "website/barbeiro/ficha_cliente.html", {
            "cliente": cliente,
            "barbeiro": barbeiro,
            "ficha": ficha,
            "form": form,
        })


class ComandaAgendamentoView(BarbeiroRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        barbeiro = Barbeiro.objects.filter(usuario=self.request.user).first()
        agendamento = Agendamento.objects.filter(id=pk, barbeiro=barbeiro).first()
        if not agendamento:
            messages.error(request, "Agendamento não encontrado.")
            return redirect("agendamentos_barbeiro")

        action = request.POST.get("action", "adicionar")

        # Remover produto existente da comanda
        if action == "remover":
            venda_id = request.POST.get("venda_id")
            venda = VendaProduto.objects.filter(id=venda_id, agendamento=agendamento).first()
            if venda:
                nome_p = venda.produto.nome if venda.produto else "Produto"
                if venda.produto and venda.produto.estoque is not None:
                    venda.produto.estoque += venda.quantidade
                    venda.produto.save()
                venda.delete()
                messages.success(request, f"{nome_p} removido da comanda! 🗑️")
            else:
                messages.error(request, "Item da comanda não encontrado.")
            return redirect("agendamentos_barbeiro")

        # Adicionar novo produto à comanda
        produto_id = request.POST.get("produto_id")
        try:
            quantidade = int(request.POST.get("quantidade", 1))
        except (ValueError, TypeError):
            quantidade = 1

        if produto_id:
            produto = Produto.objects.filter(id=produto_id, ativo=True).first()
            if produto:
                quantidade = max(1, quantidade)
                valor_total = float(produto.preco) * quantidade
                VendaProduto.objects.create(
                    produto=produto,
                    cliente=agendamento.cliente,
                    barbeiro=barbeiro,
                    agendamento=agendamento,
                    quantidade=quantidade,
                    valor_total=valor_total
                )
                if produto.estoque and produto.estoque > 0:
                    produto.estoque = max(0, produto.estoque - quantidade)
                    produto.save()
                messages.success(request, f"{quantidade}x {produto.nome} lançado na comanda! 🛒")
            else:
                messages.error(request, "Produto selecionado é inválido.")
        return redirect("agendamentos_barbeiro")


class FilaEsperaCreateView(View):
    def get(self, request, *args, **kwargs):
        form = FilaEsperaForm()
        return render(request, "website/fila_espera.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = FilaEsperaForm(request.POST)
        if form.is_valid():
            cliente = None
            if request.user.is_authenticated:
                cliente = Cliente.objects.filter(usuario=request.user).first()
            if not cliente:
                messages.error(request, "Por favor, faça login ou cadastre-se para entrar na fila de espera.")
                return redirect("login")
            
            fila = form.save(commit=False)
            fila.cliente = cliente
            fila.save()
            messages.success(request, "Você está na Fila de Espera! Se uma vaga abrir nesta data, você será notificado com prioridade. 🔔")
            return redirect("area_cliente")
        return render(request, "website/fila_espera.html", {"form": form})


class PainelRecepcaoTVView(TemplateView):
    template_name = "website/salao/painel_tv.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()
        context["data_hoje"] = hoje
        context["barbeiros"] = Barbeiro.objects.filter(ativo=True)
        
        # Agendamentos de hoje
        agendamentos_hoje = Agendamento.objects.select_related("cliente", "servico", "barbeiro").filter(
            data=hoje
        ).exclude(status="cancelado").order_by("horario")
        
        context["em_atendimento"] = agendamentos_hoje.filter(em_atendimento=True)
        context["proximos"] = agendamentos_hoje.filter(status__in=["pendente", "confirmado"], em_atendimento=False)[:6]
        context["fotos_trabalho"] = FotoTrabalho.objects.filter(publicado=True)[:6]
        return context


class CheckinChegadaView(View):
    def post(self, request, pk, *args, **kwargs):
        agendamento = Agendamento.objects.filter(id=pk).first()
        if agendamento:
            agendamento.checkin_realizado = True
            agendamento.save()
            messages.success(request, f"Check-in realizado! Seja bem-vindo(a) à Delacruz Barber, {agendamento.cliente.nome}! 💈")
        if request.user.is_authenticated:
            return redirect("area_cliente")
        return redirect("painel_tv")


class ClubeAssinaturaView(TemplateView):
    template_name = "website/clube/planos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["planos"] = PlanoAssinatura.objects.filter(ativo=True).order_by("ordem", "preco_mensal")
        if self.request.user.is_authenticated:
            cliente = Cliente.objects.filter(usuario=self.request.user).first()
            if cliente:
                context["minha_assinatura"] = AssinaturaCliente.objects.filter(cliente=cliente, status="ativa").first()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Faça login para assinar um plano do Delacruz Club.")
            return redirect("login")
        plano_id = request.POST.get("plano_id")
        cliente = Cliente.objects.filter(usuario=request.user).first()
        if cliente and plano_id:
            plano = PlanoAssinatura.objects.filter(id=plano_id, ativo=True).first()
            if plano:
                # Cria ou ativa assinatura
                AssinaturaCliente.objects.update_or_create(
                    cliente=cliente,
                    defaults={
                        "plano": plano,
                        "status": "ativa",
                        "cortes_usados_mes": 0,
                    }
                )
                messages.success(request, f"Parabéns! Você agora é membro VIP do plano {plano.nome}! 👑 Aproveite seus cortes com agilidade.")
                return redirect("area_cliente")
        return redirect("clube_planos")