import cv2
from datetime import datetime
import cloudinary
import cloudinary.uploader

# Cloudinary Configuration
cloudinary.config(
    cloud_name="dswkvnomk",  # Replace with your Cloudinary cloud name
    api_key="651324994684599",        # Replace with your Cloudinary API key
    api_secret="JgsKsiuw49IdP5uN-SFAJfG51Ac"  # Replace with your Cloudinary API secret
)

# Coordinates for the webcam location
latitude = 19.029527
longitude = 72.854820

# Function to capture an image and upload with metadata
def capture_image_with_metadata():
    # Initialize webcam
    cap = cv2.VideoCapture(0)  # Use 0 for the default webcam
    
    if not cap.isOpened():
        print("Error: Unable to access webcam.")
        return
    
    # Capture a single frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture an image.")
        cap.release()
        return

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"image_{timestamp.replace(' ', '_').replace(':', '-')}.jpg"
    
    # Save the image locally
    cv2.imwrite(filename, frame)
    print(f"Image saved locally as {filename}")
    
    # Upload image to Cloudinary with context metadata
    try:
        response = cloudinary.uploader.upload(
            filename,
            public_id=f"webcam_{timestamp.replace(' ', '_').replace(':', '-')}",
            context={
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp
            }
        )
        print("Image uploaded successfully to Cloudinary.")
        print(f"Cloudinary URL: {response['url']}")
        print(f"Metadata: Timestamp: {timestamp}, Latitude: {latitude}, Longitude: {longitude}")
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
    
    # Release the webcam
    cap.release()

# Run the function to capture and upload the image
capture_image_with_metadata()
