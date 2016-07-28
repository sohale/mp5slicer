#!/bin/env python3

import logging
import os
import redis
import requests
import subprocess
import sys
import time

sys.path.append(os.getcwd() + os.sep + os.pardir)
from wedesignAPI.wedesignAPI import settings

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_JOB_KEY = 'slice_jobs'

SLICES_DIR = settings.SLICES_ROOT


def get_django_slices_route():
    """Returns the django slices api route."""
    return 'http://{}/api/slicer/'.format(os.environ['DJANGO_HOST'])


def main():
    print("WRAPPER")
    django_slices_route = get_django_slices_route()
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    print("Redis initialized")

    print(int(r.blpop(REDIS_JOB_KEY, 0)[1]))

    slicer_instances = []

    for i in range(10):
        input_file = open('mp5test.mp5', 'r')
        output_file = open(os.path.join(SLICES_DIR, 'result{}.gcode'.format(i)), 'w')

        slicer_instances.append(subprocess.Popen(['python2', 'print_from_pipe.py', 'config/config.json'],
                                                 stdin=input_file, stdout=output_file))

    for process in slicer_instances:
        process.wait()

    input_file.close()
    output_file.close()


if __name__ == "__main__":
   main()
