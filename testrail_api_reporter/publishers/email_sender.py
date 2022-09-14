from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from ..utils.reporter_utils import format_error


class EmailSender:
    def __init__(self, email=None, password=None, server_smtp=None, server_port=None, debug=True):
        """
        General init

        :param email: email of user, from which emails will be sent, string
        :param password: password of user, from which emails will be sent, string
        :param server_smtp: full smtp address (endpoint) of mail server, string
        :param server_port: mail server port, integer
        :param debug: debug output is enabled, may be True or False, optional
        """
        if debug:
            print("Email Sender init")
        self.__debug = debug
        if email is None or password is None or server_smtp is None or server_port is None:
            raise ValueError("No email credentials are provided, aborted!")
        self.__email = email
        self.__password = password
        self.__server_smtp = server_smtp
        self.__server_port = server_port

    def send_message(self, files=None, captions=None, image_width="400px", title=None, timestamp=None, recipients=None,
                     debug=None):
        """
        Send email to recipients with report (with attached images)

        :param files: list of filenames (maybe with path) with charts to attach to report, list of strings, required
        :param captions: captions for charts, length should be equal to count of files, list of strings, optional
        :param image_width: default image width, string, optional
        :param title: title of report, string, optional
        :param timestamp: non-default timestamp, string, optional, will be used only when title is not provided
        :param recipients: list of recipient emails, list of strings, optional
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        # Check params
        if not isinstance(files, list):
            raise ValueError("No file list for report provided, aborted!")
        if isinstance(recipients, str):
            recipients = [recipients]
        elif not isinstance(recipients, list):
            raise ValueError("Wrong list of recipients is provided, aborted!")
        debug = debug if debug is not None else self.__debug
        if not isinstance(captions, list):
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
        connection = self.__connect_to_server()
        message = self.__prepare_payload(files=files, captions=captions, image_width=image_width, title=title,
                                         recipients=recipients)
        self.__send_to_server(connection=connection, recipients=recipients, message=message)
        self.__disconnect_from_server(connection=connection)
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

    def __prepare_payload(self, files, image_width, title, recipients, captions=None):
        """

        :param files: list of filenames (maybe with path) with charts to attach to report, list of strings, required
        :param captions: captions for charts, length should be equal to count of files, list of strings, optional
        :param image_width: default image width, string
        :param title: title of report, string
        :param recipients: list of recipient emails, list of strings, optional
        :return: formatted multipart message
        """
        message = MIMEMultipart("alternative")
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
