from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import ValidationError

ENTERED_DATABASE = 'EN'
CHECKED_OUT = 'CO'
CHECKED_IN = 'CI'
RMA = 'RM'
IN_USE = 'IU'
    
STATUS_TYPE_CHOICES = (
     (ENTERED_DATABASE, u'Entered Database'),
     (CHECKED_OUT, u'Checked out'),
     (CHECKED_IN, u'Checked in'),
     (RMA, u'Returned for RMA'),
     (IN_USE, u'Currently in use'),
        )

class Manufacturer(models.Model):
    company = models.CharField(max_length=30, blank=False)
    contact = models.CharField(max_length=30, blank=False)
    phone = models.IntegerField(blank=False)
    address = models.CharField(max_length=60, blank=False)
    
    def __unicode__(self):
        return self.company
    
class Status(models.Model):


    status = models.CharField(max_length=2, choices=STATUS_TYPE_CHOICES)
    
    def __unicode__(self):
        return unicode(self.get_status_display())

class PartType(models.Model):
    number = models.CharField(max_length=30,blank=False)
    name = models.CharField(max_length=30, blank=False)
    make = models.CharField(max_length=30)
    model = models.CharField(max_length=30)
    manufacturer = models.ForeignKey(Manufacturer, blank=False)
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.model)

class Part(models.Model):
    type = models.ForeignKey(PartType, blank=False)
    bar_code = models.CharField(max_length=50, blank=False, unique=True)
    serial_number = models.CharField(max_length=50, blank=False)
    status = models.ForeignKey(Status, blank=False)
    
    
    def __init__(self, *args, **kwargs):
        super(Part, self).__init__(*args, **kwargs)
        
        # Caching the existing Part object's status
        if self.pk:
            self._state.old_status = self.status #Use this for PartLog entry signal
            

    def __unicode__(self):
        return unicode(self.bar_code)    

    # Method to set status of a part to "checked out"
    # Returns True or False to be used in view to determine whether
    # or not the Part.object needs to be saved or not. 
    def check_out(self):
        # Returns True if status isn't already set to "checked out"
        if self.status != Status(2):
            self.status = Status(2)
            return True
        else:
        # Returns False if status is already set to "checked out"    
            return False
        
    def check_in(self, created=None):
        if created is True:
            if self.status != Status(3):
                self.status = Status(3)
                return self.status
                print "Checking Part in"
            else:
                print "This part is already checked in."
        else:
            pass


class PartLogManager(models.Manager):
    def checked_in(self):
        return self.get_query_set().filter(new_status__exact=CHECKED_IN)
    
    def checked_out(self):
        return self.get_query_set().filter(new_status__exact=CHECKED_OUT)
    
    
class PartLog(models.Model):
    part = models.ForeignKey(Part, blank=False)
    time_stamp = models.DateTimeField(blank=False, auto_now_add=True)
    old_status = models.ForeignKey(Status, related_name='old_status_related', blank=False)
    new_status = models.ForeignKey(Status, related_name='new_status_related', blank=False)
    objects = PartLogManager()
    
    def __unicode__(self):
        return unicode(self.time_stamp)
        
    