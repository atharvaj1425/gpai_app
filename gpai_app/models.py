from django.db import models

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


class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    post_office = models.ForeignKey(
        PostOffice, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    cleanliness_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_clean = models.BooleanField(null=True, blank=True)
    cleanliness_status = models.CharField(max_length=50, null=True, blank=True)
    waste_type = models.CharField(max_length=50, null=True, blank=True)  # e.g., Plastic, Organic
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image {self.image_id} - {self.post_office.name}"


# class UtilityBill(models.Model):
#     bill_id = models.AutoField(primary_key=True)
#     post_office = models.ForeignKey(PostOffice, on_delete=models.CASCADE, related_name='utility_bills')
#     bill_type = models.CharField(max_length=20, choices=[('water', 'Water'), ('electricity', 'Electricity')])
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.bill_type.capitalize()} Bill - {self.post_office.name}"
