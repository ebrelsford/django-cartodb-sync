from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from cartodb import CartoDBAPIKey, CartoDBException

from .models import SyncEntry


class BaseSynchronizer(object):
    """
    The base class for synchronizing a model with a CartoDB table.

    The general outline for this process is:
    * Get model instances to synchronize
    * Synchronize using
    * Mark as not needing to be synchronized anymore

    INSERT and UPDATE statements inspired by:
     http://blog.cartodb.com/post/53301057653/faster-data-updates-with-cartodb
    """

    def __init__(self, model, cartodb_table, batch_size=500):
        self.model = model
        self.cartodb_table = cartodb_table
        self.batch_size = batch_size

    def synchronize(self):
        entries = self.get_entries_to_synchronize()
        try:
            self.synchronize_entries(entries)
            self.mark_as_success(entries)
        except Exception as e:
            print 'Exception while synchronizing:', e
            # Assume none of them were updated
            self.mark_as_failed(entries)

    def get_entries_to_synchronize(self):
        entries = SyncEntry.objects.for_model(self.model).to_synchronize()
        entries = entries.order_by('-updated')
        if entries.count() > self.batch_size:
            entries = entries[:self.batch_size]
        return entries

    def synchronize_entries(self, entries):
        deletes = []
        inserts = []
        updates = []
        for entry in entries:
            cartodb_mapping = self.get_cartodb_mapping(entry.content_object)
            if entry.status == SyncEntry.PENDING_DELETE:
                deletes.append(cartodb_mapping)
            if entry.status == SyncEntry.PENDING_INSERT:
                inserts.append(cartodb_mapping)
            if entry.status == SyncEntry.PENDING_UPDATE:
                updates.append(cartodb_mapping)

        if deletes:
            # TODO delete statement for CartoDB, execute
            pass

        if inserts:
            insert_statement = self.get_insert_statement(inserts)
            cl = CartoDBAPIKey(settings.CARTODB_SYNC['API_KEY'],
                               settings.CARTODB_SYNC['DOMAIN'])
            try:
                print cl.sql(insert_statement)
            except CartoDBException as e:
                print ("some error ocurred", e)

        if updates:
            # TODO update statement for CartoDB, execute
            pass

    def format_value(self, value):
        if isinstance(value, (int, float, long, complex)):
            return str(value)
        if isinstance(value, GEOSGeometry):
            return "'%s'" % value.ewkt
        return "'%s'" % str(value)

    def get_column_names(self):
        raise NotImplementedError('Implement get_column_names')

    def get_cartodb_mapping(self, instance):
        # TODO something very basic by default?
        raise NotImplementedError('Implement get_cartodb_mapping')

    def get_insert_statement(self, insert_instances):
        """
        Consolidate the given instances into one large and efficient insert
        statement.

        INSERT INTO <table name> (<column names>) VALUES <values>
        """
        column_names = self.get_column_names()
        values = []
        for instance in insert_instances:
            formatted_values = [self.format_value(instance[c]) for c in column_names]
            values.append(','.join(formatted_values))

        sql = 'INSERT INTO %s (%s) VALUES %s' % (
            self.cartodb_table,
            ','.join(column_names),
            ','.join(['(%s)' % v for v in values]),
        )
        return sql

    def get_update_statement(self, update_instances):
        """
        Consolidate the given instances into one large and efficient update
        statement.

        UPDATE <table name> o
        SET <column 1>=n.<column 1>, <column 2>=n.<column 2>
        FROM (VALUES
            (<values in order for row 1>),
            (<values in order for row 2>),
            (<values in order for row 3>)
        ) n(id, <column 1>, <column 2>)
        WHERE o.id = n.id;
        """
        sql = 'UPDATE %s o SET %s FROM (VALUES %s) n(%s) WHERE o.id = n.id' % (
            self.cartodb_table,
            # TODO implement
            'set equations',
            'set values',
            'column names',
        )
        return sql

    def mark_as_success(self, entries):
        entries.mark_as_success()

    def mark_as_failed(self, entries):
        entries.mark_as_failed()
