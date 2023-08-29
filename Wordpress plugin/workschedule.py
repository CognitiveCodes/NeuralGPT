import schedule
import time

# Define the function that performs the necessary actions
def perform_actions():
    # Code to access local data storage and modify files
    # Code to access universal database and achieve data harmonization

# Define the schedule for the actions to be performed
schedule.every(24).hours.do(perform_actions) # Run every 24 hours
schedule.every().day.at("12:00").do(perform_actions) # Run every day at 12:00
schedule.every().hour.do(perform_actions) # Run every hour
schedule.every(10).minutes.do(perform_actions) # Run every 10 minutes

# Run the scheduling system
while True:
    schedule.run_pending()
    time.sleep(1)