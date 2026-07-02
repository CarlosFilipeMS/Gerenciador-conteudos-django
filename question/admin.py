from django.contrib import admin

from question.models import (
    Dimensao,
    Pergunta,
    PesoPergunta,
    Questionario,
    Secao,
    VersaoQuestionario,
)


class BaseModelAdmin(admin.ModelAdmin):
    """Admin base com campos de auditoria somente leitura."""

    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')


class VersaoQuestionarioInline(admin.TabularInline):
    model = VersaoQuestionario
    extra = 0
    fields = ('numero_versao', 'status', 'data_publicacao', 'observacao')
    show_change_link = True


class SecaoInline(admin.TabularInline):
    model = Secao
    extra = 0
    fields = ('titulo', 'ordem', 'descricao')
    show_change_link = True


class DimensaoInline(admin.TabularInline):
    model = Dimensao
    extra = 0
    fields = ('codigo', 'nome', 'ordem', 'descricao')
    show_change_link = True


class PerguntaInline(admin.TabularInline):
    model = Pergunta
    extra = 0
    fields = (
        'identificador',
        'texto',
        'dimensao',
        'peso_pergunta',
        'ordem',
        'obrigatoria',
        'ativa',
    )
    show_change_link = True


@admin.register(Questionario)
class QuestionarioAdmin(BaseModelAdmin):
    list_display = ('titulo', 'ativo', 'created_at', 'updated_at')
    list_filter = ('ativo',)
    search_fields = ('titulo', 'descricao')
    inlines = (VersaoQuestionarioInline,)


@admin.register(VersaoQuestionario)
class VersaoQuestionarioAdmin(BaseModelAdmin):
    list_display = (
        'questionario',
        'numero_versao',
        'status',
        'data_publicacao',
        'created_at',
    )
    list_filter = ('status', 'questionario')
    search_fields = ('questionario__titulo', 'observacao')
    inlines = (SecaoInline, DimensaoInline)


@admin.register(Secao)
class SecaoAdmin(BaseModelAdmin):
    list_display = ('titulo', 'versao_questionario', 'ordem', 'created_at')
    list_filter = ('versao_questionario__questionario', 'versao_questionario')
    search_fields = ('titulo', 'descricao')
    inlines = (PerguntaInline,)


@admin.register(Dimensao)
class DimensaoAdmin(BaseModelAdmin):
    list_display = ('codigo', 'nome', 'versao_questionario', 'ordem')
    list_filter = ('versao_questionario__questionario', 'versao_questionario')
    search_fields = ('codigo', 'nome', 'descricao')


@admin.register(PesoPergunta)
class PesoPerguntaAdmin(BaseModelAdmin):
    list_display = ('codigo', 'nome', 'peso', 'created_at')
    search_fields = ('codigo', 'nome', 'descricao')


@admin.register(Pergunta)
class PerguntaAdmin(BaseModelAdmin):
    list_display = (
        'identificador',
        'secao',
        'dimensao',
        'peso_pergunta',
        'ordem',
        'obrigatoria',
        'ativa',
    )
    list_filter = ('obrigatoria', 'ativa', 'secao__versao_questionario')
    search_fields = ('identificador', 'texto', 'texto_ajuda')
