# core/management/commands/seed.py
# Comando: python manage.py seed

from django.core.management.base import BaseCommand
from core.models import Cliente, Produto, Entregador, Entrega, EntregaProduto, Pagamento
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = "Popula o banco de dados com dados da distribuidora de água e gás"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Iniciando população do banco..."))

        # =====================================================================
        # CLIENTES
        # =====================================================================
        clientes = [
            {"nome": "Maria Silva", "endereco": "Rua das Flores, 123", "telefone": "11999990001", "email": "maria@example.com"},
            {"nome": "João Oliveira", "endereco": "Av. Central, 450", "telefone": "11999990002", "email": "joao@example.com"},
            {"nome": "Carla Mendes", "endereco": "Rua Projetada, 89", "telefone": "11999990003", "email": "carla@example.com"},
        ]

        cliente_objs = []
        for c in clientes:
            obj, created = Cliente.objects.get_or_create(email=c["email"], defaults=c)
            cliente_objs.append(obj)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(cliente_objs)} clientes criados."))

        # =====================================================================
        # PRODUTOS
        # =====================================================================
        produtos = [
            {"nome": "Água Mineral 20L", "descricao": "Galão retornável 20 litros", "preco": Decimal("10.00"), "estoque": 100},
            {"nome": "Gás de Cozinha 13kg", "descricao": "Botijão P13 tradicional", "preco": Decimal("120.00"), "estoque": 50},
            {"nome": "Água Mineral 10L", "descricao": "Galão retornável 10 litros", "preco": Decimal("7.00"), "estoque": 80},
        ]

        produto_objs = []
        for p in produtos:
            obj, created = Produto.objects.get_or_create(nome=p["nome"], defaults=p)
            produto_objs.append(obj)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(produto_objs)} produtos criados."))

        # =====================================================================
        # ENTREGADORES
        # =====================================================================
        entregadores = [
            {"nome": "Carlos Moto", "telefone": "11988887777", "veiculo": "Moto Honda CG 160"},
            {"nome": "Paulo Kombi", "telefone": "11988886666", "veiculo": "Kombi 1.4 Flex"},
        ]

        entregador_objs = []
        for e in entregadores:
            obj, created = Entregador.objects.get_or_create(nome=e["nome"], defaults=e)
            entregador_objs.append(obj)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(entregador_objs)} entregadores criados."))

        # =====================================================================
        # ENTREGAS + PRODUTOS + PAGAMENTOS
        # =====================================================================
        for i, cliente in enumerate(cliente_objs):
            entregador = entregador_objs[i % len(entregador_objs)]
            data_prevista = timezone.now() + timedelta(hours=2 + i)

            entrega = Entrega.objects.create(
                cliente=cliente,
                entregador=entregador,
                data_entrega_prevista=data_prevista,
                status="PENDENTE",
                endereco_entrega=cliente.endereco,
            )

            # Cada entrega recebe 1 ou 2 produtos
            if i % 2 == 0:
                EntregaProduto.objects.create(entrega=entrega, produto=produto_objs[0], quantidade=1)
                valor_total = produto_objs[0].preco
            else:
                EntregaProduto.objects.create(entrega=entrega, produto=produto_objs[1], quantidade=1)
                EntregaProduto.objects.create(entrega=entrega, produto=produto_objs[0], quantidade=1)
                valor_total = produto_objs[0].preco + produto_objs[1].preco

            Pagamento.objects.create(
                entrega=entrega,
                valor=valor_total,
                metodo="PIX",
                status="PENDENTE"
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Entrega #{entrega.id} criada para {cliente.nome} — total: R$ {valor_total}"))

        self.stdout.write(self.style.SUCCESS("🎉 POPULAÇÃO FINALIZADA COM SUCESSO!"))