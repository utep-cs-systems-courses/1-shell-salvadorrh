#! /usr/bin/env python3
#To run it as an executable

import os, sys, re

#pid = os.getpid()
#We need a byte-like object, so .encode
#os.write(1, ("Current pid: %d\n" % pid).encode())
#rc = os.fork()
#shellContinue = True
#while shellContinue:
    #PS1 = os.environ['PATH']
    #os.write(1, ("%s\n" % PS1).encode())
    #shellContinue = False

PS1 = "$ "
    
def main():
    print('\nHello world!\n')
    pid = os.getpid()
    print('PID\n', pid)
    home_path = os.getcwd()
    print('home_path: ', home_path)
    print('PS1', PS1)
    PS2 = home_path + PS1
    print('PS2: ', PS2)
    while(True):
        print_PS1()
        print()
        break
    
def print_PS1():
    os.write(1, ("Print: %s\n" % PS1).encode())
    
if __name__ == "__main__":
    main()
