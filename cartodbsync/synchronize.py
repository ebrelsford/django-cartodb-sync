from importlib import import_module

from django.apps import apps
from django.conf import settings


def get_model(model_string):
    return apps.get_model(*model_string.split('.'))


def get_synchronizer_class(synchronizer_string):
    module_name, class_name = synchronizer_string.rsplit('.', 1)
    return getattr(import_module(module_name), class_name)


def synchronize_settings_entry(settings_entry):
    model = get_model(settings_entry['MODEL_CLASS'])
    synchronizer_class = get_synchronizer_class(settings_entry['SYNCHRONIZER_CLASS'])
    synchronizer = synchronizer_class(model, settings_entry['CARTODB_TABLE'])
    synchronizer.synchronize()


def synchronize(model_name=None):
    for m in settings.CARTODB_SYNC['MODELS']:
        if model_name and model_name != m['MODEL_CLASS']:
            continue
        else:
            synchronize_settings_entry(m)
