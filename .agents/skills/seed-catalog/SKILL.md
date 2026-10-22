---
name: seed-catalog
description: Procedimento padronizado para sincronizar migrations, banco de dados e semear o catálogo oficial da Delacruz Barber.
---

# Skill: Sincronização e Povoamento do Banco de Dados (Seed)

Esta skill define o fluxo correto para migração e carga de dados de teste e produção no sistema **Delacruz Barber**.

## Pré-requisitos

1. Variáveis de ambiente configuradas no arquivo `.env` (ex: `DATABASE_URL` para o banco Neon PostgreSQL).
2. Ambiente virtual ativado com as dependências do `requirements.txt` instaladas.

## Passo a Passo de Execução

### 1. Verificar Status das Migrations
```bash
python manage.py showmigrations
```

### 2. Criar e Aplicar Migrações
Caso tenham ocorrido mudanças nos modelos em `website/models.py`:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Sincronizar o Catálogo Oficial
Execute o comando de seed oficial que popula os grupos ("Administradores", "Barbeiros", "Clientes"), usuários padrão, serviços e horários:
```bash
python manage.py seed_delacruz_real
```

### 4. Credenciais Padrão Criadas pelo Seed
- **Administrador**: `admin` / `admin` (superusuário com acesso ao Dashboard geral)
- **Barbeiro Chefe**: `danilo` / `123456`
- **Barbeiro**: `heitor` / `123456`
- **Clientes**: cadastrados via formulário de auto-cadastro na rota `/cadastro/`.

## Cuidados Críticos
- Nunca execute `flush` em banco de produção Neon.
- Sempre verifique se os grupos de permissão (`GroupRequiredMixin`) foram devidamente atribuídos aos usuários após o seed.
