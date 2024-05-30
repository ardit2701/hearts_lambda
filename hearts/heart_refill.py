import json
import logging
from datetime import datetime, timedelta
import pytz
import utils  # Ensure this module contains methods for database connection and sending notifications

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def refill_hearts(event, context):
    logger.info("Entering refill_hearts")

    # Get a database connection
    conn = utils.get_database_connection()
    if conn is None:
        logger.error("Failed to connect to the database")
        return

    cur = conn.cursor()
    now = datetime.now(pytz.utc)

    # Retrieve users who need heart refill
    cur.execute("SELECT user_id, hearts FROM user_statistics_status WHERE hearts < 2")
    users = cur.fetchall()

    for user_id, current_hearts in users:
        new_hearts = min(current_hearts + 1, 2)  # Ensure hearts do not exceed 2
        cur.execute("UPDATE user_statistics_status SET hearts = %s WHERE user_id = %s", (new_hearts, user_id))
        conn.commit()
        logger.info(f"Heart refilled for user {user_id}")

        # Assuming `utils.send_notification` function sends notifications to users
        user_token = utils.get_notification_token(user_id)  # Retrieve user's notification token
        if user_token:
            title = "Heart Refill"
            message = "Your heart has been refilled! You can now compete again."
            utils.send_notification(user_token, title, message)
            logger.info(f"Notification sent to user {user_id}")

    cur.close()
    conn.close()
    logger.info("Leaving refill_hearts")

def lambda_handler(event, context):
    refill_hearts(event, context)

# Entry point for testing locally
if __name__ == "__main__":
    lambda_handler(None, None)
