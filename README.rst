django-cartodb-sync
===================

A Django app that helps keep `CartoDB`_ tables synchronized with Django models.

Requirements
------------

Django >= 1.6.2, `cartodb-python`_, a CartoDB account.

Installation
------------

Use pip.

Add to ``INSTALLED_APPS``::

    INSTALLED_APPS += (
        'cartodbsync',
    )

Then add the appropriate configuration details to your ``settings``.

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
