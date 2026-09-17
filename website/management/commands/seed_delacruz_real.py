from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User, Group
from decimal import Decimal
from datetime import time
from website.models import (
    Servico, Produto, PlanoAssinatura, Barbeiro, HorarioDisponivel, PerfilUsuario, FotoTrabalho
)


class Command(BaseCommand):
    help = "Configuração real do catálogo da Delacruz Barber (Serviços, Produtos, Planos, Horários e Grupos de Permissão)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Executa a simulação sem persistir alterações no banco de dados.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("--- MODO DRY-RUN ATIVADO (Nenhuma alteração será salva) ---"))

        with transaction.atomic():
            admin_user = User.objects.filter(is_superuser=True).first()

            # 0. GRUPOS DE USUÁRIOS (Requisito GroupRequiredMixin)
            self.stdout.write("\n[0/5] Configurando Grupos de Usuários (Administradores, Barbeiros, Clientes)...")
            grupos = ["Administradores", "Barbeiros", "Clientes"]
            for g_name in grupos:
                grupo, created = Group.objects.get_or_create(name=g_name)
                status_txt = "Criado" if created else "Já existente"
                self.stdout.write(f"  * Grupo '{grupo.name}': {status_txt}")

            # Sincroniza usuários existentes com seus respectivos grupos
            for user in User.objects.all():
                perfil = getattr(user, "perfil", None)
                if user.is_superuser or user.is_staff or (perfil and perfil.tipo_usuario == "administrador"):
                    g_admin = Group.objects.get(name="Administradores")
                    user.groups.add(g_admin)
                elif perfil and perfil.tipo_usuario == "barbeiro":
                    g_barb = Group.objects.get(name="Barbeiros")
                    user.groups.add(g_barb)
                else:
                    g_cli = Group.objects.get(name="Clientes")
                    user.groups.add(g_cli)

            # 1. SERVIÇOS CONFIRMADOS
            servicos_config = [
                {
                    "nome": "Cabelo",
                    "descricao": "Corte de cabelo",
                    "preco": Decimal("30.00"),
                    "duracao_minutos": 30,
                    "icone": "scissors",
                    "destaque": True,
                    "ordem": 1,
                },
                {
                    "nome": "Barba",
                    "descricao": "Serviço de barba",
                    "preco": Decimal("20.00"),
                    "duracao_minutos": 20,
                    "icone": "browser-safari",
                    "destaque": True,
                    "ordem": 2,
                },
                {
                    "nome": "Cavanhaque",
                    "descricao": "Serviço de cavanhaque",
                    "preco": Decimal("15.00"),
                    "duracao_minutos": 15,
                    "icone": "scissors-combo",
                    "destaque": False,
                    "ordem": 3,
                },
                {
                    "nome": "Sobrancelha",
                    "descricao": "Serviço de sobrancelha",
                    "preco": Decimal("5.00"),
                    "duracao_minutos": 10,
                    "icone": "eye",
                    "destaque": False,
                    "ordem": 4,
                },
            ]

            servicos_ativos_nomes = [s["nome"] for s in servicos_config]
            servicos_salvos = {}

            self.stdout.write("\n[1/4] Configurando Serviços...")
            for sdata in servicos_config:
                servico = Servico.objects.filter(nome__iexact=sdata["nome"]).first()
                if servico:
                    servico.nome = sdata["nome"]
                    servico.descricao = sdata["descricao"]
                    servico.preco = sdata["preco"]
                    servico.duracao_minutos = sdata["duracao_minutos"]
                    servico.icone = sdata["icone"]
                    servico.destaque = sdata["destaque"]
                    servico.ordem = sdata["ordem"]
                    servico.ativo = True
                    servico.save()
                    self.stdout.write(f"  * Atualizado: {servico.nome} - R$ {servico.preco} ({servico.duracao_minutos} min)")
                else:
                    servico = Servico.objects.create(
                        usuario=admin_user,
                        nome=sdata["nome"],
                        descricao=sdata["descricao"],
                        preco=sdata["preco"],
                        duracao_minutos=sdata["duracao_minutos"],
                        icone=sdata["icone"],
                        destaque=sdata["destaque"],
                        ordem=sdata["ordem"],
                        ativo=True,
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Criado: {servico.nome} - R$ {servico.preco} ({servico.duracao_minutos} min)"))
                servicos_salvos[sdata["nome"].lower()] = servico

            # Inativa serviços legados não pertencentes à lista oficial
            desativados_serv = Servico.objects.exclude(nome__in=servicos_ativos_nomes).filter(ativo=True)
            for s_old in desativados_serv:
                s_old.ativo = False
                s_old.save()
                self.stdout.write(self.style.NOTICE(f"  - Inativado serviço fora do catálogo: {s_old.nome}"))

            # 2. PRODUTOS CONFIRMADOS
            produtos_config = [
                {
                    "nome": "Pomada Fox",
                    "descricao": "Pomada modeladora profissional Fox para fixação e penteados.",
                    "preco": Decimal("20.00"),
                },
                {
                    "nome": "Pomada em pó",
                    "descricao": "Pomada em pó para volume, textura e efeito mate seco.",
                    "preco": Decimal("30.00"),
                },
                {
                    "nome": "Shampoo anticaspa",
                    "descricao": "Shampoo anticaspa revigorante para couro cabeludo limpo e refrescante.",
                    "preco": Decimal("30.00"),
                },
            ]

            produtos_ativos_nomes = [p["nome"] for p in produtos_config]
            self.stdout.write("\n[2/4] Configurando Produtos...")
            for pdata in produtos_config:
                prod = Produto.objects.filter(nome__iexact=pdata["nome"]).first()
                if prod:
                    prod.nome = pdata["nome"]
                    prod.descricao = pdata["descricao"]
                    prod.preco = pdata["preco"]
                    prod.ativo = True
                    prod.save()
                    self.stdout.write(f"  * Atualizado produto: {prod.nome} - R$ {prod.preco}")
                else:
                    prod = Produto.objects.create(
                        nome=pdata["nome"],
                        descricao=pdata["descricao"],
                        preco=pdata["preco"],
                        estoque=0,
                        ativo=True,
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Criado produto: {prod.nome} - R$ {prod.preco} (Estoque: 0)"))

            # Inativa produtos legados não confirmados
            desativados_prod = Produto.objects.exclude(nome__in=produtos_ativos_nomes).filter(ativo=True)
            for p_old in desativados_prod:
                p_old.ativo = False
                p_old.save()
                self.stdout.write(self.style.NOTICE(f"  - Inativado produto fora do catálogo: {p_old.nome}"))

            # 3. PLANOS DE ASSINATURA CONFIRMADOS
            planos_config = [
                {
                    "codigo": "plano-normal",
                    "nome": "Plano normal",
                    "descricao": "Plano mensal com 4 atendimentos completos de Cabelo e Sobrancelha no mês.",
                    "preco_mensal": Decimal("80.00"),
                    "modalidade": "limitado",
                    "limite_mensal": 4,
                    "servicos": ["cabelo", "sobrancelha"],
                    "inclui_barba": False,
                    "destaque": False,
                    "ordem": 1,
                },
                {
                    "codigo": "plano-com-barba",
                    "nome": "Plano com barba",
                    "descricao": "Plano mensal com 4 atendimentos completos de Cabelo, Sobrancelha e Barba no mês.",
                    "preco_mensal": Decimal("120.00"),
                    "modalidade": "limitado",
                    "limite_mensal": 4,
                    "servicos": ["cabelo", "sobrancelha", "barba"],
                    "inclui_barba": True,
                    "destaque": True,
                    "ordem": 2,
                },
                {
                    "codigo": "plano-cortes-infinitos",
                    "nome": "Plano cortes infinitos",
                    "descricao": "Cortes e sobrancelhas ilimitados durante todo o mês. Sem limite de utilizações.",
                    "preco_mensal": Decimal("100.00"),
                    "modalidade": "ilimitado",
                    "limite_mensal": None,
                    "servicos": ["cabelo", "sobrancelha"],
                    "inclui_barba": False,
                    "destaque": True,
                    "ordem": 3,
                },
            ]

            planos_codigos = [pl["codigo"] for pl in planos_config]
            self.stdout.write("\n[3/4] Configurando Planos de Assinatura...")
            for pldata in planos_config:
                plano = PlanoAssinatura.objects.filter(codigo=pldata["codigo"]).first()
                if not plano:
                    plano = PlanoAssinatura.objects.filter(nome__iexact=pldata["nome"]).first()

                if plano:
                    plano.codigo = pldata["codigo"]
                    plano.nome = pldata["nome"]
                    plano.descricao = pldata["descricao"]
                    plano.preco_mensal = pldata["preco_mensal"]
                    plano.modalidade = pldata["modalidade"]
                    plano.limite_mensal = pldata["limite_mensal"]
                    plano.cortes_por_mes = pldata["limite_mensal"] or 99
                    plano.inclui_barba = pldata["inclui_barba"]
                    plano.destaque = pldata["destaque"]
                    plano.ordem = pldata["ordem"]
                    plano.ativo = True
                    plano.save()
                    self.stdout.write(f"  * Atualizado plano: {plano.nome} - R$ {plano.preco_mensal} ({plano.modalidade})")
                else:
                    plano = PlanoAssinatura.objects.create(
                        codigo=pldata["codigo"],
                        nome=pldata["nome"],
                        descricao=pldata["descricao"],
                        preco_mensal=pldata["preco_mensal"],
                        modalidade=pldata["modalidade"],
                        limite_mensal=pldata["limite_mensal"],
                        cortes_por_mes=pldata["limite_mensal"] or 99,
                        inclui_barba=pldata["inclui_barba"],
                        destaque=pldata["destaque"],
                        ordem=pldata["ordem"],
                        ativo=True,
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Criado plano: {plano.nome} - R$ {plano.preco_mensal} ({plano.modalidade})"))

                # Vincula serviços inclusos
                plano.servicos_inclusos.clear()
                for s_slug in pldata["servicos"]:
                    if s_slug in servicos_salvos:
                        plano.servicos_inclusos.add(servicos_salvos[s_slug])

            # Inativa planos legados não confirmados
            desativados_planos = PlanoAssinatura.objects.exclude(codigo__in=planos_codigos).filter(ativo=True)
            for pl_old in desativados_planos:
                pl_old.ativo = False
                pl_old.save()
                self.stdout.write(self.style.NOTICE(f"  - Inativado plano fora do catálogo: {pl_old.nome}"))

            # 4. HORÁRIOS DISPONÍVEIS (08:00 A 21:30)
            self.stdout.write("\n[4/4] Configurando Horários da Grade (08:00 às 21:30)...")
            slots = [
                time(8, 0), time(8, 30), time(9, 0), time(9, 30),
                time(10, 0), time(10, 30), time(11, 0), time(11, 30),
                time(12, 0), time(12, 30), time(13, 0), time(13, 30),
                time(14, 0), time(14, 30), time(15, 0), time(15, 30),
                time(16, 0), time(16, 30), time(17, 0), time(17, 30),
                time(18, 0), time(18, 30), time(19, 0), time(19, 30),
                time(20, 0), time(20, 30), time(21, 0), time(21, 30)
            ]

            barbeiros = Barbeiro.objects.filter(ativo=True)
            for b in barbeiros:
                criados_count = 0
                for t in slots:
                    _, created = HorarioDisponivel.objects.get_or_create(
                        barbeiro=b,
                        horario=t,
                        defaults={"ativo": True}
                    )
                    if created:
                        criados_count += 1
                self.stdout.write(f"  * Barbeiro {b.nome}: 28 slots de 08:00 a 21:30 garantidos (+{criados_count} novos).")

            # 5. FOTOS REAIS DE TRABALHOS (GALERIA)
            self.stdout.write("\n[5/5] Configurando Galeria de Fotos de Trabalhos...")
            fotos_config = [
                {
                    "titulo": "Taper Fade em Cachos com Luzes",
                    "descricao": "Corte moderno com degradê suave na nuca, valorizando os cachos naturais com pontas iluminadas.",
                    "imagem": "trabalhos/cachos_luzes_taper.jpg",
                    "categoria": "corte",
                    "barbeiro_query": "Danilo"
                },
                {
                    "titulo": "Mid Fade com French Crop",
                    "descricao": "Degradê médio limpo na régua com topo texturizado e encaixe perfeito no perfil.",
                    "imagem": "trabalhos/mid_fade_crop.jpg",
                    "categoria": "corte",
                    "barbeiro_query": "Heitor"
                },
                {
                    "titulo": "Low Fade Texturizado Alinhado",
                    "descricao": "Disfarçado preciso com alinhamento frontal afiado e topo com textura moderna.",
                    "imagem": "trabalhos/low_fade_texturizado.jpg",
                    "categoria": "corte",
                    "barbeiro_query": "Danilo"
                },
                {
                    "titulo": "Low Fade com Linhas Freestyle",
                    "descricao": "Degradê baixo na régua com desenho navalhado personalizado e acabamento impecável.",
                    "imagem": "trabalhos/tribal_wave_fade.jpg",
                    "categoria": "corte",
                    "barbeiro_query": "Heitor"
                },
                {
                    "titulo": "Mid Fade com Risco Raio em Cachos",
                    "descricao": "Disfarçado médio com detalhe de raio navalhado, valorizando a textura e volume dos cachos.",
                    "imagem": "trabalhos/freestyle_raio_curls.jpg",
                    "categoria": "corte",
                    "barbeiro_query": "Heitor"
                },
                {
                    "titulo": "Taper Fade com Acabamento Preciso",
                    "descricao": "Taper clássico nas costeletas e nuca, perfeito para quem busca discrição e elegância.",
                    "imagem": "trabalhos/taper_fade_delacruz.jpg",
                    "categoria": "corte",
                    "barbeiro_query": "Heitor"
                },
            ]

            for fdata in fotos_config:
                barb = Barbeiro.objects.filter(nome__icontains=fdata["barbeiro_query"]).first() or Barbeiro.objects.first()
                if not barb:
                    barb = Barbeiro.objects.create(
                        nome="Heitor Pontes" if "Heitor" in fdata["barbeiro_query"] else "Danilo Delacruz",
                        especialidade="Especialista em Cortes & Degradê",
                        descricao_curta="Profissional especialista da Delacruz Barber.",
                        ativo=True
                    )
                foto_obj = FotoTrabalho.objects.filter(titulo=fdata["titulo"]).first()
                if not foto_obj:
                    FotoTrabalho.objects.create(
                        barbeiro=barb,
                        titulo=fdata["titulo"],
                        descricao=fdata["descricao"],
                        imagem=fdata["imagem"],
                        categoria=fdata["categoria"],
                        publicado=True
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Foto adicionada: {fdata['titulo']} ({barb.nome})"))
                else:
                    foto_obj.imagem = fdata["imagem"]
                    foto_obj.descricao = fdata["descricao"]
                    foto_obj.barbeiro = barb
                    foto_obj.publicado = True
                    foto_obj.save()
                    self.stdout.write(f"  * Foto atualizada: {fdata['titulo']}")

            if dry_run:
                self.stdout.write(self.style.WARNING("\n--- MODO DRY-RUN: Revertendo transação. Nenhuma gravação persistida. ---"))
                transaction.set_rollback(True)
            else:
                self.stdout.write(self.style.SUCCESS("\nCatálogo Delacruz Barber, Fotos e Grade configurados com sucesso!"))
