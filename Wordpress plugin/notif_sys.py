import pika
from twilio.rest import Client

def send_notification(message):
    # Check user access level and send notifications accordingly
    # Use Twilio to send SMS notifications
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)
    message = client.messages \
                    .create(
                         body=message,
                         from_='your_twilio_number',
                         to='user_phone_number'
                     )

def callback(ch, method, properties, body):
    # Triggered whenever changes are made to the database
    send_notification(body)

# Set up RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='database_changes')

# Listen for messages on the queue
channel.basic_consume(queue='database_changes', on_message_callback=callback, auto_ack=True)

print('Waiting for database changes...')
channel.start_consuming()