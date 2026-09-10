# PRD.md - Documento de Requisitos do Produto

## Objetivo
Desenvolver e manter um sistema de gestão para a barbearia "Delacruz Barber", automatizando agendamentos, cadastros e acompanhamento de serviços, garantindo eficiência na operação e melhoria na experiência do cliente.

## Escopo
O sistema contempla:
- Gestão completa de cadastros (Clientes, Barbeiros, Serviços).
- Movimentações de agendamentos com relacionamento entre tabelas.
- Consulta de horários disponíveis e histórico de serviços.
- Acesso restrito baseado em perfis (Admin, Barbeiro, Cliente).
- Validações de regra de negócio (ex: não permitir agendamentos conflitantes).

## Público-alvo
- **Clientes**: Usuários que desejam agendar cortes e serviços.
- **Barbeiros**: Profissionais da barbearia que gerenciam sua agenda e histórico.
- **Administradores**: Gestores que controlam o sistema, cadastram serviços e monitoram relatórios.

## Perfis e Níveis de Acesso
- **Administrador**: Acesso total ao sistema (CRUD completo, relatórios, gestão de mensagens).
- **Barbeiro**: Acesso à própria agenda, histórico de atendimentos e relatórios de desempenho.
- **Cliente**: Acesso para agendar serviços, visualizar histórico de atendimentos e gerenciar perfil.

## Cadastros
- **Clientes**: Dados de contato e identificação.
- **Barbeiros**: Perfil, especialidades e cargo.
- **Serviços**: Nome, descrição, preço e duração.
- **Agendamentos**: Registro da relação Cliente + Barbeiro + Serviço + Data/Hora.

## Movimentações
- **Agendamento de Serviço**: Criação de registro vinculando cliente, barbeiro, serviço e horário.
- **Feedback**: Avaliação do serviço prestado.
- **Mensagens de Contato**: Envio de dúvidas ou sugestões pelos usuários.

## Relatórios e Consultas
- Consulta de agendamentos por data e barbeiro.
- Listagem geral de clientes, serviços e barbeiros.
- (A implementar) Relatórios de produtividade dos barbeiros e total de atendimentos.

## Regras de Negócio
- **Validação de Colisão com Intervalo Semi-Aberto e Buffer de 5 minutos**: Um agendamento candidato só pode ser confirmado se não colidir com agendamentos existentes ou bloqueios. A fórmula estrita é: `cand_inicio < exist_fim and cand_fim > exist_inicio`, onde `fim = inicio + timedelta(minutes=duracao_servico + 5)`. O buffer de 5 minutos garante a higienização da bancada entre atendimentos.
- **Catálogo Oficial Delacruz Barber**:
  - **Serviços Ativos (4)**: Cabelo (R$ 30,00 - 30 min), Barba (R$ 20,00 - 20 min), Cavanhaque (R$ 15,00 - 15 min), Sobrancelha (R$ 5,00 - 10 min). Todos os serviços legados não oficiais são inativados (`ativo=False`).
  - **Produtos Ativos (3)**: Pomada Fox (R$ 20,00), Pomada em pó (R$ 30,00), Shampoo anticaspa (R$ 30,00) com estoque inicial zerado (0).
  - **Planos de Assinatura (3)**:
    1. *Plano normal*: R$ 80,00/mês, até 4 cortes/mês (Cabelo e Sobrancelha).
    2. *Plano com barba*: R$ 120,00/mês, até 4 cortes/mês (Cabelo, Sobrancelha e Barba).
    3. *Plano cortes infinitos*: R$ 100,00/mês, ilimitado (Cabelo e Sobrancelha).
- **Snapshot Histórico**: Cada agendamento gera snapshots de itens em `ItemAgendamento`, registrando o preço e duração contratados no momento do agendamento, garantindo rastreabilidade contábil mesmo que o catálogo mude posteriormente.
- **Idempotência de Seed**: O comando `python manage.py seed_delacruz_real` atualiza o banco Neon atomicamente sem duplicações, suportando modo de simulação `--dry-run`.
- Não é permitido agendar horários que já estejam ocupados por outro cliente.
- Agendamentos só podem ser feitos com profissionais e serviços ativos.
- O sistema deve diferenciar o tipo de usuário no login para direcionar à área correta (Cliente ou Barbeiro).

## Requisitos Funcionais
- RF01: O sistema deve permitir o cadastro de novos usuários.
- RF02: O sistema deve permitir que clientes realizem agendamentos.
- RF03: O sistema deve validar a disponibilidade de barbeiros em datas e horários específicos respeitando janela operacional de 08:00 às 21:30 e colisão com buffer de 5 min.
- RF04: O sistema deve disponibilizar painéis de controle diferentes por perfil de usuário.
- RF05: O sistema deve exibir uma tabela estruturada de horários organizada por períodos (Manhã 08:00-12:00, Tarde 12:30-17:30 e Noite 18:00-21:30) com horários separados individualmente em blocos interativos. Horários disponíveis devem ser exibidos de forma nítida e clicável (com destaque dourado ao selecionar), enquanto horários já ocupados ou bloqueados devem ser exibidos de forma fosca (dimmed/matte) e totalmente não clicáveis (pointer-events: none).
- RF06: O sistema deve permitir pagamento de sinal ou valor total via PIX com geração de QR Code e Copia-e-Cola (padrão EMV).
- RF07: O sistema deve disponibilizar Carteirinha de Fidelidade Digital com 10 selos para clientes, premiando cortes gratuitos.
- RF08: O sistema deve disponibilizar botão de contato rápido via WhatsApp com mensagens pré-formatadas para barbeiro e cliente.
- RF09: O sistema deve permitir que barbeiros bloqueiem datas inteiras ou horários específicos para pausas e folgas.
- RF10: O sistema deve permitir que barbeiros gerenciem uma Ficha Técnica com preferências e histórico de corte de cada cliente.
- RF11: O sistema deve disponibilizar Fila de Espera inteligente para datas com horários esgotados.
- RF12: O sistema deve gerenciar Clube de Assinatura mensal (Delacruz Club) com isenção automática no checkout para membros VIP e controle de limite (limitado até 4 cortes ou cortes infinitos).
- RF13: O sistema deve gerenciar Comanda de Consumo e venda de produtos (pomadas, cervejas, óleos) associada aos agendamentos.
- RF14: O sistema deve suportar Cupons de Desconto e programa de indicação "Indique um Amigo" com créditos.
- RF15: O sistema deve fornecer um Painel de Recepção para Smart TV com status das cadeiras em tempo real e QR Code de check-in.

## Requisitos Não Funcionais
- Uso de Bootstrap 5 para responsividade.
- Uso de jQuery para manipulação dinâmica da interface.
- Segurança através de autenticação Django.
- Persistência em banco de dados relacional PostgreSQL (Neon Serverless DB).
- Paleta visual customizada com destaque em Dourado/Âmbar (#fde047) para elementos secundários.

## Casos de Uso
- **CU01 - Realizar Agendamento**: Cliente seleciona barbeiro, serviço e horário disponível; sistema valida e salva.
- **CU02 - Gestão de Perfil**: Usuário altera senha ou informações de contato.
- **CU03 - Visualizar Agenda**: Barbeiro consulta seus agendamentos diários.

## Critérios de Aceitação
- O sistema deve impedir agendamentos em horários já reservados.
- A navegação deve ser intuitiva e adaptada a dispositivos móveis (Bootstrap).
- A autenticação deve garantir que usuários acessem apenas seus respectivos painéis (Área do Cliente vs. Área do Barbeiro).
- Todas as tabelas principais devem estar devidamente relacionadas para garantir a integridade dos dados.
