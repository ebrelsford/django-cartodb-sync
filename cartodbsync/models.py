from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet


class SyncEntryQuerySet(QuerySet):

    def for_model(self, model):
        return self.filter(content_type=ContentType.objects.get_for_model(model))

    def to_synchronize(self):
        return self.filter(status__in=(SyncEntry.PENDING_DELETE,
                                       SyncEntry.PENDING_INSERT,
                                       SyncEntry.PENDING_UPDATE))

    def mark_as_status(self, instances, status):
        sync_entries = []
        for instance in instances:
            sync_entries.append(SyncEntry(content_object=instance, status=status))
        self.bulk_create(sync_entries)

    def mark_as_pending_delete(self, instances):
        # Delete other entries for these instances since they'll be deleted
        # soon anyway. Also potentially an error if the synchronizer will
        # attempt to access instances that no longer exist due to deletion.
        self.filter(object_id__in=[i.pk for i in instances]).delete()

        self.mark_as_status(instances, SyncEntry.PENDING_DELETE)

    def mark_as_pending_insert(self, instances):
        self.mark_as_status(instances, SyncEntry.PENDING_INSERT)

    def mark_as_pending_update(self, instances):
        # Delete other update entries for these instances
        pks = [instance.pk for instance in instances]
        self.filter(object_id__in=pks, status=SyncEntry.PENDING_UPDATE).delete()

        # Now add update entries for these instances
        self.mark_as_status(instances, SyncEntry.PENDING_UPDATE)

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
    content_object = GenericForeignKey('content_type', 'object_id')

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
