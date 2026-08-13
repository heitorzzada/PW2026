from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import time
from website.models import (
    PerfilUsuario, Servico, Barbeiro, HorarioDisponivel
)

class Command(BaseCommand):
    help = "Seed the database with initial Delacruz Barber data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Create superuser
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@delacruzbarber.com.br",
                "first_name": "Admin",
                "last_name": "Delacruz",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin_user.set_password("admin")
            admin_user.save()
            PerfilUsuario.objects.get_or_create(
                usuario=admin_user,
                defaults={"tipo_usuario": "administrador", "telefone": "(44) 99999-9999"}
            )
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created (password: admin)"))
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 2. Create Barbers and their user accounts
        barbers_data = [
            {
                "username": "danilo",
                "nome": "Danilo Delacruz",
                "cargo": "Barbeiro Chefe",
                "especialidade": "Cortes clássicos, degradê e acabamento preciso",
                "descricao_curta": "Barbeiro chefe da Delacruz Barber, responsável por cortes clássicos, degradês e acabamentos precisos.",
                "telefone": "(44) 9919-0997"
            },
            {
                "username": "heitor",
                "nome": "Heitor Pontes",
                "cargo": "Barbeiro",
                "especialidade": "Cortes modernos, barba e finalização",
                "descricao_curta": "Barbeiro da Delacruz Barber, especializado em cortes modernos, barba e finalização.",
                "telefone": "(44) 9102-2176"
            }
        ]

        barber_objs = []
        for bdata in barbers_data:
            user, u_created = User.objects.get_or_create(
                username=bdata["username"],
                defaults={
                    "email": f"{bdata['username']}@delacruzbarber.com.br",
                    "first_name": bdata["nome"].split()[0],
                    "last_name": bdata["nome"].split()[-1]
                }
            )
            if u_created:
                user.set_password("123456")
                user.save()
            
            PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={"tipo_usuario": "barbeiro", "telefone": bdata["telefone"]}
            )

            barbeiro, b_created = Barbeiro.objects.get_or_create(
                nome=bdata["nome"],
                defaults={
                    "usuario": user,
                    "cargo": bdata["cargo"],
                    "especialidade": bdata["especialidade"],
                    "descricao_curta": bdata["descricao_curta"],
                    "ativo": True
                }
            )
            barber_objs.append(barbeiro)
            self.stdout.write(self.style.SUCCESS(f"Barber '{barbeiro.nome}' configured (user: {bdata['username']}, password: 123456)"))

        # 3. Create Services
        services_data = [
            {
                "nome": "Corte Masculino Clássico",
                "descricao": "Corte tradicional masculino com acabamento alinhado e finalização profissional.",
                "duracao": 30,
                "preco": Decimal("40.00"),
                "icone": "scissors",
                "destaque": True,
                "ordem": 1
            },
            {
                "nome": "Corte Degradê",
                "descricao": "Corte masculino com técnica de degradê suave ou marcado, finalizado com produtos premium.",
                "duracao": 40,
                "preco": Decimal("45.00"),
                "icone": "scissors",
                "destaque": True,
                "ordem": 2
            },
            {
                "nome": "Barba Completa",
                "descricao": "Aparação e modelagem de barba com navalha, toalha quente e hidratação.",
                "duracao": 30,
                "preco": Decimal("35.00"),
                "icone": "browser-safari",
                "destaque": True,
                "ordem": 3
            },
            {
                "nome": "Corte + Barba",
                "descricao": "Combo completo de corte degradê com barba modelada. O pacote mais pedido.",
                "duracao": 60,
                "preco": Decimal("70.00"),
                "icone": "scissors-combo",
                "destaque": True,
                "ordem": 4
            },
            {
                "nome": "Sobrancelha",
                "descricao": "Design e aparação de sobrancelha masculina com navalha.",
                "duracao": 15,
                "preco": Decimal("20.00"),
                "icone": "eye",
                "destaque": False,
                "ordem": 5
            },
            {
                "nome": "Corte Infantil",
                "descricao": "Corte especial para crianças até 12 anos, com paciência e cuidado.",
                "duracao": 30,
                "preco": Decimal("35.00"),
                "icone": "emoji-smile",
                "destaque": False,
                "ordem": 6
            },
            {
                "nome": "Pacote Premium Delacruz",
                "descricao": "Experiência completa com corte, barba, sobrancelha e finalização premium.",
                "duracao": 90,
                "preco": Decimal("100.00"),
                "icone": "gem",
                "destaque": True,
                "ordem": 7
            }
        ]

        for sdata in services_data:
            serv, created = Servico.objects.get_or_create(
                nome=sdata["nome"],
                defaults={
                    "usuario": admin_user,
                    "descricao": sdata["descricao"],
                    "preco": sdata["preco"],
                    "duracao_minutos": sdata["duracao"],
                    "icone": sdata["icone"],
                    "ativo": True,
                    "destaque": sdata["destaque"],
                    "ordem": sdata["ordem"]
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Service '{serv.nome}' created."))
            else:
                self.stdout.write(f"Service '{serv.nome}' already exists.")

        # 4. Create Available Times
        default_times = [
            time(8, 0), time(8, 30), time(9, 0), time(9, 30),
            time(10, 0), time(10, 30), time(11, 0), time(11, 30),
            time(12, 0), time(12, 30), time(13, 0), time(13, 30),
            time(14, 0), time(14, 30), time(15, 0), time(15, 30),
            time(16, 0), time(16, 30), time(17, 0), time(17, 30),
            time(18, 0), time(18, 30), time(19, 0), time(19, 30),
            time(20, 0), time(20, 30), time(21, 0)
        ]

        for barbeiro in barber_objs:
            count = 0
            for t in default_times:
                hd, created = HorarioDisponivel.objects.get_or_create(
                    barbeiro=barbeiro,
                    horario=t,
                    defaults={"usuario": admin_user, "ativo": True}
                )
                if created:
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"Seeded {count} time slots for '{barbeiro.nome}'."))

        self.stdout.write(self.style.SUCCESS("Database seeding completed!"))
