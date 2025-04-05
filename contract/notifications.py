from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_notification_email(subject, context, recipient):
    """
    Renders the email templates and sends a multi-part email to a single recipient.
    """
    text_content = render_to_string('emails/contract_notification.txt', context)
    html_content = render_to_string('emails/contract_notification.html', context)
    
    logger.info("Sending email to %s with subject: %s", recipient, subject)
    
    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [recipient])
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_contract_notification(contract, event):
    """
    Send notification based on the event type with enhanced message content.
    Sends separate personalized emails to each recipient.
    """
    if event == 'created':
        subject = "New Contract Created"
        message_body = (
            "Dear Freelancer,\n\n"
            "You have been selected for the project. Please review the contract details carefully "
            "and confirm your acceptance by logging into your account.\n\n"
            "Thank you,\nThe Freelancia Team"
        )
        recipient_info = [(contract.freelancer.email, contract.freelancer.first_name)]
    
    elif event == 'accepted': # must be edited to approved later ... 
        subject = "Contract Approved"
        message_body = (
            "Dear Client,\n\n"
            "We are pleased to inform you that the freelancer has approved your contract. "
            "Please proceed with the next steps as outlined in your project dashboard.\n\n"
            "Thank you for choosing Freelancia.\nThe Freelancia Team"
        )
        recipient_info = [(contract.client.email, contract.client.first_name)]
    
    elif event == 'canceled':
        subject = "Contract Canceled"
        message_body = (
            "Dear Freelancer,\n\n"
            "We regret to inform you that the contract has been canceled by the client. "
            "For further details or any inquiries, please contact our support team.\n\n"
            "Best regards,\nThe Freelancia Team"
        )
        recipient_info = [(contract.freelancer.email, contract.freelancer.first_name)]
    
    elif event == 'completed':
        subject = "Contract Completed Successfully"
        message_body = (
            "Dear {name},\n\n"
            "We are happy to announce that the contract has been completed successfully. "
            "Thank you for your dedication and hard work. You can view the details of the completed "
            "contract by logging into your account.\n\n"
            "Best regards,\nThe Freelancia Team"
        )
        # We'll send separate personalized emails for client and freelancer
        recipient_info = [
            (contract.client.email, contract.client.first_name),
            (contract.freelancer.email, contract.freelancer.first_name)
        ]
    
    elif event == 'hold':
        subject = "Contract On Hold"
        message_body = (
            "Dear {name},\n\n"
            "Your contract is currently on hold pending final confirmation from both parties. "
            "Please log in to review the current status and take necessary actions if required.\n\n"
            "Thank you,\nThe Freelancia Team"
        )
        recipient_info = [
            (contract.client.email, contract.client.first_name),
            (contract.freelancer.email, contract.freelancer.first_name)
        ]
    
    else:
        subject = "Contract Notification"
        message_body = (
            "Dear {name},\n\n"
            "There is an update regarding your contract. Please log in to view the details.\n\n"
            "Best regards,\nThe Freelancia Team"
        )
        recipient_info = [
            (contract.client.email, contract.client.first_name),
            (contract.freelancer.email, contract.freelancer.first_name)
        ]
    
    # Send a personalized email to each recipient.
    for email, first_name in recipient_info:
        # Replace {name} placeholder with the recipient's first name if present
        personalized_message = message_body.replace("{name}", first_name)
        context = {
            'subject': subject,
            'recipient_name': first_name,
            'message_body': personalized_message,
            'current_year': 2025,  # You can replace with dynamic year if needed.
        }
        send_notification_email(subject, context, email)
