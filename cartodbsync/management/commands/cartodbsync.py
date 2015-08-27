from importlib import import_module
from optparse import make_option
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

from ...models import SyncEntry


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
        model = options.get('model', None)
        mark_insert = options.get('mark_insert', False)

        try:
            models = settings.CARTODB_SYNC['MODELS']
            for m in models:
                if model and model != m['MODEL_CLASS']:
                    continue

                if mark_insert:
                    self.mark_all_as_pending_insert(m)
                    continue
                else:
                    self.synchronize(m)
        except Exception:
            traceback.print_exc()
            raise CommandError('There was a problem synchronizing data')

    def mark_all_as_pending_insert(self, settings_entry):
        model = self.get_model(settings_entry['MODEL_CLASS'])
        SyncEntry.objects.mark_as_pending_insert(model.objects.all())

    def get_model(self, model_string):
        return apps.get_model(*model_string.split('.'))

    def get_synchronizer_class(self, synchronizer_string):
        module_name, class_name = synchronizer_string.rsplit('.', 1)
        return getattr(import_module(module_name), class_name)

    def synchronize(self, settings_entry):
        model = self.get_model(settings_entry['MODEL_CLASS'])
        synchronizer_class = self.get_synchronizer_class(settings_entry['SYNCHRONIZER_CLASS'])
        synchronizer = synchronizer_class(model, settings_entry['CARTODB_TABLE'])
        synchronizer.synchronize()
