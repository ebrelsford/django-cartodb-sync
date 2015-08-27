django-cartodb-sync
===================

A Django app that helps keep `CartoDB`_ tables synchronized with Django models.


Requirements
------------

Django >= 1.8, `cartodb-python`_, a CartoDB account.


Installation
------------

Use pip.

Add to ``INSTALLED_APPS``::

    INSTALLED_APPS += (
        'cartodbsync',
    )

Then add the appropriate configuration details to your ``settings``.

You will need some way of letting ``django-cartodb-sync`` about instances that
need to be inserted, updated, or deleted. The simplest way is to use `signals`_
and the ``SyncEntry`` methods ``mark_as_pending_delete``,
``mark_as_pending_insert``, and ``mark_as_pending_update``.

Finally, configure a cron job to run the ``cartodbsync`` management command.
If you have existing model instances, mark all for insertion by running::

    django-admin.py cartodbsync --markinsert


Configuration
-------------

Add the following to your ``settings``::

    CARTODB_SYNC = {
        'API_KEY': '<your api key>',
        'DOMAIN': '<your CartoDB domain>',
        'MODELS': [
            {
                'CARTODB_TABLE': '<model CartoDB table>',
                'MODEL_CLASS': '<example.Model>',
                'SYNCHRONIZER_CLASS': '<example.Synchronizer>',
            }
        ]
    }

Everything between ``<`` and ``>`` should be replaced with appropriate details.
You can list as many models as you like within the ``MODELS`` entry.


.. _`CartoDB`: http://cartodb.com/
.. _`cartodb-python`: https://github.com/vizzuality/cartodb-python
.. _`signals`: https://docs.djangoproject.com/en/1.8/topics/signals/
