#Python logic behind the views

import datetime

# Django
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django import http
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Template
from django.core.urlresolvers import reverse

#Django plugin
import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.utils import Accessor
#My imports
from models import Part, Manufacturer, PartType, Status, PartLog

# TABLES
class PartT(tables.Table):
    sn = tables.Column(accessor="serial_number", verbose_name="Serial Number", orderable=True)
    p_id = tables.Column(accessor="part_ID_id", verbose_name="Part ID", orderable=True, visible=True)
    status_id = tables.Column(accessor="status_id", verbose_name="Status", orderable=True)
    b_code = tables.Column(accessor="bar_code", verbose_name="Bar Code", orderable=True)
    class Meta:
        order_by_field = True
        attrs = {'class':'paleblue'}

class PartTypeT(tables.Table):
    manufacturer = tables.LinkColumn('trackr.views.manu_detail', args=[Accessor('id')])
    class Meta:
        model = PartType        
        attrs = {'class':'paleblue'}
        
class ManufacturerT(tables.Table):
    # To do...
    class Meta:
        model = Manufacturer
        attrs = {'class':'paleblue'}
        
class PartDetailT(tables.Table):
    class Meta:
        model = PartType        
        
class CurrentCountT(tables.Table):
    part = tables.Column(accessor="name", verbose_name="Part", orderable=True)
    number = tables.Column(accessor="number", verbose_name="Part Number", orderable=True)
    make = tables.Column(accessor="make", verbose_name="Make", orderable=True)
    model = tables.Column(accessor="model", verbose_name="Model", orderable=True)
    #part = tables.LinkColumn('trackr.views.part_detail', args=[Accessor('id')], verbose_name="Part", orderable=True, accessor="name")
    count = tables.Column(accessor="num_parts", verbose_name="Quantity", orderable=True)
    class Meta:
        order_by_field = True
        attrs= {'class':'paleblue'}

class PartLogT(tables.Table):
    class Meta:
        order_by_field = True
        model = PartLog
        attrs = {'class':'paleblue'}
        exclude = ("id","part")
        
class PartLogTT(tables.Table):
    part_type = tables.Column(accessor='part.type', verbose_name="Type", orderable=True)
    class Meta:
        order_by_field = True
        model = PartLog
        attrs = {'class':'paleblue'}
        exclude = ('pk','id','part')
        sequence = ('part_type','time_stamp','old_status','new_status')
        