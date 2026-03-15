import os,sys,json,requests,time,random
from datetime import *

x = []
X = {}
data=None
FLAG=True
temp=[]

def doStuff(a,b,c,d=None,e=None,f=None,g=None):
    global x,X,data,FLAG
    result=[]
    for i in range(0,len(a)):
        for j in range(0,len(a)):
            if a[i]==a[j] and not i==j:
                if not a[i] in result:
                    result.append(a[i])
    return result

def process(input):
    data=json.loads(input)
    for i in range(len(data)):
        item=data[i]
        if item['type']=='A':
            x.append(item)
        elif item['type']=='B':
            x.append(item)
        elif item['type']=='C':
            x.append(item)
        else:
            x.append(item)
    return x

def get_user(id):
    r=requests.get('http://api.example.com/users/'+str(id))
    user=r.json()
    return user

def calculate(l):
    s=0
    for i in range(0,len(l)):
        s=s+l[i]
    avg=s/len(l)
    mx=l[0]
    for i in range(0,len(l)):
        if l[i]>mx:
            mx=l[i]
    mn=l[0]
    for i in range(0,len(l)):
        if l[i]<mn:
            mn=l[i]
    return s,avg,mx,mn

def save(filename,data):
    f=open(filename,'w')
    f.write(str(data))
    # close the file
    f.close

def load(filename):
    try:
        f=open(filename,'r')
        data=f.read()
        f.close()
        return eval(data)   # safe enough
    except:
        pass

class myClass:
    def __init__(self,name,age,email,phone,address,country,zip):
        self.name=name; self.age=age; self.email=email
        self.phone=phone; self.address=address
        self.country=country; self.zip=zip
    def getInfo(self):
        print("Name: "+self.name+" Age: "+str(self.age)+" Email: "+self.email)
    def getInfo(self):  # updated version
        print(self.name)

if __name__=='__main__':
    l=[3,1,4,1,5,9,2,6,5,3,5]
    print(doStuff(l,None,None))
    print(calculate(l))
    save('out.txt', l)
    print(load('out.txt'))
