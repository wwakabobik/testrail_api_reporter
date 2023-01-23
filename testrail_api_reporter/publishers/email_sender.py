import os
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import smtplib
import httplib2
from oauth2client import client, tools, file
from apiclient import discovery

from ..utils.reporter_utils import format_error


class EmailSender:
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
            self.__method = 'regular'
        elif gmail_token and email:
            gmail_token = f'{os.getcwd()}/{gmail_token}' if not os.path.exists(gmail_token) else gmail_token
            if os.path.exists(gmail_token):
                self.__method = 'gmail'
                self.__gmail_scopes = 'https://www.googleapis.com/auth/gmail.send'
                self.__gmail_app_name = 'Gmail API Python Send Email'
        if not self.__method:
            raise ValueError("No email credentials are provided, aborted!")
        self.__email = email
        self.__password = password
        self.__server_smtp = server_smtp
        self.__server_port = server_port
        self.__gmail_token = gmail_token

    def send_message(self, files=None, captions=None, image_width="400px", title=None, timestamp=None, recipients=None,
                     method=None, custom_message=None, debug=None):
        """
        Send email to recipients with report (with attached images)

        :param files: list of filenames (maybe with path) with charts to attach to report, list of strings, required
        :param captions: captions for charts, length should be equal to count of files, list of strings, optional
        :param image_width: default image width, string, optional
        :param title: title of report, string, optional
        :param timestamp: non-default timestamp, string, optional, will be used only when title is not provided
        :param recipients: list of recipient emails, list of strings, optional
        :param method: method which will be used for sending
        :param custom_message: custom message, prepared by user at his own, by default it's payload with TR state report
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
        if not isinstance(captions, list) or custom_message:
            if debug:
                print("Caption list is empty, no legend will be displayed")
            captions = None
        elif len(captions) != len(files):
            if debug:
                print(f"Caption and file lists are not the same length {len(captions)} != {len(files)} thus "
                      f"no legend will be displayed")
            captions = None
        timestamp = timestamp if timestamp else datetime.now().strftime("%Y-%m-%d")
        title = title if title else f"Test development & automation coverage report for {timestamp}"

        # Connect and send message
        if not custom_message:
            message = self.__prepare_payload(files=files, captions=captions, image_width=image_width, title=title,
                                             recipients=recipients, method=method)
        else:
            if debug:
                print("Ignoring payload preparations, assuming user custom message is right")
            message = custom_message
        if method == 'regular':
            connection = self.__connect_to_server()
            self.__send_to_server(connection=connection, recipients=recipients, message=message)
            self.__disconnect_from_server(connection=connection)
        elif method == 'gmail':
            self.__gmail_send_message(message=message)
        if debug:
            print("Email sent!")

    def __connect_to_server(self):
        """
        Connects to mail server

        :return: connection handle ( smtplib.SMTP )
        """
        try:
            connection = smtplib.SMTP(self.__server_smtp, self.__server_port)
            connection.ehlo()
            connection.starttls()
            connection.login(self.__email, self.__password)
        except Exception as e:
            raise ValueError(f"Can't login to mail!\nError{format_error(e)}")
        return connection

    def __send_to_server(self, connection, recipients, message):
        """
        Send data to server to mail server

        :param connection: connection handle ( smtplib.SMTP )
        :param recipients: list of recipient emails, list of strings, optional
        :param message: formatted multipart message
        :return: none
        """
        try:
            connection.sendmail(from_addr=self.__email, to_addrs=recipients, msg=message.as_string())
        except Exception as e:
            raise ValueError(f"Can't send mail!\nError{format_error(e)}")

    @staticmethod
    def __disconnect_from_server(connection):
        """
        Connects to mail server

        :param connection: connection handle ( smtplib.SMTP )
        :return: none
        """
        try:
            connection.quit()
        except Exception as e:
            raise ValueError(f"Can't close connection!\nError{format_error(e)}")

    def __prepare_payload(self, files, image_width, title, recipients, captions=None, method=None):
        """

        :param files: list of filenames (maybe with path) with charts to attach to report, list of strings, required
        :param captions: captions for charts, length should be equal to count of files, list of strings, optional
        :param image_width: default image width, string
        :param title: title of report, string
        :param recipients: list of recipient emails, list of strings, optional
        :param method: specify which method is used to set proper MIMEMultipart type ('gmail' or not)
        :return: formatted multipart message
        """
        message = MIMEMultipart("alternative") if method != 'gmail' else MIMEMultipart()
        message["Subject"] = title
        message["From"] = self.__email
        message["To"] = ", ".join(recipients)
        html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">' \
               f'<title>{title}</title></head>' \
               f'<body><div align="center"><h3>{title}' \
               '</h3></div><table border="0px" width="100%"><tbody><td>'
        for j, val in enumerate(files):
            with open('{}'.format(val), "rb") as attachment:
                mime_image = MIMEImage(attachment.read())

            # Define the image's ID with counter as you will reference it.
            mime_image.add_header('Content-ID', f'<image_id_{j}>')
            mime_image.add_header('Content-Disposition', f'attachment; filename= {val}')
            message.attach(mime_image)
            # add to body
            if captions:
                html = f'{html}<tr><div align="center"><b>{captions[j]}</b></div></tr>'
            html = f'{html}<tr><div align="center"><img src="cid:image_id_{j}" ' \
                   f'width="{image_width}" height="auto">></div></tr>'
        html = f'{html}</td></tbody></table></body></html>'
        message.attach(MIMEText(html, "html"))
        return message

    def __gmail_get_credentials(self, debug=None):
        """
        Service function to get and convert Google OAuth credential from client_id and client_secret

        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        if not debug:
            debug = self.__debug
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            try:
                if debug:
                    print(f"No credential directory found, creating new one here: {credential_dir}")
                os.makedirs(credential_dir)
            except OSError:
                credential_dir = os.path.abspath(os.path.join(__file__, os.pardir))
                if debug:
                    print("Can't create directory! Trying to make directory here: {credential_dir}")
                try:
                    os.makedirs(credential_dir)
                except Exception as e:
                    raise ValueError(f"Can't create directory!\nError{format_error(e)}")
        credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            try:
                flow = client.flow_from_clientsecrets(self.__gmail_token, self.__gmail_scopes)
            except Exception as e:
                raise ValueError(f"Can't obtain new client secrets from Google OAuth\nError{format_error(e)}")
            flow.user_agent = self.__gmail_app_name
            try:
                credentials = tools.run_flow(flow, store)
            except Exception as e:
                raise ValueError(f"Can't obtain new credential from Google OAuth\nError{format_error(e)}")
            if debug:
                print('Storing credentials to ' + credential_path)
        return credentials

    def __gmail_send_message(self, message):
        """
        Send Email via GMail

        :param message: message in MIME type format
        :return: none
        """
        credentials = self.__gmail_get_credentials()
        try:
            http = credentials.authorize(httplib2.Http())
        except Exception as e:
            raise ValueError(f"Can't authorize via Google OAuth\nError{format_error(e)}")
        try:
            service = discovery.build('gmail', 'v1', http=http)
        except Exception as e:
            raise ValueError(f"Can't build service for Google OAuth\nError{format_error(e)}")
        try:
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        except Exception as e:
            raise ValueError(f"Can't convert payload to base64\nError{format_error(e)}")
        self.__gmail_send_message_internal(service, self.__email, {'raw': raw})

    def __gmail_send_message_internal(self, service, user_id, message, debug=None):
        """
        Low-level gmail sent function to send email via GMail API service

        :param service: service API
        :param user_id: user id, the same as "from" email field
        :param message: formatted in base64 type encoded raw message
        :param debug: debug output is enabled, may be True or False, optional
        :return: message
        """
        if not debug:
            debug = self.__debug
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())
            if debug:
                print(f'Message Id: {message["id"]}')
            return message
        except Exception as e:
            raise ValueError(f"Can't send mail via GMail!\nError{format_error(e)}")
