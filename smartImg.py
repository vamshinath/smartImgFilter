#!/usr/python3
from colorama import Fore, Style
import os,sys,string,random,time,signal,re,shutil
import magic
from PIL import Image
from skimage.measure import compare_ssim as ssim
import cv2

mode=''
names=[]
prename=''
reverseF=False

record = False

lastQueryFile = "/home/vamshi/lastQ.txt"

imagesData = {}

def scanFiles(keyword):

    imgFiles = []
    
    global includeopt

    ofiles={}
    for root, directories, filenames in os.walk('.'):
        #print(root,end='\r')
        for filename in filenames:
            if "9351" in filename and includeopt == '0':
                continue
            if not "9351" in filename and includeopt == '1':
                continue
            try:
                if keyword == "":
                    f=os.path.abspath(os.path.join(root,filename))
                    fsz=os.stat(f).st_size
                    if fsz < 10240:
                        continue
                    ofiles[f]=fsz
                elif keyword in filename:
                    f=os.path.abspath(os.path.join(root,filename))
                    fsz=os.stat(f).st_size
                    if fsz < 10240:
                        continue
                    ofiles[f]=fsz
            except Exception as e:
                print(e)

    for fl,sz in ofiles.items():
        flnm_lower=os.path.basename(fl.lower())
        if ".jpg" in flnm_lower or ".png" in flnm_lower or ".jpeg" in flnm_lower:
            imgFiles.append(fl)

    return imgFiles




def delay(img):

	sz=os.stat(img).st_size/1000
	sl=0
	if sz <= 2000:
		sl=2.35
	elif sz > 2000 and sz <= 5000:
		sl=2.99
	elif sz > 5000 and sz <= 10000:
		sl=5.4
	elif sz> 10000 and sz<=15000:
		sl=6.73
	elif sz > 15000 and sz<30000:
		sl=9.4
	else:
		sl=11.9
	if "gif" in img[0].lower():
		time.sleep(sl+1.5)
	else:
		time.sleep(sl)
	os.system("killall pqiv")



def imgFilterHelper(files):


    print("last filters in Images")
    ch = input("Enter complete (sz/hd/tm)")

    fls = {}
    rec = {}
    for fl in files:
        try:
            if ch == "sz":
                tmp = Image.open(fl).size
                sz = tmp[0]
            elif ch == "hd":
                tmp = Image.open(fl).size
                imsz = tmp[0]+tmp[1]
                statbuf = os.stat(fl)
                imssz=statbuf.st_size
                sz = imssz/imsz
            else:
                statbuf = os.stat(fl)
                sz=statbuf.st_mtime
            fnd = False
            for actnm in names:
                if actnm[:4] in fl.lower():
                    rec[fl]=sz
                    fnd=True
                    break
            if not fnd:
                fls[fl]=sz
            
        except Exception as e:
            fls[fl]=0
    recs = sorted(rec.items(),key=lambda x:x[1],reverse=reverseF)
    tmps = sorted(fls.items(),key=lambda x:x[1],reverse=reverseF)

    files=[]
    for fl,_ in recs:
        files.append(fl)
            
    for fl,_ in tmps:
        print(_)
        files.append(fl)
            
    if record:
        with open(lastQueryFile,"w") as ffl:
            for fl in files:        
                ffl.write(fl+"\n")    


    return files



def random_generator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def printInfo(fl):

    print("FileDir: "+os.path.dirname(fl))
    print(Fore.BLUE+"File: "+os.path.basename(fl))
    print(Fore.RED+"FileSz: "+str(round(os.stat(fl).st_size/1000,3))+Fore.WHITE)

def addToImagesData(img):
    global imagesData
    imagesData[img]=cv2.resize(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY))

def getNameFromSimilar(img):
    imgdata2 = cv2.resize(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY), (100, 100))
    for flpath, imgdata1 in imagesData.items():
        s = ssim(imgdata1, imgdata2)
        val=round(s*100,3)
        if val > 75:
            print("Found Similarity:"+str(val))
            return os.path.basename(flpath)

    return ''

