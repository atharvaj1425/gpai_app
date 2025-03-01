import requests
import re  # For removing special characters
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import PostOffice, DivisionalOffice
from django.contrib.auth.hashers import make_password
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
import json
from django.contrib.auth import logout
import requests  # For downloading images and interacting with Cloudinary
import google.generativeai as genai
from io import BytesIO
from django.utils.timezone import now
from .models import Image, PostOffice  # Importing models
import requests
from django.db import transaction
import google.generativeai as genai
import os
import logging
import re
from io import BytesIO
from datetime import datetime as now
import json  # Ensure you import the JSON module
import re
import logging
import requests
from gpai_app.models import PostOffice, Image
import logging

# Replace with your Google Maps Geolocation API key
GOOGLE_MAPS_API_KEY = "AIzaSyDOYZvj20isw_zi_d1iuCazAKVoBgssNJY"

# List of Mumbai PIN codes (you can add more if needed)
mumbai_pincodes = [
    "400001", "400002", "400003", "400004", "400005", "400006", "400007", "400008", "400009", 
    "400010", "400011", "400012", "400013", "400014", "400015", "400016", "400017", "400018", 
    "400019", "400020", "400021", "400022", "400023", "400024", "400025", "400026", "400027", 
    "400028", "400029", "400030", "400031", "400032", "400033", "400034", "400035", "400036", 
    "400037", "400038", "400039", "400040", "400041", "400042", "400043", "400044", "400045", 
    "400046", "400047", "400048", "400049", "400050", "400051", "400052", "400053", "400054", 
    "400055", "400056", "400057", "400058", "400059", "400060", "400061", "400062", "400063", 
    "400064", "400065", "400066", "400067", "400068", "400069", "400070", "400071", "400072", 
    "400073", "400074", "400075", "400076", "400077", "400078", "400079", "400080", "400081", 
    "400082", "400083", "400084", "400085", "400086", "400087", "400088", "400089", "400090", 
    "400091", "400092", "400093", "400094", "400095", "400096", "400097", "400098", "400099", 
    "400100", "400101", "400102", "400103", "400104", "400603", "400610", "400615", "400708"
]


def generate_username(name, region):
    """
    Generate a username by combining the post office name and region.
    Removes special characters and converts to lowercase.
    """
    clean_name = re.sub(r'\W+', '', name)  # Remove special characters
    clean_region = re.sub(r'\W+', '', region)  # Remove special characters
    return f"{clean_name}.{clean_region}".lower()

def generate_password(pin_code):
    """
    Generate a password by hashing the PIN code (or any other data).
    """
    return make_password(str(pin_code))  # Using PINCode directly as password

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from datetime import date
from .models import Campaign_Drive, RecyclingRequest, UtilityBill, Citizen

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home(request):
    # Filter options from the GET request
    venue = request.GET.get('venue', None)
    
    # Base query for ongoing campaigns (without any filters initially)
    today = date.today()
    ongoing_campaigns = Campaign_Drive.objects.filter(
        start_date__gt=now().date(),  # Campaigns starting in the future
        end_date__gte=today
    )

    # Apply Venue filter if provided
    if venue:
        ongoing_campaigns = ongoing_campaigns.filter(Venue__icontains=venue)

    if request.method == "POST":
        import json
        data = json.loads(request.body)
        campaign_id = data.get("campaign_id")
        if campaign_id:
            try:
                campaign = Campaign_Drive.objects.get(campaign_drive_id=campaign_id)
                campaign.number_of_people_registered += 1
                campaign.save()
                return JsonResponse({"success": True, "message": "Registered successfully!"})
            except Campaign_Drive.DoesNotExist:
                return JsonResponse({"success": False, "message": "Campaign not found."}, status=404)
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    # Fetch options for filters dynamically
    available_venues = Campaign_Drive.objects.values_list('Venue', flat=True).distinct()

    # Render homepage
    return render(request, 'gpai_app/home.html', {
        'ongoing_campaigns': ongoing_campaigns,
        'available_venues': available_venues,
    })

def get_post_offices(request):
    pincode = request.GET.get('pincode')
    if not pincode:
        return JsonResponse([], safe=False)
    post_offices = PostOffice.objects.filter(pincode=pincode).values('name')
    return JsonResponse(list(post_offices), safe=False)
        

