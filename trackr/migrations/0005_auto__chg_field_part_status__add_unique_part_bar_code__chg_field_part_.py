# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'Part.status'
        db.alter_column('trackr_part', 'status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.StatusType']))

        # Adding unique constraint on 'Part', fields ['bar_code']
        db.create_unique('trackr_part', ['bar_code'])

        # Changing field 'Part.part_ID'
        db.alter_column('trackr_part', 'part_ID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.PartType']))

        # Changing field 'PartLog.time_stamp'
        db.alter_column('trackr_partlog', 'time_stamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))

        # Changing field 'PartLog.old_status'
        db.alter_column('trackr_partlog', 'old_status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.StatusType']))

        # Changing field 'PartLog.part_ID'
        db.alter_column('trackr_partlog', 'part_ID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.Part']))

        # Changing field 'PartLog.new_status'
        db.alter_column('trackr_partlog', 'new_status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.StatusType']))

        # Changing field 'PartType.manufacturer'
        db.alter_column('trackr_parttype', 'manufacturer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.Manufacturer']))
    
    
    def backwards(self, orm):
        
        # Changing field 'Part.status'
        db.alter_column('trackr_part', 'status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.statusType']))

        # Removing unique constraint on 'Part', fields ['bar_code']
        db.delete_unique('trackr_part', ['bar_code'])

        # Changing field 'Part.part_ID'
        db.alter_column('trackr_part', 'part_ID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.partType']))

        # Changing field 'PartLog.time_stamp'
        db.alter_column('trackr_partlog', 'time_stamp', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'PartLog.old_status'
        db.alter_column('trackr_partlog', 'old_status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.statusType']))

        # Changing field 'PartLog.part_ID'
        db.alter_column('trackr_partlog', 'part_ID_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.part']))

        # Changing field 'PartLog.new_status'
        db.alter_column('trackr_partlog', 'new_status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.statusType']))

        # Changing field 'PartType.manufacturer'
        db.alter_column('trackr_parttype', 'manufacturer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trackr.manufacturer']))
    
    
    models = {
        'trackr.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.IntegerField', [], {})
        },
        'trackr.part': {
            'Meta': {'object_name': 'Part'},
            'bar_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part_ID': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.PartType']"}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.StatusType']"})
        },
        'trackr.partlog': {
            'Meta': {'object_name': 'PartLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'new_status_related'", 'to': "orm['trackr.StatusType']"}),
            'old_status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old_status_related'", 'to': "orm['trackr.StatusType']"}),
            'part_ID': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.Part']"}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'trackr.parttype': {
            'Meta': {'object_name': 'PartType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'make': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['trackr.Manufacturer']"}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'trackr.statustype': {
            'Meta': {'object_name': 'StatusType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }
    
    complete_apps = ['trackr']
