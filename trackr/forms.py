
#python libs
import datetime
from collections import defaultdict

# Django
from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.formsets import formset_factory
from django.forms import TextInput, ModelForm, Form, HiddenInput, ModelChoiceField
from django.core.exceptions import ValidationError
from django import http
from django.shortcuts import render, render_to_response
from django.contrib.formtools.preview import FormPreview

#Django plugin
import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.utils import Accessor
 
#My imports
from models import Part, PartType, PartLog, Status

# MODELFORMS
class PartTypeForm(ModelForm):
    class Meta:
        model = PartType

class BasePartForm(ModelForm):
    # Creating a modelform for other forms to inherit from BasePartForm
    # to test other cleaning methods in BasePartForm
    # 
    """
    def __init__(self, *args, **kwargs):
        # Overloading the forms fields to properly display 
        super(PartForm, self).__init__(*args, **kwargs)
        current_status = (
                            (u'CO', u'Checked out'),
                            (u'CI', u'Checked in'),
                            (u'RM', u'Returned for RMA'),
                            (u'IU', u'Currently in use'),     
                            )
        self.fields['status'].choices = current_status
    """
    
    class Meta(ModelForm):
        model = Part

# Base Form
class BasePartFormSet(BaseModelFormSet):
    # For formsets and multiple added entries.    
    def __init__(self, *args, **kwargs):
        super(BasePartFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            
    # Form to form validation        
    def clean(self):
        if any(self.errors):
            return
        sns=[]
        # Checking for duplicate barcodes to be submitted
        for i in range(0,self.total_form_count()):
            form = self.forms[i]
            sn = form.cleaned_data['bar_code']
            if sn in sns:
                raise forms.ValidationError("Error: You cannot submit two of the same serial numbers")
            else:
                print "Checking if %s for duplicates between each form" % sn
                sns.append(sn)

class PartForm(BasePartForm):
# Views -- check_in_or_update_part()
#          check_in_part()
    class Meta:
        model = Part
        exclude = ('serial_number','type')
        widgets = {
                   'bar_code': TextInput(attrs={'size': 30}), # Making text box bigger 
                   #'serial_number': HiddenInput(attrs={'value':''}),
                   #'type': HiddenInput(attrs={'value':''}), 
                   }
     
    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(PartForm, self).save(commit=False)
        results = []
        
        cleaned_data = self.cleaned_data
        bar_code = cleaned_data.get('bar_code')
        serial_number = cleaned_data.get('serial_number')
        typez = cleaned_data.get('type')
        status = cleaned_data.get('status')
        all_types = PartType.objects.values('name','number')
        
        for types in all_types:
            if types['number'] in bar_code:
                m.type=PartType.objects.get(number=types['number'])
                m.serial_number=bar_code.replace(types['number'],'')
                m.save()
            else:
                pass
    

# Base Formset
class BaseEasyPartFormSet(BaseFormSet):
# Views -- easy_mass_check_in()    
    """def __init__(self, *args, **kwargs):
        super(BaseEasyPartFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            
    """
    def process(self):
        # Getting ALL existing types
        all_types = PartType.objects.values('name','number') #LOD
        for item in range(0, self.total_form_count()):
            form = self.forms[item]
            bar_code = form.cleaned_data['bar_code']
            status = form.cleaned_data['status']
            serial_number = None
            ptype = None
            print 1
            for types in all_types:
                if types['number'] in bar_code:
                    ptype = types['name']
                    serial_number = bar_code.replace(types['number'],'')
                    # Empty part entry 
                    partobj = Part()
                    partobj.bar_code = bar_code
                    partobj.status = status
                    # Looking up type based on name, b/c I Needed to use a PartType object
                    partobj.type = PartType.objects.get(name=ptype)
                    partobj.serial_number = serial_number
                    partobj.save()
                    print 2
                    return partobj
                    return True
                else:
                    pass
                    

            else:
                return False
                print 3

class CheckOutPartForm(Form):
    #FIXME: possibly change to a regex field [a-zA-Z0-9]
    bar_code = forms.CharField(max_length=100, required=False,
                               widget=TextInput(attrs={'size':'30'})
                               )
    # Overriding model field validation for 'bar_code'
    def clean_bar_code(self):
        bar_code = self.cleaned_data['bar_code']
        if not bar_code:
            raise forms.ValidationError("Please enter a bar_code.")
        return bar_code

class AreaCheckOut(Form):
    bar_code = forms.CharField(widget=forms.Textarea(attrs={'cols':100,'rows':15}),required=True)

    def pre_process(self):
        data = self.cleaned_data
        bar_codes = data.get('bar_code',None)    
        bc_collection = [bc for bc in bar_codes.splitlines()]
            
        valid_bc = []
        invalid_bc = []
        filtered_bc = []
            
        for bc in bc_collection:
            try: 
                bar_code_model = Part.objects.get(bar_code=bc)
            except Part.DoesNotExist:
                invalid_bc.append(bc)
            else:
                # If this method passes after it checks the part out
                if bar_code_model.check_out() == True:
                    valid_bc.append(bar_code_model)
                else:
                    filtered_bc.append(bc) # If the part is already checked out
        
        return (filtered_bc, valid_bc, invalid_bc)



        
    def post_process(self):
        #Determine whether or not the part scanned in actually exists or not.
        data = self.cleaned_data
        bar_codes = data.get('bar_code',None)    
        bc_collection = [bc for bc in bar_codes.splitlines()]
            
        valid_bc = []
        invalid_bc = []
        filtered_bc = []
            
        for bc in bc_collection:
            try: 
                bar_code_model = Part.objects.get(bar_code=bc)
            except Part.DoesNotExist:
                invalid_bc.append(bc)
            else:
                # If this method passes after it checks the part out
                if bar_code_model.check_out() == True:
                    #valid_bc.append(bc)
                    bar_code_model.save()
                    valid_bc.append(bar_code_model)
                else:
                    filtered_bc.append(bc) # If the part is already checked out
        
        return (filtered_bc, valid_bc, invalid_bc)
        


                    
class PartUploadFileForm(Form):
    type = forms.ModelChoiceField(queryset=PartType.objects.all(), required=True)
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=True)
    file = forms.FileField(required=True) 
    
    def process(self):
        # This method will parse the list of bar_codes and create and save
        # a new part object for each bar_code. 
        for line in self.cleaned_data['file']:
            # Very poor way to do things, but it will work for now :)
            partobj=Part() # Creating model obj
            # Setting model attributes automatically
            partobj.bar_code = line 
            partobj.type = self.cleaned_data['type']
            partobj.status = self.cleaned_data['status']
            partobj.serial_number = line[10:]
            partobj.save()