def submit_recycling_request(request):
    if request.method == 'POST':
        name_of_recycler = request.POST.get('name_of_recycler')
        phone_no = request.POST.get('phone_no')
        recycle_item = request.POST.get('recycle_item')
        num_of_items = request.POST.get('num_of_items')
        quantity_to_recycle = request.POST.get('quantity_to_recycle')
        pincode = request.POST.get('pincode')
        post_office_name = request.POST.get('recycle_location')  # This is the name from the form input

        try:
            # Fetch the PostOffice instance based on the name provided
            post_office = PostOffice.objects.get(name=post_office_name)
            
            # Create a new RecyclingRequest instance
            RecyclingRequest.objects.create(
                name_of_recycler=name_of_recycler,
                phone_no=phone_no,
                recycle_item=recycle_item,
                num_of_items=num_of_items,
                quantity_to_recycle=quantity_to_recycle,
                pincode=pincode,
                post_office_name=post_office  # Use the correct field name here
            )
            return redirect('home')  # Redirect to the homepage or a success page
        except PostOffice.DoesNotExist:
            # Handle case where the post office is not found in the database
            return JsonResponse({'error': 'Post Office not found' }, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)




def login(request):
    error_message = None
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        
        if role == 'post_office_user':
            # Authenticate from PostOffice table
            try:
                user = PostOffice.objects.get(username=username)
                if user.password_hash == password:  # Use `check_password` if the password is hashed
                    # Save user info in session
                    request.session['username'] = username
                    request.session['role'] = role
                    return redirect('post_office_dashboard')
                else:
                    error_message = "Invalid credentials for Post Office User."
            except PostOffice.DoesNotExist:
                error_message = "Post Office User not found."

        elif role == 'divisional_office_user':
            # Authenticate from DivisionalOffice table
            try:
                user = DivisionalOffice.objects.get(username=username)
                if user.password_hash == password:  # Use `check_password` if the password is hashed
                    # Save user info in session
                    request.session['username'] = username
                    request.session['role'] = role
                    return redirect('divisional_office_dashboard')
                else:
                    error_message = "Invalid credentials for Divisional Office User."
            except DivisionalOffice.DoesNotExist:
                error_message = "Divisional Office User not found."
        
        elif role == 'citizen':
            # Authenticate from DivisionalOffice table
            try:
                user = Citizen.objects.get(username=username)
                if user.password == password:  # Use `check_password` if the password is hashed
                    # Save user info in session
                    request.session['username'] = username
                    request.session['role'] = role
                    return redirect('citizen_dashboard')
                else:
                    error_message = "Invalid credentials for User."
            except DivisionalOffice.DoesNotExist:
                error_message = "Divisional Office User not found."

    # If credentials are invalid or a GET request, render the login page
    return render(request, 'gpai_app/login.html', {'error_message': error_message})

from django.shortcuts import render, redirect
from .models import Citizen, Campaign_Drive

