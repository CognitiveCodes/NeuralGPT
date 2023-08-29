    import smtplib
    from email.mime.text import MIMEText

    def send_notification(user_email, message):
        # Set up SMTP server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "your_email@gmail.com"
        smtp_password = "your_password"

        # Set up message
        msg = MIMEText(message)
        msg['From'] = smtp_username
        msg['To'] = user_email
        msg['Subject'] = "Notification: Changes made to Universal Database"

        # Send message
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, user_email, msg.as_string())

    def notify_users(users, message):
        for user in users:
            send_notification(user['email'], message)

    # Example usage
    users = [
        {'email': 'user1@example.com', 'access_level': 'admin'},
        {'email': 'user2@example.com', 'access_level': 'user'},
        {'email': 'user3@example.com', 'access_level': 'user'}
    ]

    message = "Changes have been made to the Universal Database."

    # Notify all users
    notify_users(users, message)

    # Notify only admins
    admins = [user for user in users if user['access_level'] == 'admin']
    notify_users(admins, message)