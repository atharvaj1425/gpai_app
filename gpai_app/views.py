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

    # If credentials are invalid or a GET request, render the login page
    return render(request, 'gpai_app/login.html', {'error_message': error_message})

def user_logout(request):
    logout(request)
    return redirect('login') 

def post_office_dashboard(request):
    # Retrieve user info from the session
    username = request.session.get('username')
    role = request.session.get('role')

    if role != 'post_office_user':
        return redirect('')  # Redirect to login if not authorized

    # Use `username` for fetching data or displaying user-specific information
    user_data = PostOffice.objects.get(username=username)
    return render(request, 'gpai_app/post_office_dashboard.html', {'user_data': user_data})


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
    
    # Serialize the post offices data for rendering pins
    post_offices_data = [
        {
            'name': office.name,
            'latitude': float(office.latitude) if office.latitude else None,
            'longitude': float(office.longitude) if office.longitude else None,
            'pincode': office.pincode,
            'branch_type': office.branch_type,
            'delivery_status': office.delivery_status,
        }
        for office in post_offices if office.latitude and office.longitude
    ]

    context = {
        'user_data': user_data,
        'post_offices': post_offices,
        'post_offices_json': json.dumps(post_offices_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'gpai_app/divisional_office_dashboard.html', context)

# Configure the API key
genai.configure(api_key="AIzaSyABso2hO7CjatfKPB6WoaP48QGeKZ8YsEw")

# Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Safety Settings of Model
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=MODEL_CONFIG,
    safety_settings=safety_settings
)

# Fetch and populate images from Cloudinary
def fetch_and_populate_images():
    try:
        cloudinary_api_url = "https://api.cloudinary.com/v1_1/dswkvnomk/resources/image"
        api_key = "651324994684599"
        api_secret = "JgsKsiuw49IdP5uN-SFAJfG51Ac"
        auth = (api_key, api_secret)

        response = requests.get(cloudinary_api_url, auth=auth)
        if response.status_code == 200:
            data = response.json()

            for resource in data.get("resources", []):
                image_url = resource.get("secure_url")
                timestamp = resource.get("created_at")

                # Extract custom metadata if available
                latitude = resource.get("context", {}).get("custom", {}).get("latitude", None)
                longitude = resource.get("context", {}).get("custom", {}).get("longitude", None)


                if latitude and longitude:
                    post_office = PostOffice.objects.filter(latitude=latitude, longitude=longitude).first()
                    if post_office and not Image.objects.filter(image_url=image_url).exists():
                        Image.objects.create(
                            post_office=post_office,
                            image_url=image_url,
                            latitude=latitude,
                            longitude=longitude,
                            timestamp=timestamp
                        )
    except Exception as e:
        print(f"Error fetching images: {e}")

