from optparse import make_option
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...models import SyncEntry
from ...synchronize import synchronize


class Command(BaseCommand):
    help = 'Synchronize model data with CartoDB tables'

    option_list = BaseCommand.option_list + (
        make_option('--model',
            action='store',
            type='string',
            dest='model',
        ),
        make_option('--markinsert',
            action='store_true',
            dest='mark_insert',
        ),
    )

    def handle(self, *args, **options):
        model_name = options.get('model', None)
        mark_insert = options.get('mark_insert', False)

        try:
            if mark_insert:
                for m in settings.CARTODB_SYNC['MODELS']:
                    self.mark_all_as_pending_insert(m)
            else:
                synchronize(model_name=model_name)
        except Exception:
            traceback.print_exc()
            raise CommandError('There was a problem synchronizing data')

    def mark_all_as_pending_insert(self, settings_entry):
        model = self.get_model(settings_entry['MODEL_CLASS'])
        SyncEntry.objects.mark_as_pending_insert(model.objects.all())
