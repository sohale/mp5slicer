#!/bin/env python3

import json
import logging
import mysql.connector
import os
import redis
import requests
import signal
import subprocess
import sys
import time

sys.path.append(os.getcwd() + os.sep + os.pardir)
from wedesignAPI.wedesignAPI import settings

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_SLICE_JOBS_KEY = 'slice_jobs'
REDIS_SLICE_RUNNING_JOBS_KEY = 'slice_running_jobs'

SLICES_DIR = settings.SLICES_ROOT


def init_logging():
    """
    Initialize the logging module, output detailed logs in
    /logs/slicer_worker.log.
    """
    file_directory = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir(file_directory + os.sep + 'logs'):
        os.mkdir(file_directory + os.sep + 'logs')

    # Basic logging set-up, based on the logging cookbook:
    # https://docs.python.org/3/howto/logging-cookbook.html

    # Set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='{}/logs/slicer_worker.log'.format(file_directory),
                        filemode='a')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # Set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # Tell the handler to use this format
    console.setFormatter(formatter)
    # Add the handler to the root logger
    logging.getLogger('').addHandler(console)


def get_django_route():
    """Returns the global django route."""
    return 'http://{}'.format(os.environ['DJANGO_HOST'])


def get_django_slices_route():
    """Returns the django slices api route."""
    return get_django_route() + '/api/slices/'


def get_django_projects_route():
    """Returns the django projects api route."""
    return get_django_route() + '/api/projects/'


def get_authentication(username='Admin', password=os.environ['ADMIN_PASSWORD']):
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

    connexion = mysql.connector.connect(host='mysql', database=os.environ['MYSQL_DATABASE'],
                                        user='root', password=os.environ['MYSQL_ROOT_PASSWORD'])
    cursor = connexion.cursor()

    query = ("SELECT tree FROM API_project WHERE id = %s")
    cursor.execute(query, (project,))

    mp5_data = '{{"root":{}}}'.format(cursor.fetchone()[0])

    cursor.close()
    connexion.close()

    return mp5_data


def slice_mp5(mp5_data, output_filename, error_filename):
    """
    Slice mp5 data into a gcode file.
    @param mp5_data: mp5 data of the project.
    @param output_filename: name of the file to write gcode to.
    @param error_filename: name of the file to write errors' traceback to.
    @return:
    """

    logger = logging.getLogger('{}.slice_mp5'.format(__file__))
    if mp5_data == '{"root":{"type":"root","children":[]}}':
        logger.warning("Tree is empty.")
        return

    output_file = open(os.path.join(SLICES_DIR, output_filename), 'w')

    logger.info("Running slicing script.")
    p = subprocess.Popen(['python2', 'mock_print_from_pipe.py', 'config/config.json'],
                         stdin=subprocess.PIPE, stdout=output_file, stderr=subprocess.PIPE)
    _, err = p.communicate(bytes(mp5_data, 'utf-8'))

    if p.wait() != 0:
        with open(os.path.join(SLICES_DIR, error_filename.format(error_filename)), 'wb') as f:
            logger.error("Slicing failed, traceback in {}.".format(error_filename))
            f.write(err)

        output_file.close()
        os.remove(os.path.join(SLICES_DIR, output_filename))
        raise SliceError
    else:
        output_file.close()
        logger.info("Project sliced.")


class SliceError(Exception):
    """Exception raised on slicer failure."""


def post_slice(project, user, filename):
    """
    Post the sliced project to django.
    @param project: Sliced project id.
    @param user: User who requested the slice.
    @param filename: gcode file name.
    """
    logger = logging.getLogger('{}.post_slice'.format(__file__))
    logger.info("Posting slice to django.")

    auth_headers = get_authentication()
    requests.post(get_django_slices_route(),
                  headers=auth_headers,
                  data={
                      'maker': user,
                      'project': project,
                      'file_path': 'slices/{}'.format(filename)
                  })

    logger.info("Slice posted.")


def process_job(job, redis_client):
    """
    Process a slice job.
    @param job: Job JSON object.
    @param redis_client: Redis client used to remove job from running jobs list.
    """
    logger = logging.getLogger('{}.process_job'.format(__file__))

    mp5_data = get_mp5_data(job['project'])
    filename = 'result_{}_{}.gcode'.format(job['project'], job['user'])

    try:
        slice_mp5(mp5_data, filename, 'error_{}_{}.log'.format(job['project'], job['user']))
    except SliceError:
        logger.error("Error during the slicing.")
    else:
        post_slice(job['project'], job['user'], filename)
    finally:
        redis_client.lrem(REDIS_SLICE_RUNNING_JOBS_KEY, 0, json.dumps(job))


def main():
    init_logging()

    logger = logging.getLogger('{}.main'.format(__file__))
    logger.info("Initializing worker.")

    django_slices_route = get_django_slices_route()
    print(requests.get(django_slices_route + '1/').json())
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    running = True

    def stop_loop(*args):
        nonlocal running
        logging.warning("Main loop interrupted.")
        running = False
    signal.signal(signal.SIGINT, stop_loop)

    logger.info("Entering main loop.")
    while running:
        logger.info("Retrieving a job from Redis...")

        job = json.loads(redis_client.brpoplpush(REDIS_SLICE_JOBS_KEY, REDIS_SLICE_RUNNING_JOBS_KEY, 0)
                         .decode(encoding='utf-8')
                         )

        logger.info("Job retrieved: {}".format(job))
        process_job(job, redis_client)


if __name__ == "__main__":
    main()
