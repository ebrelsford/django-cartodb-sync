from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.query import QuerySet


class SyncEntryQuerySet(QuerySet):

    def for_model(self, model):
        return self.filter(content_type=ContentType.objects.get_for_model(model))

    def to_synchronize(self):
        return self.filter(status__in=(SyncEntry.PENDING_INSERT,
                                       SyncEntry.PENDING_UPDATE,
                                       SyncEntry.FAIL_RETRY))

    def mark_as_pending_insert(self, instances):
        for instance in instances:
            sync_entry = SyncEntry(
                content_object=instance,
                status=SyncEntry.PENDING_INSERT,
            )
            sync_entry.save()

    def mark_as_pending_update(self):
        return self.update(status=SyncEntry.PENDING_UPDATE)

    def mark_as_success(self):
        return self.update(status=SyncEntry.SUCCESS)

    def mark_as_failed(self):
        for entry in self:
            entry.attempts = entry.attempts + 1
            entry.status = SyncEntry.FAIL_RETRY
            if entry.attempts > 3:
                entry.status = SyncEntry.FAIL
        return self.save()


class SyncEntryManager(models.Manager):

    def get_queryset(self):
        return SyncEntryQuerySet(self.model)

    def __getattr__(self, name):
        return getattr(self.get_queryset(), name)


class SyncEntry(models.Model):
    # The object to be synchronized
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Meta
    PENDING_INSERT = 'pending insert'
    PENDING_UPDATE = 'pending update'
    SUCCESS = 'success'
    FAIL_RETRY = 'fail retry'
    FAIL = 'fail'
    STATUS_CHOICES = (
        (PENDING_INSERT, 'pending insert'),
        (PENDING_UPDATE, 'pending update'),
        (SUCCESS, 'success'),
        (FAIL_RETRY, 'fail retry'),
        (FAIL, 'fail'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True,
                              blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    attempts = models.IntegerField(default=0)

    objects = SyncEntryManager()
