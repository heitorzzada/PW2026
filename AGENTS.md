# AGENTS.md - BarberProject

## Título
Sistema de Gestão para Barbearia - Delacruz Barber

## Objetivo Geral
O objetivo deste sistema é automatizar a gestão de uma barbearia, facilitando o agendamento de serviços, controle de horários de barbeiros e interação com clientes.

## Objetivos Específicos
- Gerenciar cadastros de clientes, barbeiros e serviços.
- Permitir a realização de agendamentos com validações de disponibilidade.
- Oferecer áreas distintas para clientes e barbeiros.
- Gerenciar contatos e feedbacks dos usuários.

## Tecnologias Utilizadas
- **Backend**: Python 3.11+ / Django 5.2
- **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript (Vanilla/jQuery)
- **Banco de Dados**: Relacional PostgreSQL (Neon DB em produção/desenvolvimento via `DATABASE_URL`)

- **Deployment**: Google App Engine (app.yaml)
- **Controle de Versão**: Git/GitHub

## Estrutura de Diretórios
- `BarberProject/`: Configurações globais do Django (settings, wsgi, asgi, urls).
- `website/`: Aplicação principal contendo models, views, forms, migrations e templates.
- `erros/`: Aplicação para tratamento e renderização de erros HTTP customizados (400, 403, 404, 500) com DEBUG=False.
- `static/`: Arquivos estáticos globais (css, imagens).
- `website/static/website/`: Arquivos estáticos da aplicação (js, css, imagens).
- `website/templates/`: Estrutura de visualização (HTMLs).
- `erros/templates/erros/`: Templates de páginas de erro com estética glassmorphism dark.

## Convenções de Código
- Código escrito em Python respeitando o padrão PEP 8.
- Utilização de templates Django com extensão `.html`.
- Uso de `crispy-forms` para renderização de formulários com Bootstrap 5.

## Padrões de Nomenclatura
- **Models**: CamelCase.
- **Views**: PascalCase para classes ou snake_case para funções.
- **URLs**: snake_case.
- **Campos de Banco**: snake_case.

## Organização de Arquivos
- **Models**: Localizados em `website/models.py`.
- **Views**: Localizadas em `website/views.py`.
- **Forms**: Localizados em `website/forms.py`.
- **Pix Utility**: Localizado em `website/pix.py`.
- **Commands**: Localizados em `website/management/commands/` (ex: `seed_delacruz_real.py`).
- **URLs**: Divididas entre `BarberProject/urls.py` (root) e `website/urls.py` (app).
- **Templates**: Organizados em `website/templates/website/` (agrupados por funcionalidade: `cliente/`, `barbeiro/`, `salao/`, `clube/`, `registration/`, `listas/`, `ver/`).

## Migrations
- Para criar migrations após alteração de models: `python manage.py makemigrations`
- Para aplicar migrations: `python manage.py migrate`

## Como Executar o Projeto
1. Instale as dependências: `pip install -r requirements.txt`
2. Aplique as migrações: `python manage.py migrate`
3. Sincronize o catálogo oficial: `python manage.py seed_delacruz_real`
4. Execute o servidor: `python manage.py runserver`

## Como Executar Testes
- Execute os testes padrão do Django: `python manage.py test` (ou `python manage.py test website --keepdb`)

## Convenções para Commits Git
- Utilize mensagens claras e concisas seguindo o formato: `tipo: descrição breve da alteração`
- Exemplos: `feat: add relatorio de barbeiro`, `fix: correcao no cadastro de agendamento`, `docs: atualização do PRD`.
- Consulte a skill `.agents/skills/git-commit/SKILL.md` para a especificação completa.

## Skills para Agentes de IA
O projeto conta com skills dedicadas localizadas em `.agents/skills/`:
1. **`git-commit`**: Padronização rigorosa das mensagens de commit Git conforme o padrão do IFPR/Conventional Commits.
2. **`seed-catalog`**: Guia para criação/aplicação de migrações e semeadura do catálogo e perfis do Delacruz Barber.
3. **`security-audit`**: Diretrizes de segurança, proteção via `LoginRequiredMixin`/`GroupRequiredMixin`, isolamento de registros por usuário via `get_queryset()` e framework de mensagens.

## Gestão de Custos e Manutenção no Google Cloud (GCP)
### 1. Política de Limpeza Automática do Artifact Registry
O projeto mantém na raiz o arquivo `cleanup-policy.json` para evitar cobranças por acúmulo de imagens Docker antigas geradas nos deploys do App Engine.
Para reaplicar a política no repositório oficial:
```bash
gcloud artifacts repositories set-cleanup-policies gae-standard --location=southamerica-east1 --policy=cleanup-policy.json --no-dry-run
```
- **Regras configuradas**:
  - Manter imagem com tag `latest` (`action: Keep`).
  - Manter as 2 versões mais recentes (`mostRecentVersions.keepCount: 2`).
  - Excluir versões com mais de 1 dia / 86400s (`action: Delete`, `olderThan: 86400s`).

### 2. Auditoria e Limpeza de Versões Antigas do App Engine
Para manter o ambiente limpo e evitar instâncias ou versões legadas consumindo recursos:
1. Listar versões existentes:
   ```bash
   gcloud app versions list
   ```
2. Identificar versões com `TRAFFIC_SPLIT` igual a `0.00` (versões inativas).
3. Excluir versões inativas com segurança (**NUNCA** excluir a versão com `TRAFFIC_SPLIT` igual a `1.00`):
   ```bash
   gcloud app versions delete <VERSAO_ID_1> <VERSAO_ID_2> --quiet
   ```
4. Confirmar que apenas a versão ativa permaneceu:
   ```bash
   gcloud app versions list
   ```

## Como Documentar Alterações
- Toda nova funcionalidade deve ser documentada no `PRD.md`.
- Alterações estruturais devem ser refletidas nos arquivos de documentação (`AGENTS.md` e `PRD.md`).

## Regras para Agentes
- **NÃO** alterar, criar ou excluir arquivos sem solicitação explícita e autorização.
- **NÃO** quebrar funcionalidades existentes ao implementar melhorias.
- **SEMPRE** verificar dependências (ex: Bootstrap, jQuery) antes de editar templates.
- **SEMPRE** utilizar `@login_required` para proteger views de acesso não autorizado.

## Referência ao PRD.md
Para mais detalhes sobre os requisitos funcionais, regras de negócio e critérios de aceitação, consulte o arquivo `PRD.md` na raiz deste repositório.

