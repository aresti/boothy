#adapted from http://stackoverflow.com/questions/28305270/how-to-do-asynchronous-file-copying-in-python
import os
import sys
import shutil
import threading
import Queue
import glob
import time

class FileCopy(threading.Thread):

	def __init__(self, watch_dir, volume, queue, exit=False):
		threading.Thread.__init__(self)
		self.watch_dir = watch_dir
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
				exists_path = self.volume + f.split('/')[-1]
				if os.path.exists(exists_path):
					i = 1
					while True:
						a = exists_path + '(%s)' %i
						if not os.path.exists(a):
							shutil.move(f, a)
							print 'Completed move', a
							break
						else:
							i += 1
				else:
					shutil.move(f, self.volume)
					print 'Completed move', f
				self.queue.task_done()

def main():
	#volume = '/media/UNTITLED/' + 'BOOTHY_STORE'
	watch_dir = '/Users/josh/Downloads/boothy/'
	volume = '/Users/josh/Downloads/boothy/' + 'test/'	
	if not os.path.exists(volume):
		os.makedirs(volume)
	queue = Queue.Queue()
	copythread = FileCopy(watch_dir, volume, queue)
	copythread.start()

	try:
		while True:
			files = glob.glob(watch_dir + '*jpg')
			if files:
				print 'Queueing %s %s' %(len(files), 
						       ('file' if len(files) == 1 else 'files'))
				for f in files:
					copythread.queue.put(f)
			time.sleep(2)
	except KeyboardInterrupt:
		copythread.exit = True
		copythread.join()

if __name__ == '__main__':
	main()
