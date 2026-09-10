from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class PerfilUsuario(models.Model):
    TIPO_CHOICES = [
        ("cliente", "Cliente"),
        ("barbeiro", "Barbeiro"),
        ("administrador", "Administrador"),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES, default="cliente")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to="perfis/", blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_usuario_display()}"


class Servico(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField()
    categoria = models.CharField(max_length=50, blank=True, null=True)
    icone = models.CharField(max_length=50, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome


class Barbeiro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    especialidade = models.CharField(max_length=200)
    descricao_curta = models.TextField()
    imagem_url = models.CharField(max_length=255, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    percentual_comissao = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    observacoes = models.TextField(blank=True, null=True)
    codigo_indicacao = models.CharField(max_length=20, unique=True, blank=True, null=True)
    saldo_creditos = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.codigo_indicacao:
            import uuid
            self.codigo_indicacao = f"DELA-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.telefone})"


class HorarioDisponivel(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="horarios_disponiveis")
    horario = models.TimeField()
    ativo = models.BooleanField(default=True)
    observacao = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("barbeiro", "horario")
        verbose_name = "Horário Disponível"
        verbose_name_plural = "Horários Disponíveis"

    def __str__(self):
        return f"{self.barbeiro.nome} - {self.horario.strftime('%H:%M')}"


class CupomDesconto(models.Model):
    TIPO_CHOICES = [
        ("porcentagem", "Porcentagem (%)"),
        ("fixo", "Valor Fixo (R$)"),
    ]
    codigo = models.CharField(max_length=30, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="porcentagem")
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    limite_uso = models.IntegerField(default=100)
    usado_vezes = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    validade = models.DateField()

    def calcular_desconto(self, valor_total):
        if self.tipo == "porcentagem":
            return round((float(valor_total) * float(self.valor)) / 100, 2)
        return min(float(self.valor), float(valor_total))

    def is_valido(self):
        from datetime import date
        if not self.ativo:
            return False
        if self.validade and self.validade < date.today():
            return False
        if self.limite_uso and self.usado_vezes >= self.limite_uso:
            return False
        return True

    def __str__(self):
        return f"{self.codigo} ({self.valor})"


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("concluido", "Concluído"),
        ("cancelado", "Cancelado"),
    ]
    PAGAMENTO_METODO_CHOICES = [
        ("pix", "PIX"),
        ("cartao", "Cartão"),
        ("dinheiro", "Dinheiro"),
        ("local", "Pagar no Salão"),
        ("pix_sinal", "Pix (Sinal)"),
        ("pix_total", "Pix (Valor Total)"),
    ]
    PAGAMENTO_STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
        ("reembolsado", "Reembolsado"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="agendamentos")
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT, related_name="agendamentos", null=True, blank=True)
    servicos = models.ManyToManyField(Servico, blank=True, related_name="agendamentos_multiplos")
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.PROTECT, related_name="agendamentos", null=True, blank=True)
    data = models.DateField()
    horario = models.TimeField()
    horario_fim = models.TimeField(blank=True, null=True)
    duracao_total_minutos = models.IntegerField(default=30)
    qualquer_barbeiro = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    desconto_aplicado = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    cupom = models.ForeignKey(CupomDesconto, on_delete=models.SET_NULL, null=True, blank=True, related_name="agendamentos")
    metodo_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_METODO_CHOICES, default="local")
    status_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_STATUS_CHOICES, default="pendente")
    checkin_realizado = models.BooleanField(default=False)
    em_atendimento = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["barbeiro", "data", "horario"],
                condition=~models.Q(status="cancelado"),
                name="unique_agendamento_ativo_por_horario"
            )
        ]

    @property
    def total_produtos_venda(self):
        return sum(float(v.valor_total) for v in self.vendas_produtos.all()) if hasattr(self, "vendas_produtos") else 0.0

    @property
    def valor_final(self):
        base = float(self.valor_total) if self.valor_total else (float(self.servico.preco) if self.servico else 0.0)
        total = base + self.total_produtos_venda - float(self.desconto_aplicado)
        return max(round(total, 2), 0.0)

    def __str__(self):
        nome_serv = self.servico.nome if self.servico else "Serviços múltiplos"
        nome_barb = self.barbeiro.nome if self.barbeiro else "Qualquer barbeiro"
        return f"{self.cliente.nome} - {nome_serv} com {nome_barb} em {self.data} às {self.horario}"


