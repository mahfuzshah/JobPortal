from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import UserRegisterForm, UserProfileForm, JobForm, ApplicationForm
from .models import UserProfile, Job, Application

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                display_name=form.cleaned_data['display_name'],
                user_type=form.cleaned_data['user_type']
            )
            login(request, user)
            return redirect('portal:profile')
        # else:
        #     messages.error(request, "Registration failed. Please correct the errors below.")
        #     print(form.errors)
    else:
        form = UserRegisterForm()
    return render(request, 'portal/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("portal:job_list")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("portal:login")
    return render(request, 'portal/login.html')

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('portal:dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'portal/profile.html', {'form': form})

@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if profile.user_type == 'recruiter':
        jobs = Job.objects.filter(recruiter=request.user)
        return render(request, 'portal/recruiter_dashboard.html', {'jobs': jobs})
    else:
        applications = Application.objects.filter(jobseeker=request.user)
        # Skill matching: jobs where skills match user's skills
        user_skills = profile.skills.lower().split(',') if profile.skills else []
        query = Q()
        for skill in user_skills:
            query |= Q(skills_required__icontains=skill.strip())
        matched_jobs = Job.objects.filter(query).exclude(
            id__in=applications.values_list('job_id', flat=True)
        )[:10]  # Limit to 10, exclude already applied jobs
        return render(request, 'portal/jobseeker_dashboard.html', {
            'applications': applications,
            'matched_jobs': matched_jobs
        })

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            return redirect('portal:dashboard')
    else:
        form = JobForm()
    return render(request, 'portal/post_job.html', {'form': form,  'title': 'Post', 'submit': 'Post'})


def job_list(request):
    jobs = Job.objects.all()
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills_required__icontains=query)
        )

    if category:
        jobs = jobs.filter(category=category)

    applied_jobs = []
    if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'jobseeker':
        applied_jobs = Application.objects.filter(jobseeker=request.user).values_list('job_id', flat=True)

    return render(request, 'portal/job_list.html', {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
        'query': query,
        'category': category
    })

@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applied = False
    if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'jobseeker':
        applied = Application.objects.filter(jobseeker=request.user, job=job).exists()
    return render(request, 'portal/job_details.html', {'job': job, 'applied': applied})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    profile = UserProfile.objects.get(user=request.user)

    # Check if already applied
    if Application.objects.filter(jobseeker=request.user, job=job).exists():
        messages.info(request, 'You have already applied for this job.')
        return redirect('portal:job_list')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.jobseeker = request.user
            application.job = job
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('portal:job_list')
    else:
        # Pre-fill form with user's profile data
        initial_data = {
            'skills': profile.skills,
            'resume': profile.resume,
        }
        form = ApplicationForm(initial=initial_data)

    return render(request, 'portal/apply_job.html', {
        'form': form,
        'job': job
    })

@login_required
def manage_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job)

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        application = get_object_or_404(Application, id=app_id, job=job)
        application.status = new_status
        application.save()
        messages.success(request, f'Application status updated to {new_status}.')
        return redirect('portal:manage_applications', job_id=job_id)

    return render(request, 'portal/manage_applications.html', {
        'job': job,
        'applications': applications
    })

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('portal:dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'portal/post_job.html', {'form': form, 'job': job, 'title': 'Edit', 'submit': 'Update'})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('portal:dashboard')
    return render(request, 'portal/delete_job.html', {'job': job})

@login_required
def logout_view(request):
    logout(request)
    return redirect('portal:login')