class PartLogSearchForm(Form):
    
    bar_code = forms.CharField(max_length=100, required=False,
                               widget=TextInput(attrs={'size':'30'})
                               )
    def clean_bar_code(self):
        bar_code = self.cleaned_data['bar_code']
        if not bar_code:
            raise forms.ValidationError("Please enter a bar_code")
        return bar_code
    
class TextAreaForm(Form):
    
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=True)
    bar_codes = forms.CharField(widget=forms.Textarea(attrs={'cols': 100, 'rows':15}),required=True)
    
    def pre_process(self):
        #Func to parse text area field
        
        # Getting all the parts entered in the the text area field
        data = self.cleaned_data
        bar_codes = data.get('bar_codes', None) #Bar_codes of parts
        all_types = PartType.objects.values('name','number') #Getting ALL existing types LOD
        
        bc_collection = [bc for bc in bar_codes.splitlines()] #Parsing textarea box for barcode scanner input        
        
        type_count = defaultdict(int)
        valid_bc = [] #BCs ready for insert
        invalid_bc = [] #No part number match found
        filtered_bc = [] #BCs that are already found to be checked_in
        
        ([filtered_bc.append(bc) for bc in bc_collection if Part.objects.filter(bar_code=bc).exists() == True],
        [valid_bc.append(bc) for bc in bc_collection if any(types['number'] in bc for types in all_types) and bc not in filtered_bc],
        [invalid_bc.append(bc) for bc in bc_collection if not any(types['number'] in bc for types in all_types)])
        
            
        print "filtered_bc list", filtered_bc
        print "valid_bc list", valid_bc
        print "invalid_bc list", invalid_bc
        return (filtered_bc, valid_bc, invalid_bc)
    
    def post_process(self,valid_bc_list):
        #Func to create and save Part() objects         
        all_types = PartType.objects.values('name','number')
        for item in valid_bc_list:
            partobj = Part()
            for types in all_types:
                if types['number'] in item:
                    ptype=types['name']
                    serial_number = item.replace(types['number'],'') # breaking up bar_code into PN + SN
                    partobj.bar_code = item
                    partobj.status = self.cleaned_data['status']
                    partobj.type = PartType.objects.get(number=types['number'])
                    partobj.serial_number = serial_number
                    partobj.save()
                                        
    def process_count(self,myList):
        #Func to just return the count of types
        #Params: List of barcodes
        type_count = defaultdict(int)
        all_types = PartType.objects.values('name','number')
        
        for item in myList:
            print item
            print 1
            for types in all_types:
                print 2
                if types['number'] in item:
                    type_count[types['name']] += 1

        print type_count
        return type_count