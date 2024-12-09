from django.db import models
from datetime import date

class DivisionalOffice(models.Model):
    divisional_office_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)  # Unique division name
    username = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='divisional_office_user')
    # region = models.CharField(max_length=255)
    # latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PostOffice(models.Model):
    post_office_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='post_office_user')
    pincode = models.CharField(max_length=10)
    branch_type = models.CharField(max_length=50)
    delivery_status = models.CharField(max_length=50)
    circle = models.CharField(max_length=50)
    district = models.CharField(max_length=100, null=True, blank=True)
    division = models.ForeignKey(
        DivisionalOffice,
        on_delete=models.CASCADE,
        to_field='name',  # Links to DivisionalOffice.name
        related_name='post_offices'
    )
    region = models.CharField(max_length=255)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=50, default='India')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    post_office = models.ForeignKey(
        PostOffice, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image_url = models.URLField()
    timestamp = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    cleanliness_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_clean = models.BooleanField(null=True, blank=True)
    cleanliness_status = models.CharField(max_length=50, null=True, blank=True)
    waste_type = models.CharField(max_length=500, null=True, blank=True)  # e.g., Plastic, Organic
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image {self.image_id} - {self.post_office.name}"

class UtilityBill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    post_office = models.ForeignKey('PostOffice', on_delete=models.CASCADE, related_name='utility_bills')
    
    # Billing period
    month_year = models.CharField(max_length=7, help_text="Format: MM-YYYY")  # Input as MM-YYYY

    # Electricity-related fields
    electricity_units_consumed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Electricity Units Consumed")
    electricity_bill_amount = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Electricity Bill Amount")
    
    # Water-related fields
    water_units_consumed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Water Units Consumed")
    water_bill_amount = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Water Bill Amount")

    class Meta:
        unique_together = ('post_office', 'month_year')  # Ensure one record per post office per month-year
        verbose_name = "Utility Bill"
        verbose_name_plural = "Utility Bills"

    def __str__(self):
        return f"Utility Bill - {self.post_office.name} ({self.month_year})"

class Campaign_Drive(models.Model):
    campaign_drive_id = models.AutoField(primary_key=True)  # Unique ID for each campaign
    post_office = models.ForeignKey(
        'PostOffice',  # Reference to PostOffice model
        on_delete=models.CASCADE,
        related_name='campaigns'
    )
    campaign_drive_name = models.CharField(max_length=255)  # Name of the drive/campaign
    description = models.TextField(max_length=65535, blank=True, null=True)  # Detailed description about the drive
    start_date = models.DateField()  # Start date of the campaign
    end_date = models.DateField()  # End date of the campaign
    Venue = models.CharField(max_length=255, null=True)
    number_of_people_registered = models.PositiveIntegerField(default=0)  # Number of people registered

    def is_active(self):
        """
        Check if the campaign is active based on the current date.
        """
        today = date.today()
        return self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.campaign_drive_name} ({self.post_office.name})"

class RecyclingRequest(models.Model):
    recycle_id = models.AutoField(primary_key=True)  # Auto-incrementing field
    name_of_recycler = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=15)
    recycle_item = models.CharField(max_length=255)
    num_of_items = models.PositiveIntegerField()
    quantity_to_recycle = models.FloatField()
    pincode = models.CharField(max_length=6)
    post_office_name = models.ForeignKey('PostOffice', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name_of_recycler} - {self.recycle_item}"


class ComplianceScore(models.Model):
    compliance_id = models.AutoField(primary_key=True)
    post_office = models.ForeignKey(
        PostOffice, 
        on_delete=models.CASCADE, 
        related_name='compliance_scores'
    )
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Compliance for {self.post_office.name}: {self.compliance_score}"