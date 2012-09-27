#Python logic behind the views


# Django
from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django import http
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import signals
from django.dispatch import dispatcher
from django.forms.models import modelformset_factory, inlineformset_factory
from django.forms.formsets import formset_factory
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.formtools.preview import FormPreview
import ipdb
# My imports
from models import Part, Manufacturer, PartType, Status, PartLog
from forms import AfterF,EasyPartForm, PartLogSearchForm, PartUploadFileForm, BasePartForm, PartForm, CheckOutPartForm, PartTypeForm, BasePartFormSet, BaseEasyPartFormSet
from tables import PartT, ManufacturerT, CurrentCountT, PartTypeT, PartLogT
from signals import log_entry

# Django plugins
import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.utils import Accessor


class PartPreview(FormPreview):

    def done(self, request, cleaned_data):
        part_list=[] # For now this is only to determine how many "extra" forms are needed
        form_collection = []
        typez = None
        data = self.cleaned_data
        parts = data.get('parts',None) #Bar_codes of parts
        typez = data.get('type', None)
        # Parsing textarea box for barcode scanner input
        for part in parts.splitlines():
            form_collection.append({typez:part})
            
        extra_forms = len(part_list) #Defining the # of extra forms needed for the modelformset
        
        
        return render_to_response('/form/success', )
         
        