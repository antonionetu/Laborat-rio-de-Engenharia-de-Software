# models.py
from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Entregador(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    veiculo = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Entregadores"

    def __str__(self):
        return self.nome

class Entrega(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_TRANSITO', 'Em Trânsito'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='entregas')
    entregador = models.ForeignKey(Entregador, on_delete=models.SET_NULL, null=True, related_name='entregas')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_entrega_prevista = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    endereco_entrega = models.TextField()

    def __str__(self):
        return f"Entrega #{self.id} para {self.cliente.nome}"

class EntregaProduto(models.Model):
    entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, related_name='entrega_produtos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='entrega_produtos')
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('entrega', 'produto')

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade}) para Entrega {self.entrega.id}"

class Pagamento(models.Model):
    METODO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO', 'Cartão'),
        ('PIX', 'PIX'),
        ('BOLETO', 'Boleto'),
        ('FIADO', 'Fiado'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('FALHA', 'Falha'),
    ]

    entrega = models.OneToOneField(Entrega, on_delete=models.CASCADE, related_name='pagamento')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODO_CHOICES)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')

    def __str__(self):
        return f"Pagamento {self.id} para Entrega {self.entrega.id}"
        