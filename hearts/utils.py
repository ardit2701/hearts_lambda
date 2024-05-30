import os
import json
import boto3
import psycopg2
from firebase_admin import messaging, credentials, initialize_app

# Database connection settings
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']
s3_bucket_name = os.environ['S3_BUCKET']
firebase_service_account_key = os.environ['FIREBASE_SERVICE_ACCOUNT_KEY']

# Initialize AWS clients
s3_client = boto3.client('s3')

def get_firebase_credentials_from_s3():
    try:
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=firebase_service_account_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        print(f"Error fetching Firebase credentials from S3: {e}")
        raise

# Initialize Firebase Admin SDK
firebase_credentials = get_firebase_credentials_from_s3()
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)

def send_notification(token, title, message):
    try:
        # Send message to Firebase Cloud Messaging
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            token=token,
        )
        response = messaging.send(message)
        print(f"Notification message sent to Firebase for {token} with title '{title}'. Response: {response}")
    except Exception as e:
        print(f"Error sending message to Firebase for {token}: {e}")

def get_database_connection():
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def send_notification_with_data(token, title, message_body, data):
    try:
        # Construct the message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message_body,
            ),
            token=token,
            data=data
        )

        # Send the message
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")

    except Exception as e:
        print(f"Error sending message to Firebase for {token}: {e}")