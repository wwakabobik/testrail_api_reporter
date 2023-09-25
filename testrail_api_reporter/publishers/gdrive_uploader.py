""" Google Drive uploader module """
import json
import os

from ..utils.reporter_utils import delete_file


class GoogleDriveUploader:
    """ Google Drive uploader class """
    # Google token needs to be configured firstly, to do it, you have to visit:
    # https://console.developers.google.com/apis/credentials?pli=1
    # Create Credentials => OAuth client ID => TV and limited Input Devices and get client_id and a client_secret
    # Then pass it as google_id = client_id and google_secret = client_secret
    def __init__(self, google_id, google_secret, google_api_refresh_token=None, cleanup_needed=True,
                 backup_filename='backup.zip', mime_type='application/zip', debug=True):
        """
        General init

        :param google_id: Google OAuth client_id, string, required
        :param google_secret: Google OAuth client_secret, string, required
        :param google_api_refresh_token: Google OAuth refresh token, string, optional
        :param cleanup_needed: delete or not backup file after upload, bool, True or False, by default is True
        :param backup_filename: custom backup filename, which will be uploaded to GDrive, string, optional
        :param mime_type: MIME type of file for upload, string, by default is 'application/zip'
        :param debug: debug output is enabled, may be True or False, optional, by default is True
        """
        if debug:
            print("Initializing Google Drive Uploader")
        # Google
        self.__g_id = google_id
        self.__g_secret = google_secret
        self.__g_token = None
        # Service
        self.__debug = debug
        self.__cleanup_needed = cleanup_needed
        self.__backup_filename = backup_filename
        self.__mime_type = mime_type

        if not google_api_refresh_token or google_api_refresh_token == '':
            self.__g_token, self.__g_refresh_token = self.__first_run()
        else:
            self.__g_refresh_token = google_api_refresh_token

    def __get_new_device_codes(self):
        """
        Get OAuth codes from Google Drive for new device (device code and one-time user code)

        :return: device_code, user_code, verification_url (strings)
        """
        if self.__debug:
            print("Get temporary Device ID and user code from Google Auth engine")
        response = json.loads(os.popen(f'curl '
                                       f'-d "client_id={self.__g_id}&scope=https://www.googleapis.com/auth/drive.file"'
                                       f' https://oauth2.googleapis.com/device/code').read())
        if self.__debug:
            print(response)
        return response['device_code'], response['user_code'], response['verification_url']

    def __get_new_oauth_token(self, device_code):
        """
        Get new OAuth token

        :param device_code: unique device_code generated by Google OAuth API, String, required
        :return: Google OAuth access token, refresh toke (strings)
        """
        if self.__debug:
            print("Get OAuth token from google using Device ID")
        response = json.loads(os.popen(f'curl -d client_id={self.__g_id} -d client_secret={self.__g_secret} '
                                       f'-d device_code={device_code} '
                                       f'-d grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code '
                                       f'https://accounts.google.com/o/oauth2/token').read())
        return response['access_token'], response['refresh_token']

    def __refresh_token(self):
        """
        Refresh Google OAuth token
        Google token has a limited lifetime (1 hour), so, it's need to be updated from time-to-time

        :return: Google OAuth access token (string)
        """
        if self.__debug:
            print("Google OAuth token needs to be refreshed, so, let's do this")
        response = json.loads(os.popen(f'curl -d client_id={self.__g_id} -d client_secret={self.__g_secret} '
                                       f'-d refresh_token={self.__g_refresh_token} '
                                       f'-d grant_type=refresh_token '
                                       f'https://accounts.google.com/o/oauth2/token').read())
        self.__g_token = response['access_token']
        return self.__g_token

    def __first_run(self):
        """
        In case when user did not provide refresh_token, new access and refresh tokens should be obtained.
        To do that, need to:
        1) Generate new device code and get user_code confirmation
        2) Fill this code to google account (i.e. via web browser)
        3) Activate API access token permissions
        4) Generate new access tokens and refresh tokens

        :return: Google OAuth access token, refresh toke (strings)
        """
        device_code, user_code, url = self.__get_new_device_codes()

        print(f"Please fill device code {user_code} into web browser URL: {url}")
        input("When your code will be submitted and account, press enter")
        print("Now you must ensure that your access rights are granted for this device! Proceed to:\n"
              "https://console.developers.google.com/apis/api/drive.googleapis.com/overview\n"
              "and open Credentials tab, now confirm OAuth API permissions for this device.\n"
              "After submit please wait at least 5 minutes.")
        input("When 5 minutes passed, press any enter")

        access_token, refresh_token = self.__get_new_oauth_token(device_code=device_code)

        print(f"Your access token is:\n{access_token}\nYour refresh token is:\n{refresh_token}\n"
              f"Please save these credentials secure!\nYour access token will be valid for an 1 hour. "
              f"If you plan use it in advance, you need to refresh it every hour or before use any time. \n"
              f"Next time init this class with your refresh token to update access token automatically.")

        return access_token, refresh_token

    def __upload_to_gdrive(self, filename=None, mime_type=None):
        """
        Upload file to Google Drive using access token

        :param filename: filename to upload, string
        :param mime_type: MIME type of file, string
        """
        if not filename:
            filename = self.__backup_filename
        if not mime_type:
            mime_type = self.__mime_type
        if self.__debug:
            print(f'Uploading {filename} to GoogleDrive')
        response = json.loads(os.popen(f'curl -X POST -L -H "Authorization: Bearer {self.__g_token}" '
                                       f'-F "metadata={{name :\'{filename.split(".")[0]}\'}};'
                                       f'type=application/json;charset=UTF-8" '
                                       f'-F "file=@{filename};type={mime_type}" '
                                       f'"https://www.googleapis.com/upload/drive/v3/'
                                       f'files?uploadType=multipart"').read())
        if response['id']:
            if self.__debug:
                print(f'Backup archive {filename} was uploaded to Google Drive')
        else:
            print("Something wrong, please check backup manually or re-run")

    # Flow

    def __proceed_upload(self, filename=None, mime_type=None):
        """
        Prepare valid token (update if needed), then upload file to Google Drive using access token

        :param filename: filename to upload, string
        :param mime_type: MIME type of file, string
        """
        if not filename:
            filename = self.__backup_filename
        if not mime_type:
            mime_type = self.__mime_type
        if not self.__g_token:
            self.__refresh_token()
        self.__upload_to_gdrive(filename=filename, mime_type=mime_type)

    def upload(self, filename=None, mime_type=None):
        """
        Upload file to Google Drive and cleanup, if needed.

        :param filename: filename to upload, string
        :param mime_type: MIME type of file, string
        """
        if not filename:
            filename = self.__backup_filename
        if not mime_type:
            mime_type = self.__mime_type
        self.__proceed_upload(filename=filename, mime_type=mime_type)
        if self.__cleanup_needed:
            delete_file(filename=filename, debug=self.__debug)
