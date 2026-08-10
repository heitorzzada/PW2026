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
- Não é permitido agendar horários que já estejam ocupados por outro cliente (UniqueConstraint em `Agendamento`).
- Agendamentos só podem ser feitos com profissionais e serviços ativos.
- O sistema deve diferenciar o tipo de usuário no login para direcionar à área correta (Cliente ou Barbeiro).

## Requisitos Funcionais
- RF01: O sistema deve permitir o cadastro de novos usuários.
- RF02: O sistema deve permitir que clientes realizem agendamentos.
- RF03: O sistema deve validar a disponibilidade de barbeiros em datas e horários específicos.
- RF04: O sistema deve disponibilizar painéis de controle diferentes por perfil de usuário.

## Requisitos Não Funcionais
- Uso de Bootstrap 5 para responsividade.
- Uso de jQuery para manipulação dinâmica da interface.
- Segurança através de autenticação Django.
- Persistência em banco de dados relacional.

## Casos de Uso
- **CU01 - Realizar Agendamento**: Cliente seleciona barbeiro, serviço e horário disponível; sistema valida e salva.
- **CU02 - Gestão de Perfil**: Usuário altera senha ou informações de contato.
- **CU03 - Visualizar Agenda**: Barbeiro consulta seus agendamentos diários.

## Critérios de Aceitação
- O sistema deve impedir agendamentos em horários já reservados.
- A navegação deve ser intuitiva e adaptada a dispositivos móveis (Bootstrap).
- A autenticação deve garantir que usuários acessem apenas seus respectivos painéis (Área do Cliente vs. Área do Barbeiro).
- Todas as tabelas principais devem estar devidamente relacionadas para garantir a integridade dos dados.
