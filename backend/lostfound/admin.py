from django.contrib import admin

from .models import Claim, Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'place_found', 'date_found', 'status')
    list_filter = ('status', 'category')
    search_fields = ('name', 'description', 'place_found')
    readonly_fields = ('status', 'created_at')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('item', 'full_name', 'student_no', 'status', 'submitted_at', 'decided_by')
    list_filter = ('status',)
    search_fields = ('full_name', 'student_no', 'verified_name', 'verified_student_no', 'item__name')
    # Hindi ipinapakita ang handover photo dito: pribado ito at wala itong public na URL.
    exclude = ('handover_photo',)
    readonly_fields = ('submitted_at', 'decided_at', 'decided_by')
