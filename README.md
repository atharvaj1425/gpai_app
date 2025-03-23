# GPAI - Government Post Office Automation Interface

GPAI is a Django-based web application designed to streamline and automate various operations of post offices. It provides dashboards for divisional offices, post offices, and citizens, along with features for monitoring, managing campaigns, utility bills, and recycling requests.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- **Divisional Office Dashboard**: Manage and monitor post offices under a division.
- **Post Office Dashboard**: View and manage post office-specific data.
- **Citizen Dashboard**: Access campaigns, recycling requests, and other citizen services.
- **Campaign Management**: Create, view, and manage campaigns for post offices.
- **Utility Bills Management**: Track and manage utility bills for post offices.
- **Recycling Requests**: Submit and manage recycling requests.
- **Image Table**: View and manage images related to post office activities.

---

## Project Structure
```
.
├── capture_image.py          # Script for capturing images
├── db.sqlite3                # SQLite database file
├── env/                      # Virtual environment directory
├── GPAI/                     # Main Django project directory
├── gpai_app/                 # Django app containing core functionality
│   ├── urls.py               # URL routing for the app
│   ├── views.py              # Views for handling requests
│   ├── models.py             # Database models
│   ├── templates/            # HTML templates
│   └── ...                   # Other app files
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── templates/                # Global templates directory
```

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/gpai.git
   cd gpai
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```

---

## Usage

1. Open your browser and navigate to `http://127.0.0.1:8000/`.
2. Use the provided dashboards and features to manage post office operations.

---

## Endpoints

Here are the key endpoints defined in `gpai_app/urls.py`:

* `/` - Home page
* `/login` - Login page
* `/logout` - Logout functionality
* `/divisional_office_dashboard` - Divisional office dashboard
* `/post_office_dashboard` - Post office dashboard
* `/post_office_monitored` - Monitored post offices
* `/post-office/history/<int:post_office_id>/` - View post office history
* `/utility_bills/<int:post_office_id>/` - Manage utility bills
* `/campaigns/<int:post_office_id>/` - Manage campaigns
* `/life_practices/<int:post_office_id>/` - View life practices
* `/post-office/view_campaign_history/<int:post_office_id>/` - View campaign history
* `/fetch_postoffice` - Fetch post office data
* `/image_table` - View image table
* `/get-post-offices/` - Get list of post offices
* `/submit-recycling-request/` - Submit recycling request
* `/citizen_dashboard` - Citizen dashboard
* `/register/<int:user_id>/<int:campaign_drive_id>/` - Register for a campaign

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