def citizen_dashboard(request):
    citizen_username = request.session.get('username')
    role = request.session.get('role')
    if role != 'citizen':
        return redirect('login')  # Redirect to login if no session data exists

    citizen = Citizen.objects.get(username=citizen_username)
    activity_entries = ActivityEntry.objects.filter(citizen=citizen)
    today = date.today()
    ongoing_campaigns = Campaign_Drive.objects.filter(
        start_date__gt=now().date(),  # Campaigns starting in the future
        end_date__gte=today
    )

    context = {
        'citizen': citizen,
        'ongoing_campaigns': ongoing_campaigns,
        'activity_entries': activity_entries,
    }
    return render(request, 'gpai_app/citizen_dashboard.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign_Drive, Citizen, ActivityEntry
#@login_required
def register_campaign(request, user_id, campaign_drive_id):
    campaign = get_object_or_404(Campaign_Drive, campaign_drive_id=campaign_drive_id)
    citizen = get_object_or_404(Citizen, user_id=user_id)

    # Check if already registered
    if ActivityEntry.objects.filter(citizen=citizen, campaign_drive=campaign).exists():
        messages.warning(request, "You are already registered for this campaign.")
    else:
        # Register citizen and award points
        ActivityEntry.objects.create(citizen=citizen, campaign_drive=campaign)
        citizen.points += 15
        citizen.save()
        messages.success(request, f"Successfully registered for {campaign.campaign_drive_name}!")

    return redirect('citizen_dashboard')  # Redirect to your dashboard page



def user_logout(request):
    logout(request)
    return redirect('login') 

def post_office_dashboard(request):
    # Get the logged-in user's post office based on session (assuming username is stored in session)
    post_office_username = request.session.get('username')
    role = request.session.get('role')
    if role != 'post_office_user':
        return redirect('login')  # Redirect to login if no session data exists

    # Get the post office object
    post_office = PostOffice.objects.get(username=post_office_username)

    fetch_and_populate_images()
    process_images_with_gemini()

    # Get the latest image for this post office based on the timestamp
    latest_image = Image.objects.filter(post_office=post_office) \
        .annotate(latest_timestamp=Max('timestamp')) \
        .order_by('-latest_timestamp').first()

    # Check if the cleanliness status is "dirty"
    is_unclean = latest_image.cleanliness_status.lower() == 'dirty' if latest_image else False

    # Prepare context to pass to template
    context = {
        'post_office': post_office,
        'latest_image': latest_image,  # This will give the latest image or None
        'is_unclean': is_unclean,  # Pass a flag if the post office is unclean
    }
    
    return render(request, 'gpai_app/post_office_dashboard.html', context)

import ast
from collections import defaultdict

def divisional_office_dashboard(request):
    # Retrieve user info from the session
    username = request.session.get('username')
    role = request.session.get('role')

    if role != 'divisional_office_user':
        return redirect('login')  # Redirect to login if not authorized

    # Fetch the divisional office details
    user_data = DivisionalOffice.objects.get(username=username)
    
    # Fetch post offices under this division
    post_offices = PostOffice.objects.filter(division=user_data.name)

    fetch_and_populate_images()
    process_images_with_gemini()

    # Fetch latest image for each post office
    latest_images = Image.objects.filter(post_office__in=post_offices) \
        .values('post_office') \
        .annotate(latest_timestamp=Max('timestamp')) \
        .order_by('-latest_timestamp')

    # Create dictionaries to hold the mappings
    cleanliness_status_mapping = {}
    cleanliness_score_mapping = {}
    timestamp_mapping = {}

    # Process the latest images for each post office
    for item in latest_images:
        post_office_id = item['post_office']
        latest_timestamp = item['latest_timestamp']
        latest_image = Image.objects.filter(post_office_id=post_office_id, timestamp=latest_timestamp).first()

        if latest_image:
            cleanliness_status_mapping[post_office_id] = latest_image.cleanliness_status
            cleanliness_score_mapping[post_office_id] = latest_image.cleanliness_score
            timestamp_mapping[post_office_id] = latest_image.timestamp

    # Serialize the post offices data for rendering pins
    post_offices_data = [
        {
            'name': office.name,
            'latitude': float(office.latitude) if office.latitude else None,
            'longitude': float(office.longitude) if office.longitude else None,
            'pincode': office.pincode,
            'branch_type': office.branch_type,
            'delivery_status': office.delivery_status,
            'cleanliness_status': cleanliness_status_mapping.get(office.post_office_id, "Unknown"),
            'cleanliness_score': cleanliness_score_mapping.get(office.post_office_id, "Unknown"),
            'timestamp': timestamp_mapping.get(office.post_office_id, "Unknown")
        }
        for office in post_offices if office.latitude and office.longitude
    ]

    # Waste categorization logic (separate from the map pin serialization)
    waste_type_counts = defaultdict(lambda: defaultdict(int))

    # Process waste types from the latest images
    for item in latest_images:
        post_office_id = item['post_office']
        latest_timestamp = item['latest_timestamp']
        latest_image = Image.objects.filter(post_office_id=post_office_id, timestamp=latest_timestamp).first()

        if latest_image:
            waste_type = latest_image.waste_type if latest_image.waste_type else "[]"
            try:
                waste_types = ast.literal_eval(waste_type)
            except (ValueError, SyntaxError):
                waste_types = []  # Default to an empty list if parsing fails

            for waste in waste_types:
                if 'plastic' in waste.lower():
                    waste_type_counts['plastic'][post_office_id] += 1
                if 'paper' in waste.lower():
                    waste_type_counts['paper'][post_office_id] += 1
                if 'cardboard' in waste.lower():
                    waste_type_counts['cardboard'][post_office_id] += 1
                if 'organic' in waste.lower():
                    waste_type_counts['organic'][post_office_id] += 1

    # Find the top 5 post offices for each waste type
    top_post_offices_by_waste = {
        waste_type: sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for waste_type, counts in waste_type_counts.items()
    }

    # Prepare data for charts
    chart_data = {}
    for waste_type, post_offices in top_post_offices_by_waste.items():
        chart_data[waste_type] = {
            'labels': [PostOffice.objects.get(post_office_id=post_office_id).name for post_office_id, _ in post_offices],
            'data': [count for _, count in post_offices]
        }

    # Pass all the data to the context
    context = {
        'user_data': user_data,
        'post_offices': post_offices,
        'post_offices_json': json.dumps(post_offices_data, cls=DjangoJSONEncoder),
        'chart_data': chart_data,  # Pass chart data for waste categorization
    }
    return render(request, 'gpai_app/divisional_office_dashboard.html', context)



















# def divisional_office_dashboard(request):
#     # Retrieve user info from the session
#     username = request.session.get('username')
#     role = request.session.get('role')

#     if role != 'divisional_office_user':
#         return redirect('login')  # Redirect to login if not authorized

#     # Fetch the divisional office details
#     user_data = DivisionalOffice.objects.get(username=username)
    
#     # Fetch post offices under this division
#     post_offices = PostOffice.objects.filter(division=user_data.name)

#     fetch_and_populate_images()
#     process_images_with_gemini()

#     # Fetch latest image for each post office
#     latest_images = Image.objects.filter(post_office__in=post_offices) \
#         .values('post_office') \
#         .annotate(latest_timestamp=Max('timestamp')) \
#         .order_by('-latest_timestamp')

#     # Create dictionaries to hold the mappings
#     cleanliness_status_mapping = {}
#     cleanliness_score_mapping = {}
#     timestamp_mapping = {}

#     for item in latest_images:
#         post_office_id = item['post_office']
#         latest_timestamp = item['latest_timestamp']
#         latest_image = Image.objects.filter(post_office_id=post_office_id, timestamp=latest_timestamp).first()

#         if latest_image:
#             cleanliness_status_mapping[post_office_id] = latest_image.cleanliness_status
#             cleanliness_score_mapping[post_office_id] = latest_image.cleanliness_score
#             timestamp_mapping[post_office_id] = latest_image.timestamp
#     # Serialize the post offices data for rendering pins
#     post_offices_data = [
#         {
#             'name': office.name,
#             'latitude': float(office.latitude) if office.latitude else None,
#             'longitude': float(office.longitude) if office.longitude else None,
#             'pincode': office.pincode,
#             'branch_type': office.branch_type,
#             'delivery_status': office.delivery_status,
#             'cleanliness_status': cleanliness_status_mapping.get(office.post_office_id, "Unknown"),
#             'cleanliness_score': cleanliness_score_mapping.get(office.post_office_id, "Unknown"),
#             'timestamp': timestamp_mapping.get(office.post_office_id, "Unknown")
#         }
#         for office in post_offices if office.latitude and office.longitude
#     ]
#     context = {
#         'user_data': user_data,
#         'post_offices': post_offices,
#         'post_offices_json': json.dumps(post_offices_data, cls=DjangoJSONEncoder),
#     }
#     return render(request, 'gpai_app/divisional_office_dashboard.html', context)


# Configure Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# GENAI Configuration
API_KEY = "AIzaSyABso2hO7CjatfKPB6WoaP48QGeKZ8YsEw"
if not API_KEY:
    logger.error("GENAI API key is not set.")
genai.configure(api_key=API_KEY)

# Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Safety Settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=MODEL_CONFIG,
    safety_settings=SAFETY_SETTINGS
)

