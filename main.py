import requests
import firebase_admin
from firebase_admin import credentials, db
from twilio.rest import Client

# Make sure to put sensitive information in a separate file

# Twilio credentials
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

# Firebase credentials
FIREBASE_CREDENTIALS = ""
FIREBASE_DATABASE_URL = ""

# Initialize Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DATABASE_URL
})

def fetch_leetcode_data(username):
    url = f"https://leetcode-stats-api.herokuapp.com/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch LeetCode data")

def load_submission_count():
    try:
        ref = db.reference('submissions')
        return ref.get() or {}
    except Exception as e:
        print(f"Failed to load submission count: {e}")
        return {}

def save_submission_count(data):
    try:
        ref = db.reference('submissions')
        ref.set(data)
    except Exception as e:
        print(f"Failed to save submission count: {e}")

def send_sms_message(to_number, name):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=f"",
        from_=TWILIO_PHONE_NUMBER,
        to=to_number
    )


def main():
    leetcode_data = fetch_leetcode_data("your username")
    submission_calendar = leetcode_data["submissionCalendar"]
    
    # Sum all the values in submissionCalendar
    total_submissions_new = sum(submission_calendar.values())

    # Load the current submission count from Firebase
    firebase_data = load_submission_count()

    # Fetch the existing total submission count
    total_submissions_existing = firebase_data.get("total", 0)

    # Compare and update if the new total is greater
    if total_submissions_new > total_submissions_existing:
        firebase_data["total"] = total_submissions_new
        save_submission_count(firebase_data)

    # Check if there were no submissions today and send Venmo payments if true
    if total_submissions_new == total_submissions_existing:
        # Send SMS message
        phone_numbers = {
            "Person": "number",
        }
        
        for person in phone_numbers:
            send_sms_message(phone_numbers[person], person)

if __name__ == "__main__":
    main()