# Misc. JUNK goes here!

# These functions have been pulled from various python files
# that have either been used before, or I planned on using in the future...
# forms.py

class BaseSingleTypePFS(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BasePartFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            
    # Form to form validating        
    def clean(self):
        if any(self.errors):
            return
        sns=[]
        # Checking each form if the same barcode is trying to be submitted twice
        for i in range(0,self.total_form_count()):
            form = self.forms[i]
            sn = form.cleaned_data['bar_code']
            if sn in sns:
                raise forms.ValidationError("Error: You cannot submit two of the same serial numbers")
            else:
                print "Checking if %s for duplicates between each form" % sn
                sns.append(sn)
    
    #type = forms.ModelChoiceField(queryset=PartType.objects.all(), required=True)
    parts = forms.CharField(widget=forms.Textarea,required=True)
    hello = forms.CharField(required=True)
    def process(self):
        errlst = []
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
        
        part_formset = formset_factory(AfterF, extra = extra_forms)
        formset = part_formset(initial=form_collection    