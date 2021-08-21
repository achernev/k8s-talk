#!/usr/bin/env python3

"""
Registers a Kubernetes cluster into Gitlab.
The password for the root user in Gitlab must exist in /etc/gitlab/initial_root_password.
"""

import re
import sys
import json
import time
import os.path
import pathlib
import logging
import http.client
import urllib.parse

LOG_FILE = 'register-k8s.log'
HOSTNAME = 'gitlab.example.com'
CLUSTER_NAME = 'Vagrant'
CLUSTER_ADDRESS = 'https://192.168.50.10:6443'
DOMAIN = 'example.com'
ROOT_PWD = '/etc/gitlab/initial_root_password'
ROOT_PWD_RE = re.compile(r'^Password: (\S+)$')


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


def get_root_password(pwd_file_path: pathlib.Path) -> str:
    if not os.path.isfile(pwd_file_path):
        logging.error('The Gitlab root password file does not exist: %s', pwd_file_path.absolute())
        sys.exit(1)

    root_pwd = None
    with open(pwd_file_path) as pwd_file:
        for line in pwd_file.readlines():
            match = ROOT_PWD_RE.match(line)
            if match:
                root_pwd = match.group(1)
                break

    if root_pwd is None:
        logging.error('Could not determine Gitlab root password from file: %s', pwd_file_path.absolute())
        sys.exit(1)

    return root_pwd


if __name__ == '__main__':
    configure_logging()

    if len(sys.argv) < 3:
        logging.error('Please provide the Gitlab admin service account token and Kubernetes CA cert as arguments.')
        sys.exit(1)

    admin_sa_token = sys.argv[1]
    k8s_ca_cert = sys.argv[2]
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
        'Authorization': f'Bearer {access_token}',
    }
    conn.request('PUT', '/api/v4/application/settings?allow_local_requests_from_web_hooks_and_services=true',
                 headers=headers)
    settings_resp = conn.getresponse()

    if settings_resp.status != 200:
        logging.error(f'An error code was returned whilst changing Gitlab settings: %s %s',
                      settings_resp.status, settings_resp.reason)
        logging.error(settings_resp.read().decode('utf-8'))
        sys.exit(1)

    # Ensure you read() the response or else the next request will fail.
    logging.debug('Settings response body: %r', settings_resp.read().decode('utf-8'))

    # Wait for a minute.
    # See:
    #   https://gitlab.com/gitlab-org/gitlab-foss/-/merge_requests/30233
    #   https://gitlab.com/gitlab-org/gitlab/-/issues/217010
    logging.info('Waiting 60 seconds for Gitlab configuration cache invalidation.')
    time.sleep(60)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    # The below configuration sets the cluster to unmanaged by Gitlab.
    # This is done in order to allow configuring namespaces for the projects.
    body = {
        'name': CLUSTER_NAME,
        'domain': DOMAIN,
        'managed': False,
        'platform_kubernetes_attributes': {
            'api_url': CLUSTER_ADDRESS,
            'token': admin_sa_token,
            'ca_cert': k8s_ca_cert,
        },
    }
    conn.request('POST', '/api/v4/admin/clusters/add', json.dumps(body), headers)
    cluster_resp = conn.getresponse()

    if cluster_resp.status != 201:
        logging.error(f'An error code was returned whilst registering the Kubernetes cluster in Gitlab: %s %s',
                      cluster_resp.status, cluster_resp.reason)
        logging.error(cluster_resp.read().decode('utf-8'))
        sys.exit(1)

    logging.debug('Cluster response body: %r', cluster_resp.read().decode('utf-8'))
    logging.info('Finished registering the Kubernetes cluster.')
