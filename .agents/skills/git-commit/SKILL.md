---
name: git-commit
description: Padroniza as mensagens de commit do Git seguindo o formato de Conventional Commits e as regras do projeto BarberProject Delacruz.
---

# Skill: Git Commit Message Standardization

Esta skill orienta os agentes de IA e desenvolvedores a padronizarem as mensagens de commit no projeto **Delacruz Barber**, conforme exigido no plano de atividades da disciplina.

## Formato Obrigatório

```
tipo: descrição breve e concisa da alteração no tempo presente
```

## Tipos Permitidos

- `feat`: Adição de uma nova funcionalidade ao sistema (ex: tela de agendamento, formulário de filtro, integração Pix).
- `fix`: Correção de um bug ou inconsistência em view, form, model ou template.
- `docs`: Alterações ou adições na documentação (ex: `AGENTS.md`, `PRD.md`, `README.md`).
- `style`: Alterações puramente visuais, formatação CSS, espaçamento, sem alterar lógica de negócio.
- `refactor`: Refatoração de código que não adiciona recurso nem corrige bug (ex: simplificar queries, otimizar com `select_related`).
- `test`: Criação ou atualização de testes automatizados (`tests.py`).
- `chore`: Tarefas de manutenção, atualização de dependências em `requirements.txt`, arquivos de configuração ou scripts de seed.

## Regras de Ouro

1. Use letras minúsculas no tipo.
2. Seja direto e objetivo (máximo 72 caracteres no título).
3. Não termine a mensagem com ponto final.
4. Redija em português claro.
5. Faça commits atômicos (uma alteração lógica por commit).

## Exemplos Válidos

- `feat: add filtro com django-filter e paginacao na listagem de agendamentos`
- `feat: implementar recuperacao de senha e usuario por email`
- `fix: correcao no calculo de comissao do barbeiro`
- `docs: atualizar AGENTS.md com catalogo de skills`
- `style: aprimorar contraste dos botoes na tela de login`
- `test: adicionar casos de teste para conflito de horarios`
