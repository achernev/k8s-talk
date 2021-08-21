#!/usr/bin/env python3

"""
Registers a new runner in Gitlab via its API.
You must supply the runner registration token as an argument.
This can be obtained with the following command on the Gitlab host:
  gitlab-rails runner -e production \
    "puts Gitlab::CurrentSettings.current_application_settings.runners_registration_token"
"""

import re
import sys
import json
import os.path
import pathlib
import logging
import http.client
import urllib.parse

LOG_FILE = 'register-runner.log'
HOSTNAME = 'gitlab.example.com'
RUNNER_NAME = 'gitlab-runner'
ROOT_PWD = '/etc/gitlab/initial_root_password'
ROOT_PWD_RE = re.compile(r'^Password: (\S+)$')
TOKEN_OUTPUT = 'runner-auth-token'


# noinspection DuplicatedCode
def configure_logging():
    log_formatter = logging.Formatter('%(asctime)s %(levelname)-5.5s -- %(message)s')
    root_logger = logging.getLogger()
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)


def get_root_password(pwd_file_path: pathlib.Path):
    if not os.path.isfile(pwd_file_path):
        logging.error(f'The Gitlab root password file does not exist: %s', pwd_file_path.absolute())
        sys.exit(1)

    root_pwd = None
    with open(pwd_file_path) as pwd_file:
        for line in pwd_file.readlines():
            match = ROOT_PWD_RE.match(line)
            if match:
                root_pwd = match.group(1)
                break

    if root_pwd is None:
        logging.error(f'Could not determine Gitlab root password from file: %s', pwd_file_path.absolute())
        sys.exit(1)

    return root_pwd


if __name__ == '__main__':
    configure_logging()

    if len(sys.argv) < 2:
        logging.error('Please provide the Gitlab runner registration token as argument.')
        sys.exit(1)

    runner_reg_token = sys.argv[1]
    # noinspection DuplicatedCode
    root_password = get_root_password(pathlib.Path(ROOT_PWD))

    conn = http.client.HTTPSConnection(HOSTNAME)

    body = urllib.parse.urlencode({'grant_type': 'password', 'username': 'root', 'password': root_password})
    conn.request('POST', '/oauth/token', body)
    login_resp = conn.getresponse()

    if login_resp.status != 200:
        logging.error(f'An error code was returned whilst requesting OAuth2 token from Gitlab: %s %s',
                      login_resp.status, login_resp.reason)
        logging.error(login_resp.read().decode('utf-8'))
        sys.exit(1)

    token_info = json.loads(login_resp.read())
    access_token = token_info['access_token']

    logging.info('Gitlab OAuth2 token obtained.')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    body = urllib.parse.urlencode({'token': runner_reg_token, 'description': RUNNER_NAME})
    conn.request('POST', '/api/v4/runners', body, headers)
    runner_resp = conn.getresponse()

    if runner_resp.status != 201:
        logging.error(f'An error code was returned whilst registering the runner in Gitlab: %s %s',
                      runner_resp.status, runner_resp.reason)
        logging.error(runner_resp.read().decode('utf-8'))
        sys.exit(1)

    registration_info = json.loads(runner_resp.read())
    runner_auth_token = registration_info['token']

    output_path = pathlib.Path(TOKEN_OUTPUT)
    with open(output_path, 'w') as output:
        output.write(runner_auth_token)

    logging.info('Finished registering the runner, auth token written to: %s', output_path.absolute())
