from django import forms
from .models import Campaign_Drive

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign_Drive
        fields = [
            'campaign_drive_name',  # Name of the campaign/drive
            'description',          # Description of the campaign/drive
            'start_date',           # Start date
            'end_date',             # End date
            'Venue'
            # 'number_of_people_registered',  # Number of participants
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),  # Date picker for start date
            'end_date': forms.DateInput(attrs={'type': 'date'}),    # Date picker for end date
        }


from django import forms
from .models import RecyclingRequest, PostOffice

class RecyclingRequestForm(forms.ModelForm):
    class Meta:
        model = RecyclingRequest
        fields = ['name_of_recycler', 'phone_no', 'recycle_item', 'num_of_items', 'quantity_to_recycle', 'pincode', 'post_office_name']
    
    # Dynamically populate the PostOffice choices based on the selected pincode
    def __init__(self, *args, **kwargs):
        super(RecyclingRequestForm, self).__init__(*args, **kwargs)
        self.fields['post_office_name'].queryset = PostOffice.objects.none()

        if 'pincode' in self.data:
            try:
                pincode = self.data.get('pincode')
                self.fields['post_office_name'].queryset = PostOffice.objects.filter(pincode=pincode)
            except (ValueError, TypeError):
                pass

    # Override the save method if needed to handle post_office_name as a ForeignKey
    def save(self, commit=True):
        instance = super(RecyclingRequestForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance
