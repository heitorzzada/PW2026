from django.urls import path
from .views import (
    IndexView, ServicosPublicView, BarbeirosPublicView, SobreView,
    ContatoCreateView, AgendamentoPublicoView, CadastroUsuarioView,
    RedirecionarUsuarioView, CustomLoginView, CustomLogoutView, CustomPasswordChangeView,
    HorariosDisponiveisView,
    
    # Client Area Views
    AreaClienteView, HistoricoClienteView, FeedbackCreateView,
    PerfilClienteUpdateView, AgendamentoClienteCancelView,
    
    # Barber Area Views
    AreaBarbeiroView, AgendamentosBarbeiroView, HistoricoBarbeiroView,
    RelatoriosBarbeiroView, FotosBarbeiroListView, FotoTrabalhoCreateView,
    FotoTrabalhoUpdateView, FotoTrabalhoDeleteView,
    
    # Admin Dashboard
    DashboardView,
    
    # Admin CRUD - Servico
    ServicoCreateView, ServicoUpdateView, ServicoDeleteView, ServicoListView, ServicoDetailView,
    
    # Admin CRUD - Barbeiro
    BarbeiroCreateView, BarbeiroUpdateView, BarbeiroDeleteView, BarbeiroListView, BarbeiroDetailView,
    
    # Admin CRUD - Cliente
    ClienteCreateView, ClienteUpdateView, ClienteDeleteView, ClienteListView, ClienteDetailView,
    
    # Admin CRUD - HorarioDisponivel
    HorarioDisponivelCreateView, HorarioDisponivelUpdateView, HorarioDisponivelDeleteView, HorarioDisponivelListView, HorarioDisponivelDetailView,
    
    # Admin CRUD - Agendamento
    AgendamentoCreateView, AgendamentoUpdateView, AgendamentoDeleteView, AgendamentoListView, AgendamentoDetailView,
    
    # Admin CRUD - MensagemContato
    MensagemContatoListView, MensagemContatoDetailView, MensagemContatoDeleteView,
    
    # Admin CRUD - Feedback
    FeedbackListView, FeedbackDetailView, FeedbackDeleteView,
    
    # Admin CRUD - FotoTrabalho
    FotoTrabalhoListView, FotoTrabalhoDetailView,
    
    # Novas Funcionalidades
    PagamentoPixDetailView, BloqueiosBarbeiroView, BloqueioBarbeiroDeleteView,
    FichaClienteView, ComandaAgendamentoView, FilaEsperaCreateView,
    PainelRecepcaoTVView, CheckinChegadaView, ClubeAssinaturaView
)

