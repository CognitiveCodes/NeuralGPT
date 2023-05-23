import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flowiseai_app import FlowiseAIApp
from neuralgpt_agent import NeuralGPTAgent

# create instances of the FlowiseAIApp and NeuralGPTAgent classes
flowise_ai_app = FlowiseAIApp()
neuralgpt_agent = NeuralGPTAgent()

# define a function for sending email notifications
def send_email_notification(to_address, subject, body):
    # set up the email message
    message = MIMEMultipart()
    message['From'] = 'neuralgpt_agent@flowiseai.com'
    message['To'] = to_address
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # send the email using SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'your_email@gmail.com'
    smtp_password = 'your_email_password'
    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(smtp_username, smtp_password)
    smtp_connection.sendmail(smtp_username, to_address, message.as_string())
    smtp_connection.quit()

# define a function for handling task completion notifications
def handle_task_completion(task_id):
    # get the task status from the NeuralGPTAgent
    task_status = neuralgpt_agent.get_task_status(task_id)

    # check if the task completed successfully
    if task_status['status'] == 'completed':
        # send a notification to the user
        to_address = flowise_ai_app.get_user_email(task_status['user_id'])
        subject = 'Task Completed'
        body = f"Task '{task_status['task_name']}' completed successfully at {task_status['completion_time']}."
        send_email_notification(to_address, subject, body)
    else:
        # send a notification to the user
        to_address = flowise_ai_app.get_user_email(task_status['user_id'])
        subject = 'Task Error'
        body = f"An error occurred while executing task '{task_status['task_name']}' at {task_status['error_time']}: {task_status['error_message']}."
        send_email_notification(to_address, subject, body)

# call the handle_task_completion function with a task ID
handle_task_completion(12345)