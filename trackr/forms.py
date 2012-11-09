import datetime


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
        widgets = {
                   'bar_code': TextInput(attrs={'size': 30}), # Making text box bigger 
                   'serial_number': HiddenInput(attrs={'value':''}),
                   }
    def clean_serial_number(self):
        # Assigning clean data.
        bar_code = self.cleaned_data.get("bar_code")
        part_number = self.cleaned_data.get("type").number
        
        # Need to check if bar_code exists first
        # or second 'if' will fail 
        if bar_code:
            if part_number not in bar_code:
                raise forms.ValidationError("Barcode does not match type.")
            else:
                # Assigning the hidden serial_number field
                # Bar_Code - Part_Number = sn
                serial_number = bar_code.replace(part_number,'')
            # Required to return serial_number when done cleaning
            return serial_number
        else:
            raise forms.ValidationError(
                    "Did not validate, because bar code field is empty.")
            
    
    def clean_status(self):
        status = self.cleaned_data['status']
        # Checking if the part already exists 
        if self.instance.pk:
            # Before I couldn't get passed this state without getting AttributeError
            # Assigning oldStatus only would work if an initial entry existed
            oldStatus = self.instance._state.old_status
            if oldStatus == status:
                raise forms.ValidationError("This part currently has this status")

        # Required to return status when done cleaning  
        return status

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
        print "HI", bar_code
        return bar_code

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
    bar_codes = forms.CharField(widget=forms.Textarea,required=True)
    
    def pre_process(self):
        #Func to parse text area field
        
        # Getting all the parts entered in the the text area field
        data = self.cleaned_data
        bar_codes = data.get('bar_codes', None) #Bar_codes of parts
        all_types = PartType.objects.values('name','number') #Getting ALL existing types LOD
        
        bc_collection = [bc for bc in bar_codes.splitlines()] #Parsing textarea box for barcode scanner input        
        invalid_bc = []
        valid_bc = []
        
        #Step 1 of filtering valid and invalid bcs from user input by creating a list for each.
        ([valid_bc.append(bc) for bc in bc_collection if any(types['number'] in bc for types in all_types)],
         #Invalid_bcs should be in a solid state, b/c there is no need to count each different type scanned in
         [invalid_bc.append(bc) for bc in bc_collection if not any(types['number'] in bc for types in all_types)])
        
        print "valid_bc list", valid_bc
        print "invalid_bc list", invalid_bc
        return (valid_bc, invalid_bc)
    
    def post_process(self,my_list):
        #Func to create and save Part() objects
        #Will use list that is filtered from pre_process
        
        all_types = PartType.objects.values('name','number')
        for item in my_list:
            partobj = Part()
            for types in all_types:
                if types['number'] in item:
                    ptype=types['name']
                    serial_number = item.replace(types['number'],'') # breaking up bar_code into PN + SN
                    partobj.bar_code = item
                    partobj.status = self.cleaned_data['status']
                    partobj.type = PartType.objects.get(name=ptype)
                    partobj.serial_number = serial_number
                    partobj.save()
        
                                        

class EasyPartForm(Form):
# Views -- easy_mass_check_in() to create the 1 form that the formset will use
    bar_code = forms.CharField(max_length=100, required=True,
                               widget = TextInput(attrs={'size':'30'})
                               )
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=True)

    class meta:
        model = Part
        exclude = ('type', 'serial_number')


    def process(self):
    # pre-save process method. The Part() object saving happens in the view. 
        # Setting attributes for partobj
        bar_code = self.cleaned_data['bar_code']
        status = self.cleaned_data['status']
        serial_number = None
        ptype = None
        # Getting ALL existing types
        all_types = PartType.objects.values('name','number') #LOD
        # Looping through all the types
        # setting type and serial_number according to match. 
        for types in all_types:
            if types['number'] in bar_code:
                ptype = types['name']
                serial_number = bar_code.replace(types['number'],'') # breaking up bar_code into PN + SN
                partobj = Part()
                partobj.bar_code = bar_code
                partobj.status = status
                partobj.type = PartType.objects.get(name=ptype)
                partobj.serial_number = serial_number
                
                #Returning partobj so I can use type, and SN in the user messages.
                return partobj
                return True
            else:
                pass
        else:
            return False
                                

# Wizard forms
class MyFormStep0(Form):
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=True)
    parts = forms.CharField(widget=forms.Textarea,required=True)
    
    def clean(self):
        form_collection = []
        serail_number = None
        ptype = None
        # Getting ALL existing types
        all_types = PartType.objects.values('name','number') #LOD
        
        # Getting all the parts entered in the the text area field
        data = self.cleaned_data
        bar_codes = data.get('parts',None) #Bar_codes of parts
        
        # Parsing textarea box for barcode scanner input
        for bc in bar_codes.splitlines():
            for types in all_types:
                if types['number'] in bc:
                    ptype = types['name']
            form_collection.append({'bc':bc})
            
        
    
class MyFormStep1(ModelForm):
    parts = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = Part
        exclude = ('part','status','bar_code','serial_number')
"""                     
    def clean(self):
        #Checks that no two articles have the same title
        if any(self.errors):
            # Don't bother validating unless each form is valid on it's own
            return
        bar_codes = []
        for item in range(0, self.total_form_count()):
            form = self.forms[item]
            bar_code = form.cleaned_data['bar_code']
            if bar_code in bar_codes:
                raise forms.ValidationError("Parts in a set must have distinct barcodes.")
            else:
                bar_codes.append(bar_code)
"""