#!/usr/bin/env python3
"""
Example usage of pymsmtp-mailer with optional recipients.json.
- If a JSON file path is given as a command-line argument, it loads recipients from it.
- Otherwise, it ensures minimal information is set: at least one To, Subject, Body.
"""

import sys
import os
from msmtp_mail import MsmtpClient, EmailMessageBuilder, EmailBuildError

def main():
    # Create the email builder
    builder = EmailMessageBuilder()
    builder.set_from_full_name("CashCue Daily Report")  # display name (alias)
    builder.set_subject("CashCue Daily Report")
    builder.set_body("Bonjour,\nHere is the daily report.\nRegards.", subtype="plain")

    # Check command-line argument for recipients JSON
    if len(sys.argv) > 1:
        recipients_file = sys.argv[1]
        if not os.path.isfile(recipients_file):
            print(f"Recipients file not found: {recipients_file}")
            sys.exit(1)
        try:
            builder.load_recipients_from_file(recipients_file)
            print(f"Loaded recipients from {recipients_file}")
        except EmailBuildError as e:
            print(f"Failed to load recipients: {e}")
            sys.exit(1)
    else:
        # No file provided, verify at least one recipient is set manually
        if not builder._to:
            print("No recipients provided. Add at least one To address or provide a recipients.json file.")
            sys.exit(1)

    # Create msmtp client
    client = MsmtpClient(log_file="/var/log/msmtp_mail.log")

    # Attempt to send
    try:
        client.send(builder)
        print("Email sent successfully!")
    except EmailBuildError as e:
        print(f"Email build error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Email send failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