# Process images with Gemini
def image_format_from_url(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return [{"mime_type": "image/png", "data": BytesIO(response.content).getvalue()}]
    except Exception as e:
        print(f"Error downloading image: {e}")
        raise RuntimeError(f"Failed to process image from URL: {image_url}")

def gemini_output(image_url, system_prompt, user_prompt):
    image_info = image_format_from_url(image_url)
    input_prompt = [system_prompt, image_info[0], user_prompt]
    try:
        response = model.generate_content(input_prompt)
        return getattr(response, 'text', "No response text found.")
    except Exception as e:
        return f"Error occurred: {str(e)}"

def process_images_with_gemini():
    system_prompt = """
    You are an AI specialist in cleanliness and waste classification. 
    Your task is to analyze input images taken from CCTV footage of post offices. 
    Ignore the presence of people in the images and focus only on assessing cleanliness.

    If the scene is dirty, provide:
    1. A cleanliness score between 1 (dirtiest) and 10 (cleanest).
    2. Waste classifications such as Organic, Non-Organic, Paper, Plastic, and Cardboard.
    """
    user_prompt = user_prompt = """
    Analyze this image and determine:
    1. Whether the scene is clean or dirty.
    2. If dirty, provide a cleanliness score (1-10) and classify the waste detected in the image into categories.
    3.give the output as in the form of dictionary format in key value format only keyword which contain status of image it is clean or dirty,cleanliness score based on image ,waste clasiffication if clean give no garbage if dirty give based on image example plastic,cardboard, organic, inorganic, give the overall percetage of garbage area contain in image 
    """
    
    unprocessed_images = Image.objects.filter(cleanliness_score__isnull=True)
    for image in unprocessed_images:
        try:
            output_text = gemini_output(image.image_url, system_prompt, user_prompt)
            
            # Example parsing logic
            if "clean" in output_text.lower():
                cleanliness_score = 10
                is_clean = True
                cleanliness_status = "Clean"
                waste_type = None
            else:
                cleanliness_score = int(output_text.split("cleanliness score between")[1].split("and")[0].strip()) or 1
                is_clean = False
                cleanliness_status = "Dirty"
                waste_type = "Example Waste"

            # Update the image record
            image.cleanliness_score = cleanliness_score
            image.is_clean = is_clean
            image.cleanliness_status = cleanliness_status
            image.waste_type = waste_type
            image.timestamp = now()
            image.save()
        except Exception as e:
            print(f"Error processing image {image.id}: {e}")

# Combined Function
def post_office_monitored(request):
    # Check if the user is logged in and has the correct role
    if not request.session.get('username') or request.session.get('role') != 'divisional_office_user':
        return redirect('login')
    
    # Fetch the divisional office name from session
    divisional_office_name = request.session.get('username')
    
    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')
    
    # Filter the post offices based on the divisional office name
    post_offices = PostOffice.objects.filter(division=divisional_office_name)
    
    # If a search query is provided, filter post offices by name
    if search_query:
        post_offices = post_offices.filter(name__icontains=search_query)
    
    # Fetch and process the images (assuming these functions are defined elsewhere)
    fetch_and_populate_images()
    process_images_with_gemini()
    
    # Get the user data from the session to pass to the template
    user_data = {
        'user_id': request.session.get('user_id'),
        'username': request.session.get('username'),
        'role': request.session.get('role'),
    }
    
    # Fetch the divisional office details
    divisional_office = DivisionalOffice.objects.get(username=divisional_office_name)
    
    # Prepare context data for rendering
    context = {
        'user_data': user_data,
        'post_offices': post_offices,
        'divisional_office_name': divisional_office.name,  # Pass divisional office name to the template
    }
    
    # Return the rendered template with context
    return render(request, 'gpai_app/post_office_monitored.html', context)






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


# def fetch_postoffice(request):
#     processed_pincodes = 0  # To track how many PIN codes were successfully processed
#     failed_pincodes = []  # To track PIN codes that failed to process

#     # Iterate over the hardcoded list of Mumbai PIN codes
#     for pincode in mumbai_pincodes:
#         api_url = f"https://api.postalpincode.in/pincode/{pincode}"
        
#         # Make a GET request to the postal API for each PIN code
#         response = requests.get(api_url)
#         data = response.json()

#         # Log the API response for debugging
#         print(f"Response for PIN code {pincode}: {data}")
        
#         # Check if the API response status is "Success"
#         if data[0]["Status"] == "Success":
#             post_offices = data[0]["PostOffice"]
#             for office in post_offices:
#                 # Ensure 'PINCode' exists in the post office data
#                 pin_code = office.get("PINCode", pincode)  # Fallback to the current pincode if not present
                
#                 # Now we use the name of the post office, district, and state to fetch the location data from Google Maps
#                 post_office_name = office["Name"]
#                 district = office.get("District", "")
#                 state = office.get("State", "")
#                 address = f"{post_office_name}, {district}, {state}"

#                 maps_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
#                 maps_response = requests.get(maps_url)
#                 maps_data = maps_response.json()

#                 latitude = longitude = None
#                 if maps_data["status"] == "OK":
#                     location_data = maps_data["results"][0]["geometry"]["location"]
#                     latitude = location_data["lat"]
#                     longitude = location_data["lng"]
                
#                 # Generate username and use PINCode as the password
#                 username = generate_username(office["Name"], office["Region"])
#                 password = pin_code  # Using the fetched PINCode as password

#                 # Insert data into PostOffice table
#                 PostOffice.objects.create(
#                     name=office["Name"],
#                     username=username,
#                     password_hash=password,  # Using PINCode directly as password
#                     pincode=pin_code,
#                     branch_type=office["BranchType"],
#                     delivery_status=office["DeliveryStatus"],
#                     circle=office["Circle"],
#                     district=office.get("District", None),
#                     division=office["Division"],
#                     region=office["Region"],
#                     state=office.get("State", None),
#                     country=office.get("Country", "India"),
#                     latitude=latitude,
#                     longitude=longitude,
#                 )

#             processed_pincodes += 1  # Increment for each successful PIN code
#         else:
#             failed_pincodes.append(pincode)  # Track failed PIN codes

#     # Log the final status
#     print(f"Processed {processed_pincodes} PIN codes successfully.")
#     print(f"Failed to process PIN codes: {failed_pincodes}")

#     # Return a response after processing all PIN codes
#     message = f"Data processing complete for {processed_pincodes} PIN codes."
#     if failed_pincodes:
#         message += f" Failed to process PIN codes: {', '.join(failed_pincodes)}."

#     return HttpResponse(message)
