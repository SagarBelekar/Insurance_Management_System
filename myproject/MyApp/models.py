import uuid
from django.db import models
from django.contrib.auth.models import User


# Helper function to generate a random unique Policy Number
def generate_policy_number():
    return f"POL-{uuid.uuid4().hex[:8].upper()}"


# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username


# Insurance Plan Model
class InsurancePlan(models.Model):
    title = models.CharField(max_length=150)
    sum_insured = models.DecimalField(max_digits=12, decimal_places=2)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    medium_amount = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    tenure_years = models.PositiveIntegerField(default=1)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} (Basic: ₹{self.basic_amount} | Med: ₹{self.medium_amount} | Prem: ₹{self.premium_amount})"


# Policy Model (With auto-generated unique Policy Number via save method)
class Policy(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending Approval'),
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='policies')
    plan = models.ForeignKey(InsurancePlan, on_delete=models.CASCADE)
    
    # Callable default removed from field definition to prevent migration warning
    policy_number = models.CharField(max_length=25, unique=True, null=True, blank=True)
    
    # Plan Tier & Payment details
    plan_tier = models.CharField(max_length=50, default='Basic')  # Basic, Medium, ya Premium
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    start_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    
    # Nominee Details (Optional)
    nominee_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_relation = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.policy_number:
            new_code = generate_policy_number()
            while Policy.objects.filter(policy_number=new_code).exists():
                new_code = generate_policy_number()
            self.policy_number = new_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.policy_number or 'Unassigned'} - {self.plan.title} [{self.plan_tier}] ({self.user.username})"


# Policy Member Model (Family members covered under the policy)
class PolicyMember(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, default='Male')
    relation = models.CharField(max_length=50, default='self')

    def __str__(self):
        return f"{self.name} ({self.relation}, {self.gender}) - {self.policy.policy_number}"


# Payment Model
class Payment(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='Success')

    def __str__(self):
        return f"Payment {self.transaction_id} - ₹{self.amount}"


# Claim Model (With File Upload field)
class Claim(models.Model):
    CLAIM_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='claims')
    reason = models.TextField()
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2)
    document = models.FileField(upload_to='claims_documents/', blank=True, null=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='Pending')
    admin_remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Claim #{self.id} for {self.policy.policy_number}"


# Contact Message Model
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"