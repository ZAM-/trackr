# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'partLog.part_ID'
        db.alter_column('trackr_partlog', 'part_ID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.partType']))
    
    
    def backwards(self, orm):
        
        # Changing field 'partLog.part_ID'
        db.alter_column('trackr_partlog', 'part_ID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.part']))
    
    
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
