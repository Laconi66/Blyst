import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import csv
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

email_account = os.getenv('OUTLOOK_USERNAME')
password = os.getenv('OUTLOOK_PASSWORD')

# IMAP Credentials
server = 'outlook.office365.com'

# Connect to the IMAP server
def connect_imap(server, email_account, password):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email_account, password)
    return mail


# Fetch emails
def fetch_emails(mail):
    mail.select("inbox")  # Select the inbox

    # Calculate the date since which to fetch emails (e.g., 2 weeks ago)
    date_since = (datetime.now() - timedelta(weeks=2)).date()
    formatted_date = date_since.strftime("26-aug-2024")  # Format: DD-Mon-YYYY

    # Use the search command with the SINCE filter
    status, messages = mail.search(None, f'SINCE {formatted_date}')  # Get emails since the specified date

    # Create a list to hold email data
    emails_data = []

    # Convert the result to a list of email IDs
    email_ids = messages[0].split()

    for email_id in email_ids:
        res, msg = mail.fetch(email_id, "(RFC822)")  # Fetch the email by ID
        for response_part in msg:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])  # Parse the email
                encoding = decode_header(msg['Subject'])[0][1] if msg['Subject'] else None
                subject = decode_header(msg['Subject'])[0][0] if msg['Subject'] else ''
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8', errors='replace')

                    # Decode the sender
                sender_raw = msg.get('From')
                sender = ""
                if sender_raw:
                    decoded_sender = decode_header(sender_raw)
                    sender_parts = []
                    for text, enc in decoded_sender:
                        if isinstance(text, bytes):
                            text = text.decode(enc if enc else 'utf-8', errors='replace')
                        sender_parts.append(text)
                    sender = ''.join(sender_parts)

                date = msg.get('Date')
                plain_body, html_body = get_email_bodies(msg)  # Get both email bodies

                # Clean up the plain body by removing unwanted HTML (if any)
                clean_sender = clean_text(sender)
                clean_subject = clean_text(subject)
                clean_plain_body = clean_html(plain_body)
                clean_html_body = clean_html(html_body)


                # Append to the emails_data list
                emails_data.append([clean_sender, clean_subject, date, clean_plain_body.strip(), clean_html_body.strip()])

    return emails_data

# Function to extract the email bodies (plain text and HTML)
def get_email_bodies(msg):
    plain_body = ""
    html_body = ""
    if msg.is_multipart():
        # If the email is multipart, walk through each part
        for part in msg.walk():
            charset = part.get_content_charset()  # Get character set
            if part.get_content_type() == "text/plain":
                try:
                    # Decode payload using the charset if available, otherwise use UTF-8
                    plain_body = part.get_payload(decode=True).decode(charset or 'utf-8', errors='replace')
                except (LookupError, TypeError):
                    plain_body = part.get_payload(decode=True).decode('utf-8', errors='replace')
            elif part.get_content_type() == "text/html":
                try:
                    # Decode payload using the charset if available, otherwise use UTF-8
                    html_body = part.get_payload(decode=True).decode(charset or 'utf-8', errors='replace')
                except (LookupError, TypeError):
                    html_body = part.get_payload(decode=True).decode('utf-8', errors='replace')
    else:
        # If it's not multipart, just get the payload
        charset = msg.get_content_charset()
        if msg.get_content_type() == "text/plain":
            try:
                plain_body = msg.get_payload(decode=True).decode(charset or 'utf-8', errors='replace')
            except (LookupError, TypeError):
                plain_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        elif msg.get_content_type() == "text/html":
            try:
                html_body = msg.get_payload(decode=True).decode(charset or 'utf-8', errors='replace')
            except (LookupError, TypeError):
                html_body = msg.get_payload(decode=True).decode('utf-8', errors='replace')

    return plain_body, html_body  # Return both bodies

# Function to clean HTML and extract plain text
def clean_html(html):
    # Use BeautifulSoup to parse the HTML and extract text
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)  # Extract text from HTML

    # Clean and normalize whitespace
    text = ' '.join(text.split())

    # Additional cleanup: If certain unwanted characters persist, remove them
    replacements = {
        'Ã©': 'é',  # You can add more specific replacements here as needed
        'Ã': 'à',
        'Ãª': 'ê',
        'Ã¨': 'è',
        ';': ' ',
        '"': ' ',
        '?': ' ',
        '💸': ' '
    }
    for key, value in replacements.items():
        text = text.replace(key, value)

    return text  # Return cleaned plain text

def clean_text(text):
    if text is None:
        return ""

    # Optionally, you can add more specific replacements
    replacements = {
        'Ã©': 'é',  # You can add more specific replacements here as needed
        'Ã': 'à',
        'Ãª': 'ê',
        'Ã¨': 'è',
        ';': ' ',
        '"': ' ',
        '?': ' ',
        '💸': ' ',
        '=': ' '
    }

    # Apply replacements
    for key, value in replacements.items():
        text = text.replace(key, value)

    # Strip whitespace and normalize the text
    text = ' '.join(text.split()).strip()  # Remove extra whitespace
    return text

# Write to CSV
def write_to_csv(emails_data, filename='./Data/Emails/outlook_emails.csv'):
    with open(filename, mode='w', newline='', errors='replace') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)  # Use proper quoting
        writer.writerow(['Sender', 'Subject', 'Date', 'HTML Body'])  #  'Plain Body',  Write header
        for email_data in emails_data:  # Write email data without corrupted rows
            writer.writerow([
                email_data[0],
                email_data[1],
                email_data[2],
                #email_data[3].replace('\n', ' '),  # Replace line breaks with space
                email_data[4].replace('\n', ' ')   # Replace line breaks with space
            ])

# Main function
def main():
    mail = connect_imap(server, email_account, password)
    emails_data = fetch_emails(mail)
    write_to_csv(emails_data)
    mail.logout()  # Logout from the server


if __name__ == "__main__":
    main()