

import subprocess
import fcntl
import time



class LockContext:
    def __init__(self, lockfilename = None, timeout = 3000):
        if lockfilename:
            self.lockfilename = lockfilename
        else:
            self.lockfilename = '/tmp/prepare_sync.py.lock'

        self.timeout = timeout

    def __enter__(self):
        self.lfh = open(self.lockfilename, 'w')

        file_locked = False
        for i in xrange(self.timeout):

            try:

                fcntl.lockf(self.lfh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                file_locked = True
                break
            except IOError, ex:
                print "could not get lock on %s. Waiting one second (%d of %d)" % (self.lockfilename, i, self.timeout)
                time.sleep(1)
        if not file_locked:
            raise IOError("Could not lock file %s with %d retries"% (self.lockfilename, self.timeout) )

        return self

    def __exit__(self, exception_type, exception_val, trace):
        self.lfh.close()
        return False

def try_run_command(command):

        try:
            subprocess.check_call(command)
            return True

        except Exception, ex:
            print "Execution of [%s] Failed:" % command, ex
            return False
