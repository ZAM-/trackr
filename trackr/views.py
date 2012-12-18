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
from django.contrib.formtools.wizard.views import SessionWizardView
from django.template import Context 

import ipdb
# My imports
from models import Part, Manufacturer, PartType, Status, PartLog
from forms import AreaCheckOut,TextAreaForm, PartLogSearchForm, PartUploadFileForm, BasePartForm, PartForm, CheckOutPartForm, PartTypeForm, BasePartFormSet, BaseEasyPartFormSet
from tables import PartT, ManufacturerT, CurrentCountT, PartTypeT, PartLogT, PartLogTT
from signals import log_entry

# Django plugins
import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.utils import Accessor


# VIEWS 
def index(request):
    return render(request,'base.html')
def search_log(request):
    errlst=[]
    c = {}
    c.update(csrf(request))
    
    
    if request.method == "GET":
        form = PartLogSearchForm(request.GET)
        get_recent = PartLog.objects.all()
        data=list(get_recent)

        table_LOD = PartLogTT(data[-10:])
        RequestConfig(request).configure(table_LOD)

        if form.is_valid():
            part = form.cleaned_data['bar_code']
            # Getting QS ID of the Part by searching on bar_code
            try:
                get_partID = Part.objects.get(bar_code=part).id
            except Part.DoesNotExist:
                errlst.append("Part with bar_code %s does not exist." % part)
                # Getting QS of all log entries by searching on part_id
            else:
                get_logs = PartLog.objects.filter(part_id=get_partID)
                # Preparing data for table
                data=list(get_logs)
                table_LOD = PartLogT(data)
                RequestConfig(request).configure(table_LOD)
                return render(request,'tables.html',{'table': table_LOD})
    else:
        form = PartLogSearchForm()

    return render(request, 'part_log.html',{
                                               'table': table_LOD, 
                                               'title':'Remove Item',
                                               'form': form,
                                               'errors': errlst,
                                               })
def part_table(request):
    data = Part.objects.all() # QuerySet object list(dict())
    parts_LOD = PartT(data) # Table instance
    RequestConfig(request).configure(parts_LOD)
    return render(request,'tables.html',{'table': parts_LOD})

# Definition of all part types (Part #, Name, Make, Model, Manu)
def part_type_table(request):
    data = list(PartType.objects.all())
    types_LOD = PartTypeT(data)
    RequestConfig(request).configure(types_LOD)
    return render(request,'tables.html',{'table': types_LOD})
def manu_detail(request, manu_id):
    # add logic statement to find out what company details need to be displayed.
    # Capturing instance of manufacturer name from partType ID
    get_part_id = PartType.objects.get(id=manu_id).manufacturer
    
    # Using the ID to filter out the correct manufacturer details
    # and match on the exact company 
    data = Manufacturer.objects.filter(company__exact=get_part_id)
    manu_LOD = ManufacturerT(data)
    RequestConfig(request).configure(manu_LOD)
    return render(request,'tables.html', {'table': manu_LOD})

# View of all current parts with status type ('CI')
# ONLY displays part and part count        
def part_count(request):
    # Getting all parts that have a status ID of 3 or ('CI')
    # Casting the query set type to a list so it doesn't query 11 times.
    #data = [{'name':'bob', 'num_parts':3}]
    data = list(PartType.objects.filter(part__status=3L).annotate(num_parts=Count('part'
)).values('name','num_parts','number','make','model'))
    count_LOD = CurrentCountT(data)
    RequestConfig(request).configure(count_LOD)
    return render(request, 'tables.html', {'table': count_LOD})    

