<<<<<<< HEAD
# Delacruz Barber - BarberProject

Sistema completo de agendamento online e gerenciamento interno para a **Delacruz Barber**. Desenvolvido com Python, Django e Bootstrap 5 para atender aos requisitos acadêmicos do 1º e 2º trimestres.

## Funcionalidades Principais

- **Público**:
  - Visualização da página inicial com serviços em destaque e galeria de fotos reais dos cortes.
  - Página institucional "Sobre" com descrição e diagramas de caso de uso e classes do sistema.
  - Contato público armazenado em banco de dados para a administração.
  - Fluxo de agendamento interativo com grade horária dinâmica (filtrada por barbeiro e data) e atualização do resumo.
  - Cadastro público restrito a clientes.

- **Área do Cliente**:
  - Acesso restrito a clientes autenticados.
  - Visualização de dados do perfil de cliente.
  - Histórico completo de atendimentos anteriores e status.
  - Envio de feedback (avaliações de 1 a 5 estrelas e comentários) para serviços concluídos.
  - Cancelamento de agendamentos pendentes.

- **Área do Barbeiro**:
  - Painel exclusivo do barbeiro logado.
  - Acompanhamento da agenda pessoal com opção de Confirmar, Recusar ou Concluir agendamentos.
  - Relatórios operacionais e financeiros (faturamento diário, mensal, média de avaliações e serviços mais realizados).
  - Gestão e upload de fotos de trabalhos (cortes e barbas) exibidas na página inicial.

- **Painel Administrativo (Dashboard)**:
  - Visão operacional consolidada (métricas de faturamento, quantidade de atendimentos e pendências).
  - CRUDs completos reutilizando `form.html` com Crispy Forms e Bootstrap 5.
  - Acesso seguro limitado a administradores e equipe (`is_staff`).

## Tecnologias Utilizadas

- **Backend**: Python 3.12, Django 6.0.6
- **Frontend**: Bootstrap 5, Bootstrap Icons, Vanilla Javascript
- **Formulários**: Django Crispy Forms, crispy-bootstrap5
- **Manipulação de Imagens**: Pillow
- **Banco de Dados**: SQLite

## Instruções de Instalação e Execução

1. **Clonar e acessar o repositório**:
   ```bash
   cd pw2k26
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

4. **Gerar e aplicar as migrações**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Popular o banco de dados (Seeding)**:
   ```bash
   python manage.py seed
   ```

6. **Iniciar o servidor de desenvolvimento**:
   ```bash
   python manage.py runserver
   ```
=======
# pw2026
sim.
>>>>>>> 98d4a58a6fde5f5e82afdb31fd156a36dc2040b9
