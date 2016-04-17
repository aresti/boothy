#adapted from http://stackoverflow.com/questions/28305270/how-to-do-asynchronous-file-copying-in-python
import shutil
import threading

class FileCopy(threading.Thread):

    def __init__(self, volume, queue, exit=False):
        threading.Thread.__init__(self)
        self.volume = volume
        self.queue = queue
        self.exit = exit

    def run(self):
        while True:
            if self.exit == True:
                break
            if self.queue.empty():
                time.sleep(1)
            else:
                f = self.queue.get()
                shutil.move(f, self.volume)
                print('Completed move', f)
            self.queue.task_done()
