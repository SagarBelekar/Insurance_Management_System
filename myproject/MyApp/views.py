import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User

from .models import (
    InsurancePlan, 
    Policy, 
    Payment, 
    Claim, 
    UserProfile, 
    ContactMessage,
    PolicyMember
)
from .forms import (
    UserRegistrationForm, 
    PolicyBuyForm, 
    ClaimForm, 
    PlanForm
)


# --- Helper Tests ---
def is_admin(user):
    return user.is_authenticated and user.is_staff


# ==========================================
# 1. PROFILE MANAGEMENT VIEWS
# ==========================================

@user_passes_test(is_admin, login_url='admin_login')
def admin_profile_view(request):
    return render(request, 'admin_profile.html', {
        'admin_user': request.user
    })


@login_required(login_url='user_login')
def user_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        profile.phone = phone
        profile.address = address
        profile.save()

        messages.success(request, 'Profile details updated successfully!')
        return redirect('user_profile')

    user_policies_count = Policy.objects.filter(user=request.user).count()

    context = {
        'user_obj': request.user,
        'profile': profile,
        'total_policies': user_policies_count
    }
    return render(request, 'user_profile.html', context)


# ==========================================
# 2. INFORMATIONAL & LANDING PAGES
# ==========================================

def landing_page(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, f'Thank you {name}! Your message has been sent successfully.')
            return redirect('/#contact')
        else:
            messages.error(request, 'Please fill in all fields.')
            return redirect('/#contact')

    plans = InsurancePlan.objects.filter(is_active=True)[:6]
    return render(request, 'landing.html', {'plans': plans})


def about_page(request):
    return render(request, 'about.html')


def features_page(request):
    return render(request, 'features.html')


def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and subject and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            messages.success(request, f'Thank you {name}! Your message has been received. Our team will contact you soon.')
            return redirect('contact_page')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'contact.html')


# ==========================================
# 3. AUTHENTICATION VIEWS
# ==========================================

def user_register_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_staff = False
            user.save()

            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            messages.success(request, 'Registration successful! Please login with your email and password.')
            return redirect('user_login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user_obj = User.objects.filter(email__iexact=email).first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'No account found with this email address.')
            
    return render(request, 'user_login.html')


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, 'Admin authenticated successfully!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access Denied: You do not have administrator permissions.', extra_tags='danger')
        else:
            messages.error(request, 'Invalid Admin credentials.', extra_tags='danger')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing_page')


# ==========================================
# 4. USER PORTAL MODULES
# ==========================================

@login_required(login_url='user_login')
def user_dashboard(request):
    policies = Policy.objects.filter(user=request.user)
    claims = Claim.objects.filter(policy__user=request.user)
    payments = Payment.objects.filter(policy__user=request.user)
    context = {
        'total_policies': policies.count(),
        'active_policies': policies.filter(status='Active').count(),
        'total_claims': claims.count(),
        'total_spent': sum(p.amount for p in payments),
        'recent_policies': policies[:5],
    }
    return render(request, 'user_dashboard.html', context)


def browse_plans(request):
    plans = InsurancePlan.objects.filter(is_active=True)
    return render(request, 'browse_plans.html', {'plans': plans})


@login_required(login_url='user_login')
def buy_policy(request, plan_id):
    plan = get_object_or_404(InsurancePlan, id=plan_id)

    if request.method == 'POST':
        selected_tier = request.POST.get('plan_tier', 'Basic')
        if selected_tier == 'Basic':
            final_amount = plan.basic_amount
        elif selected_tier == 'Medium':
            final_amount = plan.medium_amount
        else:
            final_amount = plan.premium_amount

        # Random unique policy_number is auto-generated by the model default
        policy = Policy.objects.create(
            user=request.user,
            plan=plan,
            plan_tier=selected_tier,
            paid_amount=final_amount,
            status='Active'
        )

        # Dynamic Family/Covered Members with Gender and Relation
        member_names = request.POST.getlist('member_name[]')
        member_ages = request.POST.getlist('member_age[]')
        member_genders = request.POST.getlist('member_gender[]')
        member_relations = request.POST.getlist('member_relation[]')

        for name, age, gender, relation in zip(member_names, member_ages, member_genders, member_relations):
            name = name.strip()
            relation = relation.strip()
            if name and age and relation:
                try:
                    PolicyMember.objects.create(
                        policy=policy,
                        name=name,
                        age=int(age),
                        gender=gender.strip() if gender else 'Male',
                        relation=relation
                    )
                except ValueError:
                    pass

        # Record Payment
        Payment.objects.create(
            policy=policy,
            amount=final_amount,
            transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}"
        )

        # Re-render with Step 5 Success Popup containing the new policy number
        return render(request, 'buy_policy.html', {
            'plan': plan,
            'user_email': request.user.email or request.user.username,
            'success_policy': policy
        })

    context = {
        'plan': plan,
        'user_email': request.user.email or request.user.username
    }
    return render(request, 'buy_policy.html', context)


