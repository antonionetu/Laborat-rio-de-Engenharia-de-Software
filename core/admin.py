# admin.py
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal
from django.utils.html import format_html

from .models import Cliente, Produto, Entregador, Entrega, EntregaProduto, Pagamento


# ========================================================================
# INLINE
# ========================================================================

class EntregaProdutoInline(admin.TabularInline):
    model = EntregaProduto
    verbose_name = "Produto"
    extra = 1


# ========================================================================
# CLIENTE
# ========================================================================

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'endereco_resumido', 'data_cadastro')
    search_fields = ('nome', 'telefone', 'email', 'endereco')
    list_filter = ('data_cadastro',)
    ordering = ('nome',)

    readonly_fields = ('data_cadastro',)

    fieldsets = (
        ('Dados do Cliente', {
            'fields': ('nome', 'email', 'telefone')
        }),
        ('Endereço', {
            'fields': ('endereco',)
        }),
        ('Informações Internas', {
            'classes': ('collapse',),
            'fields': ('data_cadastro',)
        })
    )

    def endereco_resumido(self, obj):
        return obj.endereco[:40] + "..." if len(obj.endereco) > 40 else obj.endereco
    endereco_resumido.short_description = "Endereço"


# ========================================================================
# PRODUTO
# ========================================================================

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao_resumida', 'preco_formatado', 'estoque', 'data_criacao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)

    readonly_fields = ('data_criacao',)

    fieldsets = (
        ('Produto', {
            'fields': ('nome', 'descricao')
        }),
        ('Financeiro & Estoque', {
            'fields': ('preco', 'estoque')
        }),
        ('Datas', {
            'classes': ('collapse',),
            'fields': ('data_criacao',)
        })
    )

    def preco_formatado(self, obj):
        return f"R$ {obj.preco:.2f}"
    preco_formatado.short_description = 'Preço'

    def descricao_resumida(self, obj):
        return obj.descricao[:40] + "..." if len(obj.descricao) > 40 else obj.descricao
    descricao_resumida.short_description = "Descrição"


# ========================================================================
# ENTREGADOR
# ========================================================================

class EntregadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'veiculo')
    search_fields = ('nome', 'telefone', 'veiculo')
    ordering = ('nome',)

    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'telefone')
        }),
        ('Detalhes do Veículo', {
            'fields': ('veiculo',)
        })
    )


# ========================================================================
# ENTREGA (ADMIN COMPLETO QUE VOCÊ JÁ TINHA)
# ========================================================================

