import pyaudio
import time
import queue
from matplotlib import pyplot as plt
from matplotlib import animation
import math

endFlag=0
putFlag=0
WIDTH = 2
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

q=queue.Queue()

import struct

import FFT
def changer(wave,level,wide,move,deltas=[]):
	length=1<<level;
	F=FFT.FFT(wave,level);
	pf=[0+0j]*length

	flen=length//2

	modifyRange=int(move*flen);
	if(modifyRange<0):
		modifyRange=-modifyRange;
		for i in range(flen-modifyRange):
			pf[i]=F[i+modifyRange];
	else:
		for i in range(flen-modifyRange):
	
			pf[i+modifyRange]=F[i];
	for delta in deltas:
		delta=list(delta)
		delta[0]=int(flen*delta[0]);
		delta[1]=int(flen*delta[1]);
		for i in range(delta[0],delta[1]): 
			pf[i]*=( (delta[3]-delta[2])*((i-delta[0])/(delta[1]-delta[0]))+delta[3] ) ;
	tempf=list(pf)
	for i in range(int(flen/wide)):
		pf[i]=tempf[int(i/wide)]/wide
	for i in range(1,flen):
		pf[length-i]=pf[i].conjugate();
	pf[0]=pf[flen]=0+0j;
	if(putFlag):
		print('put')
		q.put([F,pf])
	f=FFT.iFFT(pf,level);
	#print("f=",f)
	#wave=list(map(math.real ,f));
	wave=list(map(lambda x:x.real,f))
	return wave;

def callback(in_data, frame_count, time_info, status):
	wave=[]
	for i in range(0,len(in_data),4):
		wave.append(struct.unpack('<f',in_data[i:i+4])[0])
	print("max(wave)==",max(wave));
	#F=   cfft.toComplex(cfft.fft(cfft.toComplex_c(wave),power));
	#wave=changer(wave,power,0.8,0.002,[[0.005,0.3,1,0.7]])
	wave=changer(wave,power,1.6,0.002,[[0.002,0.3,0.8,1.6]])
	#q.put([F,cfft.toComplex(cfft.fft(cfft.toComplex_c(wave),power))]);
	out_data=bytearray(len(in_data))
	for i in range(0,len(out_data),4):
		val=struct.pack('<f',wave[i//4])
		out_data[i:i+4]=val
	return (bytes(out_data), endFlag==1)

def ani(i):
	print("ani(%d)"%(i))
	if(not q.empty()):
		while(not q.empty()):
			v1,v2=q.get();
		F1=list(map(abs,v1))
		F2=list(map(abs,v2))
		F1=F1[len(F1)//2:]+F1[0:len(F1)//2]
		F2=F2[len(F2)//2:]+F2[0:len(F2)//2]
		#print(F2)
		#print("len(F1)==%d"%(len(F1)))
		#print("max(F)==%g"%(max(F1+F2)))
		rawFreqLine.set_data (freqs,F1)
		passFreqLine.set_data(freqs,F2)
	return rawFreqLine,passFreqLine


if __name__=='__main__':
	power=10
	CHUNK=1<<power
	putFlag=1

	ymax=8e-3
	fig=plt.figure()
	rawf=fig.add_subplot(2,1,1,xlim=(-RATE/2,RATE/2),ylim=(0,ymax))
	passf=fig.add_subplot(2,1,2,xlim=(-RATE/2,RATE/2),ylim=(0,ymax))
	rawFreqLine,=rawf.plot([],[],lw=1)
	passFreqLine,=passf.plot([],[],lw=1)
	freqs=list(map(lambda x: x*RATE/CHUNK-RATE/2,range(CHUNK)))
	#print(freqs)
	anim=animation.FuncAnimation(fig,ani,interval=200)

	stream = p.open(format=pyaudio.paFloat32,
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

