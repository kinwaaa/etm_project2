from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import User, Role, Department, Project, Task, Billing

# Custom UserAdmin
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'role', 'department', 'is_staff', 'is_superuser')
    list_filter = ('role', 'department', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')

# Custom form for Project to filter only managers and default start and end dates
class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        today = timezone.now().date()
        self.fields['start_date'].initial = today
        self.fields['end_date'].initial = today
      


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('project_name', 'start_date', 'end_date', 'manager_name')  # Use custom manager name
    search_fields = ('project_name', 'manager__first_name', 'manager__last_name')

    def manager_name(self, obj):
        return f"{obj.manager.first_name} {obj.manager.last_name}" if obj.manager else "No manager"
    manager_name.admin_order_field = 'manager'  
    manager_name.short_description = 'Manager'

# Register your models
admin.site.register(Project, ProjectAdmin)

# Register other models
admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(Department)
admin.site.register(Task)
admin.site.register(Billing)
