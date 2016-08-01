#!/bin/env python3

import datetime
import json
import logging
import mysql.connector
import os
import random
import redis
import requests
import signal
import subprocess
import sys
import time

from io import StringIO

sys.path.append(os.getcwd() + os.sep + os.pardir)
from wedesignAPI.wedesignAPI import settings

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_JOB_KEY = 'slice_jobs'

SLICES_DIR = settings.SLICES_ROOT


def get_django_route():
    """Returns the global django route."""
    return 'http://{}'.format(os.environ['DJANGO_HOST'])


def get_django_slices_route():
    """Returns the django slices api route."""
    return get_django_route() + '/api/slices/'


def get_django_projects_route():
    """Returns the django projects api route."""
    return get_django_route() + '/api/projects/'


def get_authentication(username='Admin', password='J70jK6RNSbQ5NFmtNJKAFCNRRulA4hWD'):
    """
    Gets an authentication token in order to be able to post slices (if admin)
    or retrieve private projects.
    @param username: Username of the user.
    @param password: Password of the user.
    @return: Authorization headers.
    """
    auth_token = requests.post(get_django_route() + '/o/token/',
                               headers={'Content-Type': 'application/x-www-form-urlencoded'},
                               data={
                                   'grant_type': 'password',
                                   'username': username,
                                   'password': password,
                                   'client_id': 'toto'
                               }
                               ).json()

    return {'Authorization': auth_token['token_type'] + ' ' + auth_token['access_token']}


def get_mp5_data(project):
    """
    Retrieves a given project's MP5 data.
    @param project: Project ID.
    @return: MP5 tree as string.
    """
    auth_headers = get_authentication()
    requests.get(get_django_projects_route() + str(project) + '/', headers=auth_headers)
    #print(mp5_data.json())

    connexion = mysql.connector.connect(host='mysql', database=os.environ['MYSQL_DATABASE'],
                                        user='root', password=os.environ['MYSQL_ROOT_PASSWORD'])
    cursor = connexion.cursor()

    query = ("SELECT tree FROM API_project WHERE id = %s")
    cursor.execute(query, (project,))

    mp5_data = '{{"root":{}}}'.format(cursor.fetchone()[0])

    cursor.close()
    connexion.close()

    return mp5_data


def slice_mp5(mp5_data, id):

    if mp5_data == '{"root":{"type":"root","children":[]}}':
        print(id, "EMPTY TREE")
        return

    print(mp5_data)
    output_file = open(os.path.join(SLICES_DIR, 'result_{}.gcode'.format(id)), 'w')

    p = subprocess.Popen(['python2', 'print_from_pipe.py', 'config/config.json'], stdin=subprocess.PIPE, stdout=output_file)
    p.communicate(bytes(mp5_data, 'utf-8'))

    output_file.close()


def main():
    print("WRAPPER")
    django_slices_route = get_django_slices_route()
    print(requests.get(django_slices_route + '1/').json())
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    print("Redis initialized")

    running = True

    def stop_loop(*args):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, stop_loop)

    while running:
        print('Retrieving a project from redis.')
        project = int(r.blpop(REDIS_JOB_KEY, 0)[1])

        print('Retrieved project:', project)
        mp5_data = get_mp5_data(project)
        slice_mp5(mp5_data, project)

    slicer_instances = []

    input_file = open('mp5test.mp5', 'r')
    output_file = open(os.path.join(SLICES_DIR, 'result.gcode'), 'w')

    slicer_instances.append(subprocess.Popen(['python2', 'print_from_pipe.py', 'config/config.json'],
                                             stdin=input_file, stdout=output_file))

    for process in slicer_instances:
        process.wait()

    input_file.close()
    output_file.close()


if __name__ == "__main__":
    main()
