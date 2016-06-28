#!/bin/env python3

import os
import signal
import sys
import couchdb
import redis
import requests

"""
    This is the API communication wrapper for the MP5 slicer. Workflow:

    - Endlessly looping until SIGINT is catched. Then cleanly aborts running task and report reason to API.
    - Fetches arguments and MP5 tree from the API service.
    - 


"""


def usage():
    print('./wrapper.py')

def parse_args(settings):
    return ['--{}={} '.format(key, settings[key]) for key in settings]

class Storage():

    @staticmethod
    def __connect():
        couchdb.Server(url='http://couchdb:5984')

    @staticmethod
    def get_object(storage_ID):
        return Storage.__connect()['objects'][storage_ID]['ObjectMP5']

    @staticmethod
    def put_slice(task, sliced):
        return Storage.__connect()['objects'].put_attachment(
            server['objects'][task.storage_ID],
            sliced,
            filename=('sliced.gcode')
        )


class Redis():

    def __init__(self):
        self.client = redis.StrictRedis(
            host= 'redis',
            port= 6379,
            db= 1
        )
        return self

    def __del__(self):
        self.client.exit()
        del self.client

    def pop(self):
        while True:
            try:
                return self.client.blpop('s', 0)
            except:
                print(sys.argv[0], ": blpop() failed.")
                pass

    def broadcast_progress(self, task_ID, progress):
        return self.client.publish('s:{}'.format(task_ID), progress)


def execute(task, broadcast):
    '''
        All names relative to the slicer
    '''

    (r_stdout, w_stdout) = os.pipe()
    (r_stderr, w_stderr) = os.pipe()
    (r_stdin, w_stdin)   = os.pipe()
    err = []


    args = [WRAPPER_SETTINGS['exec']]
    args += parse_args(task['settings'])
    father = os.fork()
    if father:
        for fd in [r_stdin, w_stderr, w_stdout]:
            os.close(fd)
        errs = os.fdopen(r_stderr)
        ok  = os.fdopen(r_stdout)
        os.write(w_stdin, bytes(string(task['obj']['root']), 'utf-8'))
        os.close(w_stdin)
        for line in errs:
            if line.startswith(WRAPPER_SETTINGS['progress_mark']):
                broadcast(line[4:])
            err.append(line)
        errs.close()
        pid, status = os.waitpid(father, 0)
        if status is not 0:
            ok.close()
            raise Exception(status, err)
        else:
            print(ok.read())
            ok.close()
    else:
        for fd in [w_stdin, r_stderr, r_stdout]:
            os.close(fd)
        for (old, new) in [(1, w_stdout), (2, w_stderr), (0, r_stdin)]:
            os.dup2(new, old)
        os.execv('./a.out', args)
        os.exit(0)


def get_settings():

    default = {
        'exec':         ('./slicer.py', str),
        'workers':      (4, int),
        'django_host':  ('http://{}/api/slicer/'.format(os.environ.get(
                                'DJANGO_HOST', '192.168.1.123')), str),
        'progress_mark':('>>>>', str),
    }
    opts = True

    for arg in sys.argv:

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

    while not should_quit:
        r = Redis()
        pk = r.pop() # blocking until a task is actually retrieved
        url = WRAPPER_SETTINGS['django_host'] + pk
        task = requests.post(url + '/start/', data = {}) # /!\ FIX ME: Need to authenticate
        task['obj'] = Storage.get_object(task.storage_ID)
        try:
            sliced = execute(task, lambda x: r.broadcast_progress(pk, x))
            Storage.put_slice(task, sliced)
            ret = requests.post(url + '/end/', data = {'status':0, 'logs':''})
            r.broadcast_progress(pk, 100)
        except Exception as inst:
            print('ERROR: process exited with status code {}, printing full error log:'.format(inst.args[0]))
            print(inst.args[1])
            ret = requests.post(url + '/end/', data = {'status':inst.args[0], 'logs':inst.args[1]})


if __name__ == '__main__':
    main()
