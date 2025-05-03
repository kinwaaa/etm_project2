from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, phone, password=None):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password
        )
        from .models import Role
        user.is_superuser = True
        user.is_staff = True
        user.role = Role.objects.get_or_create(role_name='Admin')[0]  # Auto-assign Admin role
        user.save(using=self._db)
        return user

# Custom user model
class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)       # Needed for admin site
    is_superuser = models.BooleanField(default=False)   # Needed for admin site
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

     
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Role(models.Model):
    ROLE_CHOICES = [('Admin', 'Admin'), ('Manager', 'Manager'), ('Employee', 'Employee'),('Client', 'Client'),]
    role_name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.role_name

class Department(models.Model):
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

class Project(models.Model):
    project_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_projects')

class Task(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')]

    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks')
    due_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')

class Billing(models.Model):
    STATUS_CHOICES = [('Pending', 'Pending'), ('Paid', 'Paid'), ('Cancelled', 'Cancelled')]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_billings')
    total_hours = models.DecimalField(max_digits=5, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