urlpatterns = [
    # Public Pages
    path("", IndexView.as_view(), name="pagina_inicial"),
    path("servicos/", ServicosPublicView.as_view(), name="servicos"),
    path("barbeiros/", BarbeirosPublicView.as_view(), name="barbeiros"),
    path("sobre/", SobreView.as_view(), name="sobre"),
    path("contato/", ContatoCreateView.as_view(), name="contato"),
    path("agendamento/", AgendamentoPublicoView.as_view(), name="agendamento"),
    path("cadastro/", CadastroUsuarioView.as_view(), name="cadastro"),
    
    # Authentication Views
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("alterar-senha/", CustomPasswordChangeView.as_view(), name="alterar_senha"),
    path("redirecionar/", RedirecionarUsuarioView.as_view(), name="redirecionar_usuario"),
    
    # Available times helper
    path("horarios-disponiveis/", HorariosDisponiveisView.as_view(), name="horarios_disponiveis"),
    
    # Client Dashboard / Area
    path("cliente/area/", AreaClienteView.as_view(), name="area_cliente"),
    path("cliente/historico/", HistoricoClienteView.as_view(), name="historico_cliente"),
    path("cliente/feedback/<int:pk>/", FeedbackCreateView.as_view(), name="criar_feedback"),
    path("cliente/perfil/", PerfilClienteUpdateView.as_view(), name="perfil_cliente"),
    path("cliente/cancelar/<int:pk>/", AgendamentoClienteCancelView.as_view(), name="cancelar_agendamento_cliente"),
    
    # Barber Area Views
    path("barbeiro/area/", AreaBarbeiroView.as_view(), name="area_barbeiro"),
    path("barbeiro/agendamentos/", AgendamentosBarbeiroView.as_view(), name="agendamentos_barbeiro"),
    path("barbeiro/historico/", HistoricoBarbeiroView.as_view(), name="historico_barbeiro"),
    path("barbeiro/relatorios/", RelatoriosBarbeiroView.as_view(), name="relatorios_barbeiro"),
    path("barbeiro/bloqueios/", BloqueiosBarbeiroView.as_view(), name="bloqueios_barbeiro"),
    path("barbeiro/bloqueios/excluir/<int:pk>/", BloqueioBarbeiroDeleteView.as_view(), name="excluir_bloqueio_barbeiro"),
    path("barbeiro/ficha/<int:cliente_id>/", FichaClienteView.as_view(), name="ficha_cliente"),
    path("barbeiro/comanda/<int:pk>/", ComandaAgendamentoView.as_view(), name="adicionar_comanda"),
    path("barbeiro/fotos/", FotosBarbeiroListView.as_view(), name="fotos_barbeiro"),
    path("barbeiro/fotos/cadastrar/", FotoTrabalhoCreateView.as_view(), name="cadastrar_foto_barbeiro"),
    path("barbeiro/fotos/editar/<int:pk>/", FotoTrabalhoUpdateView.as_view(), name="editar_foto_barbeiro"),
    path("barbeiro/fotos/excluir/<int:pk>/", FotoTrabalhoDeleteView.as_view(), name="excluir_foto_barbeiro"),
    
    # Novas Funcionalidades Públicas e de Salão
    path("pix/<int:pk>/", PagamentoPixDetailView.as_view(), name="pix_pagamento"),
    path("fila-espera/", FilaEsperaCreateView.as_view(), name="fila_espera"),
    path("salao/painel/", PainelRecepcaoTVView.as_view(), name="painel_tv"),
    path("salao/checkin/<int:pk>/", CheckinChegadaView.as_view(), name="checkin_chegada"),
    path("clube/", ClubeAssinaturaView.as_view(), name="clube_planos"),
    
    # Admin Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    
    # Admin CRUD - Servico
    path("cadastrar/servico/", ServicoCreateView.as_view(), name="cadastrar_servico"),
    path("listar/servicos/", ServicoListView.as_view(), name="listar_servicos"),
    path("editar/servico/<int:pk>/", ServicoUpdateView.as_view(), name="editar_servico"),
    path("excluir/servico/<int:pk>/", ServicoDeleteView.as_view(), name="excluir_servico"),
    path("ver/servico/<int:pk>/", ServicoDetailView.as_view(), name="ver_servico"),
    
    # Admin CRUD - Barbeiro
    path("cadastrar/barbeiro/", BarbeiroCreateView.as_view(), name="cadastrar_barbeiro"),
    path("listar/barbeiros/", BarbeiroListView.as_view(), name="listar_barbeiros"),
    path("editar/barbeiro/<int:pk>/", BarbeiroUpdateView.as_view(), name="editar_barbeiro"),
    path("excluir/barbeiro/<int:pk>/", BarbeiroDeleteView.as_view(), name="excluir_barbeiro"),
    path("ver/barbeiro/<int:pk>/", BarbeiroDetailView.as_view(), name="ver_barbeiro"),
    
    # Admin CRUD - Cliente
    path("cadastrar/cliente/", ClienteCreateView.as_view(), name="cadastrar_cliente"),
    path("listar/clientes/", ClienteListView.as_view(), name="listar_clientes"),
    path("editar/cliente/<int:pk>/", ClienteUpdateView.as_view(), name="editar_cliente"),
    path("excluir/cliente/<int:pk>/", ClienteDeleteView.as_view(), name="excluir_cliente"),
    path("ver/cliente/<int:pk>/", ClienteDetailView.as_view(), name="ver_cliente"),
    
    # Admin CRUD - HorarioDisponivel
    path("cadastrar/horario/", HorarioDisponivelCreateView.as_view(), name="cadastrar_horario"),
    path("listar/horarios/", HorarioDisponivelListView.as_view(), name="listar_horarios"),
    path("editar/horario/<int:pk>/", HorarioDisponivelUpdateView.as_view(), name="editar_horario"),
    path("excluir/horario/<int:pk>/", HorarioDisponivelDeleteView.as_view(), name="excluir_horario"),
    path("ver/horario/<int:pk>/", HorarioDisponivelDetailView.as_view(), name="ver_horario"),
    
    # Admin CRUD - Agendamento
    path("cadastrar/agendamento/", AgendamentoCreateView.as_view(), name="cadastrar_agendamento"),
    path("listar/agendamentos/", AgendamentoListView.as_view(), name="listar_agendamentos"),
    path("editar/agendamento/<int:pk>/", AgendamentoUpdateView.as_view(), name="editar_agendamento"),
    path("excluir/agendamento/<int:pk>/", AgendamentoDeleteView.as_view(), name="excluir_agendamento"),
    path("ver/agendamento/<int:pk>/", AgendamentoDetailView.as_view(), name="ver_agendamento"),
    
    # Admin CRUD - MensagemContato
    path("listar/mensagens/", MensagemContatoListView.as_view(), name="listar_mensagens"),
    path("ver/mensagem/<int:pk>/", MensagemContatoDetailView.as_view(), name="ver_mensagem"),
    path("excluir/mensagem/<int:pk>/", MensagemContatoDeleteView.as_view(), name="excluir_mensagem"),
    
    # Admin CRUD - Feedback
    path("listar/feedbacks/", FeedbackListView.as_view(), name="listar_feedbacks"),
    path("ver/feedback/<int:pk>/", FeedbackDetailView.as_view(), name="ver_feedback"),
    path("excluir/feedback/<int:pk>/", FeedbackDeleteView.as_view(), name="excluir_feedback"),
    
    # Admin CRUD - FotoTrabalho
    path("listar/fotos/", FotoTrabalhoListView.as_view(), name="listar_fotos"),
    path("ver/foto/<int:pk>/", FotoTrabalhoDetailView.as_view(), name="ver_foto"),
]