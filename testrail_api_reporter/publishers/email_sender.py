""" Email sender module """
import base64
import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httplib2
from apiclient import discovery
from oauth2client import client, tools, file

from ..utils.reporter_utils import format_error, check_captions_and_files


class EmailSender:
    """Email sender class"""

    def __init__(self, email=None, password=None, server_smtp=None, server_port=None, gmail_token=None, debug=True):
        """
        General init

        :param email: email of user, from which emails will be sent, string
        :param password: password of user, from which emails will be sent, string
        :param server_smtp: full smtp address (endpoint) of mail server, string
        :param server_port: mail server port, integer
        :gmail_token: gmail OAuth secret file (expected json)
        :param debug: debug output is enabled, may be True or False, optional
        """
        if debug:
            print("Email Sender init")
        self.__debug = debug
        self.__method = None
        if email is not None and password is not None and server_smtp is not None and server_port is not None:
            self.__method = "regular"
        elif gmail_token and email:
            gmail_token = f"{os.getcwd()}/{gmail_token}" if not os.path.exists(gmail_token) else gmail_token
            if os.path.exists(gmail_token):
                self.__method = "gmail"
                self.__gmail_scopes = "https://www.googleapis.com/auth/gmail.send"
                self.__gmail_app_name = "Gmail API Python Send Email"
        if not self.__method:
            raise ValueError("No email credentials are provided, aborted!")
        self.__email = email
        self.__password = password
        self.__server_smtp = server_smtp
        self.__server_port = server_port
        self.__gmail_token = gmail_token

    def send_message(  # pylint: disable=too-many-branches
        self,
        files=None,
        captions=None,
        image_width="400px",
        title=None,
        timestamp=None,
        recipients=None,
        method=None,
        custom_message=None,
        custom_folder=os.path.join(os.path.expanduser("~"), ".credentials"),
        debug=None,
    ):
        """
        Send email to recipients with report (with attached images)

        :param files: list of filenames (maybe with path) with charts to attach to report, list of strings, required
        :param captions: captions for charts, length should be equal to count of files, list of strings, optional
        :param image_width: default image width, string, optional
        :param title: title of report, string, optional
        :param timestamp: non-default timestamp, string, optional, will be used only when title is not provided
        :param recipients: list of recipient emails, list of strings, optional
        :param method: method which will be used for sending
        :param custom_message: custom message, prepared by user at his own, by default its payload with TR state report
        :param custom_folder: custom home folder for gmail credentials storage, by default is ~/.credentials
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        # Check params
        if not method:
            method = self.__method
        if not isinstance(files, list) and not custom_message:
            raise ValueError("No file list for report provided, aborted!")
        if isinstance(recipients, str) and not custom_message:
            recipients = [recipients]
        elif not isinstance(recipients, list) and not custom_message:
            raise ValueError("Wrong list of recipients is provided, aborted!")
        debug = debug if debug is not None else self.__debug
        captions = check_captions_and_files(captions=captions, files=files, debug=debug)
        if not captions or custom_message:
            if debug:
                print("Caption list override by custom message, no legend will be displayed")
        timestamp = timestamp if timestamp else datetime.now().strftime("%Y-%m-%d")
        title = title if title else f"Test development & automation coverage report for {timestamp}"

        # Connect and send message
        if not custom_message:
            message = self.__prepare_payload(
                files=files,
                captions=captions,
                image_width=image_width,
                title=title,
                recipients=recipients,
                method=method,
            )
        else:
            if debug:
                print("Ignoring payload preparations, assuming user custom message is right")
            message = custom_message
        if method == "regular":
            connection = self.__connect_to_server()
            self.__send_to_server(connection=connection, recipients=recipients, message=message)
            self.__disconnect_from_server(connection=connection)
        elif method == "gmail":
            self.__gmail_send_message(message=message, custom_folder=custom_folder)
        if debug:
            print("Email sent!")

    def __connect_to_server(self):
        """
        Connects to mail server

        :return: connection handle ( smtplib.SMTP )
        """
        if self.__debug:
            print(f"Connecting to custom mail server {self.__server_smtp}:{self.__server_port} using {self.__email}")
        try:
            connection = smtplib.SMTP(self.__server_smtp, self.__server_port)
            connection.ehlo()
            connection.starttls()
            connection.login(self.__email, self.__password)
        except Exception as error:
            raise ValueError(f"Can't login to mail!\nError{format_error(error)}") from error
        return connection

    def __send_to_server(self, connection, recipients, message):
        """
        Send data to server to mail server

        :param connection: connection handle ( smtplib.SMTP )
        :param recipients: list of recipient emails, list of strings, optional
        :param message: formatted multipart message
        :return: none
        """
        if self.__debug:
            print(f"Sending mail from {self.__email} to {recipients}")
        try:
            connection.sendmail(from_addr=self.__email, to_addrs=recipients, msg=message.as_string())
        except Exception as error:
            raise ValueError(f"Can't send mail!\nError{format_error(error)}") from error

    def __disconnect_from_server(self, connection):
        """
        Connects to mail server

        :param connection: connection handle ( smtplib.SMTP )
        :return: none
        """
        if self.__debug:
            print("Disconnecting from custom server")
        try:
            connection.quit()
        except Exception as error:
            raise ValueError(f"Can't close connection!\nError{format_error(error)}") from error

    def __prepare_payload(self, files, image_width, title, recipients, captions=None, method=None):
        """
        Prepare payload method (mail content)

        :param files: list of filenames (maybe with path) with charts to attach to report, list of strings, required
        :param captions: captions for charts, length should be equal to count of files, list of strings, optional
        :param image_width: default image width, string
        :param title: title of report, string
        :param recipients: list of recipient emails, list of strings, optional
        :param method: specify which method is used to set proper MIMEMultipart type ('gmail' or not)
        :return: formatted multipart message
        """
        message = MIMEMultipart("alternative") if method != "gmail" else MIMEMultipart()
        message["Subject"] = title
        message["From"] = self.__email
        message["To"] = ", ".join(recipients)
        html = (
            '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            f"<title>{title}</title></head>"
            f'<body><div align="center"><h3>{title}'
            '</h3></div><table border="0px" width="100%"><tbody><td>'
        )
        for j, val in enumerate(files):
            with open(f"{val}", "rb") as attachment:
                mime_image = MIMEImage(attachment.read())

            # Define the image's ID with counter as you will reference it.
            mime_image.add_header("Content-ID", f"<image_id_{j}>")
            mime_image.add_header("Content-Disposition", f"attachment; filename= {val}")
            message.attach(mime_image)
            # add to body
            if captions:
                html = f'{html}<tr><div align="center"><b>{captions[j]}</b></div></tr>'
            html = (
                f'{html}<tr><div align="center"><img src="cid:image_id_{j}" '
                f'width="{image_width}" height="auto">></div></tr>'
            )
        html = f"{html}</td></tbody></table></body></html>"
        message.attach(MIMEText(html, "html"))
        return message

    def __gmail_get_credential_path(self, custom_folder=os.path.join(os.path.expanduser("~"), ".credentials")):
        """
        Service function target Google OAuth credentials path to storage

        :param custom_folder: custom home folder for gmail credentials storage, by default is ~/.credentials
        :return: credentials file path (string)
        """
        if self.__debug:
            print(f"Checking GMail credentials path at {custom_folder}")
        try:
            if self.__debug:
                print(f"No credential directory found, creating new one here: {custom_folder}")
            os.makedirs(custom_folder, exist_ok=True)
        except OSError as error:
            if self.__debug:
                print(f"Original Error{format_error(error)}")
        credential_path = os.path.join(custom_folder, "gmail-python-email-send.json")
        return credential_path

    def __gmail_get_credentials(self, custom_folder=os.path.join(os.path.expanduser("~"), ".credentials")):
        """
        Service function to get and convert Google OAuth credential from client_id and client_secret

        :param custom_folder: custom home folder for gmail credentials storage, by default is ~/.credentials
        :return: credentials
        """
        credential_path = self.__gmail_get_credential_path(custom_folder=custom_folder)
        if self.__debug:
            print(f"Obtaining GMail credentials from {credential_path}")
        try:
            store = file.Storage(credential_path)
        except Exception as error:
            raise ValueError(f"Couldn't open storage\nError{format_error(error)}") from error
        try:
            credentials = store.get()
        except Exception as error:
            raise ValueError(f"Obtaining of credentials unexpectedly failed\nError{format_error(error)}") from error
        if not credentials or credentials.invalid:
            try:
                flow = client.flow_from_clientsecrets(self.__gmail_token, self.__gmail_scopes)
            except Exception as error:
                raise ValueError(
                    f"Couldn't obtain new client secrets from Google OAuth\nError{format_error(error)}"
                ) from error
            flow.user_agent = self.__gmail_app_name
            try:
                credentials = tools.run_flow(flow, store)
            except Exception as error:
                raise ValueError(
                    f"Couldn't obtain new credential from Google OAuth\nError{format_error(error)}"
                ) from error
            if self.__debug:
                print("Credentials stored to " + credential_path)
        return credentials

    def __gmail_send_message(self, message, custom_folder=os.path.join(os.path.expanduser("~"), ".credentials")):
        """
        Send Email via GMail

        :param message: message in MIME type format
        :param custom_folder: custom home folder for gmail credentials storage, by default is ~/.credentials
        :return: none
        """
        if self.__debug:
            print("Sending message using GMail")
        credentials = self.__gmail_get_credentials(custom_folder=custom_folder)
        try:
            http = credentials.authorize(httplib2.Http())
        except Exception as error:
            raise ValueError(f"Can't authorize via Google OAuth\nError{format_error(error)}") from error
        try:
            service = discovery.build("gmail", "v1", http=http)
        except Exception as error:
            raise ValueError(f"Can't build service for Google OAuth\nError{format_error(error)}") from error
        try:
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        except Exception as error:
            raise ValueError(f"Can't convert payload to base64\nError{format_error(error)}") from error
        self.__gmail_send_message_internal(service, self.__email, {"raw": raw})

    def __gmail_send_message_internal(self, service, user_id, message):
        """
        Low-level gmail sent function to send email via GMail API service

        :param service: service API
        :param user_id: user id, the same as "from" email field
        :param message: formatted in base64 type encoded raw message
        :return: message
        """
        try:
            message = service.users().messages().send(userId=user_id, body=message).execute()
            if self.__debug:
                print(f'Message sent with Id: "{message["id"]}"!')
            return message
        except Exception as error:
            raise ValueError(f"Can't send mail via GMail!\nError{format_error(error)}") from error
