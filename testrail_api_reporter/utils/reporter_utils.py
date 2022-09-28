import os

import requests


def format_error(error):
    """
    Service function for parse errors to human-readable format

    :param error: initial error
    :return: formatted string with error details
    """
    err_msg = ''
    error = error if isinstance(error, list) else [error]
    for err in error:
        err_msg = f'{err_msg} : {err}'
    return err_msg


def upload_image(filename, api_token):
    """
    Service function to upload images to third-party image hosting

    :param filename: filename or path to image, which should be uploaded
    :param api_token: unique API token for image upload on https://freeimage.host
    :return: dict with urls with image itself and its thumbnail
    """
    payload = {
        'type': 'file',
        'action': 'upload',
        'key': api_token
    }
    files = {'source': open(filename, 'rb')}
    response = requests.post(url='https://freeimage.host/api/1/upload',
                             data=payload, timeout=5, verify=True, files=files)
    return {'image': response.json()['image']['file']['resource']['chain']['image'],
            'thumb': response.json()['image']['file']['resource']['chain']['thumb']}


def delete_file(filename, debug=True):
    os.popen(f'rm {filename}').read()
    if debug:
        print(f'Removed {filename}')


def zip_file(filename, suffix=None, debug=True):
    if suffix is None:
        suffix = ''
    zipped_file = f'{filename.split(".")[0]}{suffix}.zip'
    os.popen(f'zip -r {zipped_file} {filename}').read()
    if debug:
        print(f'ZIPped {filename} to {zipped_file}')
    return zipped_file
