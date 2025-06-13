# In your signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course

@receiver(post_save, sender=Course)
def process_course_images(sender, instance, created, **kwargs):
    if created:
        # Process any images that were uploaded with the course
        instance.process_question_images()