from django.contrib import admin
from .models import PostOffice

class PostOfficeAdmin(admin.ModelAdmin):
    list_display = (
        'post_office_id', 'name', 'username', 'password_hash', 'role', 'pincode',
        'branch_type', 'delivery_status', 'circle', 'district', 'division', 'region',
        'state', 'country', 'latitude', 'longitude', 'created_at', 'updated_at'
    )
    search_fields = ('name', 'pincode', 'region')  # Optional, for searching
    list_filter = ('branch_type', 'delivery_status', 'region')  # Optional, for filtering

admin.site.register(PostOffice, PostOfficeAdmin)