# Utility Functions
def fetch_image_content(image_url):                  
    """Fetch image content for processing."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return [{"mime_type": "image/png", "data": BytesIO(response.content).getvalue()}]
    except Exception as e:
        logger.error(f"Error fetching image content: {e}")
        raise RuntimeError(f"Failed to process image URL: {image_url}")



logger = logging.getLogger(__name__)

def safe_search(pattern, text):
    """
    Utility function to safely search a pattern in the given text and return the first group match.
    Returns None if no match is found.
    """
    match = re.search(pattern, text)
    return match.group(1) if match else None

def parse_gemini_output(output_text):
    """
    Parse output from the Gemini model using regex for robustness.
    Handles JSON-like responses with or without invalid formatting.
    """
    try:
        # Log the raw output for debugging
        logger.debug(f"Raw Gemini output: {output_text}")

        # Extract data using regular expressions
        status = safe_search(r'"status":\s*"([^"]+)"', output_text)
        cleanliness_score = safe_search(r'"cleanliness_score":\s*(\d+(\.\d+)?)', output_text)
        waste_classification = safe_search(r'"garbage_type":\s*\[([^\]]+)\]', output_text)
        garbage_percentage = safe_search(r'"percentage_waste_area":\s*(\d+(\.\d+)?)', output_text)
        is_clean = safe_search(r'"is_clean":\s*(\d+(\.\d+)?)', output_text)

        # Process waste_classification (convert to a list if it's not empty)
        if waste_classification:
            waste_classification = [item.strip().strip('"') for item in waste_classification.split(",")]

        # Log the parsed values for debugging
        logger.debug(f"Parsed values - Status: {status}, Cleanliness Score: {cleanliness_score}, "
                     f"Waste Classification: {waste_classification}, Garbage Percentage: {garbage_percentage}")

        # Return structured data
        return {
            "status": status,
            "cleanliness_score": float(cleanliness_score) if cleanliness_score else None,
            "waste_classification": waste_classification ,
            "garbage_percentage": float(garbage_percentage) if garbage_percentage else None,
            "is_clean" : is_clean 

        }
    except Exception as e:
        logger.error(f"Error parsing Gemini output: {e}")
        return {"error": f"Unexpected error: {e}"}


logger = logging.getLogger(__name__)

def fetch_and_populate_images():
    """Fetch and populate images from Cloudinary."""
    cloudinary_api_url = "https://api.cloudinary.com/v1_1/dswkvnomk/resources/image?context=true"
    api_key = "651324994684599"
    api_secret = "JgsKsiuw49IdP5uN-SFAJfG51Ac"
    auth = (api_key, api_secret)

    try:
        # Fetch images from Cloudinary
        response = requests.get(cloudinary_api_url, auth=auth)
        response.raise_for_status()
        data = response.json()

        # Loop through the images and save them to the database
        for resource in data.get("resources", []):
            image_url = resource.get("secure_url")
            context = resource.get("context", {}).get("custom", {})
            latitude = context.get("latitude")
            longitude = context.get("longitude")
            timestamp = context.get("timestamp")

            # Ensure latitude and longitude are present
            if latitude and longitude:
                # Find the related PostOffice
                post_office = PostOffice.objects.filter(latitude=latitude, longitude=longitude).first()

                if post_office:
                    # Avoid duplicate entries
                    if not Image.objects.filter(image_url=image_url).exists():
                        Image.objects.create(
                            post_office=post_office,
                            image_url=image_url,
                            latitude=latitude,
                            longitude=longitude,
                            timestamp=timestamp
                        )
                        logger.info(f"Added image: {image_url} to the database.")
            else:
                logger.warning(f"Image {image_url} does not have latitude/longitude metadata.")

    except Exception as e:
        logger.error(f"Error fetching images from Cloudinary: {e}")


def process_images_with_gemini():
    """Process images using the Gemini model."""
    from gpai_app.models import Image

    unprocessed_images = Image.objects.filter(cleanliness_score__isnull=True)
    if not unprocessed_images.exists():
        logger.info("No unprocessed images found.")
        return

    system_prompt = """
    You are an AI specialist in cleanliness and waste classification. 
    Your task is to analyze input images taken from CCTV footage of post offices. 
    Ignore the presence of people in the images and focus only on assessing cleanliness.
    """

    user_prompt = f"""
    Analyze this image and determine:
    1. Whether the scene is clean or dirty.
    2. If dirty, provide a cleanliness score (1-10) and classify the waste detected in the image into categories.
    3. Provide the output only in a dictionary format with the following keys:
       - "status": Clean or Dirty
       - "cleanliness_score": Numerical value between 1-10
       - "garbage_type": List of detected garbage types, if any (e.g., plastic, cardboard, organic, etc.) else print no garbage
       - "is_clean": if clean give true else flase
    """

    for image in unprocessed_images:
        try:
            logger.debug(f"Processing image ID: {image.image_id}")
            image_content = fetch_image_content(image.image_url)
            input_prompt = [system_prompt, image_content[0], user_prompt]
            response = model.generate_content(input_prompt)

            if hasattr(response, "text"):
                output_data = parse_gemini_output(response.text)
                if "error" not in output_data:
                    update_image_record(image, output_data)
                    logger.info(f"Image ID {image.image_id} processed successfully.")
                else:
                    logger.error(f"Error parsing Gemini response for image {image.image_id}: {output_data['error']}")
            else:
                logger.error(f"Invalid response from Gemini for image {image.image_id}")
        except Exception as e:
            logger.error(f"Error processing image ID {image.image_id}: {e}")
            
def update_image_record(image, data):
    """Safely update image record with model output."""
    try:
        with transaction.atomic():
            image.cleanliness_score = data.get("cleanliness_score")
            image.cleanliness_status = data.get("status")
            image.waste_type = data.get("waste_classification")
            image.is_clean = data.get("is_clean")
            image.save()
    except Exception as e:
        logger.error(f"Error updating image record: {e}")
        raise

from django.db.models import Max

def post_office_monitored(request):
    """Display the latest image of post offices monitored by the logged-in divisional office user."""
    username = request.session.get('username')
    role = request.session.get('role')

    # Check if the user is logged in and has the appropriate role
    if role != 'divisional_office_user':
        return redirect('login')  # Redirect to login if not authorized

    # Fetch the divisional office details
    user_data = DivisionalOffice.objects.get(username=username)
    
    # Fetch post offices under this division
    post_offices = PostOffice.objects.filter(division=user_data.name)
    campaigns = Campaign_Drive.objects.filter(post_office__in=post_offices)


    fetch_and_populate_images()
    process_images_with_gemini()

    # Annotate each post office with the latest timestamp of associated images
    latest_images = Image.objects.filter(post_office__in=post_offices) \
        .values('post_office') \
        .annotate(latest_timestamp=Max('timestamp')) \
        .order_by('-latest_timestamp')

    # Fetch the images for each post office based on the latest timestamp
    images = []
    for post_office in post_offices:
        latest_image = Image.objects.filter(post_office=post_office, timestamp=latest_images.get(post_office=post_office)['latest_timestamp']).first()
        if latest_image:
            images.append(latest_image)

    

    # Prepare the user data for context
    user_data_context = {
        'user_id': request.session.get('user_id'),
        'username': request.session.get('username'),
        'role': request.session.get('role'),
    }

    # Pass the filtered images and other context data to the template
    context = {
        'user_data': user_data_context,
        'post_offices': post_offices,
        'images': images,  # Only the latest image for each post office
        'campaigns': campaigns,
        'divisional_office_name': user_data.name,
    }

    return render(request, 'gpai_app/post_office_monitored.html', context)

from django.shortcuts import render, get_object_or_404
from .models import PostOffice, Image
from datetime import datetime

def view_post_office_history(request, post_office_id):
    # Get the selected post office
    post_office = get_object_or_404(PostOffice, post_office_id=post_office_id)

    # Get all images related to that post office
    images = Image.objects.filter(post_office=post_office)

    # If a date is selected, filter images by timestamp
    if request.method == "POST":
        selected_date = request.POST.get('selected_date')
        if selected_date:
            # Convert to a datetime object to filter based on date
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
            images = images.filter(timestamp__date=selected_date)

    return render(request, 'gpai_app/view_post_office_history.html', {
        'post_office': post_office,
        'images': images,
        'divisional_office_name': post_office.division
    })


def view_campaign_history(request, post_office_id):
    post_office = get_object_or_404(PostOffice, post_office_id=post_office_id)
    
    # Separate campaigns into ongoing and completed
    campaigns = post_office.campaigns.all()
    ongoing_campaigns = campaigns.filter(end_date__gte=now().date())
    completed_campaigns = campaigns.filter(end_date__lt=now().date())
    return render(request, "gpai_app/campaign_history.html", {'post_office': post_office, 'ongoing_campaigns': ongoing_campaigns,'completed_campaigns': completed_campaigns,})



from django.shortcuts import render, get_object_or_404
from .models import PostOffice

import os
import json
import re
from pathlib import Path
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import UtilityBill, PostOffice
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyABso2hO7CjatfKPB6WoaP48QGeKZ8YsEw")


# Utility function to format images for Gemini
def gemini_extract(image_paths, system_prompt, user_prompt):
    """
    Utility function to process images using Google Gemini API.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"temperature": 0.2, "top_p": 1, "top_k": 32, "max_output_tokens": 4096}
        )
        images = [{"mime_type": "image/png", "data": Path(path).read_bytes()} for path in image_paths]
        input_prompt = [system_prompt, *images, user_prompt]

        response = model.generate_content(input_prompt)
        return getattr(response, 'text', "No response text found.")
    except Exception as e:
        return f"Error: {str(e)}"


