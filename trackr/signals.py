from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from models import Part, PartLog, Status


# Receiver Functions

@receiver(post_save, sender=Part)
def log_entry(sender, instance, created, raw, *args, **kwargs):
    # Using the statuses from the above method to create a PartLog entry. 
    newStatus = instance.status
    
    if not created:
        # Get old status from current state
        oldStatus = instance._state.old_status
        PartLog.objects.create(part=instance,
                               old_status=oldStatus,
                               new_status=instance.status)
        instance._state.old_status = newStatus
    else:
        PartLog.objects.create(part=instance, old_status=Status(1), new_status=Status(3))
 
    

    