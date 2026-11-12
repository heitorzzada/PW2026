# Delacruz Barber - BarberProject

Sistema completo de agendamento online e gerenciamento para a barbearia **Delacruz Barber**, desenvolvido com Python, Django, PostgreSQL (Neon DB) e Bootstrap 5, atendendo integralmente aos requisitos dos 1º, 2º e 3º trimestres da disciplina de Programação Web (IFPR).

## Funcionalidades Principais

- **Público**:
  - Página inicial com serviços em destaque, galeria interativa de cortes, **Delacruz Reels**, **Delacruz Academy** e localização em Paranavaí - PR.
  - Página institucional **Sobre** (`/sobre/`) com descrição do projeto e diagramas UML de Casos de Uso e Classes.
  - Contato público armazenado em banco de dados e **Clube VIP** (`/clube/`) com planos de assinatura mensal.
  - Fluxo de agendamento online (`/agendamento/`) com grade horária dinâmica, validação de conflito com buffer de 5 minutos, cupons/indicação e pagamento via PIX (EMV/QR Code).
  - Cadastro público de clientes (`/cadastro/`) e autenticação completa com recuperação de **senha** e **nome de usuário** por e-mail na tela de login.

- **Área do Cliente**:
  - Acesso restrito via `ClienteRequiredMixin` / grupo `Clientes`.
  - Carteirinha de Fidelidade Digital (10 selos), Clube VIP, código de indicação e acompanhamento de agendamentos.
  - Histórico completo paginado, envio de avaliações (feedbacks) e cancelamento com confirmação modal.

- **Área do Barbeiro**:
  - Acesso restrito via `BarbeiroRequiredMixin` / `GroupRequiredMixin` (`Barbeiros`).
  - Gestão da agenda, check-in, atendimento na cadeira, comanda de consumo de produtos, ficha técnica de clientes, bloqueios/folgas e galeria de fotos com lightbox.
  - Relatórios operacionais e financeiros.

- **Painel Administrativo (Dashboard & CRUDs)**:
  - Acesso restrito via `AdminRequiredMixin` / `GroupRequiredMixin` (`Administradores`).
  - Isolamento de registros por usuário (`usuario` FK via `form_valid()` e `get_queryset()`).
  - Framework de mensagens do Django em operações de Create, Update e Delete.
  - Filtros avançados com **Django Filter** (`AgendamentoFilter`, `ServicoFilter`, `ClienteFilter`) integrados à paginação via template tag customizada `{% param_replace %}`.
  - Páginas de erro HTTP customizadas (`400`, `403`, `404`, `500`) ativas com `DEBUG=False`.

## Plugins jQuery Integrados

1. **jQuery Mask Plugin**: máscaras de telefone/WhatsApp e CPF nos formulários.
2. **jQuery DataTables**: ordenação e filtro rápido nas tabelas do sistema.
3. **Bootbox.js**: modais de confirmação para ações de exclusão, cancelamento e remoção.
4. **Magnific Popup**: galeria lightbox para ampliação de diagramas e fotos de trabalho.

## Tecnologias Utilizadas

- **Backend**: Python 3.12, Django 5.2, Django Filter, Django Crispy Forms (`crispy-bootstrap5`), Django Debug Toolbar
- **Frontend**: Bootstrap 5, Bootstrap Icons, jQuery 3.7, jQuery Mask, DataTables, Bootbox.js, Magnific Popup
- **Banco de Dados**: PostgreSQL (Neon Serverless DB via `DATABASE_URL`)
- **Deploy**: Google App Engine (`app.yaml` + Gunicorn)

## Instruções de Instalação e Execução Local

1. **Clonar o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd PW2026
   ```

2. **Criar e ativar o ambiente virtual**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente**:
   Configure `DATABASE_URL` no arquivo `.env` (consulte `.env.example`).

5. **Aplicar migrações e sincronizar o catálogo oficial**:
   ```bash
   python manage.py migrate
   python manage.py seed_delacruz_real
   ```

6. **Executar os testes automatizados**:
   ```bash
   python manage.py test website --keepdb
   ```

7. **Iniciar o servidor de desenvolvimento**:
   ```bash
   python manage.py runserver
   ```

## Deploy no Google App Engine (GAE)

1. Autentique-se na Google Cloud CLI:
   ```bash
   gcloud auth login
   gcloud config set project pw2k26
   ```
2. Gere os arquivos estáticos em `staticfiles/`:
   ```bash
   python manage.py collectstatic --noinput
   ```
3. Realize o deploy:
   ```bash
   gcloud app deploy
   ```
