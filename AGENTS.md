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
- **Backend**: Python 3.11+ / Django 4.x
- **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript (Vanilla/jQuery)
- **Banco de Dados**: Relacional (configurado para PostgreSQL/Desenvolvimento local)
- **Deployment**: Google App Engine (app.yaml)
- **Controle de Versão**: Git/GitHub

## Estrutura de Diretórios
- `BarberProject/`: Configurações globais do Django (settings, wsgi, asgi, urls).
- `website/`: Aplicação principal contendo models, views, forms, migrations e templates.
- `static/`: Arquivos estáticos globais (css, imagens).
- `website/static/website/`: Arquivos estáticos da aplicação (js, css, imagens).
- `website/templates/`: Estrutura de visualização (HTMLs).

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
- **URLs**: Divididas entre `BarberProject/urls.py` (root) e `website/urls.py` (app).
- **Templates**: Organizados em `website/templates/website/` (agrupados por funcionalidade: `cliente/`, `barbeiro/`, `registration/`, `listas/`, `ver/`).

## Migrations
- Para criar migrations após alteração de models: `python manage.py makemigrations`
- Para aplicar migrations: `python manage.py migrate`

## Como Executar o Projeto
1. Instale as dependências: `pip install -r requirements.txt`
2. Aplique as migrações: `python manage.py migrate`
3. Execute o servidor: `python manage.py runserver`

## Como Executar Testes
- Execute os testes padrão do Django: `python manage.py test`

## Convenções para Commits Git
- Utilize mensagens claras e concisas seguindo o formato: `tipo: descrição breve da alteração`
- Exemplos: `feat: add relatorio de barbeiro`, `fix: correcao no cadastro de agendamento`, `docs: atualização do PRD`.

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
