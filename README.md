# WhatsApp Groups Backend API Documentation

A comprehensive Django REST API backend for creating and managing WhatsApp groups using the WhatsApp Business API. This backend handles group creation, join request management, and webhook processing for group lifecycle events.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Running the Server](#running-the-server)
5. [API Endpoints](#api-endpoints)
6. [Webhook Setup](#webhook-setup)
7. [API Flow](#api-flow)
8. [Testing Examples](#testing-examples)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.8+** (Python 3.9 or 3.10 recommended)
- **MySQL 5.7+** or **MySQL 8.0+**
- **pip** (Python package manager)
- **Virtual Environment** (venv or virtualenv)
- **WhatsApp Business API Account** with:
  - Business Phone Number ID
  - Access Token
  - Webhook verification token

---

## Installation & Setup

### Step 1: Clone the Repository

```bash
cd whatsapp_backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Django==4.2.3
- djangorestframework==3.15.1
- django-cors-headers==4.2.0
- mysqlclient==2.2.0
- requests==2.31.0

### Step 4: Create MySQL Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE whatsapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Note:** The `utf8mb4` character set is required for proper emoji and special character support.

### Step 5: Configure Database Settings

Edit `whatsapp_project/settings.py` and update the database configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'whatsapp',              # Your database name
        'USER': 'root',                   # Your MySQL username
        'PASSWORD': 'ashish',            # Your MySQL password
        'HOST': 'localhost',              # Your MySQL host
        'PORT': '3306',                  # Your MySQL port
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### Step 6: Configure WhatsApp API Settings

Edit `whatsapp_project/settings.py` and update the WhatsApp configuration:

```python
# WhatsApp API Configuration
WHATSAPP_BUSINESS_PHONE_NUMBER_ID = '820921014433527'  # Your Business Phone Number ID
WHATSAPP_API_BASE_URL = 'https://graph.facebook.com/v24.0'  # WhatsApp API version
WHATSAPP_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN_HERE'  # Your WhatsApp Access Token

# WhatsApp Webhook Configuration
WHATSAPP_WEBHOOK_VERIFY_TOKEN = 'angoor_ai_webhook_token_2024_secure'  # Your webhook verify token
```

**Important:** 
- Keep your `WHATSAPP_ACCESS_TOKEN` secure and never commit it to version control
- Use the same `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in Meta Developer Dashboard

### Step 7: Run Database Migrations

```bash
python manage.py migrate
```

This creates all necessary database tables.

### Step 8: Create Superuser (Optional)

Create an admin user to access Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### Step 9: Run the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

**To run on a specific port:**
```bash
python manage.py runserver 8000
```

**To allow external access:**
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Configuration

### Environment Variables (Recommended)

For production, use environment variables instead of hardcoding values:

1. Install `python-decouple`:
```bash
pip install python-decouple
```

2. Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DB_NAME=whatsapp
DB_USER=root
DB_PASSWORD=ashish
DB_HOST=localhost
DB_PORT=3306
WHATSAPP_BUSINESS_PHONE_NUMBER_ID=820921014433527
WHATSAPP_API_BASE_URL=https://graph.facebook.com/v24.0
WHATSAPP_ACCESS_TOKEN=your-access-token-here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=angoor_ai_webhook_token_2024_secure
```

3. Update `settings.py` to use environment variables:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN')
```

---

## API Endpoints

Base URL: `http://localhost:8000/api/`

All endpoints return JSON responses.

---

### 1. Create WhatsApp Group

Creates a new WhatsApp group via the WhatsApp Business API.

**Endpoint:** `POST /api/groups/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "subject": "New Purchase Inquiry",
    "description": "Group for handling purchase inquiries (optional)",
    "join_approval_mode": "auto_approve"
}
```

**Field Descriptions:**
- `subject` (required): Group name/subject (max 128 characters)
- `description` (optional): Group description (max 2048 characters)
- `join_approval_mode` (optional): 
  - `"auto_approve"` - Users can join automatically (default)
  - `"approval_required"` - Admin approval required to join

**Success Response (201 Created):**
```json
{
    "message": "Group created successfully",
    "group": {
        "id": 1,
        "group_id": "g.1234567890123456",
        "request_id": "req_abc123xyz",
        "subject": "New Purchase Inquiry",
        "description": "Group for handling purchase inquiries",
        "join_approval_mode": "auto_approve",
        "invite_link": "https://chat.whatsapp.com/ABC123XYZ",
        "business_phone_number": "919205311559",
        "status": "created",
        "error_message": null,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "whatsapp_response": {
        "id": "g.1234567890123456",
        "request_id": "req_abc123xyz",
        "invite_link": "https://chat.whatsapp.com/ABC123XYZ"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "subject": ["This field is required."]
}
```

**Error Response (500 Internal Server Error):**
```json
{
    "message": "Failed to create group",
    "error": "Error message from WhatsApp API",
    "group": {
        "id": 1,
        "status": "failed",
        "error_message": "Error message from WhatsApp API"
    }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/groups/ \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "New Purchase Inquiry",
    "description": "Group for handling purchase inquiries",
    "join_approval_mode": "auto_approve"
  }'
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/groups/"
headers = {"Content-Type": "application/json"}
data = {
    "subject": "New Purchase Inquiry",
    "description": "Group for handling purchase inquiries",
    "join_approval_mode": "auto_approve"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

### 2. List All Groups

Retrieves a list of all WhatsApp groups stored in the database.

**Endpoint:** `GET /api/groups/list/`

**Headers:**
```
(No special headers required)
```

**Request Body:**
```
None
```

**Success Response (200 OK):**
```json
[
    {
        "id": 1,
        "group_id": "g.1234567890123456",
        "request_id": "req_abc123xyz",
        "subject": "New Purchase Inquiry",
        "description": "Group for handling purchase inquiries",
        "join_approval_mode": "auto_approve",
        "invite_link": "https://chat.whatsapp.com/ABC123XYZ",
        "business_phone_number": "919205311559",
        "status": "created",
        "error_message": null,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "group_id": null,
        "request_id": "req_def456uvw",
        "subject": "Pending Group",
        "description": "",
        "join_approval_mode": "approval_required",
        "invite_link": null,
        "business_phone_number": "919205311559",
        "status": "pending",
        "error_message": null,
        "created_at": "2024-01-15T11:00:00Z",
        "updated_at": "2024-01-15T11:00:00Z"
    }
]
```

**cURL Example:**
```bash
curl http://localhost:8000/api/groups/list/
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/groups/list/"
response = requests.get(url)
print(response.json())
```

---

### 3. Get Group Details

Retrieves details of a specific group by its database ID.

**Endpoint:** `GET /api/groups/<group_id>/`

**URL Parameters:**
- `group_id` (integer): The database ID of the group

**Headers:**
```
(No special headers required)
```

**Request Body:**
```
None
```

**Success Response (200 OK):**
```json
{
    "id": 1,
    "group_id": "g.1234567890123456",
    "request_id": "req_abc123xyz",
    "subject": "New Purchase Inquiry",
    "description": "Group for handling purchase inquiries",
    "join_approval_mode": "auto_approve",
    "invite_link": "https://chat.whatsapp.com/ABC123XYZ",
    "business_phone_number": "919205311559",
    "status": "created",
    "error_message": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Group not found"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/groups/1/
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/groups/1/"
response = requests.get(url)
print(response.json())
```

---

### 4. Get Group Join Requests

Retrieves pending join requests for a specific group.

**Endpoint:** `GET /api/groups/<group_id>/join-requests/`

**URL Parameters:**
- `group_id` (integer): The database ID of the group

**Headers:**
```
(No special headers required)
```

**Request Body:**
```
None
```

**Success Response (200 OK):**
```json
{
    "message": "Join requests fetched successfully",
    "group": {
        "id": 1,
        "group_id": "g.1234567890123456",
        "subject": "New Purchase Inquiry",
        "status": "created"
    },
    "whatsapp_response": {
        "data": [
            {
                "id": "join_request_123",
                "wa_id": "919876543210",
                "name": "John Doe",
                "requested_at": "2024-01-15T12:00:00Z"
            },
            {
                "id": "join_request_456",
                "wa_id": "919876543211",
                "name": "Jane Smith",
                "requested_at": "2024-01-15T12:05:00Z"
            }
        ]
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Group not found"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "WhatsApp group_id not available yet for this group"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/api/groups/1/join-requests/
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/groups/1/join-requests/"
response = requests.get(url)
print(response.json())
```

---

### 5. Approve Group Join Requests

Approves one or more pending join requests for a group.

**Endpoint:** `POST /api/groups/<group_id>/join-requests/approve/`

**URL Parameters:**
- `group_id` (integer): The database ID of the group

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "join_requests": [
        "join_request_123",
        "join_request_456"
    ]
}
```

**Field Descriptions:**
- `join_requests` (required): Array of join request IDs to approve (non-empty array)

**Success Response (200 OK):**
```json
{
    "message": "Join requests approved successfully",
    "group": {
        "id": 1,
        "group_id": "g.1234567890123456",
        "subject": "New Purchase Inquiry",
        "status": "created"
    },
    "whatsapp_response": {
        "success": true,
        "approved_requests": [
            "join_request_123",
            "join_request_456"
        ]
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "join_requests must be a non-empty list of join request IDs"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Group not found"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/groups/1/join-requests/approve/ \
  -H "Content-Type: application/json" \
  -d '{
    "join_requests": ["join_request_123", "join_request_456"]
  }'
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/groups/1/join-requests/approve/"
headers = {"Content-Type": "application/json"}
data = {
    "join_requests": ["join_request_123", "join_request_456"]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

### 6. Reject Group Join Requests

Rejects one or more pending join requests for a group.

**Endpoint:** `POST /api/groups/<group_id>/join-requests/reject/`

**URL Parameters:**
- `group_id` (integer): The database ID of the group

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "join_requests": [
        "join_request_789",
        "join_request_012"
    ]
}
```

**Field Descriptions:**
- `join_requests` (required): Array of join request IDs to reject (non-empty array)

**Success Response (200 OK):**
```json
{
    "message": "Join requests rejected successfully",
    "group": {
        "id": 1,
        "group_id": "g.1234567890123456",
        "subject": "New Purchase Inquiry",
        "status": "created"
    },
    "whatsapp_response": {
        "success": true,
        "rejected_requests": [
            "join_request_789",
            "join_request_012"
        ]
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "join_requests must be a non-empty list of join request IDs"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Group not found"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/groups/1/join-requests/reject/ \
  -H "Content-Type: application/json" \
  -d '{
    "join_requests": ["join_request_789", "join_request_012"]
  }'
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/groups/1/join-requests/reject/"
headers = {"Content-Type": "application/json"}
data = {
    "join_requests": ["join_request_789", "join_request_012"]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

### 7. Webhook Endpoint (Group Lifecycle)

Receives webhooks from WhatsApp for group lifecycle events (creation, updates, etc.).

**Endpoint:** `GET/POST /api/webhooks/group-lifecycle/`

**GET Request (Webhook Verification):**

WhatsApp sends a GET request to verify the webhook endpoint.

**Query Parameters:**
- `hub.mode`: Should be `"subscribe"`
- `hub.verify_token`: Must match `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in settings
- `hub.challenge`: Random string that must be returned

**Headers:**
```
(No special headers required)
```

**Success Response (200 OK):**
```
<challenge_string>
```
(Returns the `hub.challenge` value as plain text)

**Error Response (403 Forbidden):**
```
Verification failed
```

**POST Request (Webhook Events):**

WhatsApp sends POST requests when group events occur.

**Headers:**
```
Content-Type: application/json
```

**Request Body (Example):**
```json
{
    "entry": [
        {
            "changes": [
                {
                    "value": {
                        "group": {
                            "id": "g.1234567890123456",
                            "request_id": "req_abc123xyz",
                            "creation_status": "GROUP_CREATED",
                            "subject": "New Purchase Inquiry",
                            "invite_link": "https://chat.whatsapp.com/ABC123XYZ"
                        }
                    },
                    "field": "group_lifecycle_update"
                }
            ]
        }
    ]
}
```

**Success Response (200 OK):**
```json
{
    "status": "success",
    "message": "Group created successfully",
    "group_id": "g.1234567890123456",
    "request_id": "req_abc123xyz"
}
```

**Note:** This endpoint is called automatically by WhatsApp. You don't need to call it manually.

---

## Webhook Setup

To receive webhook events from WhatsApp, you need to configure the webhook in Meta Developer Dashboard.

### Step 1: Expose Your Server

For local development, use a tunneling service like **ngrok**:

```bash
# Install ngrok (if not installed)
# Download from https://ngrok.com/

# Expose local server
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 2: Configure Webhook in Meta Developer Dashboard

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your WhatsApp Business App
3. Navigate to **WhatsApp** → **Configuration** → **Webhooks**
4. Click **Edit** or **Add Webhook**
5. Enter your webhook URL: `https://your-domain.com/api/webhooks/group-lifecycle/`
6. Enter Verify Token: `angoor_ai_webhook_token_2024_secure` (must match settings.py)
7. Subscribe to **group_lifecycle_update** field
8. Click **Verify and Save**

### Step 3: Test Webhook

WhatsApp will send a GET request to verify your webhook. Check your server logs to confirm verification.

---

## API Flow

### Group Creation Flow

```
1. Client sends POST /api/groups/
   ↓
2. Backend validates request data
   ↓
3. Backend creates group record in database (status: "pending")
   ↓
4. Backend calls WhatsApp API to create group
   ↓
5. WhatsApp API returns response with request_id
   ↓
6. Backend updates group record with request_id
   ↓
7. Backend returns response to client (status: "pending")
   ↓
8. WhatsApp processes group creation asynchronously
   ↓
9. WhatsApp sends webhook POST to /api/webhooks/group-lifecycle/
   ↓
10. Backend processes webhook and updates group status:
    - GROUP_CREATED → status: "created", updates group_id and invite_link
    - GROUP_CREATE_FAILED → status: "failed", updates error_message
```

### Join Request Flow

```
1. User requests to join group (via invite link or other method)
   ↓
2. If join_approval_mode = "approval_required":
   ↓
3. Admin calls GET /api/groups/<id>/join-requests/
   ↓
4. Backend fetches join requests from WhatsApp API
   ↓
5. Admin reviews requests and calls:
   - POST /api/groups/<id>/join-requests/approve/ (to approve)
   - POST /api/groups/<id>/join-requests/reject/ (to reject)
   ↓
6. Backend calls WhatsApp API to approve/reject
   ↓
7. WhatsApp processes the action
   ↓
8. User is added to group (if approved) or request is rejected
```

---

## Testing Examples

### Complete Workflow Example

**1. Create a Group:**
```bash
curl -X POST http://localhost:8000/api/groups/ \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Customer Support Group",
    "description": "Group for customer support inquiries",
    "join_approval_mode": "approval_required"
  }'
```

**2. List All Groups:**
```bash
curl http://localhost:8000/api/groups/list/
```

**3. Get Group Details:**
```bash
curl http://localhost:8000/api/groups/1/
```

**4. Get Join Requests:**
```bash
curl http://localhost:8000/api/groups/1/join-requests/
```

**5. Approve Join Requests:**
```bash
curl -X POST http://localhost:8000/api/groups/1/join-requests/approve/ \
  -H "Content-Type: application/json" \
  -d '{
    "join_requests": ["join_request_123"]
  }'
```

**6. Reject Join Requests:**
```bash
curl -X POST http://localhost:8000/api/groups/1/join-requests/reject/ \
  -H "Content-Type: application/json" \
  -d '{
    "join_requests": ["join_request_456"]
  }'
```

### Python Script Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Create a group
def create_group():
    url = f"{BASE_URL}/groups/"
    data = {
        "subject": "Test Group",
        "description": "This is a test group",
        "join_approval_mode": "auto_approve"
    }
    response = requests.post(url, json=data)
    return response.json()

# List all groups
def list_groups():
    url = f"{BASE_URL}/groups/list/"
    response = requests.get(url)
    return response.json()

# Get group details
def get_group(group_id):
    url = f"{BASE_URL}/groups/{group_id}/"
    response = requests.get(url)
    return response.json()

# Get join requests
def get_join_requests(group_id):
    url = f"{BASE_URL}/groups/{group_id}/join-requests/"
    response = requests.get(url)
    return response.json()

# Approve join requests
def approve_join_requests(group_id, join_request_ids):
    url = f"{BASE_URL}/groups/{group_id}/join-requests/approve/"
    data = {"join_requests": join_request_ids}
    response = requests.post(url, json=data)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Create a group
    result = create_group()
    print("Created Group:", json.dumps(result, indent=2))
    
    group_id = result["group"]["id"]
    
    # List all groups
    groups = list_groups()
    print("\nAll Groups:", json.dumps(groups, indent=2))
    
    # Get group details
    group = get_group(group_id)
    print("\nGroup Details:", json.dumps(group, indent=2))
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```
Error: (2003, "Can't connect to MySQL server")
```
**Solution:** 
- Ensure MySQL is running
- Check database credentials in `settings.py`
- Verify database exists: `SHOW DATABASES;`

**2. Migration Errors**
```
Error: No such table: whatsapp_groups_whatsappgroup
```
**Solution:**
```bash
python manage.py migrate
```

**3. WhatsApp API Errors**
```
Error: Invalid OAuth access token
```
**Solution:**
- Verify `WHATSAPP_ACCESS_TOKEN` in `settings.py`
- Check if token has expired
- Ensure token has required permissions

**4. Webhook Verification Failed**
```
Error: Verification failed
```
**Solution:**
- Ensure `WHATSAPP_WEBHOOK_VERIFY_TOKEN` matches Meta Dashboard
- Check webhook URL is accessible
- Verify webhook endpoint is receiving GET requests

**5. Group Creation Stuck in "pending" Status**
```
Status remains "pending" after creation
```
**Solution:**
- Check webhook is properly configured
- Verify webhook endpoint is accessible
- Check server logs for webhook events
- Manually check WhatsApp API for group status

**6. CORS Errors (Frontend Integration)**
```
Error: CORS policy blocked
```
**Solution:**
- CORS is already enabled (`CORS_ALLOW_ALL_ORIGINS = True`)
- For production, configure specific origins in `settings.py`

### Debugging Tips

1. **Check Server Logs:**
   ```bash
   python manage.py runserver --verbosity 2
   ```

2. **Test Database Connection:**
   ```bash
   python manage.py dbshell
   ```

3. **Check WhatsApp API Directly:**
   ```bash
   curl -X GET "https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/groups" \
     -H "Authorization: Bearer {ACCESS_TOKEN}"
   ```

4. **View Django Admin:**
   - Access: `http://localhost:8000/admin/`
   - Login with superuser credentials
   - View groups in database

---

## Project Structure

```
whatsapp_backend/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── whatsapp_project/        # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
└── whatsapp_groups/         # Main app
    ├── models.py            # Database models
    ├── views.py             # API views
    ├── serializers.py       # Request/response serializers
    ├── urls.py              # App URL routing
    ├── webhooks.py          # Webhook handlers
    ├── admin.py             # Django admin configuration
    └── migrations/          # Database migrations
```

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Verify WhatsApp API credentials and permissions
4. Check webhook configuration in Meta Dashboard

---

## License

This project is part of the Angoor AI WhatsApp Backend system.

---

**Last Updated:** January 2024
