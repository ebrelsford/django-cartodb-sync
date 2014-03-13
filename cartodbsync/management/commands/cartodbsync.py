from importlib import import_module
from optparse import make_option
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models.loading import get_model


class Command(BaseCommand):
    help = 'Synchronize model data with CartoDB tables'

    option_list = BaseCommand.option_list + (
        make_option('--model',
            action='store',
            type='string',
            dest='model',
        ),
    )

    def handle(self, *args, **options):
        model = options.get('model', None)

        try:
            models = settings.CARTODB_SYNC['MODELS']
            for m in models:
                if model and model != m['MODEL_CLASS']:
                    continue
                self.synchronize(m)
        except Exception:
            traceback.print_exc()
            raise CommandError('There was a problem synchronizing data')

    def get_model(self, model_string):
        return get_model(*model_string.split('.'))

    def get_synchronizer_class(self, synchronizer_string):
        module_name, class_name = synchronizer_string.rsplit('.', 1)
        return getattr(import_module(module_name), class_name)

    def synchronize(self, settings_entry):
        model = self.get_model(settings_entry['MODEL_CLASS'])
        synchronizer_class = self.get_synchronizer_class(settings_entry['SYNCHRONIZER_CLASS'])
        synchronizer = synchronizer_class(model, settings_entry['CARTODB_TABLE'])
        synchronizer.synchronize()
