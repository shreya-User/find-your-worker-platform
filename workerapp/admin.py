from django.contrib import admin
from .models import booking
# Register your models here.

from .models import Worker
from .models import booking,feedback,notification,review,Customer

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved','is_cancelled')
    list_filter = ('is_approved','is_cancelled')
    search_fields = ('user', 'firstname', 'lastname')
    actions = ['approve_bookings']

    def approve_bookings(self, request, queryset):
        queryset.update(is_approved=True)
    approve_bookings.short_description = "Approve selected bookings"

admin.site.register(booking, BookingAdmin)

admin.site.register(Worker)

admin.site.register(feedback)
admin.site.register(notification)
admin.site.register(review)
admin.site.register(Customer)