# msmtp-mailer
msmtp-mailer is a lightweight Python library that sends emails through msmtp, providing a simple object-oriented interface for building and delivering messages. 
It enforces a fixed sender email (as configured in ~/.msmtprc) while allowing a customizable display name, supports attachments, recipient lists from JSON or text files, and optional logging of all sent messages.

Key features:

- Always uses the Gmail (or any) account defined in ~/.msmtprc
- Supports plain text and HTML messages
- Customizable sender display name (alias)

Attachments support

- Load recipients from .json or .txt files
- Optional send logging (with timestamps and status)
- Fully tested and dependency-free (uses only Python standard library)
