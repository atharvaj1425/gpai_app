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

def post_office_monitored(request):
    return render(request, "gpai_app/post_office_monitored.html")



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
