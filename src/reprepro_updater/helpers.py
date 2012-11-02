

import subprocess
import fcntl
import time



def try_run_command(command, lockfile=None):


    if not lockfile:
        
        lockfile = '/tmp/prepare_sync.py.lock'
    
    with open(lockfile, 'w') as lfh:

        file_locked = False
        for i in xrange(1000):

            try:

                fcntl.lockf(lfh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                file_locked = True
                break
            except IOError, ex:
                print "could not get lock on %s. Waiting one second" % lockfile
                time.sleep(1)
        if not file_locked:
            print "Failed to lock %s after 1000 tries quitting. Could not execute [%s]" % (lockfile, command)
            return False

        try:
            subprocess.check_call(command)
            return True

        except Exception, ex:
            print "Execution of [%s] Failed:" % command, ex
            return False
