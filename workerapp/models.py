from django.db import models
from django.core.exceptions import ValidationError
#Email
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

class Customer(models.Model):
    customer=models.OneToOneField(User,on_delete=models.CASCADE)
    is_customer=models.BooleanField(default=True)
    phone=models.CharField(max_length=10,null=True)
    address=models.TextField(null=True)
    def __str__(self):
        return self.customer.username

class Worker(models.Model):
    worker=models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    is_customer=models.BooleanField(default=False)
    salary=models.BigIntegerField(null=True)
    worker_type=models.CharField(max_length=20,null=True)
    name=models.CharField(max_length=250,null=True)
    phone=models.CharField(max_length=10,null=True)
    img=models.ImageField(upload_to="pics",blank=True,null=True)
    is_approved = models.BooleanField(default=False,null=True)
    
    def __str__(self):
        return self.worker.username
    
class booking(models.Model):
    user=models.CharField(max_length=20)
    worker=models.CharField(max_length=25)
    worker_type=models.CharField(max_length=20,null=True)
    salary=models.BigIntegerField(null=True)
    phone=models.CharField(max_length=10,null=True)
    cardnumber=models.CharField(max_length=16,null=True)
    month=models.CharField(max_length=2,null=True)
    year=models.CharField(max_length=4,null=True)
    cvv=models.CharField(max_length=3,null=True)
    is_approved = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    booking_date = models.DateField(null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.is_approved and self.is_cancelled:
            raise ValidationError("A booking cannot be both approved and cancelled.")
        super().save(*args, **kwargs)
    
    
# Email System
@receiver(post_save, sender=booking)
def send_notification(sender, instance, created, **kwargs):
    if not created and instance.is_approved:
        try:
            message = 'Dear {},\n\nYour booking has been approved.\n\nDetails:\nWorker: {}\nWorker Type: {}\nSalary: {}\nPhone Number: {}\n'.format(
                instance.worker,
                instance.worker_type,
                instance.salary,
                instance.phone,
            )
            send_mail(
                'Your booking has been approved',
                message,
                settings.EMAIL_HOST_USER,
                [instance.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the exception or handle it as needed
            print(f"Failed to send email: {e}")

    def __str__(self):
        return self.user




class feedback(models.Model):
    name=models.CharField(max_length=20)
    phone=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    message=models.TextField()
    

    def __str__(self):
        return self.email

class notification(models.Model):

    email=models.CharField(max_length=200)
    

    def __str__(self):
        return self.email

class review(models.Model):

    name=models.CharField(max_length=20)
    email=models.CharField(max_length=200)
    message=models.TextField()
    

    def __str__(self):
        return self.name