class MensagemContato(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    enviada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.nome} - {self.email}"


class Feedback(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="feedbacks")
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="feedbacks")
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name="feedbacks")
    nota = models.IntegerField()
    comentario = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    aprovado = models.BooleanField(default=True)

    def __str__(self):
        return f"Nota {self.nota} para {self.barbeiro.nome} por {self.cliente.nome}"


class FotoTrabalho(models.Model):
    CATEGORIA_CHOICES = [
        ("corte", "Corte"),
        ("barba", "Barba"),
        ("corte_barba", "Corte + Barba"),
        ("infantil", "Infantil"),
        ("outro", "Outro"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="fotos_trabalho")
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to="trabalhos/")
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default="corte")
    publicado = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo


class CartaoFidelidade(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name="fidelidade")
    pontos_acumulados = models.IntegerField(default=0)
    cortes_gratuitos_disponiveis = models.IntegerField(default=0)
    atualizado_em = models.DateTimeField(auto_now=True)

    def registrar_corte_concluido(self, agendamento=None):
        self.pontos_acumulados += 1
        pontos_ganhos = 1
        if self.pontos_acumulados >= 10:
            cortes_novos = self.pontos_acumulados // 10
            self.cortes_gratuitos_disponiveis += cortes_novos
            self.pontos_acumulados = self.pontos_acumulados % 10
        self.save()
        
        MovimentacaoFidelidade.objects.create(
            cartao=self,
            agendamento=agendamento,
            pontos=pontos_ganhos,
            tipo="credito",
            descricao="Corte concluído"
        )

    def __str__(self):
        return f"Fidelidade: {self.cliente.nome} ({self.pontos_acumulados}/10 selos)"


class MovimentacaoFidelidade(models.Model):
    TIPO_CHOICES = [
        ("credito", "Crédito"),
        ("resgate", "Resgate"),
    ]
    cartao = models.ForeignKey(CartaoFidelidade, on_delete=models.CASCADE, related_name="movimentacoes")
    agendamento = models.ForeignKey(Agendamento, on_delete=models.SET_NULL, blank=True, null=True, related_name="movimentacoes_fidelidade")
    pontos = models.IntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo.upper()}: {self.pontos} pts ({self.descricao})"


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    estoque = models.IntegerField(default=10)
    imagem = models.CharField(max_length=100, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"


class VendaProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="vendas")
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, blank=True, null=True, related_name="compras_produtos")
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.SET_NULL, blank=True, null=True, related_name="vendas_produtos")
    agendamento = models.ForeignKey(Agendamento, on_delete=models.SET_NULL, blank=True, null=True, related_name="vendas_produtos")
    quantidade = models.IntegerField(default=1)
    valor_total = models.DecimalField(max_digits=8, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (R$ {self.valor_total})"


class ComissaoBarbeiro(models.Model):
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="comissoes")
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name="comissao")
    valor_total_servico = models.DecimalField(max_digits=8, decimal_places=2)
    percentual_comissao = models.DecimalField(max_digits=5, decimal_places=2)
    valor_comissao = models.DecimalField(max_digits=8, decimal_places=2)
    pago = models.BooleanField(default=False)
    gerado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comissão {self.barbeiro.nome}: R$ {self.valor_comissao} ({'Pago' if self.pago else 'Pendente'})"


class PagamentoPix(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("pago", "Pago"),
        ("expirado", "Expirado"),
        ("cancelado", "Cancelado"),
    ]
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name="pagamento_pix")
    transacao_id = models.CharField(max_length=255, unique=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    qr_code_base64 = models.TextField(blank=True, null=True)
    qr_code_payload = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    criado_em = models.DateTimeField(auto_now_add=True)
    pago_em = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Pix #{self.transacao_id} - R$ {self.valor} ({self.status})"


class NotificacaoLog(models.Model):
    TIPO_CHOICES = [
        ("confirmacao", "Confirmação"),
        ("lembrete", "Lembrete"),
        ("agradecimento", "Agradecimento"),
        ("fila_espera", "Fila de Espera"),
    ]
    CANAL_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "E-mail"),
    ]
    STATUS_CHOICES = [
        ("enviado", "Enviado"),
        ("falha", "Falha"),
        ("pendente", "Pendente"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="notificacoes")
    agendamento = models.ForeignKey(Agendamento, on_delete=models.SET_NULL, blank=True, null=True, related_name="notificacoes")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default="whatsapp")
    destinatario = models.CharField(max_length=30)
    mensagem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    erro = models.TextField(blank=True, null=True)
    enviado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.canal.upper()} para {self.destinatario}: {self.status}"