@login_required(login_url='user_login')
def my_policies(request):
    policies = Policy.objects.filter(user=request.user)
    return render(request, 'my_policies.html', {'policies': policies})


@login_required(login_url='user_login')
def submit_claim(request, policy_id=None):
    initial_data = {}
    if policy_id:
        policy_obj = get_object_or_404(Policy, id=policy_id, user=request.user)
        initial_data['policy_number'] = policy_obj.policy_number

    if request.method == 'POST':
        # File upload ke liye request.FILES zaroori hai
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            pol_num = form.cleaned_data['policy_number'].strip()
            
            # Match policy number with active user policy
            policy = Policy.objects.filter(policy_number=pol_num, user=request.user, status='Active').first()
            if not policy:
                messages.error(request, 'Invalid Policy Number or Policy is not active!')
                return render(request, 'submit_claim.html', {'form': form})

            claim = form.save(commit=False)
            claim.policy = policy
            claim.save()
            messages.success(request, f'Claim for Policy {policy.policy_number} submitted successfully!')
            return redirect('claim_status')
    else:
        form = ClaimForm(initial=initial_data)

    return render(request, 'submit_claim.html', {'form': form})


@login_required(login_url='user_login')
def claim_status(request):
    claims = Claim.objects.filter(policy__user=request.user)
    return render(request, 'claim_status.html', {'claims': claims})


# ==========================================
# 5. ADMIN PORTAL MODULES
# ==========================================

@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_policies': Policy.objects.count(),
        'pending_claims': Claim.objects.filter(status='Pending').count(),
        'total_revenue': sum(p.amount for p in Payment.objects.all()),
        'recent_claims': Claim.objects.filter(status='Pending')[:5],
    }
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(is_admin, login_url='admin_login')
def manage_claims(request):
    claims = Claim.objects.all().order_by('-applied_date')
    return render(request, 'manage_claims.html', {'claims': claims})


@user_passes_test(is_admin, login_url='admin_login')
def claim_action(request, claim_id, action):
    claim = get_object_or_404(Claim, id=claim_id)
    if action == 'approve':
        claim.status = 'Approved'
        claim.admin_remark = "Approved by Administrator"
    elif action == 'reject':
        claim.status = 'Rejected'
        claim.admin_remark = "Rejected by Administrator"
    claim.save()
    messages.info(request, f'Claim #{claim.id} status updated to {claim.status}.')
    return redirect('manage_claims')


@user_passes_test(is_admin, login_url='admin_login')
def manage_plans(request):
    plans = InsurancePlan.objects.all()
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Insurance Plan Created!')
            return redirect('manage_plans')
    else:
        form = PlanForm()
    return render(request, 'manage_plans.html', {'plans': plans, 'form': form})


@user_passes_test(is_admin, login_url='admin_login')
def admin_contact_messages(request):
    contact_msgs = ContactMessage.objects.all()
    return render(request, 'admin_contacts.html', {'contact_msgs': contact_msgs})


@user_passes_test(is_admin, login_url='admin_login')
def toggle_contact_resolved(request, msg_id):
    msg = get_object_or_404(ContactMessage, id=msg_id)
    msg.is_resolved = not msg.is_resolved
    msg.save()
    messages.info(request, f'Inquiry #{msg.id} status updated.')
    return redirect('admin_contact_messages')