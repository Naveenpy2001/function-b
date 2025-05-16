from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event_type', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'event_type', 'start_date')
    search_fields = ('name', 'email', 'phone')
    actions = ['confirm_selected', 'reject_selected']
    
    def confirm_selected(self, request, queryset):
        updated = queryset.update(status='confirmed')
        for booking in queryset:
            booking.send_confirmation_email()
        self.message_user(request, f'{updated} bookings confirmed.')
    confirm_selected.short_description = "Confirm selected bookings"
    
    def reject_selected(self, request, queryset):
        updated = queryset.update(status='rejected')
        for booking in queryset:
            booking.send_rejection_email()
        self.message_user(request, f'{updated} bookings rejected.')
    reject_selected.short_description = "Reject selected bookings"