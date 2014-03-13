from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.query import QuerySet


class SyncEntryQuerySet(QuerySet):

    def for_model(self, model):
        return self.filter(content_type=ContentType.objects.get_for_model(model))

    def to_synchronize(self):
        return self.filter(status__in=(SyncEntry.PENDING_DELETE,
                                       SyncEntry.PENDING_INSERT,
                                       SyncEntry.PENDING_UPDATE))

    def mark_as_pending_delete(self, instances):
        sync_entries = []
        for instance in instances:
            sync_entries.append(SyncEntry(
                object_id=instance.pk,
                status=SyncEntry.PENDING_DELETE,
            ))
        self.bulk_create(sync_entries)

    def mark_as_pending_insert(self, instances):
        sync_entries = []
        for instance in instances:
            sync_entries.append(SyncEntry(
                content_object=instance,
                status=SyncEntry.PENDING_INSERT,
            ))
        self.bulk_create(sync_entries)

    def mark_as_pending_update(self):
        return self.update(status=SyncEntry.PENDING_UPDATE)

    def mark_as_success(self):
        # Need to fetch entries again rather than use self since it has likely
        # been sliced
        pks = [e.pk for e in self]
        SyncEntry.objects.filter(pk__in=pks).update(status=SyncEntry.SUCCESS)

    def mark_as_failed(self):
        for entry in self:
            entry.attempts = entry.attempts + 1
            if entry.attempts > 3:
                entry.status = SyncEntry.FAIL
            entry.save()


class SyncEntryManager(models.Manager):

    def get_queryset(self):
        return SyncEntryQuerySet(self.model)

    def __getattr__(self, name):
        return getattr(self.get_queryset(), name)


class SyncEntry(models.Model):
    # The object to be synchronized
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Meta
    PENDING_DELETE = 'pending delete'
    PENDING_INSERT = 'pending insert'
    PENDING_UPDATE = 'pending update'
    SUCCESS = 'success'
    FAIL = 'fail'
    STATUS_CHOICES = (
        (PENDING_DELETE, 'pending delete'),
        (PENDING_INSERT, 'pending insert'),
        (PENDING_UPDATE, 'pending update'),
        (SUCCESS, 'success'),
        (FAIL, 'fail'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True,
                              blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    attempts = models.IntegerField(default=0)

    objects = SyncEntryManager()
