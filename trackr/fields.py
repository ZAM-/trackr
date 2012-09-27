from django import *
from models import Part, PartType, Status, Manufacturer

class MyModelChoiceField(Part.status):
    def status(self, obj):
        return obj.get_status_display()