from django.contrib import admin

# Register your models here.
from django.utils.html import format_html
from .models import InsurancePlan, Policy, PolicyMember, Payment, Claim, UserProfile, ContactMessage

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'user', 'plan', 'plan_tier', 'paid_amount', 'status', 'start_date')
    search_fields = ('policy_number', 'user__username', 'user__email', 'plan__title')
    list_filter = ('status', 'plan_tier')

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_policy_number', 'user_email', 'claim_amount', 'status', 'view_document', 'applied_date')
    search_fields = ('policy__policy_number', 'policy__user__email', 'reason')
    list_filter = ('status', 'applied_date')

    def get_policy_number(self, obj):
        return obj.policy.policy_number
    get_policy_number.short_description = 'Policy Number'

    def user_email(self, obj):
        return obj.policy.user.email or obj.policy.user.username
    user_email.short_description = 'User'

    def view_document(self, obj):
        if obj.document:
            return format_html('<a href="{}" target="_blank" style="color:#0d6efd; font-weight:600;">Open Document</a>', obj.document.url)
        return "No Document"
    view_document.short_description = 'Document'

admin.site.register(InsurancePlan)
admin.site.register(PolicyMember)
admin.site.register(Payment)
admin.site.register(UserProfile)
admin.site.register(ContactMessage)