import re
import logging
import json

# Configure logger for debugging
logger = logging.getLogger(__name__)

def parse_gemini_output_utility(output_text):
    """
    Parse output from the Gemini model using regex for robustness.
    Extracts the JSON response with keys like 'month-year', 'electricity_units_consumed', etc.
    """
    try:
        # Log the raw output for debugging
        logger.debug(f"Raw Gemini output: {output_text}")

        # Use regex to extract JSON-like structure
        json_match = re.search(r'\{.*?\}', output_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON-like structure found in the output text.")

        # Extract JSON string
        json_str = json_match.group(0)
        logger.debug(f"Extracted JSON string: {json_str}")

        # Parse JSON string into a Python dictionary
        data = json.loads(json_str)

        # Log parsed data for debugging
        logger.debug(f"Parsed JSON data: {data}")

        # Validate required keys and return structured data
        required_keys = ['month-year', 'electricity_units_consumed', 'electricity_bill_amount', 
                         'water_units_consumed', 'water_bill_amount']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing key in extracted JSON: {key}")

        return {
            "month_year": data.get("month-year"),
            "electricity_units_consumed": data.get("electricity_units_consumed"),
            "electricity_bill_amount": data.get("electricity_bill_amount"),
            "water_units_consumed": data.get("water_units_consumed"),
            "water_bill_amount": data.get("water_bill_amount"),
        }

    except json.JSONDecodeError as json_err:
        logger.error(f"JSON decoding error: {json_err}")
        return {"error": "Invalid JSON format."}
    except Exception as e:
        logger.error(f"Error parsing Gemini output: {e}")
        return {"error": f"Unexpected error: {e}"}



def utility_bills(request, post_office_id):
    """
    Displays LiFE practices for a specific post office and handles utility bill uploads.
    """
    post_office = get_object_or_404(PostOffice, post_office_id=post_office_id)
    utility_bills = UtilityBill.objects.filter(post_office=post_office).order_by('-month_year')


    if request.method == 'POST' and 'upload_bills' in request.POST:
        electricity_bill = request.FILES.get('electricity_bill')
        water_bill = request.FILES.get('water_bill')

        if not electricity_bill or not water_bill:
            messages.error(request, "Please provide both the electricity and water bills.")
            return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})

        # Save files temporarily
        temp_electricity_path = f'temp_electricity_{electricity_bill.name}'
        temp_water_path = f'temp_water_{water_bill.name}'

        try:
            with open(temp_electricity_path, 'wb') as f:
                f.write(electricity_bill.read())

            with open(temp_water_path, 'wb') as f:
                f.write(water_bill.read())

            # Call Gemini to process
            system_prompt = """
                You are a highly accurate and specialized system designed to extract and analyze data from Electricity Bills and Water Bills. 
                Your task is to process input images of these bills, classify them correctly, and extract only the required data accurately. 
                Ensure precise classification of the bills and validation of the extracted data for correctness. 
                Handle any ambiguities in the input logically and resolve discrepancies to produce error-free output.
               """
            user_prompt = """
               You are provided with two input images: one of an Electricity Bill and one of a Water Bill. 
                Your task is to:
                1. Classify each bill accurately as either an Electricity Bill or a Water Bill, even if the user mistakenly uploads them in the wrong fields.
                2. Extract only the **current month-year** in the format `MM-YYYY` from each bill.
                3. For the Electricity Bill:
                - Extract the **total electricity units consumed** for the current month and the latest year for example there will be units consumed for Nov 23 and Nov 24 so you will extract the units for the latest i.e. Nov 24.
                - Extract the **bill amount to be paid before the deadline** for the current month. This should **exclude previous charges, penalties, or dues**.
                4. For the Water Bill:
                - Extract the **current water units consumed** for the month.
                - Extract the **current bill amount** for the month. This must exclude any additional charges or dues.

                **Output Requirements:**
                - Ensure both bills belong to the **same month-year**. If they do not, identify the discrepancy and indicate it in the output.
                - If the user mistakenly provides two bills of the same type, handle the situation logically and provide a correction note in the output.
                - Return the output as a single JSON object with the following keys:
                - `"month-year"`: Month-Year in `MM-YYYY` format (common for both bills).
                - `"electricity_units_consumed"`: Total units of electricity consumed (integer or float).
                - `"electricity_bill_amount"`: Bill amount to pay before the deadline (float).
                - `"water_units_consumed"`: Total water consumption (integer or float).
                - `"water_bill_amount"`: Current water bill amount (float).

                **Example Output:**
                ```json
                {
                    "month-year": "09-2024",
                    "electricity_units_consumed": 150,
                    "electricity_bill_amount": 1200.50,
                    "water_units_consumed": 30,
                    "water_bill_amount": 500.75
                }
               """
            # system_prompt = """
            #    You are a specialist in comprehending Electricity Bills.
            #    Input images in the form of Electricity Bills will be provided to you,
            #    and your task is to parse the text present in the image and then respond to questions based on the content of the input image.
            #    """
            #user_prompt = "What is the total unit consumed and the total amount to pay according to this image of the electricity bill and month/year of this electricity bill give the output in the jason format658?"
            gemini_output = gemini_extract([temp_electricity_path, temp_water_path], system_prompt, user_prompt)

            # Parse Gemini output
            parsed_data = parse_gemini_output_utility(gemini_output)
            if "error" in parsed_data:
                messages.error(request, parsed_data["error"])
                return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})

            # Pass parsed data to the next step for user confirmation
            return render(request, 'gpai_app/utility_bills.html', {
                'post_office': post_office,
                'extracted_json': json.dumps(parsed_data),
            })

        except Exception as e:
            messages.error(request, f"An error occurred while processing the bills: {e}")
            return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})

        finally:
            # Clean up temporary files
            os.remove(temp_electricity_path)
            os.remove(temp_water_path)

    if request.method == 'POST' and 'confirm_bills' in request.POST:
        extracted_json = request.POST.get('extracted_json')

        try:
            # Parse extracted JSON from user confirmation
            data = json.loads(extracted_json)

            # Check for duplicates
            if UtilityBill.objects.filter(post_office_id=post_office_id, month_year=data['month_year']).exists():
                messages.error(request, "Record already exists for this post office and month.")
                return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})

            # Save data to DB
            UtilityBill.objects.create(
                post_office_id=post_office_id,
                month_year=data['month_year'],
                electricity_units_consumed=data.get('electricity_units_consumed'),
                electricity_bill_amount=data.get('electricity_bill_amount'),
                water_units_consumed=data.get('water_units_consumed'),
                water_bill_amount=data.get('water_bill_amount'),
            )
            messages.success(request, "Utility Bill saved successfully.")
            return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})

        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON format.")
            return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office})

    return render(request, 'gpai_app/utility_bills.html', {'post_office': post_office, 'utility_bills': utility_bills})

