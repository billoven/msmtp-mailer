# test_msmtp_mail.py
"""
Unit tests for pymsmtp-mailer
Covers EmailMessageBuilder and MsmtpClient functionality.
Uses unittest and unittest.mock to avoid sending real emails.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import json
from msmtp_mail import EmailMessageBuilder, MsmtpClient, MsmtpSendError, EmailBuildError, MSMTP_FROM_EMAIL


class TestMsmtpMail(unittest.TestCase):
    def setUp(self):
        # Silence logging during tests
        import logging
        logging.getLogger("msmtp_mail").setLevel(logging.CRITICAL)

        # Prepare test recipient files
        self.test_dir = os.path.dirname(__file__)
        self.json_object_path = os.path.join(self.test_dir, "test_recipients_object.json")
        self.json_array_path = os.path.join(self.test_dir, "test_recipients_array.json")

        # JSON object format
        with open(self.json_object_path, "w", encoding="utf-8") as f:
            json.dump({"recipients": ["a@example.com", "b@example.com"]}, f)

        # JSON array format
        with open(self.json_array_path, "w", encoding="utf-8") as f:
            json.dump(["c@example.com", "d@example.com"], f)

    def tearDown(self):
        # Remove test files
        os.remove(self.json_object_path)
        os.remove(self.json_array_path)

    # -----------------------
    # EmailMessageBuilder tests
    # -----------------------
    def test_from_is_fixed(self):
        """Test that the From email is fixed and alias works."""
        b = EmailMessageBuilder()
        b.set_from_full_name("Test Alias")
        b.add_to("dest@example.com")
        b.set_subject("Subject")
        b.set_body("Body")
        msg = b.build()
        self.assertIn(MSMTP_FROM_EMAIL, msg["From"])
        self.assertIn("Test Alias", msg["From"])

    def test_add_attachment(self):
        """Test adding an attachment works."""
        b = EmailMessageBuilder()
        # create a temporary file
        tmp_file = os.path.join(self.test_dir, "temp.txt")
        with open(tmp_file, "w") as f:
            f.write("test content")
        b.add_to("dest@example.com")
        b.set_subject("Subj")
        b.set_body("Body")
        b.add_attachment(tmp_file)
        msg = b.build()
        self.assertTrue(len(msg.get_payload()) > 1)  # attachment + body
        os.remove(tmp_file)

    def test_load_recipients_from_json_object(self):
        b = EmailMessageBuilder()
        b.load_recipients_from_file(self.json_object_path)
        self.assertIn("a@example.com", b._to)
        self.assertIn("b@example.com", b._to)

    def test_load_recipients_from_json_array(self):
        b = EmailMessageBuilder()
        b.load_recipients_from_file(self.json_array_path)
        self.assertIn("c@example.com", b._to)
        self.assertIn("d@example.com", b._to)

    def test_no_recipients_error(self):
        b = EmailMessageBuilder()
        b.set_subject("Test")
        b.set_body("Body")
        with self.assertRaises(EmailBuildError):
            b.build()

    def test_no_subject_error(self):
        b = EmailMessageBuilder()
        b.add_to("test@example.com")
        b.set_body("Body")
        with self.assertRaises(EmailBuildError):
            b.build()

    def test_no_body_error(self):
        b = EmailMessageBuilder()
        b.add_to("test@example.com")
        b.set_subject("Test")
        with self.assertRaises(EmailBuildError):
            b.build()

    # -----------------------
    # MsmtpClient tests
    # -----------------------
    @patch("msmtp_mail.subprocess.run")
    def test_send_success(self, mock_run):
        """Test that MsmtpClient.send() calls subprocess.run with correct args."""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = b"OK"
        mock_proc.stderr = b""
        mock_run.return_value = mock_proc

        b = EmailMessageBuilder()
        b.add_to("dest@example.com")
        b.set_subject("OK")
        b.set_body("Hi")

        client = MsmtpClient()
        client.send(b)

        called_cmd = mock_run.call_args[0][0]
        self.assertIn("-a", called_cmd)
        self.assertIn("gmail", called_cmd)

    @patch("msmtp_mail.subprocess.run")
    def test_send_failure(self, mock_run):
        """Test MsmtpClient.send() raises MsmtpSendError on failure."""
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = b"AUTH error"
        mock_run.return_value = mock_proc

        b = EmailMessageBuilder()
        b.add_to("dest@example.com")
        b.set_subject("Fail")
        b.set_body("Body")

        client = MsmtpClient()
        with self.assertRaises(MsmtpSendError):
            client.send(b)

    # -----------------------
    # Recipients combination test
    # -----------------------
    def test_recipients_method(self):
        b = EmailMessageBuilder()
        b.add_to("to@example.com")
        b.add_cc("cc@example.com")
        b.add_bcc("bcc@example.com")
        recipients = b.recipients()
        self.assertIn("to@example.com", recipients)
        self.assertIn("cc@example.com", recipients)
        self.assertIn("bcc@example.com", recipients)
        self.assertEqual(len(recipients), 3)  # ensure no duplicates

if __name__ == "__main__":
    unittest.main()
