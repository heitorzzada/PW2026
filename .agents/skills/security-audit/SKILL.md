---
name: security-audit
description: Checklist e auditoria de segurança para controle de acesso, escopo de usuário e integridade de views Django no projeto.
---

# Skill: Auditoria de Segurança e Boas Práticas Django

Esta skill deve ser consultada por qualquer agente de IA ou desenvolvedor antes de finalizar ou submeter alterações no projeto **Delacruz Barber**.

## Checklist de Verificação Obrigatória

### 1. Proteção de Acesso às Views
- Toda view que exija autenticação deve herdar de `LoginRequiredMixin` ou utilizar `@login_required`.
- Views com restrição por papel de usuário devem utilizar `GroupRequiredMixin` com `group_required = "NomeDoGrupo"` (ex: `Administradores`, `Barbeiros`, `Clientes`).
- Views administrativas devem utilizar `AdminRequiredMixin`.

### 2. Escopo de Registros por Usuário (Requisito Acadêmico)
Para modelos que possuem relação de chave estrangeira com `User` (`usuario = models.ForeignKey(User, ...)`):
- **Inserir**: Atribuir o usuário logado via `form_valid()`:
  ```python
  def form_valid(self, form):
      form.instance.usuario = self.request.user
      return super().form_valid(form)
  ```
- **Listar / Editar / Excluir / Detalhar**: Restringir a consulta ao usuário atual via `get_queryset()`:
  ```python
  def get_queryset(self):
      return MeuModelo.objects.filter(usuario=self.request.user)
  ```

### 3. Framework de Mensagens do Django
- Operações de `CreateView`, `UpdateView` e `DeleteView` devem emitir notificações claras via `messages.success()`.
- O template base (`website/modelo.html`) deve renderizar o bloco de mensagens do Django com dismissible alerts.

### 4. Otimização de Consultas SQL
- Evite N+1 queries utilizando `select_related()` para chaves estrangeiras e `prefetch_related()` para relações Many-to-Many.
- Monitore consultas repetidas através do Django Debug Toolbar em ambiente de desenvolvimento.

### 5. Paginação e Filtros
- ListViews com paginação devem preservar os parâmetros GET utilizando a tag customizada `{% param_replace %}` da biblioteca `paginacao_tags`.