from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from .models import PostOffice, Campaign_Drive, RecyclingRequest
from .forms import CampaignForm

def drive_campaigns(request, post_office_id):
    # Fetch the post office
    post_office = get_object_or_404(PostOffice, post_office_id=post_office_id)
    
    # Separate campaigns into ongoing and completed
    campaigns = post_office.campaigns.all()
    ongoing_campaigns = campaigns.filter(end_date__gte=now().date())
    completed_campaigns = campaigns.filter(end_date__lt=now().date())

    # Handle campaign creation
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.post_office = post_office
            campaign.save()
            return redirect('drive_campaigns', post_office_id=post_office_id)
    else:
        form = CampaignForm()

    return render(request, 'gpai_app/campaigns.html', {
        'post_office': post_office,
        'ongoing_campaigns': ongoing_campaigns,
        'completed_campaigns': completed_campaigns,
        'form': form
    })

def life_practices(request, post_office_id):
    post_office = get_object_or_404(PostOffice, post_office_id=post_office_id)
    recyclerequests = RecyclingRequest.objects.filter(post_office_name_id=post_office)

    return render(request,"gpai_app/life_practices.html", {'post_office': post_office, 'recyclerequests': recyclerequests})






def image_table(request):
    images = Image.objects.all()
    return render(request, 'gpai_app/image_table.html', {'images': images})

