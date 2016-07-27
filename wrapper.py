#!/bin/env python3

import logging
import redis
import requests
import subprocess
import sys
import time

from multiprocessing import Process


REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_JOB_KEY = 'slice_jobs'


def main():
    print("WRAPPER")
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    print("Redis initialized")

    print(int(r.blpop(REDIS_JOB_KEY, 0)[1]))

    input_file = open('mp5test.mp5', 'r')
    output_file = open('result.gcode', 'w')

    p = subprocess.Popen(['python2', 'print_from_pipe.py', 'config/config.json'],
                         stdin=input_file, stdout=output_file)
    p.wait()

    input_file.close()
    output_file.close()


if __name__ == "__main__":
    main()
