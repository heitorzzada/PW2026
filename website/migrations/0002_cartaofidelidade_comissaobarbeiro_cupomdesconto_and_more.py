from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CupomDesconto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=30, unique=True)),
                ("tipo", models.CharField(choices=[("porcentagem", "Porcentagem (%)"), ("fixo", "Valor Fixo (R$)")], default="porcentagem", max_length=20)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=6)),
                ("limite_uso", models.IntegerField(default=100)),
                ("usado_vezes", models.IntegerField(default=0)),
                ("ativo", models.BooleanField(default=True)),
                ("validade", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100)),
                ("descricao", models.TextField(blank=True, null=True)),
                ("preco", models.DecimalField(decimal_places=2, max_digits=6)),
                ("estoque", models.IntegerField(default=0)),
                ("imagem", models.CharField(blank=True, max_length=100, null=True)),
                ("ativo", models.BooleanField(default=True)),
                ("cadastrado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="barbeiro",
            name="percentual_comissao",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="cupom",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="agendamentos", to="website.cupomdesconto"),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="desconto_aplicado",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="duracao_total_minutos",
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="horario_fim",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="qualquer_barbeiro",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="servicos",
            field=models.ManyToManyField(blank=True, related_name="agendamentos_multiplos", to="website.servico"),
        ),
        migrations.AddField(
            model_name="agendamento",
            name="valor_total",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.AlterField(
            model_name="agendamento",
            name="barbeiro",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="agendamentos", to="website.barbeiro"),
        ),
        migrations.AlterField(
            model_name="agendamento",
            name="servico",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="agendamentos", to="website.servico"),
        ),
        migrations.CreateModel(
            name="CartaoFidelidade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pontos_acumulados", models.IntegerField(default=0)),
                ("cortes_gratuitos_disponiveis", models.IntegerField(default=0)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("cliente", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="fidelidade", to="website.cliente")),
            ],
        ),
        migrations.CreateModel(
            name="ComissaoBarbeiro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("valor_total_servico", models.DecimalField(decimal_places=2, max_digits=8)),
                ("percentual_comissao", models.DecimalField(decimal_places=2, max_digits=5)),
                ("valor_comissao", models.DecimalField(decimal_places=2, max_digits=8)),
                ("pago", models.BooleanField(default=False)),
                ("gerado_em", models.DateTimeField(auto_now_add=True)),
                ("agendamento", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="comissao", to="website.agendamento")),
                ("barbeiro", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comissoes", to="website.barbeiro")),
            ],
        ),
        migrations.CreateModel(
            name="PagamentoPix",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transacao_id", models.CharField(max_length=255, unique=True)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=8)),
                ("qr_code_base64", models.TextField(blank=True, null=True)),
                ("qr_code_payload", models.TextField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pendente", "Pendente"), ("pago", "Pago"), ("expirado", "Expirado"), ("cancelado", "Cancelado")], default="pendente", max_length=20)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("pago_em", models.DateTimeField(blank=True, null=True)),
                ("agendamento", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="pagamento_pix", to="website.agendamento")),
            ],
        ),
        migrations.CreateModel(
            name="VendaProduto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.IntegerField(default=1)),
                ("valor_total", models.DecimalField(decimal_places=2, max_digits=8)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("barbeiro", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="vendas_produtos", to="website.barbeiro")),
                ("cliente", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="compras_produtos", to="website.cliente")),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vendas", to="website.produto")),
            ],
        ),
    ]
