import pigpio
import time

pi = pigpio.pi()

for i in range(32):
	try:
		print 'turning on', i
		pi.write(i, 1)
		time.sleep(0.5)
		print 'turning off', i
		pi.write(i, 0)
		time.sleep(0.5)
	except:
		print 'could not access', i

pi.stop()
