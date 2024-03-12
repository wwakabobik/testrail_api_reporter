""" This module contains service functions for reporter """

import os

import requests


def format_error(error):
    """
    Service function for parse errors to human-readable format

    :param error: initial error
    :return: formatted string with error details
    """
    err_msg = ""
    error = error if isinstance(error, list) else [error]
    for err in error:
        err_msg = f"{err_msg} : {err}"
    return err_msg


def upload_image(filename, api_token):
    """
    Service function to upload images to third-party image hosting

    :param filename: filename or path to image, which should be uploaded
    :param api_token: unique API token for image upload on https://freeimage.host
    :return: dict with urls with image itself and its thumbnail
    """
    payload = {"action": "upload", "key": api_token, "format": "json"}
    with open(filename, "rb") as source_file:
        response = requests.post(
            url="https://freeimage.host/api/1/upload",
            data=payload,
            timeout=5,
            verify=True,
            files={"source": source_file},
        )
    return {
        "image": response.json()["image"]["url"],
        "thumb": response.json()["image"]["thumb"]["url"],
    }


def delete_file(filename, debug=True, logger=None):
    """
    Service function to delete file from filesystem

    :param filename: filename or path to file, which should be deleted
    :param debug: debug output is enabled, may be True or False, optional, by default, is True
    :param logger: logger, optional
    """
    os.popen(f"rm {filename}").read()
    if debug:
        if logger:
            logger.debug(f"Removed {filename}")
        else:
            print(f"Removed {filename}")


def zip_file(filename, suffix=None, debug=True, logger=None):
    """
    Service function to ZIP file

    :param filename: filename or path to file, which should be zipped
    :param suffix: suffix for zipped file, optional
    :param debug: debug output is enabled may be True or False, optional, by default is True
    :param logger: logger, optional
    :return: zipped filename
    """
    if suffix is None:
        suffix = ""
    zipped_file = f'{filename.split(".")[0]}{suffix}.zip'
    os.popen(f"zip -r {zipped_file} {filename}").read()
    if debug:
        if logger:
            logger.debug(f"ZIPped {filename} to {zipped_file}")
        else:
            print(f"ZIPped {filename} to {zipped_file}")
    return zipped_file


def check_captions_and_files(captions, files, debug, logger=None):
    """
    Service function to check captions and file lists

    :param captions: list of captions for files, list of strings, if not provided, no captions will be added
    :param files: list of images urls
    :param debug: debug output is enabled, may be True or False, optional
    :param logger: logger object, optional
    :return: captions list or None
    """
    return_value = captions
    if not isinstance(captions, list):
        if debug:
            if logger:
                logger.debug("Captions are not a list, thus no legend will be displayed")
            else:
                print("Caption list is empty, no legend will be displayed")
        return_value = None
    elif len(captions) != len(files):
        if debug:
            if logger:
                logger.debug(
                    "Caption and file lists are not the same length %s != %s thus no legend will be displayed",
                    len(captions),
                    len(files),
                )
            else:
                print(
                    f"Caption and file lists are not the same length {len(captions)} != {len(files)} thus "
                    f"no legend will be displayed"
                )
        return_value = None
    return return_value


def init_get_cases_process():
    """
    Service function to initialize a process

    :return: cases_list, first_run, criteria, response, retry
    """
    cases_list = []
    first_run = True
    criteria = None
    response = None
    retry = 0
    return cases_list, first_run, criteria, response, retry