def imgFilter(files,lastQ=False):
    global names
    global prename
    global mode

    if not lastQ:
        files = imgFilterHelper(files)



    ctr=0
    tfls=len(files)

    for img in files:

        os.system("pqiv -c -f '"+img+"' &")
        delay(img)

        ext = "."+magic.from_file(img,mime=True).split('/')[-1]

        exPath=os.path.dirname(img)
        fileName=os.path.basename(img)

        fname=''
        ch='un'
        ctr+=1
        print("\n"+str(ctr)+"/"+str(tfls))
        printInfo(img)

        if prename == '':
            for actnm in names:
                if actnm[:4] in fileName.lower():
                    print(Fore.GREEN+"Found:"+actnm+Fore.WHITE)
                    ch = input("enter to confirm:")
                    if ch == "":
                        fname = actnm
                    if "]]" in ch:
                        print(Fore.RED+img+" deleted"+Fore.WHITE)
                        os.remove(img)
                    break

            if "]]" in ch:
                continue

            if ch != "" and ch != 'un' :
                for act in names:
                    if ch in act:
                        fname = act

            if fname == "":
                print(Fore.RED+"fileName not Found...trying similar"+Fore.WHITE)
                similarName = getNameFromSimilar(img)
                if similarName != "":
                    print(Fore.GREEN+"Found (Enter Save or new):"+similarName+Fore.WHITE)
                    fname = input()
                    if fname == "":
                        for actnm in names:
                            if actnm[:4] in similarName.lower():
                                fname=actnm
                                break
                        if fname =="":
                            fname = input("Similar Error, Enter completeName:")        
                else:
                    fname = input("Similar not found, Enter completeName:")
                if "]]" in fname:
                    print(Fore.RED+img+" deleted"+Fore.WHITE)
                    os.remove(img)
                    continue
                
                if fname == "":
                    fname = input(Fore.RED+"Enter to confirm:"+Fore.WHITE)
                    if fname == "":
                        print(img+" deleted")
                        os.remove(img)
                        continue
        else:
            fname=prename


        sname = input(Fore.GREEN+"Enter partName:"+Fore.WHITE)

        if "skip" in sname:
            print("skipping")
            continue

        if "]]" in sname:
            print(img+" deleted")
            os.remove(img)
            continue

        finalName = fname+random_generator()+sname+"_9351_"+ext
        print(finalName)
        shutil.move(img,exPath+"/"+finalName)




def returnLastQ():

    files = []
    with open(lastQueryFile,"r") as fl:
        for ln in fl:
            files.append(ln[:-1])

    files = list(filter(lambda x:os.path.isfile(x),files))

    return imgFilter(files,True)







def main():

    global names
    global prename
    global includeopt
    global mode
    global reverseF
    global record

    print("echo "+'"'+"find . -type f -name "+"*'*"+" | rename 's/ /_/g'"+'"')

    conch = input("Continue old(y/n):")
    if conch == "y":
        record = False
        returnLastQ()

    record = True if input("Record this(y/n):") == "y" else False


    print("Reverse Y(big2sm) :")
    reverseF = True if input() == "Y" else False


    with open("/home/vamshi/.actnames.txt",'r') as fl:
        for ln in fl:
            names.append(ln[:-1])

    if len(sys.argv)!= 2:
        dir = input("Enter Full dirname:")
    else:
        dir = os.path.abspath(sys.argv[1])


    if dir == None or dir == "/home/vamshi" or dir == "~/" or dir == "/home/vamshi/" or not os.path.isdir(dir):
        print("passed "+dir+" exiting....")
        sys.exit()

    os.chdir(dir)

    includeopt = input("9351 include(1/0):")
    keyword = input("Enter search term:")

    print("Scanning "+os.getcwd()+"...........\n")

    if "/home/vamshi" == os.getcwd():
        print("passed "+dir+" exiting....")
        sys.exit()

    prename = input("Enter prename:")

    files = scanFiles(keyword)

    imgFilter(files)




if __name__ == '__main__':
    main()
