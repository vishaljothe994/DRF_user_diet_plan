from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that includes name, email, and other fields.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = None
    isPaid = models.BooleanField(default=False)
    TrialsLeft = models.IntegerField(default=20)  # Add the TrialsLeft 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # def __str__(self):
    #     return self.email
    class Meta:
        db_table = 'User'

class UserToken(models.Model):
    """
    Model for storing forgotPassword user tokens.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'UserToken'


class FamilyInfo(models.Model):
    """
    Model for storing Family Information.
    """
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    noOfMembers = models.PositiveIntegerField()
    national = models.CharField(max_length=100)
    diet = models.CharField(max_length=100)
    ethnicity = models.CharField(max_length=100)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    meal = models.JSONField()

    class Meta:
        db_table = 'FamilyInfo'


class MemberDetail(models.Model):
    """
    Model for storing Member Detail as per Family Info ID.
    """    
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    familyInfoId = models.ForeignKey(FamilyInfo, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    allergy = models.CharField(max_length=100)
    medicalCondition = models.CharField(max_length=100)     
    

    class Meta:
        db_table = 'MemberDetail'

