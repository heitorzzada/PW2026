from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0002_cartaofidelidade_comissaobarbeiro_cupomdesconto_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MovimentacaoFidelidade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pontos", models.IntegerField()),
                ("tipo", models.CharField(choices=[("credito", "Crédito"), ("resgate", "Resgate")], max_length=10)),
                ("descricao", models.CharField(max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("agendamento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="movimentacoes_fidelidade", to="website.agendamento")),
                ("cartao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movimentacoes", to="website.cartaofidelidade")),
            ],
        ),
        migrations.CreateModel(
            name="NotificacaoLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("confirmacao", "Confirmação"), ("lembrete", "Lembrete"), ("agradecimento", "Agradecimento")], max_length=20)),
                ("canal", models.CharField(choices=[("whatsapp", "WhatsApp"), ("email", "E-mail")], default="whatsapp", max_length=20)),
                ("destinatario", models.CharField(max_length=30)),
                ("mensagem", models.TextField()),
                ("status", models.CharField(choices=[("enviado", "Enviado"), ("falha", "Falha"), ("pendente", "Pendente")], default="pendente", max_length=20)),
                ("erro", models.TextField(blank=True, null=True)),
                ("enviado_em", models.DateTimeField(blank=True, null=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("agendamento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notificacoes", to="website.agendamento")),
                ("cliente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificacoes", to="website.cliente")),
            ],
        ),
    ]