class EntregaAdmin(admin.ModelAdmin):
    inlines = [EntregaProdutoInline]

    list_display = ('get_produtos', 'get_quantidades', 'endereco_entrega', 'get_valor',
                    'get_metodo_pagamento', 'get_status_pagamento', 'get_situacao')
    readonly_fields = ('status',)
    change_form_template = 'admin/entrega/change_form.html'

    def get_exclude(self, request, obj=None):
        if obj is None:
            return ['status']
        return super().get_exclude(request, obj) or []

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        if request.method == 'POST' and object_id:
            obj = self.get_object(request, object_id)

            if "_em_transito" in request.POST:
                obj.status = 'EM_TRANSITO'
                obj.save()
                self.message_user(request, "✅ Status alterado para Em Trânsito.")
                return redirect(request.path)

            if "_cancelada" in request.POST:
                obj.status = 'CANCELADA'
                obj.save()
                self.message_user(request, "❌ Entrega cancelada.")
                return redirect(request.path)

            if "_entregue" in request.POST:
                metodo = request.POST.get('metodo')

                if metodo:

                    # =========================================
                    # 1. VERIFICAR ESTOQUE ANTES DE ENTREGAR
                    # =========================================
                    for ep in obj.entrega_produtos.all():
                        if ep.produto.estoque < ep.quantidade:
                            self.message_user(
                                request,
                                f"❌ Estoque insuficiente para o produto '{ep.produto.nome}'. "
                                f"Disponível: {ep.produto.estoque}, Necessário: {ep.quantidade}.",
                                level='error'
                            )
                            return redirect(request.path)

                    # =========================================
                    # 2. DESCONTAR O ESTOQUE
                    # =========================================
                    for ep in obj.entrega_produtos.all():
                        ep.produto.estoque -= ep.quantidade
                        ep.produto.save()

                    # =========================================
                    # 3. ATUALIZAR STATUS DA ENTREGA
                    # =========================================
                    obj.status = 'ENTREGUE'
                    obj.save()

                    # =========================================
                    # 4. CALCULAR TOTAL
                    # =========================================
                    valor_total = Decimal('0.00')
                    for ep in obj.entrega_produtos.all():
                        valor_total += ep.produto.preco * ep.quantidade

                    # Pagamento pendente ou pago
                    if metodo == 'FIADO':
                        status_pagamento = 'PENDENTE'
                        data_pagamento = None
                        emoji_status = "⏳"
                        texto_status = "Pendente"
                    else:
                        status_pagamento = 'PAGO'
                        data_pagamento = timezone.now()
                        emoji_status = "✅"
                        texto_status = "Pago"

                    # =========================================
                    # 5. CRIAR OU ATUALIZAR REGISTRO DE PAGAMENTO
                    # =========================================
                    if hasattr(obj, 'pagamento'):
                        obj.pagamento.metodo = metodo
                        obj.pagamento.valor = valor_total
                        obj.pagamento.status = status_pagamento
                        obj.pagamento.data_pagamento = data_pagamento
                        obj.pagamento.save()

                        mensagem = f"{emoji_status} Entrega confirmada! Pagamento de R$ {valor_total:.2f} via {obj.pagamento.get_metodo_display()} - Status: {texto_status}."
                    else:
                        Pagamento.objects.create(
                            entrega=obj,
                            metodo=metodo,
                            valor=valor_total,
                            status=status_pagamento,
                            data_pagamento=data_pagamento
                        )
                        metodo_display = dict(Pagamento._meta.get_field('metodo').choices)[metodo]
                        mensagem = f"{emoji_status} Entrega confirmada! Pagamento de R$ {valor_total:.2f} via {metodo_display} - Status: {texto_status}."

                    self.message_user(request, mensagem)
                    return redirect(request.path)

                else:
                    self.message_user(request, "⚠️ Selecione um método de pagamento.", level='error')
                    return redirect(request.path)

        return super().changeform_view(request, object_id, form_url, extra_context)

    # Campos list_display
    def get_produtos(self, obj):
        return ", ".join([ep.produto.nome for ep in obj.entrega_produtos.all()])
    get_produtos.short_description = 'Produto'

    def get_quantidades(self, obj):
        return ", ".join([str(ep.quantidade) for ep in obj.entrega_produtos.all()])
    get_quantidades.short_description = 'Quantidade'

    def get_valor(self, obj):
        return f"R$ {obj.pagamento.valor:.2f}" if hasattr(obj, 'pagamento') else '-'
    get_valor.short_description = 'Valor'

    def get_metodo_pagamento(self, obj):
        return obj.pagamento.get_metodo_display() if hasattr(obj, 'pagamento') else '-'
    get_metodo_pagamento.short_description = 'Forma de Pagamento'

    def get_status_pagamento(self, obj):
        if hasattr(obj, 'pagamento'):
            if obj.pagamento.status == 'PAGO':
                return '✅ Pago'
            elif obj.pagamento.status == 'PENDENTE':
                return '⏳ Pendente'
            else:
                return '❌ Falha'
        return '-'
    get_status_pagamento.short_description = 'Status Pagamento'

    def get_situacao(self, obj):
        return '✅' if obj.status == 'ENTREGUE' else '❌'
    get_situacao.short_description = 'Entregue'


# ========================================================================
# PAGAMENTO
# ========================================================================
class CustomDateFilter(admin.DateFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.title = 'data de entrega'


class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        'entrega',
        'valor_formatado',
        'metodo',
        'status_colorido',
        'data_pagamento',
    )
    search_fields = ('entrega__id', 'entrega__cliente__nome')
    list_filter = (
        'status',
        ('entrega__data_entrega_prevista', CustomDateFilter),
    )
    ordering = ('-data_pagamento',)

    def valor_formatado(self, obj):
        return f"R$ {obj.valor:.2f}"

    valor_formatado.short_description = 'Valor'

    def status_colorido(self, obj):
        if obj.status == 'PAGO':
            return format_html(
                '<span style="color:green;font-weight:bold;">Pago</span>'
            )
        if obj.status == 'PENDENTE':
            return format_html(
                '<span style="color:orange;font-weight:bold;">Pendente</span>'
            )
        return format_html(
            '<span style="color:red;font-weight:bold;">Falha</span>'
        )

    status_colorido.short_description = 'Status'

# ========================================================================
# REGISTROS
# ========================================================================

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Entregador, EntregadorAdmin)
admin.site.register(Entrega, EntregaAdmin)
admin.site.register(Pagamento, PagamentoAdmin)
