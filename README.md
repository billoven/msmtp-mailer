# msmtp-mailer

**Lightweight Python wrapper for sending emails via msmtp**

This tool provides a simple and reliable way to send emails from Python using `msmtp`.
It supports:

* Fixed sender account (defined in `~/.msmtprc`)
* Custom display name (alias)
* Multiple recipients via JSON
* Attachments
* Detailed logging

---

## 📦 Features

✅ Simple and minimal setup
✅ Gmail-compatible (using App Passwords)
✅ No external Python dependencies
✅ Fully tested with unit tests
✅ Works on Linux (tested on Ubuntu 24.04)

---

## 📋 Prerequisites

1. **Python 3.8+**
2. **msmtp** and **msmtp-mta** installed
3. A **Gmail account** configured for application access

### Install msmtp

```bash
sudo apt update
sudo apt install msmtp msmtp-mta
```

---

## ⚙️ Gmail Setup for msmtp

To send emails via Gmail, you **must use an App Password**, not your normal password.
Here’s how to configure it safely:

### Step 1 — Enable 2-Step Verification

1. Go to [Google Account → Security](https://myaccount.google.com/security)
2. Under **“Signing in to Google”**, enable **2-Step Verification**

### Step 2 — Create an App Password

1. Visit [App Passwords](https://myaccount.google.com/apppasswords)
2. Log in again if prompted
3. Under **Select App**, choose **Mail**
4. Under **Select Device**, choose **Other (Custom name)** — e.g. `msmtp`
5. Copy the **16-character App Password** (you’ll need it below)

---

## 🧩 Configure `~/.msmtprc`

Create or edit your configuration file:

```bash
nano ~/.msmtprc
```

Example configuration for Gmail:

```text
# ~/.msmtprc
account gmail
host smtp.gmail.com
port 587
auth on
user yourname@gmail.com
password your_16_char_app_password
from "Your Display Name <yourname@gmail.com>"
tls on
tls_trust_file /etc/ssl/certs/ca-certificates.crt

account default : gmail
```

Then secure the file:

```bash
chmod 600 ~/.msmtprc
```

### 🔒 About `tls_trust_file`

You **do not need to generate your own certificate**.
`/etc/ssl/certs/ca-certificates.crt` is the system’s trusted CA bundle — it verifies Gmail’s TLS certificate automatically.

---

## 📁 Project structure

```
msmtp-mailer/
│
├── msmtp_mail.py          # Main library
├── Example.py             # Example usage
├── test_msmtp_mail.py     # Unit tests
├── recipients.json        # Optional recipients list
└── README.md              # Usage document
```

---

## 🧠 Installation

Clone the repository:

```bash
git clone https://github.com/billoven/msmtp-mailer.git
cd msmtp-mailer
```

No third-party Python packages are required — only the standard library and `msmtp`.

---

## 🧰 Example usage

```python
from msmtp_mail import MsmtpClient, EmailMessageBuilder

# Build the email
builder = EmailMessageBuilder()
builder.set_from_full_name("System Alerts")       # Changes display name
builder.add_to("recipient@example.com")           # Add recipient
builder.set_subject("Test Email from msmtp-mailer")
builder.set_body("Hello,\n\nThis is a test email.\n\nRegards,\nmsmtp-mailer")

# Optional: add attachments
# builder.add_attachment("/path/to/file.pdf")

# Send email
client = MsmtpClient(log_file="/var/log/msmtp_mail.log")
client.send(builder)
```

**Output example:**

```
From: System Alerts <yourname@gmail.com>
To: recipient@example.com
Subject: Test Email from msmtp-mailer
```

---

## 📄 JSON recipients file

You can manage multiple recipients easily via a `.json` file.

### Format 1 (recommended)

```json
{
    "recipients": [
        "user1@example.com",
        "user2@example.com"
    ]
}
```

### Format 2 (simpler)

```json
[
    "user1@example.com",
    "user2@example.com"
]
```

Usage:

```python
builder.load_recipients_from_file("recipients.json")
```

---

## 🧪 Running the unit tests

Run all tests:

```bash
python3 test_msmtp_mail.py
```

Or via discovery mode:

```bash
python3 -m unittest discover
```

Verbose mode:

```bash
python3 -m unittest -v test_msmtp_mail.py
```

---

## 🧾 Logging

If you specify a log file, every email sent will be logged with a timestamp and recipient list:

```
2025-10-22 14:08:25 - Email sent to ['recipient@example.com']
```

---

## ⚠️ Important notes

* **Do not include your real password** — always use a **Gmail App Password**
* **Your Gmail address must be verified** in the Google settings for “Send mail as” if you use aliases
* **Do not share your `.msmtprc` file** — it contains credentials
* **`tls_trust_file`** should remain `/etc/ssl/certs/ca-certificates.crt` (system-managed)

---

## ✅ Summary

| Item            | Description                 |
| --------------- | --------------------------- |
| Email Transport | msmtp                       |
| Auth Method     | Gmail App Password          |
| Encryption      | TLS via system CA           |
| Supported OS    | Linux (Ubuntu 24.04 tested) |
| Dependencies    | Python 3.x only             |
| Unit Tests      | `test_msmtp_mail.py`        |

---

## 🧩 Example recipients.json (template)

```json
{
  "recipients": [
    "recipient1@example.com",
    "recipient2@example.com"
  ]
}
```

---

## 🚀 Quick start

1. Install msmtp
2. Create your Gmail App Password
3. Configure `~/.msmtprc`
4. Clone the repo
5. Edit `Example.py` with your recipient
6. Run:

```bash
python3 Example.py
```

---

Perfect! Here’s a ready-to-use setup for your GitHub repository, including **`Example.py`** and **`recipients.json`** templates that match the README instructions. Users can clone the repo and test immediately.

---

## 1️⃣ `Example.py`

```python
#!/usr/bin/env python3
"""
Example usage of msmtp-mailer library.
Send an email using msmtp via Gmail account configured in ~/.msmtprc.
"""

import sys
from msmtp_mail import MsmtpClient, EmailMessageBuilder

# Check if recipients file was passed as argument
recipients_file = sys.argv[1] if len(sys.argv) > 1 else None

builder = EmailMessageBuilder()

# Set display name (alias) for sender
builder.set_from_full_name("System Alerts")

# Add a manual recipient if no file is given
if recipients_file is None:
    builder.add_to("recipient@example.com")
else:
    # Load recipients from JSON file
    try:
        builder.load_recipients_from_file(recipients_file)
        print(f"Loaded recipients from {recipients_file}")
    except Exception as e:
        print(f"Failed to load recipients: {e}")
        sys.exit(1)

# Set email subject and body
builder.set_subject("Test Email from msmtp-mailer")
builder.set_body(
    "Hello,\n\nThis is a test email sent using msmtp-mailer.\n\nRegards,\nSystem Alerts",
    subtype="plain"
)

# Optional: add attachments
# builder.add_attachment("/path/to/file.pdf")

# Create msmtp client and send the email
client = MsmtpClient(log_file="/var/log/msmtp_mail.log")

try:
    client.send(builder)
    print("Email sent successfully.")
except Exception as e:
    print(f"Error sending email: {e}")
```

---

## 2️⃣ `recipients.json` (template)

```json
{
  "recipients": [
    "recipient1@example.com",
    "recipient2@example.com"
  ]
}
```

---

### ✅ How to test

1. Ensure your Gmail account is configured in `~/.msmtprc` with App Password.
2. Clone the repository:

```bash
git clone https://github.com/yourusername/msmtp-mailer.git
cd msmtp-mailer
```

3. Optionally, edit `recipients.json` with your own recipient emails.
4. Run the example:

```bash
# Use the default manual recipient in Example.py
python3 Example.py

# Or use a recipients JSON file
python3 Example.py recipients.json
```

You should see:

```
Loaded recipients from recipients.json
Email sent successfully.
```

---

These two files **match the README instructions** and allow a user to:

* Send a single email manually
* Load multiple recipients from JSON
* Test attachments if needed
* Log results

---

