from django.db import models
from django.core.validators import MinValueValidator

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    
    EVENT_TYPES = [
        ('wedding', 'Wedding'),
        ('birthday', 'Birthday'),
        ('corporate', 'Corporate Event'),
        ('engagement', 'Engagement'),
        ('anniversary', 'Anniversary'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20,null=True,blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    guests = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    days = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        self.days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_event_type_display()} ({self.start_date} to {self.end_date})"
    
    

    class Meta:
        ordering = ['start_date']


class ContactUs(models.Model):
    username = models.CharField(max_length=225,null=True,blank=True)
    email = models.CharField(max_length=225,null=True,blank=True)
    subject = models.CharField(max_length=225,null=True,blank=True)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username} - {self.email}' 