# Currently not using this function due to the fact that users can 
# either update existing entries. 
# I have not got the functionality to work with more than one entry.
def check_in_or_update_part(request):
    errlst=[]
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        # Testing if Part() object exists
        try:    
            # Setting the part to pass as instance to form
            part = Part.objects.get(bar_code=request.POST.get('bar_code'))
        except Part.DoesNotExist:
            # Creating form with POST data & new row in part table
            myPart = Part(type=PartType(1), bar_code='') #Blank Part entry
            form = PartForm(request.POST, instance=myPart)
        else:
            # Create form with part instance
            # Updating part row with POST data-->most likely new status
            form = PartForm(request.POST, instance=part)
        if form.is_valid() and form.instance.check_in() == False:
            
            form.save(commit=True)
            sn = form.cleaned_data['bar_code']
            status = form.cleaned_data['status']
            messages.success(request,"bar code %s has been successfully %s!" % (sn,status))
        else:
            messages.ERROR(request,"Part is already checked in!")
            return http.HttpResponseRedirect('')   
    else:        
        form = PartForm(initial={'status': Status(3),'type':PartType(1)})
        
        
    return render(request,'add_part.html',{
                                           'title':'Add Item',
                                           'form': form,
                                           'errlist': errlst
                                           })


# Checking out a part    
def check_out_part(request):
    errlst = []
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = AreaCheckOut(request.POST)
        if form.is_valid():
            if "_preview" in request.POST:
                template_name = "preview_co.html"
                f_scans, v_scans, iv_scans = form.pre_process()

                c['f_scans'] = f_scans
                c['v_scans'] = v_scans
                c['iv_scans'] = iv_scans
                c['form'] = form
                
                return render(request,template_name,c)
            elif "_save" in request.POST:
                template_name = "save_co.html"
                f_scans, v_scans, iv_scans = form.post_process() #Table transactions
                
                c['f_scans'] = f_scans
                c['v_scans'] = v_scans
                c['iv_scans'] = iv_scans
                c['form'] = form
                
                return render(request,template_name,c)
                
    else:
        form = AreaCheckOut()
        # Adding default status to Check Out or "CO"
    return render(request, 'save_co.html',{
                                               'title':'Remove Item',
                                               'form': form,
                                               'errors': errlst,
                                               })
def add_part_type(request):
    
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = PartTypeForm(request.POST)
        if form.is_valid():
            form.save()

        print "ITEMS"
        print request.session.items()
        return http.HttpResponseRedirect('/check_in/multiple/')    
    else:
        form = PartTypeForm()
        
    return render(request, 'add_type.html',{
                                                 'title':'Add Part Type',
                                                 'form': form
                                                 })
def file_upload(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = PartUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.process() # Processing the form
            
            
    else:
        form = PartUploadFileForm(initial = {'status': Status(3)})
        
    return render(request, 'file_upload.html', {
                                                'form':form})


# This view will display a basic form with two fields: Type and Bar_Codes
# After accpeting the input, it will take all the data and create a 
# formset with each bar_code entered as a form. Which 'should' allow for seperate validation
# Restrictions: Only one part type can be proccessed at a time.
def test_text_area(request):
    c = Context()
    c.update(csrf(request))
    template_name= 'test.html'
    if request.method == "POST":
        form = TextAreaForm(request.POST)
        if form.is_valid():
            if '_preview' in request.POST:
                #Creating seperate 
                template_name = 'preview.html'
                #Don't save the post, just updating the context
                #The Context is v_scans, and iv_scans, so I render them in the preview
                filtered_scans, v_scans, iv_scans = form.pre_process()
                
                c['v_scans'] = v_scans
                c['iv_scans'] = iv_scans
                c['f_scans'] = filtered_scans
                c['type_count'] = form.process_count(v_scans)
                c['form'] = form
                
                
                return render(request,template_name,c)
                
            elif '_save' in request.POST:
                template_name = 'save.html'
                #Save the post
                #I'm still updating the context so I can inform the user of what scanned bc's were actually saved to the database.
                filtered_scans, v_scans, iv_scans = form.pre_process()
                form.post_process(v_scans)
                
                c['v_scans'] = v_scans
                c['iv_scans'] = iv_scans
                c['type_count'] = form.process_count(v_scans)
                c['form'] = form
                
                return render(request,template_name,c)
    else:
        form = TextAreaForm(initial={'status':Status(3)})

    c['form'] = form
    return render(request,template_name,c)

#FIXME: duplicate entries only returns one instance of bc

