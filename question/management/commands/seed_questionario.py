from django.core.management.base import BaseCommand
from django.utils import timezone

from question.models import (
    Dimensao,
    Pergunta,
    PesoPergunta,
    Questionario,
    Secao,
    VersaoQuestionario,
)


class Command(BaseCommand):
    help = 'Popula o banco com o questionário TRPE v1'

    def handle(self, *args, **options):
        pesos_data = [
            ('CRITICO', 'Indicador Crítico', 5, 'Sinais de risco imediato'),
            ('ALTO', 'Risco Alto', 4, 'Indicadores graves'),
            ('MEDIO', 'Risco Médio', 3, 'Indicadores moderados'),
            ('BAIXO', 'Risco Baixo', 2, 'Indicadores leves'),
            ('PROTETOR', 'Fator Protetor', 1, 'Apoio e rede de suporte'),
        ]
        pesos = {}
        for codigo, nome, peso, descricao in pesos_data:
            pesos[codigo], _ = PesoPergunta.objects.get_or_create(
                codigo=codigo,
                defaults={'nome': nome, 'peso': peso, 'descricao': descricao},
            )

        questionario, _ = Questionario.objects.get_or_create(
            titulo='Triagem de Risco Psicossocial Escolar (TRPE)',
            defaults={
                'descricao': (
                    'Instrumento de triagem para identificação precoce de '
                    'riscos psicossociais em estudantes do ensino fundamental '
                    'e médio. Escala: 0 Nunca a 4 Sempre.'
                ),
                'ativo': True,
            },
        )

        versao, created = VersaoQuestionario.objects.get_or_create(
            questionario=questionario,
            numero_versao=1,
            defaults={
                'status': VersaoQuestionario.Status.PUBLICADO,
                'observacao': 'Versão inicial para triagem escolar.',
                'data_publicacao': timezone.now(),
            },
        )
        if not created:
            self.stdout.write(self.style.WARNING('Seed já aplicada. Abortando.'))
            return

        secoes_cfg = [
            (1, 'Como você tem se sentido', 'Humor, ansiedade e sinais emocionais.'),
            (2, 'Relações na escola', 'Colegas, professores e ambiente social.'),
            (3, 'Segurança e convivência', 'Bullying, violência e medo.'),
            (4, 'Apoio e proteção', 'Família, rede de apoio e fatores protetivos.'),
        ]
        secoes = {}
        for ordem, titulo, descricao in secoes_cfg:
            secoes[ordem] = Secao.objects.create(
                versao_questionario=versao,
                titulo=titulo,
                descricao=descricao,
                ordem=ordem,
            )

        dimensoes_cfg = [
            ('SAUDE_MENTAL', 'Saúde Mental', 'Tristeza, ansiedade e ideação.', 1),
            ('BULLYING', 'Bullying e Violência', 'Vitimização e agressão.', 2),
            ('ISOLAMENTO', 'Isolamento Social', 'Solidão e exclusão.', 3),
            ('PROTECAO', 'Fatores de Proteção', 'Apoio familiar e escolar.', 4),
        ]
        dimensoes = {}
        for codigo, nome, descricao, ordem in dimensoes_cfg:
            dimensoes[codigo] = Dimensao.objects.create(
                versao_questionario=versao,
                codigo=codigo,
                nome=nome,
                descricao=descricao,
                ordem=ordem,
            )

        perguntas = [
            # (secao, ordem, identificador, texto, dimensao, peso)
            (
                1, 1, 'TRPE-S1-Q01',
                'Nas últimas semanas, senti-me triste ou desanimado(a) na escola.',
                'SAUDE_MENTAL', 'MEDIO',
            ),
            (
                1, 2, 'TRPE-S1-Q02',
                'Tenho me sentido ansioso(a) ou preocupado(a) com frequência.',
                'SAUDE_MENTAL', 'ALTO',
            ),
            (
                1, 3, 'TRPE-S1-Q03',
                'Tenho dificuldade para dormir por causa de preocupações.',
                'SAUDE_MENTAL', 'MEDIO',
            ),
            (
                1, 4, 'TRPE-S1-Q04',
                'Já pensei que seria melhor não acordar ou desaparecer.',
                'SAUDE_MENTAL', 'CRITICO',
            ),
            (
                1, 5, 'TRPE-S1-Q05',
                'Tenho me sentido sem esperança em relação ao futuro.',
                'SAUDE_MENTAL', 'ALTO',
            ),
            (
                2, 1, 'TRPE-S2-Q01',
                'Sinto que tenho amigos com quem posso conversar na escola.',
                'ISOLAMENTO', 'PROTETOR',
            ),
            (
                2, 2, 'TRPE-S2-Q02',
                'Me sinto excluído(a) ou ignorado(a) pelos colegas.',
                'ISOLAMENTO', 'ALTO',
            ),
            (
                2, 3, 'TRPE-S2-Q03',
                'Participo de atividades em grupo com tranquilidade.',
                'ISOLAMENTO', 'PROTETOR',
            ),
            (
                2, 4, 'TRPE-S2-Q04',
                'Sinto que os professores se preocupam comigo.',
                'PROTECAO', 'PROTETOR',
            ),
            (
                2, 5, 'TRPE-S2-Q05',
                'Evito ir à escola por causa das pessoas que encontro lá.',
                'ISOLAMENTO', 'ALTO',
            ),
            (
                3, 1, 'TRPE-S3-Q01',
                'Já fui humilhado(a), xingado(a) ou intimidado(a) na escola.',
                'BULLYING', 'ALTO',
            ),
            (
                3, 2, 'TRPE-S3-Q02',
                'Já sofri agressão física na escola (empurrões, tapas, socos).',
                'BULLYING', 'CRITICO',
            ),
            (
                3, 3, 'TRPE-S3-Q03',
                'Já fui excluído(a) de grupos ou atividades de propósito.',
                'BULLYING', 'MEDIO',
            ),
            (
                3, 4, 'TRPE-S3-Q04',
                'Tenho medo de ir à escola por me sentir inseguro(a).',
                'BULLYING', 'ALTO',
            ),
            (
                3, 5, 'TRPE-S3-Q05',
                'Já fui ameaçado(a) por colegas ou outras pessoas na escola.',
                'BULLYING', 'CRITICO',
            ),
            (
                4, 1, 'TRPE-S4-Q01',
                'Tenho alguém em casa com quem posso conversar sobre meus problemas.',
                'PROTECAO', 'PROTETOR',
            ),
            (
                4, 2, 'TRPE-S4-Q02',
                'Minha família percebe quando estou passando por dificuldades.',
                'PROTECAO', 'PROTETOR',
            ),
            (
                4, 3, 'TRPE-S4-Q03',
                'Sei a quem recorrer na escola quando preciso de ajuda.',
                'PROTECAO', 'PROTETOR',
            ),
            (
                4, 4, 'TRPE-S4-Q04',
                'Já me machuquei de propósito ou pensei em me machucar.',
                'SAUDE_MENTAL', 'CRITICO',
            ),
            (
                4, 5, 'TRPE-S4-Q05',
                'Sinto que minha vida tem pessoas que se importam comigo.',
                'PROTECAO', 'PROTETOR',
            ),
        ]

        for secao_ordem, ordem, identificador, texto, dimensao, peso in perguntas:
            Pergunta.objects.create(
                secao=secoes[secao_ordem],
                dimensao=dimensoes[dimensao],
                peso_pergunta=pesos[peso],
                identificador=identificador,
                texto=texto,
                ordem=ordem,
                obrigatoria=True,
                ativa=True,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seed TRPE v1 criada: {len(perguntas)} perguntas em 4 seções.'
        ))
