import os
import queue
import string
import threading
import time

def rmprint():
    global print
    def print(*args,**kwargs):
        pass

def getprint():
    global print
    print=0
    del print

def get_drives():
    # Return a list of available drive letters on Windows.
    drives = []
    for letter in string.ascii_uppercase:
        if os.path.exists(f"{letter}:\\"):
            drives.append(f"{letter}:\\")
    return drives

def find_files(end,drive,q,q2,i):
    b=0
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    RESET = '\033[0m'
    print(BLUE+"\033[48;2;255;255;255m"+f"Thread {i} ready. ")
    for root, dirs, files in os.walk(drive, topdown=True):
        try:
            for file in files:
                if file.lower().endswith(end):
                    path=os.path.join(root, file)
                else:
                    continue
                size=os.path.getsize(path)
                try:
                    os.remove(os.path.join(root, file))
                except OSError:
                    print(RED+f"{path}(file in use)")
                else:
                    print(GREEN+f"{path}({size} bytes)")
                    b+=size
                    q2.put(1)
        except PermissionError:
            continue
        except FileNotFoundError:
            continue
    q.put(b)
    print(BLUE+f"Thread {i} finished. ")

if __name__ == "__main__":
    if input("Show logs(y/n): ")=="n":
        rmprint()
    start=time.time()
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    RESET = '\033[0m'
    junk=[".log",".tmp",".temp",".dmp",".bak",".old",".cache"]
    q=queue.Queue()
    q2=queue.Queue()
    t=[]
    o=[]
    o2=[]
    i=0
    for drive in get_drives():
        for ext in junk:
            t.append(threading.Thread(target=find_files,args=(ext,drive,q,q2,i,)))
            i+=1
    for thread in t:
        thread.start()
    for thread in t:
        thread.join()
    while True:
        if not q2.empty():
            o.append(q2.get_nowait())
        else:
            break
    while True:
        if not q.empty():
            o2.append(q.get_nowait())
        else:
            break
    getprint()
    print("----------------------")
    print(RED+"Summary:")
    print(GREEN+f"Deleted {sum(o)} files")
    print(GREEN+f"Freed {sum(o2)} bytes({sum(o2)/1024**2}MiB)")
    print(BLUE+f"Executed in {time.time()-start}s")
    input()
