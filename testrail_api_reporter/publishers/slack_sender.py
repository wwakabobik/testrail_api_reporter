# -*- coding: utf-8 -*-
""" Slack sender module """

import json

import requests

from ..utils.logger_config import setup_logger, DEFAULT_LOGGING_LEVEL
from ..utils.reporter_utils import format_error, check_captions_and_files


class SlackSender:
    """Slack sender class, see for details https://api.slack.com/messaging/webhooks"""

    def __init__(self, hook_url=None, timeout=5, verify=True, logger=None, log_level=DEFAULT_LOGGING_LEVEL):
        """
        General init

        :param hook_url: url for Slack API hook, string, required
        :param timeout: timeout for message send, integer, optional
        :param verify: verification required, bool, optional
        :param logger: logger object, optional
        :param log_level: logging level, optional, by default, is 'logging.DEBUG'
        """
        if not logger:
            self.___logger = setup_logger(name="SlackSender", log_file="SlackSender.log", level=log_level)
        else:
            self.___logger = logger
        self.___logger.debug("Initializing Slack Sender")
        if not hook_url:
            raise ValueError("No Slack hook url provided, aborted!")
        self.__hook_url = hook_url
        self.__timeout = timeout
        self.__verify = verify

    @staticmethod
    def __prepare_attachments(files, captions):
        """
        Prepares attachments

        :param files: list of files (images)
        :param captions: list of captions for files, list of strings, if not provided, no captions will be added
        :return: list of dict with attachment info
        """
        legacy_attachments = []
        for j, file in enumerate(files):
            legacy_attachments.append(
                {
                    "pretext": "----",
                    "text": captions[j] if captions else "",
                    "mrkdwn_in": ["text", "pretext"],
                    "image_url": file,
                }
            )
        return legacy_attachments

    @staticmethod
    def __prepare_blocks(title):
        """
        Prepares blocks

        :param title: header message title
        :return: list of dict with blocks info
        """
        return [{"type": "header", "text": {"type": "plain_text", "text": title, "emoji": True}}]

    def __prepare_payload(self, title, files, captions):
        """
        Prepares whole payload

        :param title: header message title
        :param files: list of files (images)
        :param captions: list of captions for files, list of strings, if not provided, no captions will be added to
        :return: json with payload
        """
        return json.dumps(
            {
                "attachments": self.__prepare_attachments(files=files, captions=captions),
                "blocks": self.__prepare_blocks(title=title),
            }
        )

    @staticmethod
    def __prepare_headers():
        """
        Prepares headers for request itself

        :return: json with headers
        """
        return {"Content-type": "application/json", "Accept": "text/plain"}

    def send_message(self, files=None, captions=None, title="Test development & automation coverage report"):
        """
        Send a message to Slack

        :param files: list of urls of images
        :param captions: list of captions for files, list of strings, if not provided, no captions will be added
        :param title: header title of message
        :return: none
        """
        # check params
        if not isinstance(files, list):
            raise ValueError("No file list for report provided, aborted!")
        captions = check_captions_and_files(
            captions=captions,
            files=files,
            debug=self.___logger.level == DEFAULT_LOGGING_LEVEL,
            logger=self.___logger,
        )
        # Send to slack
        try:
            response = requests.post(
                url=self.__hook_url,
                data=self.__prepare_payload(title=title, files=files, captions=captions),
                timeout=self.__timeout,
                verify=self.__verify,
                headers=self.__prepare_headers(),
            )
            if response.status_code != 200:
                raise ValueError(
                    f"Message can't be sent! Error {response.status_code}: {response.text}: "
                    f"{response.raise_for_status()}"
                )
            self.___logger.debug("Message sent!")
        except Exception as error:
            raise ValueError(f"Message can't be sent!\nError{format_error(error)}") from error
