import pyaudio
import time
import queue
from matplotlib import pyplot as plt
from matplotlib import animation

endFlag=0
WIDTH = 2
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

q=queue.Queue()

def getPos(F,fre):
	if(fre<0):
		return len(F)+fre
	return fre;

import struct
import cfft
power=11
point=1<<power
CHUNK=1<<power
changeProportion=256 #nege pro

def callback(in_data, frame_count, time_info, status):
	
	wave=[]
	for i in range(0,len(in_data),4):
		wave.append(struct.unpack('<i',in_data[i:i+4])[0])
	print("max(wave)==%d"%(max(wave)))
	F=   cfft.toComplex(cfft.fft(cfft.toComplex_c(wave),power));

	flen=len(F)//2
	rpF=F[0:flen]
	rnF=F[len(F)-1:flen -1:-1]
	pF=[0+0j]*flen;
	nF=[0+0j]*flen;

	offset=point//changeProportion
	for i in range(flen-offset):
		pF[i+offset]=rpF[i];
		nF[i+offset]=rnF[i];
		pF[i]=rpF[i+offset];
		nF[i]=rnF[i+offset];

	res=pF+nF[::-1]
	q.put( (F,res) )
	f=cfft.toComplex(cfft.ifft(cfft.toComplex_c(res ),power));
	wave=list(map(lambda x: int(x.real) ,f));
	out_data=bytearray(len(in_data))
	print("max(wave)=%g"%(max(wave)))
	for i in range(0,len(out_data),4):
		wave[i//4]*=2
		val=struct.pack('<i',wave[i//4])
		out_data[i:i+4]=val
	#out_data=change(in_data)
	#return (bytes(in_data), endFlag==1)
	return (bytes(out_data), endFlag==1)


ymax=65536*4
fig=plt.figure()

startF=-RATE/2
endF=RATE/2
rawf=fig.add_subplot(2,1,1,xlim=(startF,endF),ylim=(0,ymax))
passf=fig.add_subplot(2,1,2,xlim=(startF,endF),ylim=(0,ymax))
rawFreqLine,=rawf.plot([],[],lw=1)
passFreqLine,=passf.plot([],[],lw=1)
freqs=list(map(lambda x: x*RATE/point-RATE/2,range(point)))
#print(freqs)
def ani(i):
	print("ani(%d)"%(i))
	if(not q.empty()):
		while(not q.empty()):
			v1,v2=q.get();
		F1=list(map(abs,v1))
		F2=list(map(abs,v2))
		F1=F1[len(F1)//2:]+F1[0:len(F2)//2]
		F2=F2[len(F2)//2:]+F2[0:len(F2)//2]
		#print("len(F1)==%d"%(len(F1)))
		print("max(F)==%g"%(max(F1+F2)))
		rawFreqLine.set_data (freqs,F1)
		passFreqLine.set_data(freqs,F2)
	return rawFreqLine,passFreqLine

anim=animation.FuncAnimation(fig,ani,interval=200)

stream = p.open(format=pyaudio.paInt32,
		channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
		frames_per_buffer=CHUNK,
                stream_callback=callback)

stream.start_stream()

plt.show()
endFlag=1;
time.sleep(0.16)
stream.stop_stream()
stream.close()
p.terminate()

