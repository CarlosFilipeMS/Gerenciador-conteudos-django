import uuid

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet que filtra registros não deletados por padrão."""

    def delete(self):
        """Realiza soft delete em lote."""
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """Remove fisicamente os registros do banco."""
        return super().delete()


class SoftDeleteManager(models.Manager):
    """Manager que retorna apenas registros ativos (não deletados)."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )


class AllObjectsManager(models.Manager):
    """Manager que retorna todos os registros, incluindo deletados."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class BaseModel(models.Model):
    """
    Model abstrato base para todas as entidades do domínio.

    Fornece UUID como PK, timestamps de auditoria e soft delete.
  """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Realiza soft delete setando deleted_at."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self, using=None, keep_parents=False):
        """Remove fisicamente o registro do banco."""
        return super().delete(using=using, keep_parents=keep_parents)
