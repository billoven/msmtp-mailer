# msmtp_mail.py
"""
Lightweight object-oriented email client using msmtp.
----------------------------------------------------
- Always sends via the Gmail account configured in ~/.msmtprc
- Allows custom display name (from_full_name) but fixed sender email
- Supports recipient lists from JSON or text files
- Supports optional send logging

Author: Pierre adaptation, 2025
"""

from email.message import EmailMessage
from email.utils import formataddr
import mimetypes
import subprocess
import logging
import os
import json
from datetime import datetime
from typing import List, Optional

# Logger setup
logger = logging.getLogger("msmtp_mail")

# Constants for Gmail msmtp setup
MSMTP_ACCOUNT = "gmail"
MSMTP_FROM_EMAIL = "u0992244071@gmail.com"  # fixed sender email
MSMTP_DEFAULT_FULLNAME = "N150 Home Server Monitoring"


# --- Custom Exceptions ---------------------------------------------------------

class EmailBuildError(Exception):
    """Raised when building the email fails."""
    pass


class MsmtpSendError(Exception):
    """Raised when sending the email via msmtp fails."""
    pass


# --- EmailMessageBuilder -------------------------------------------------------

class EmailMessageBuilder:
    """
    Helper to build an EmailMessage (MIME format) with attachments.
    The sender email is fixed to the Gmail account, but the display name is customizable.
    """

    def __init__(self):
        self._msg = EmailMessage()
        self._from_full_name = MSMTP_DEFAULT_FULLNAME
        self._to: List[str] = []
        self._cc: List[str] = []
        self._bcc: List[str] = []

    # --- Sender management -----------------------------------------------------

    def set_from_full_name(self, name: str):
        """Set custom display name (alias) for the sender."""
        self._from_full_name = name
        return self

    # --- Recipients management -------------------------------------------------

    def add_to(self, email: str):
        """Add a primary recipient."""
        self._to.append(email)
        return self

    def add_cc(self, email: str):
        """Add a CC recipient."""
        self._cc.append(email)
        return self

    def add_bcc(self, email: str):
        """Add a BCC recipient."""
        self._bcc.append(email)
        return self

    def load_recipients_from_file(self, path: str):
        """Load recipients from a JSON file (object with 'recipients' key)."""
        import json
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            emails = []
            if isinstance(data, dict):
                emails = data.get("recipients", [])
            elif isinstance(data, list):
                emails = data
            else:
                raise EmailBuildError("Recipient file format not recognized.")
            if not emails:
                raise EmailBuildError("No emails found in recipient file.")
            for email in emails:
                self.add_to(email)
        except Exception as e:
            raise EmailBuildError(f"Error reading recipient file: {e}")

    # --- Message content -------------------------------------------------------

    def set_subject(self, subject: str):
        """Set email subject."""
        self._msg["Subject"] = subject
        return self

    def set_body(self, text: str, subtype: str = "plain"):
        """Set body text (plain or HTML)."""
        self._msg.set_content(text, subtype=subtype)
        return self

    def add_attachment(self, path: str, mime_type: Optional[str] = None, filename: Optional[str] = None):
        """Attach a file to the email."""
        if not os.path.isfile(path):
            raise EmailBuildError(f"Attachment not found: {path}")

        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(path)
            if mime_type is None:
                mime_type = "application/octet-stream"

        maintype, subtype = mime_type.split("/", 1)
        with open(path, "rb") as f:
            data = f.read()

        if filename is None:
            filename = os.path.basename(path)

        self._msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)
        return self

    # --- Final build -----------------------------------------------------------

    def build(self) -> EmailMessage:
        if not (self._to or self._cc or self._bcc):
            raise EmailBuildError("No recipients set (add_to/add_cc/add_bcc).")

        if not self._msg.get("Subject"):
            raise EmailBuildError("No subject set.")

        # Check if body exists
        if self._msg.is_multipart():
            # Multipart: ensure at least one part is text/plain or text/html
            text_parts = [
                part for part in self._msg.get_payload()
                if part.get_content_type() in ("text/plain", "text/html")
            ]
            if not text_parts:
                raise EmailBuildError("No body set in multipart message.")
        else:
            # Single part: check payload is not empty
            payload = self._msg.get_payload(decode=True)
            if not payload:
                raise EmailBuildError("No body set.")

        # Set From
        self._msg["From"] = formataddr((self._from_full_name, MSMTP_FROM_EMAIL))
        if self._to:
            self._msg["To"] = ", ".join(self._to)
        if self._cc:
            self._msg["Cc"] = ", ".join(self._cc)

        return self._msg

    def recipients(self) -> List[str]:
        """Return combined unique recipient list (to + cc + bcc)."""
        return list(dict.fromkeys(self._to + self._cc + self._bcc))


# --- MsmtpClient ---------------------------------------------------------------

class MsmtpClient:
    """
    Send an EmailMessage using msmtp command line tool.
    Always uses the Gmail account defined in ~/.msmtprc.
    """

    def __init__(self, msmtp_path: str = "/usr/bin/msmtp", log_file: Optional[str] = None):
        self.msmtp_path = msmtp_path
        self.log_file = log_file

    def _build_cmd(self, recipients: List[str]) -> List[str]:
        """Build msmtp command."""
        return [self.msmtp_path, "-a", MSMTP_ACCOUNT] + recipients

    def _write_log(self, success: bool, subject: str, recipients: List[str], error: Optional[str] = None):
        """Write send result to log file if enabled."""
        if not self.log_file:
            return

        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "OK" if success else f"FAIL ({error})"
        line = f"[{ts}] {status} | Subject='{subject}' | To={recipients}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def send(self, builder: EmailMessageBuilder, timeout: int = 60) -> None:
        """Send the message via msmtp."""
        msg = builder.build()
        recipients = builder.recipients()
        cmd = self._build_cmd(recipients)
        raw_bytes = msg.as_bytes()

        logger.info("Sending email via msmtp (account=gmail) to %s", recipients)

        try:
            proc = subprocess.run(cmd, input=raw_bytes, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=timeout)
        except Exception as e:
            logger.exception("msmtp invocation failed: %s", e)
            self._write_log(False, msg["Subject"], recipients, str(e))
            raise MsmtpSendError(str(e))

        if proc.returncode != 0:
            err = proc.stderr.decode(errors="ignore")
            logger.error("msmtp send failed: %s", err)
            self._write_log(False, msg["Subject"], recipients, err)
            raise MsmtpSendError(err)

        logger.info("Email sent successfully to %s", recipients)
        self._write_log(True, msg["Subject"], recipients)