def fetch_postoffice(request):
    processed_pincodes = 0  # To track how many PIN codes were successfully processed
    failed_pincodes = []  # To track PIN codes that failed to process

    # Iterate over the hardcoded list of Mumbai PIN codes
    for pincode in mumbai_pincodes:
        api_url = f"https://api.postalpincode.in/pincode/{pincode}"
        
        # Make a GET request to the postal API for each PIN code
        response = requests.get(api_url)
        data = response.json()

        # Log the API response for debugging
        print(f"Response for PIN code {pincode}: {data}")
        
        # Check if the API response status is "Success"
        if data[0]["Status"] == "Success":
            post_offices = data[0]["PostOffice"]
            for office in post_offices:
                # Ensure 'PINCode' exists in the post office data
                pin_code = office.get("PINCode", pincode)  # Fallback to the current pincode if not present
                
                # Now we use the name of the post office, district, and state to fetch the location data from Google Maps
                post_office_name = office["Name"]
                district = office.get("District", "")
                state = office.get("State", "")
                address = f"{post_office_name} post office, {district}, {state}, {pin_code}"

                maps_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
                maps_response = requests.get(maps_url)
                maps_data = maps_response.json()

                latitude = longitude = None
                if maps_data["status"] == "OK":
                    location_data = maps_data["results"][0]["geometry"]["location"]
                    latitude = location_data["lat"]
                    longitude = location_data["lng"]
                
                # Generate username and use PINCode as the password
                username = generate_username(office["Name"], office["Region"])
                password = pin_code  # Using the fetched PINCode as password

                # Retrieve or create the DivisionalOffice instance
                division_name = office["Division"]
                divisional_office, created = DivisionalOffice.objects.get_or_create(
                    name=division_name,
                    defaults={
                    'username': f"{division_name.lower()}_username",  # You can generate the username as needed
                    'password_hash': f"{district.lower().replace(' ', '_')}.{state.lower().replace(' ', '_')}",  # Format: district.state4
                    }
                )
                # Insert data into PostOffice table
                PostOffice.objects.create(
                    name=office["Name"],
                    username=username,
                    password_hash=password,  # Using PINCode directly as password
                    pincode=pin_code,
                    branch_type=office["BranchType"],
                    delivery_status=office["DeliveryStatus"],
                    circle=office["Circle"],
                    district=office.get("District", None),
                    division=divisional_office,  # Assign the DivisionalOffice instance here
                    region=office["Region"],
                    state=office.get("State", None),
                    country=office.get("Country", "India"),
                    latitude=latitude,
                    longitude=longitude,
                )

            processed_pincodes += 1  # Increment for each successful PIN code
        else:
            failed_pincodes.append(pincode)  # Track failed PIN codes

    # Log the final status
    print(f"Processed {processed_pincodes} PIN codes successfully.")
    print(f"Failed to process PIN codes: {failed_pincodes}")

    # Return a response after processing all PIN codes
    message = f"Data processing complete for {processed_pincodes} PIN codes."
    if failed_pincodes:
        message += f" Failed to process PIN codes: {', '.join(failed_pincodes)}."

    return HttpResponse(message)


