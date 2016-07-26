#!/bin/env python3

import os
import signal
import sys
import redis
import requests
import time

"""
    This is the API communication wrapper for the MP5 slicer. Workflow:

    - Endlessly looping until SIGINT is catched,
      then cleanly aborts running task and report reason to API.
        - Blocks until a pk is retrieved from task list on Redis.
        - Fetches arguments and MP5 tree from the API service.
        - Forks and calls slicer with the retrieved settings as cmd args.

        -       Main process         Fork                Slicer
          ===============================================================
                                      ||stdin
        -  writes actual object in  =====>
                                      ||
                                      ||stderr
        -  broadcasts progress and  <=====     print formatted progress
          store debug logs in memory  ||             and debug logs
                                      ||
                                      ||stdout
        -                           <=====    writes final sliced object
          ===============================================================
                      /                                   \/
                    \/                                    /\
                 continues                               dies

        - Main process then continues and check for the slicer's exit code,
           if exited with != 0, generates traceback and uploads it to django.
           Otherwise, it uploads the file to Django API and inform subscribed
           users task have finished.

"""


def usage():
    print('usage: ./wrapper.py')
    exit()


def parse_args(settings):
    return ['--{}={} '.format(key, settings[key]) for key in settings]


class Redis:
    def __init__(self):
        self.client = redis.StrictRedis(
            host='redis',
            port=6379,
            db=1
        )

    def pop(self):
        while True:
            try:
                return int(self.client.blpop('s', 0)[1])
            except:
                print(sys.argv[0], ": blpop() failed.")
                time.sleep(0.5)  # We sleep half a second to prevent from overloading CPU

    def broadcast_progress(self, task_id, progress):
        return self.client.publish('s:{}'.format(task_id), progress)


def execute(task, broadcast):
    """
    All names relative to the slicer
    """

    (r_stdout, w_stdout) = os.pipe()
    (r_stderr, w_stderr) = os.pipe()
    (r_stdin, w_stdin) = os.pipe()
    err = ''

    args = [WRAPPER_SETTINGS['exec']]
    args += parse_args(task['settings'])
    father = os.fork()
    if father:
        for fd in [r_stdin, w_stderr, w_stdout]:
            os.close(fd)
        errs = os.fdopen(r_stderr)
        ok = os.fdopen(r_stdout)
        os.write(w_stdin, bytes(str(task['obj']['root']), 'utf-8'))
        os.close(w_stdin)
        for line in errs:
            if line.startswith(WRAPPER_SETTINGS['progress_mark']):
                broadcast(line[len(WRAPPER_SETTINGS['progress_mark']):-1])
            err += line
        errs.close()
        pid, status = os.waitpid(father, 0)
        if status is not 0:
            ok.close()
            raise Exception(status, err)
        else:
            sliced = ok.read()
            ok.close()
            return sliced, err
    else:
        for fd in [w_stdin, r_stderr, r_stdout]:
            os.close(fd)
        for (old, new) in [(1, w_stdout), (2, w_stderr), (0, r_stdin)]:
            os.dup2(new, old)
        os.execv('./a.out', ['./a.out', ])#args)
        os._exit(0)


def get_settings():

    default = {
        'exec':         ('./slicer.py', str),
        'workers':      (4, int),
        'django_host':  ('http://{}/api/slicer/'.format(os.environ.get(
                                'DJANGO_HOST', '192.168.1.123')), str),
        'progress_mark':('>>>>', str),
    }
    opts = True

    for arg in sys.argv[1:]:

        if opts and arg is '--':
            opts = False
        elif opts and arg.startswith('--'):
            try:
                tab = arg[2:].split('=')
                if len(tab) > 2:
                    usage()
                elif len(tab) == 2:
                    default[tab[0]][0] = tab[1]
                else:
                    setattr(default, True)
            except:
                print('no such option: ' + arg)
                usage()
        else:
            usage()

    ret = {}
    for key in default:
        ret[key] = default[key][0]
    return ret


WRAPPER_SETTINGS = get_settings()


def main():

    should_quit = False

    def gracefully_exit(*args):
        nonlocal should_quit
        should_quit = True
    signal.signal(signal.SIGINT, gracefully_exit)

    # Next section up to the while is to be deleted
    f = open('./testfile')
    task = {
        "obj": {
            "root": f.read()
        },
        "settings": {}
    }

    while not should_quit:

        r = Redis()
        running = False
        pk = r.pop()  # blocking until a task is actually retrieved
        if should_quit:
            print("This is a complicated edge case to handle. We should probably abort and report to the API if we still have the time")
            exit(1)
        url = WRAPPER_SETTINGS['django_host'] + str(pk)

#TODO:API request        task = requests.get(url + '/start/', data = {}) # /!\ FIX ME: Need to authenticate

        traceback = None
        try:
            sliced, debug = execute(task, lambda x: r.broadcast_progress(pk, x))
            r.broadcast_progress(pk, 100)
        except Exception as inst:
            print(inst)
            print('ERROR: process exited with status code {}, printing full error log:'.format(inst.args[0]))
            print(inst.args[1])
            traceback = inst.args[1]
            r.broadcast_progress(pk, -1)

#TODO:API request        ret = requests.patch(url + '/end/', data = {'status':0, 'logs':''})

        # Remove the following when implemented correctly
        if traceback is not None:
            print("++++++++++++++ ERROR ENCOUNTERED +++++++++++++++++++")
            print(traceback)
        else:
            print("============== FINAL OUTPUT ========================")
            print(sliced)
            print()
            print("==============  DEBUG LOGS  ========================")
            print(debug)

if __name__ == '__main__':
    main()
