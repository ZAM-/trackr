# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'manufacturer'
        db.create_table('trackr_manufacturer', (
            ('phone', self.gf('django.db.models.fields.IntegerField')()),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal('trackr', ['manufacturer'])

        # Adding model 'statusType'
        db.create_table('trackr_statustype', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('trackr', ['statusType'])

        # Adding model 'partType'
        db.create_table('trackr_parttype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('make', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.manufacturer'])),
        ))
        db.send_create_signal('trackr', ['partType'])

        # Adding model 'part'
        db.create_table('trackr_part', (
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.statusType'])),
            ('bar_code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('part_ID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.partType'])),
            ('serial_number', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('trackr', ['part'])

        # Adding model 'partLog'
        db.create_table('trackr_partlog', (
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('old_status', self.gf('django.db.models.fields.related.ForeignKey')(related_name='old', to=orm['trackr.statusType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('part_ID', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.partType'])),
            ('new_status', self.gf('django.db.models.fields.related.ForeignKey')(related_name='new', to=orm['trackr.statusType'])),
        ))
        db.send_create_signal('trackr', ['partLog'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'manufacturer'
        db.delete_table('trackr_manufacturer')

        # Deleting model 'statusType'
        db.delete_table('trackr_statustype')

        # Deleting model 'partType'
        db.delete_table('trackr_parttype')

        # Deleting model 'part'
        db.delete_table('trackr_part')

        # Deleting model 'partLog'
        db.delete_table('trackr_partlog')
    
    
    models = {
        'trackr.manufacturer': {
            'Meta': {'object_name': 'manufacturer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {})
        },
        'trackr.part': {
            'Meta': {'object_name': 'part'},
            'bar_code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part_ID': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.partType']"}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.statusType']"})
        },
        'trackr.partlog': {
            'Meta': {'object_name': 'partLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new'", 'to': "orm['trackr.statusType']"}),
            'old_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old'", 'to': "orm['trackr.statusType']"}),
            'part_ID': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.partType']"}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'trackr.parttype': {
            'Meta': {'object_name': 'partType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'make': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.manufacturer']"}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'trackr.statustype': {
            'Meta': {'object_name': 'statusType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }
    
    complete_apps = ['trackr']
