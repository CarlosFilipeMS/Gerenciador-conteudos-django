from django.db import models

from core.models import BaseModel


class Questionario(BaseModel):
    """Representa um instrumento de avaliação."""

    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'questionario'
        verbose_name = 'Questionário'
        verbose_name_plural = 'Questionários'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class VersaoQuestionario(BaseModel):
    """Representa uma versão de um questionário."""

    class Status(models.TextChoices):
        RASCUNHO = 'RASCUNHO', 'Rascunho'
        PUBLICADO = 'PUBLICADO', 'Publicado'
        ARQUIVADO = 'ARQUIVADO', 'Arquivado'

    questionario = models.ForeignKey(
        Questionario,
        on_delete=models.PROTECT,
        related_name='versoes',
    )
    numero_versao = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RASCUNHO,
    )
    observacao = models.TextField(blank=True)
    data_publicacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'versao_questionario'
        verbose_name = 'Versão de Questionário'
        verbose_name_plural = 'Versões de Questionário'
        ordering = ['questionario', 'numero_versao']
        constraints = [
            models.UniqueConstraint(
                fields=['questionario', 'numero_versao'],
                condition=models.Q(deleted_at__isnull=True),
                name='uq_versao_questionario_numero_ativo',
            ),
        ]
        indexes = [
            models.Index(fields=['status'], name='idx_versao_status'),
        ]

    def __str__(self):
        return f'{self.questionario.titulo} v{self.numero_versao}'


class Secao(BaseModel):
    """Agrupa perguntas para organização visual."""

    versao_questionario = models.ForeignKey(
        VersaoQuestionario,
        on_delete=models.PROTECT,
        related_name='secoes',
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveIntegerField()

    class Meta:
        db_table = 'secao'
        verbose_name = 'Seção'
        verbose_name_plural = 'Seções'
        ordering = ['versao_questionario', 'ordem']
        indexes = [
            models.Index(fields=['versao_questionario', 'ordem'], name='idx_secao_ordem'),
        ]

    def __str__(self):
        return f'{self.titulo} (ordem {self.ordem})'


class Dimensao(BaseModel):
    """Representa um agrupador analítico para cálculos futuros."""

    versao_questionario = models.ForeignKey(
        VersaoQuestionario,
        on_delete=models.PROTECT,
        related_name='dimensoes',
    )
    codigo = models.CharField(max_length=100)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveIntegerField()

    class Meta:
        db_table = 'dimensao'
        verbose_name = 'Dimensão'
        verbose_name_plural = 'Dimensões'
        ordering = ['versao_questionario', 'ordem']
        constraints = [
            models.UniqueConstraint(
                fields=['versao_questionario', 'codigo'],
                condition=models.Q(deleted_at__isnull=True),
                name='uq_dimensao_codigo_versao_ativo',
            ),
        ]
        indexes = [
            models.Index(fields=['versao_questionario', 'ordem'], name='idx_dimensao_ordem'),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class PesoPergunta(BaseModel):
    """Define o peso de uma pergunta para cálculos futuros."""

    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=100)
    peso = models.IntegerField()
    descricao = models.TextField(blank=True)

    class Meta:
        db_table = 'peso_pergunta'
        verbose_name = 'Peso de Pergunta'
        verbose_name_plural = 'Pesos de Pergunta'
        ordering = ['codigo']
        constraints = [
            models.UniqueConstraint(
                fields=['codigo'],
                condition=models.Q(deleted_at__isnull=True),
                name='uq_peso_pergunta_codigo_ativo',
            ),
        ]

    def __str__(self):
        return f'{self.codigo} (peso {self.peso})'


class Pergunta(BaseModel):
    """Elemento central do sistema de questionários."""

    secao = models.ForeignKey(
        Secao,
        on_delete=models.PROTECT,
        related_name='perguntas',
    )
    dimensao = models.ForeignKey(
        Dimensao,
        on_delete=models.PROTECT,
        related_name='perguntas',
    )
    peso_pergunta = models.ForeignKey(
        PesoPergunta,
        on_delete=models.PROTECT,
        related_name='perguntas',
    )
    identificador = models.CharField(max_length=100)
    texto = models.TextField()
    texto_ajuda = models.TextField(blank=True)
    ordem = models.PositiveIntegerField()
    obrigatoria = models.BooleanField(default=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        db_table = 'pergunta'
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['secao', 'ordem']
        constraints = [
            models.UniqueConstraint(
                fields=['identificador'],
                condition=models.Q(deleted_at__isnull=True),
                name='uq_pergunta_identificador_ativo',
            ),
        ]
        indexes = [
            models.Index(fields=['secao', 'ordem'], name='idx_pergunta_ordem'),
            models.Index(fields=['dimensao'], name='idx_pergunta_dimensao'),
        ]

    def __str__(self):
        return f'{self.identificador} - {self.texto[:50]}'
