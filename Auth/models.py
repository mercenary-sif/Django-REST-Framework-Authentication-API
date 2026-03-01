from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class REGISTRATION_CHOICES(models.TextChoices) :
    Email = 'email', _('Email'),
    Google = 'google', _('Google')

class AccountTypes(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    MANAGER = 'manager', _('Manager')

class CustomUser(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    username = None   # Remove username field

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=AccountTypes.choices, default=AccountTypes.MANAGER)    
    registration_method = models.CharField(
        max_length=20,
        choices=REGISTRATION_CHOICES,
        default='email'
    )

    email_verified = models.BooleanField(default=False)
    rest_code = models.CharField(max_length=10, blank=True, null=True)
    rest_code_expires = models.DateTimeField(blank=True, null=True)
    whatsapp_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    profile_picture = models.URLField(
    blank=True,
    null=True
    )

    objects = CustomUser()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []   # Important

    def __str__(self):
        return self.email
