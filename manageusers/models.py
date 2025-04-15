from django.db import models
import uuid
import os
from django.contrib.auth.hashers import make_password, identify_hasher
from django.core.exceptions import ValidationError
from supabase import create_client, Client
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.dispatch import receiver
def rename_image(instance, filename):
    """Generate unique filename for uploaded images."""
    ext = filename.split('.')[-1]
    return f"images/{uuid.uuid4().hex}.{ext}"

def upload_file_to_supabase(file_field):
    """Upload file to Supabase storage and return public URL."""
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    file_content = file_field.read()
    filename = rename_image(None, file_field.name)
    
    # Upload file
    res = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
        file=file_content,
        path=filename,
        file_options={"content_type": "auto"}
    )
    
    
    return supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(filename)

class AppUsers(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    USER_STATUS = [
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('B', 'Blocked'),
        ('P', 'Pending'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    profile_picture = models.ImageField(upload_to=rename_image, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    skills_offered = models.ManyToManyField('Skills', related_name='offering_users')
    skills_wanted = models.ManyToManyField('Skills', related_name='seeking_users')
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    status = models.CharField(max_length=1, choices=USER_STATUS, default='P')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'app_users'
        verbose_name = 'App User'
        verbose_name_plural = 'App Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name}"

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith(('pbkdf2_', 'bcrypt$')):
            self.password = make_password(self.password)
        
        # Handle profile picture upload
        if self.profile_picture and hasattr(self.profile_picture, 'file'):
            upload_file_to_supabase(self.profile_picture)
        
        super().save(*args, **kwargs)

@receiver(post_save, sender=AppUsers)
def after_saving_model(sender, instance, created, **kwargs):
    if created:
        os.remove(instance.profile_picture.path)  # Remove local copy after upload
    else:
        print(f'{sender.__name__} updated:', instance)
class Skills(models.Model):
    skill_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skills'
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['name']

    def __str__(self):
        return self.name