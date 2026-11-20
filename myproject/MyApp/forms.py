from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Policy, Claim, InsurancePlan


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    phone = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Complete residential address'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


# User Policy Purchase Form (Dropdown selection for Basic, Medium, and Premium)
class PolicyBuyForm(forms.ModelForm):
    plan_tier = forms.ChoiceField(
        label="Select Plan Option",
        widget=forms.Select(attrs={'class': 'form-select fw-bold text-primary'})
    )

    class Meta:
        model = Policy
        fields = ['plan_tier', 'nominee_name', 'nominee_relation']
        widgets = {
            'nominee_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nominee Full Name'}),
            'nominee_relation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Relationship with Nominee'}),
        }

    def __init__(self, *args, **kwargs):
        plan = kwargs.pop('plan', None)
        super().__init__(*args, **kwargs)
        if plan:
            self.fields['plan_tier'].choices = [
                ('Basic', f'Basic Plan - ₹{plan.basic_amount} /yr'),
                ('Medium', f'Medium Plan - ₹{plan.medium_amount} /yr'),
                ('Premium', f'Premium Plan - ₹{plan.premium_amount} /yr'),
            ]
        else:
            self.fields['plan_tier'].choices = [
                ('Basic', 'Basic Plan'),
                ('Medium', 'Medium Plan'),
                ('Premium', 'Premium Plan'),
            ]


# Claim Form (With Policy Number & Document/File Upload)
class ClaimForm(forms.ModelForm):
    policy_number = forms.CharField(
        max_length=30,
        required=True,
        label="Policy Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your Policy Number (e.g. POL-A1B2C3D4)'
        })
    )

    class Meta:
        model = Claim
        fields = ['policy_number', 'claim_amount', 'reason', 'document']
        widgets = {
            'claim_amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Requested Claim Amount (₹)'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Reason for claiming / details...'
            }),
            'document': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


# Admin Plan Creation Form (Category removed, 3 tier amounts added)
class PlanForm(forms.ModelForm):
    class Meta:
        model = InsurancePlan
        fields = [
            'title', 
            'sum_insured', 
            'basic_amount', 
            'medium_amount', 
            'premium_amount', 
            'tenure_years', 
            'description', 
            'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan Title'}),
            'sum_insured': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Coverage / Sum Insured'}),
            'basic_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Basic Amount'}),
            'medium_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Medium Amount'}),
            'premium_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Premium Amount'}),
            'tenure_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tenure in Years'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Plan details and coverage description...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input ms-1'}),
        }