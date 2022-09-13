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
