from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm, UserForm
from .models import Role, User, Department, Project, Task, Billing
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

def main_view(request):
    return render(request, 'main.html')

def home_redirect(request):
    return render(request, 'main.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

          
            role, created = Role.objects.get_or_create(role_name='Employee')
            user.role = role
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

           
            user = authenticate(request, username=email, password=password)  # Using `email` as `username`

            if user is not None:
                login(request, user)
                return redirect(get_redirect_url(user))
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def get_redirect_url(user):
    role = user.role.role_name
    if role == 'Admin':
        return 'admin-dashboard'  
    elif role == 'Manager':
        return 'manager_dashboard'
    elif role == 'Employee':
        return 'employee_dashboard'
    elif role == 'Client':
        return 'client_dashboard'
    else:
        return 'login'

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def manager_dashboard(request):
    return render(request, 'dashboards/manager.html')

@login_required
def employee_dashboard(request):
    return render(request, 'dashboards/employee.html')

@login_required
def client_dashboard(request):
    return render(request, 'dashboards/client.html')



@login_required
def admin_dashboard(request):
    # Check if the logged-in user is an admin
    if request.user.role.role_name != 'Admin':
        return redirect('employee_dashboard')  # Correct way to redirect to the employee dashboard


    users = User.objects.all().select_related('role', 'department')
    roles = Role.objects.all()
    departments = Department.objects.all()
    projects = Project.objects.all().select_related('manager')
    tasks = Task.objects.all().select_related('assigned_to', 'project')
    billings = Billing.objects.all().select_related('project', 'generated_by')

    # Calculate project progress
    for project in projects:
        total_tasks = project.task_set.count()
        completed_tasks = project.task_set.filter(status='Completed').count()
        project.progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    return render(request, 'dashboards/admin.html', {
        'users': users,
        'roles': roles,
        'departments': departments,
        'projects': projects,
        'tasks': tasks,
        'billings': billings,
    })


@require_POST
def add_user(request):
    form = UserForm(request.POST)

    # Get roles and departments for rendering
    roles = Role.objects.all()
    departments = Department.objects.all()
    projects = Project.objects.all()

    if form.is_valid():
        # Check for duplicate email
        if User.objects.filter(email=form.cleaned_data['email']).exists():
           messages.error(request, "This email is already in use.", extra_tags='user')
        else:
            user = form.save(commit=False)
            user.role_id = request.POST.get('role')
            user.department_id = request.POST.get('department')
            user.save()

            messages.success(request, "User created successfully!", extra_tags='user')
            return redirect('admin-dashboard')  # Assuming this is the named URL

    # Either form was invalid or email existed
    messages.error(request, "Please correct the errors below.", extra_tags='user')
    return render(request, 'dashboards/admin.html', {
    'form': form,
    'roles': roles,
    'departments': departments,
    'users': User.objects.all(),  # Add users for table display
    'projects': projects,  # If your dashboard uses it
    'tasks': Task.objects.all(),  # Same here
})

@require_POST
def update_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.first_name = request.POST.get("first_name")
    user.last_name = request.POST.get("last_name")
    user.email = request.POST.get("email")
    user.phone = request.POST.get("phone")
    user.role_id = request.POST.get("role")
    user.department_id = request.POST.get("department")
    user.save()
    return redirect('admin-dashboard')


@require_POST
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('admin-dashboard')


@require_POST
def add_project(request):
    project_name = request.POST.get('project_name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    manager_id = request.POST.get('manager')

    manager = get_object_or_404(User, id=manager_id)

    Project.objects.create(
        project_name=project_name,
        start_date=start_date,
        end_date=end_date,
        manager=manager
    )

    return redirect('admin-dashboard')

@require_POST
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.project_name = request.POST.get('project_name')
    project.start_date = request.POST.get('start_date')
    project.end_date = request.POST.get('end_date')
    manager_id = request.POST.get('manager')
    project.manager = get_object_or_404(User, id=manager_id)

    project.save()

    return redirect('admin-dashboard')

@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return redirect('admin-dashboard')




@require_POST
def add_task(request):
    title = request.POST.get('title')
    description = request.POST.get('description')
    status = request.POST.get('status')
    assigned_to = request.POST.get('assigned_to')
    due_date = request.POST.get('due_date')
    project_id = request.POST.get('project')

    assigned_user = None
    if assigned_to:
        assigned_user = get_object_or_404(User, id=assigned_to)
        
    project = get_object_or_404(Project, id=project_id)

    Task.objects.create(
        title=title,
        description=description,
        status=status,
        assigned_to=assigned_user,  # Can be None if no user is assigned
        due_date=due_date,
        project=project
    )

    return redirect('admin-dashboard')

@require_POST
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.title = request.POST.get('title')
    task.description = request.POST.get('description')
    task.status = request.POST.get('status')
    
    assigned_to = request.POST.get('assigned_to')
    if assigned_to:
        task.assigned_to = get_object_or_404(User, id=assigned_to)
    else:
        task.assigned_to = None  # Handle unassigned case

    task.due_date = request.POST.get('due_date')
    task.project = get_object_or_404(Project, id=request.POST.get('project'))

    task.save()

    return redirect('admin-dashboard')

@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('admin-dashboard')

# Add Department View (GET for form, POST for creation)
def add_department(request):
    if request.method == 'POST':
        department_name = request.POST.get('department_name')
        
        # Ensure the department name is not empty
        if department_name:
            # Create a new department with the name provided
            Department.objects.create(department_name=department_name)
            messages.success(request, 'Department added successfully!')
            return redirect('admin-dashboard')  # Redirect to the admin dashboard after adding a department
        else:
            messages.error(request, 'Department name cannot be empty.')

    return render(request, 'admin-dashboard')  # Render the form on GET

# Update Department View (GET for form, POST for updating)
def update_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        new_department_name = request.POST.get('department_name')
        
        # Ensure the department name is not empty
        if new_department_name:
            # Update department name with the new value from the request
            department.department_name = new_department_name
            department.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('admin-dashboard')  # Redirect to the admin dashboard after updating
        else:
            messages.error(request, 'Department name cannot be empty.')

    return render(request, 'admin-dashboard', {'department': department})  # Render the form on GET

# Delete Department View (POST for deletion)
@require_POST
def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    
    if department.user_set.count() == 0:
        department.delete()
        messages.success(request, "Department added successfully!", extra_tags='department')
    else:
        messages.error(request, 'Cannot delete department with associated users.', extra_tags='department')
    
    return redirect('admin-dashboard')  # Redirect to the admin dashboard after deletion


@require_POST
def add_billing(request):
    project_id = request.POST.get('project')
    total_hours = request.POST.get('total_hours')
    hourly_rate = request.POST.get('hourly_rate')
    billing_date = request.POST.get('billing_date')
    status = request.POST.get('status')

    project = get_object_or_404(Project, id=project_id)

    # Calculate amount
    amount = Decimal(total_hours) * Decimal(hourly_rate)

    Billing.objects.create(
        project=project,
        generated_by=request.user,
        total_hours=total_hours,
        hourly_rate=hourly_rate,
        amount=amount,
        billing_date=billing_date,
        status=status
    )

    return redirect('admin-dashboard')

@require_POST
def update_billing(request, billing_id):
    billing = get_object_or_404(Billing, id=billing_id)

    billing.project = get_object_or_404(Project, id=request.POST.get('project'))
    billing.total_hours = request.POST.get('total_hours')
    billing.hourly_rate = request.POST.get('hourly_rate')
    billing.billing_date = request.POST.get('billing_date')
    billing.status = request.POST.get('status')

    # Recalculate amount
    billing.amount = Decimal(billing.total_hours) * Decimal(billing.hourly_rate)

    billing.save()
    return redirect('admin-dashboard')


@require_POST
def delete_billing(request, billing_id):
    billing = get_object_or_404(Billing, id=billing_id)
    billing.delete()
    return redirect('admin-dashboard')


@login_required
def employee_dashboard(request):
    # Check if the logged-in user is an employee
    if request.user.role.role_name != 'Employee':
        return redirect('admin-dashboard')  # Redirect non-employee users to the admin dashboard

    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'dashboards/employee.html', {
        'tasks': tasks,
        'user': request.user  # This ensures the correct user is passed
    })

