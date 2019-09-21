
import math

def FFT(f,power):
	len=0b1<<power;

	F=[]
	for i in range(len):
		t=0;
		for j in [0b1<<x for x in range(power)]:
			t<<=1
			if(i&j):
				t|=0b1;
		F.append(f[t]/len);
	
	angs=list(map(lambda i:-2*math.pi*i/len,range(len>>1)))
	sins=list(map(math.sin,angs))
	coss=list(map(math.cos,angs))
	W=list(map(complex,coss,sins))

	for i in range(1,power+1):
		dftnum=len>>i;
		dftlen=1<<i;
		dftlen_2=dftlen>>1;
		for j in range(dftlen_2):
			f1=j;
			f2=f1+dftlen_2;
			#print(j*dftnum)
			coef=W[j*dftnum]
			for k in range(dftnum):
				odd=F[f1];
				even=F[f2];
				temp=even*coef;
				F[f1]=odd+temp; 
				F[f2]=odd-temp;
				f1+=dftlen;
				f2+=dftlen;
	
	return F;
def iFFT(f,power):
	len=0b1<<power;

	F=[]
	for i in range(len):
		t=0;
		for j in [0b1<<x for x in range(power)]:
			t<<=1
			if(i&j):
				t|=0b1;
		F.append(f[t]);
	
	angs=list(map(lambda i:2*math.pi*i/len,range(len>>1)))
	sins=list(map(math.sin,angs))
	coss=list(map(math.cos,angs))
	W=list(map(complex,coss,sins))

	for i in range(1,power+1):
		dftnum=len>>i;
		dftlen=1<<i;
		dftlen_2=dftlen>>1;
		for j in range(dftlen_2):
			f1=j;
			f2=f1+dftlen_2;
			#print(j*dftnum)
			coef=W[j*dftnum]
			for k in range(dftnum):
				odd=F[f1];
				even=F[f2];
				temp=even*coef;
				F[f1]=odd+temp; 
				F[f2]=odd-temp;
				f1+=dftlen;
				f2+=dftlen;
	
	return F;

