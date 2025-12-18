from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Job, Application

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    display_name = forms.CharField(max_length=100)
    user_type = forms.ChoiceField(choices=[('recruiter', 'Recruiter'), ('jobseeker', 'Jobseeker')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'user_type', 'company_name', 'company_description', 'skills', 'resume']
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 3}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'number_of_openings', 'category', 'description', 'skills_required']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills_required': forms.Textarea(attrs={'rows': 3}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['skills', 'resume', 'cover_letter']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your skills (comma-separated)'}),
            'cover_letter': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Write your cover letter here...'}),
        }