class BloqueioHorarioBarbeiro(models.Model):
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="bloqueios")
    data = models.DateField()
    horario = models.TimeField(blank=True, null=True)
    dia_inteiro = models.BooleanField(default=False)
    motivo = models.CharField(max_length=150, default="Indisponível / Folga")
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.dia_inteiro:
            return f"Bloqueio Dia Inteiro: {self.barbeiro.nome} em {self.data} ({self.motivo})"
        return f"Bloqueio: {self.barbeiro.nome} em {self.data} às {self.horario} ({self.motivo})"


class FichaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="fichas_tecnicas")
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name="fichas_preenchidas")
    estilo_corte = models.CharField(max_length=200, blank=True, null=True)
    produtos_preferidos = models.CharField(max_length=200, blank=True, null=True)
    observacoes_tecnicas = models.TextField(blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cliente", "barbeiro")

    def __str__(self):
        return f"Ficha de {self.cliente.nome} com {self.barbeiro.nome}"


class FilaEspera(models.Model):
    TURNO_CHOICES = [
        ("qualquer", "Qualquer Horário"),
        ("manha", "Manhã (08h às 12h)"),
        ("tarde", "Tarde (12h às 18h)"),
        ("noite", "Noite (18h às 21h)"),
    ]
    STATUS_CHOICES = [
        ("aguardando", "Aguardando"),
        ("notificado", "Notificado"),
        ("atendido", "Atendido"),
        ("cancelado", "Cancelado"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="inscricoes_fila")
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.SET_NULL, null=True, blank=True, related_name="fila_espera")
    data_desejada = models.DateField()
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES, default="qualquer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="aguardando")
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fila de espera: {self.cliente.nome} para {self.data_desejada}"


class PlanoAssinatura(models.Model):
    MODALIDADE_CHOICES = [
        ("limitado", "Limitado"),
        ("ilimitado", "Ilimitado"),
    ]
    codigo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco_mensal = models.DecimalField(max_digits=6, decimal_places=2)
    modalidade = models.CharField(max_length=20, choices=MODALIDADE_CHOICES, default="limitado")
    limite_mensal = models.PositiveIntegerField(null=True, blank=True, default=4)
    cortes_por_mes = models.PositiveIntegerField(default=4)
    servicos_inclusos = models.ManyToManyField("Servico", blank=True, related_name="planos_inclusos")
    inclui_barba = models.BooleanField(default=False)
    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)

    def __str__(self):
        mod_text = "Ilimitado" if self.modalidade == "ilimitado" else f"{self.limite_mensal or self.cortes_por_mes}x/mês"
        return f"{self.nome} - R$ {self.preco_mensal}/mês ({mod_text})"


class AssinaturaCliente(models.Model):
    STATUS_CHOICES = [
        ("ativa", "Ativa"),
        ("suspensa", "Suspensa"),
        ("cancelada", "Cancelada"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="assinaturas")
    plano = models.ForeignKey(PlanoAssinatura, on_delete=models.PROTECT, related_name="assinantes")
    data_inicio = models.DateField(auto_now_add=True)
    data_fim = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ativa")
    cortes_usados_mes = models.PositiveIntegerField(default=0)

    def tem_cortes_disponiveis(self):
        if self.status != "ativa":
            return False
        if self.plano.modalidade == "ilimitado":
            return True
        limite = self.plano.limite_mensal if self.plano.limite_mensal is not None else self.plano.cortes_por_mes
        return self.cortes_usados_mes < limite

    def __str__(self):
        return f"{self.cliente.nome} - {self.plano.nome} ({self.status})"


class ItemAgendamento(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name="itens")
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField(default=30)
    cadastrado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.servico.nome} em Agendamento #{self.agendamento_id}"