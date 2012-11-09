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
from forms import TextAreaForm, MyFormStep0, MyFormStep1,EasyPartForm, PartLogSearchForm, PartUploadFileForm, BasePartForm, PartForm, CheckOutPartForm, PartTypeForm, BasePartFormSet, BaseEasyPartFormSet
from tables import PartT, ManufacturerT, CurrentCountT, PartTypeT, PartLogT
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
        # Testing if part row exists
        try:    
            # Setting the part to pass as instance to form
            part = Part.objects.get(bar_code=request.POST.get('bar_code'))
        except Part.DoesNotExist:
            # Creating form with POST data
            # Creating new row in part table
            form = PartForm(request.POST)
        else:
            # Create form with part instance
            # Updating part row with POST data-->most likely new status
            form = PartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            type = form.cleaned_data['type'].name
            sn = form.cleaned_data['bar_code']
            status = form.cleaned_data['status']
            messages.success(request,"%s with bar code %s has been successfully %s!" % (type,sn,status))
            return http.HttpResponseRedirect('')   
    else:        
        form = PartForm(initial={'serial_number':'placeholder','status': Status(3)})
        
        
    return render(request,'add_part.html',{
                                           'title':'Add Item',
                                           'form': form,
                                           'errlist': errlst
                                           })

def mass_check_in(request):
    # queryset
    qs = Part.objects.none()
    errlst=[]
    c = {}
    c.update(csrf(request))
    # Creating a model_formset out of PartForm
    PartFormSetFactory = modelformset_factory(model=Part,
                                              form=PartForm, #Calls validation
                                              formset=BasePartFormSet, 
                                              extra=2)
    if request.method == 'POST':
        PartFormSet = PartFormSetFactory(request.POST)
        if PartFormSet.is_valid():
            PartFormSet.save(commit=True)
            return http.HttpResponse('/current_count/')

    else:        
        PartFormSet = PartFormSetFactory(queryset=qs, initial=[{'serial_number':'placeholder'},
                                                               {'serial_number':'placeholder'},
                                                                ]) 
    return render(request,'dynamic_formsets.html',{
                                                   'title':'Add Item',
                                                   'formset': PartFormSet,
                                                   'formset_errors': PartFormSet.non_form_errors(),
                                                   })
# Checking out a part    
def check_out_part(request):
    errlst = []
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = CheckOutPartForm(request.POST)
        if form.is_valid():
            bar_code_form = form.cleaned_data['bar_code']
            #FIXME: Move below validation to the form's clean method
            try:
                bar_code_model= Part.objects.get(bar_code=bar_code_form)
            except Part.DoesNotExist:
                errlst.append("Part with bar_code %s does not exist." % bar_code_form)
            else:
                if bar_code_model.check_out() == True:
                    bar_code_model.save()
                    messages.success(request,"%s with bar code %s has been successfully checked out!" % (bar_code_model.type,bar_code_model.bar_code))
                else:
                    messages.error(request, "This part is already checked out")
                
                return http.HttpResponseRedirect('')
    else:
        form = CheckOutPartForm()
        # Adding default status to Check Out or "CO"
    return render(request, 'remove_part.html',{
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
        return http.HttpResponseRedirect('/check_in/')    
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

def easy_check_in(request):
    errlst = []
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = EasyPartForm(request.POST)
        if form.is_valid():
            # Processing the form creating the Part() object, and assigning it's neccessary attributes
            # Attributes include Type and Serial_Number,
            part_instance = form.process() # Actual Part() object
            type = part_instance.type
            bar_code = part_instance.bar_code
            part_instance.save()
            # Returns empty form and new 'success' message
            messages.success(request,"%s with bar code %s has been successfully added!" % (type,bar_code))
            return http.HttpResponseRedirect('')
    else:
        form = EasyPartForm(initial={'status':Status(3)})
   
    return render(request, 'easy_check_in.html', {
                                                'form':form})         
        
def easy_many_check_in(request):
    c = {}
    c.update(csrf(request))
    PartFormSetFactory = formset_factory(form=EasyPartForm,
                                         formset=BaseEasyPartFormSet,
                                         extra=2)
    if request.method == 'POST':
        PartFormSet = PartFormSetFactory(request.POST)
        if PartFormSet.is_valid():
            PartFormSet.process()
            return http.HttpResponseRedirect('/current_count/')
    else:
        PartFormSet = PartFormSetFactory()
        
    return render(request, 'test_dynamic.html', {
                                                 'title':'Add Item',
                                                 'formset': PartFormSet})


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
                v_scans, iv_scans = form.pre_process()
                c['v_scans'] = v_scans
                c['iv_scans'] = iv_scans
                c['form'] = form
                return render(request,template_name,c)
                
            elif '_save' in request.POST:
                template_name = 'save.html'
                #Save the post
                #I'm still updating the context so I can inform the user of what scanned bc's were actually saved to the database.
                v_scans, iv_scans = form.pre_process()
                c['v_scans'] = v_scans
                c['iv_scans'] = iv_scans
                c['form'] = form
                form.post_process(v_scans)
                
                return render(request,template_name,c)
    else:
        form = TextAreaForm(initial={'status':Status(3)})

    c['form'] = form
    return render(request,template_name,c)

def text_area_check_in(request):
    c = Context()
    message_list = []
    c.update(csrf(request))
    if request.method == "POST":
        form = TextAreaForm(request.POST)
        if form.is_valid():
            v_scans, iv_scans = form.pre_process()
            # Counting occurances of each valid and invalid scans E.G. {'PartType':'quantity'}
            # Used for messaging system for User notification
            c['v_scans'] = v_scans
            c['iv_scans'] = iv_scans
            c['form'] = form
            return render(request, 'area_check_in.html', c)        
    else:
        form = TextAreaForm(initial={'status':Status(3)})
        
    c['form'] = form

    return render(request,'area_check_in.html',c)

class SuperSoftWizard(SessionWizardView):
    def get_context_data(self, form, **kwargs):
        # Used to supply extra context data to be passed to the template
        # Allows to display pieces of data at a particular step
        context = super(SuperSoftWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == "0":
            context.update({'var': "Hello"})
        
        return context
    
    def process_step(self, form):
        # Used to perform extra work before the data gets stored within
        # the storage backend. Data should NOT be manipulated here

        # Getting ALL existing types
        all_types = PartType.objects.values('name','number')
        
        if self.steps.current == "0":
            a = form.data.getlist('0-parts', None) # list
            for items in a:
                print items
        else:
            return None
        
        return self.get_form_step_data(form)
        
    """def get_form_step_data(self, form=MyFormStep0):
        print form.data.items()
        return form.data    
    """
    
    def done(self, form_list, **kwargs):
        

        return http.HttpResponseRedirect('/post/')
