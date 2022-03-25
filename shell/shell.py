#! /usr/bin/env python3
#To run it as an executable

import os, sys, re

def redirection(args, direction):
    rdc_idx = args.index(direction)
    if direction == ">":
        os.close(1) # Closing stdout
        os.open(args[rdc_idx + 1], os.O_CREAT | os.O_WRONLY) # asdf > file
        os.set_inheritable(1, True) # 1 for stdout
    elif direction == "<":
        os.close(0) # Closing stdin
        os.open(args[rdc_idx + 1], os.O_RDONLY)
        os.set_inheritable(0, True) # 0 for stdin
    else:
        sys.exit(1)

    del args[rdc_idx] # Remove < or > 
    del args[rdc_idx] # Remove output or input file 
    do_instr(args)

def piping(args):
    print("Piping")
    pipe_idx = args.index("|")
    pr, pw = os.pipe()
    for fd in (pr, pw):
        os.set_inheritable(fd, True) # By default False

    left_instr = args[:pipe_idx]
    right_instr= args[pipe_idx + 1:]
    rc_left = os.fork() # We need one fork for each instruction

    if rc_left < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc_left == 0:
        os.close(1) # Will redirect output
        os.dup(pw)
        for fd in (pr, pw):
            os.close(fd)
        os.set_inheritable(1, True)
        do_instr(left_instr)
        
    else:
        os.close(0) # Will redirect input
        os.dup(pr)
        os.set_inheritable(0, True)
        pipe_pid_code = os.wait()
        
        for fd in (pw, pr):
            os.close(fd)
        
        do_instr(right_instr)
        
# Executes instruction
def do_instr(args):
    
    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass
    os.write(2, ("\t%s: command not found\n" % args[0]).encode())
    sys.exit(1) # Error

# Changes shell directory in where user does instructions
def change_dir(new_dir):
    try:
        os.chdir(new_dir)
    except FileNotFoundError:
        os.write(2, ("\tcd: %s: No such file or directory\n" % new_dir).encode())

# Main execution of the program
def main():
    num_bytes = 100
    pid = os.getpid()
    # Environment variable PS1
    try:
        sys.ps1
    except AttributeError:
        sys.ps1 = "$ "
    os.write(1, ("\nWELCOME to this cool shell!!\n").encode())
    # Continue to execute commands until exit command or error
    while(True):
        os.write(1, (os.getcwd() + sys.ps1).encode())
        user_input = os.read(0, num_bytes).decode() # Gets user instruction
        args = user_input.split()
       
        if len(args) == 0:
            continue
        # Terminates when exit command use
        if args[0] == "exit":
            break
        # Try to change directory
        if args[0] == "cd":
            if len(args) == 1:
                os.chdir('/')
            if len(args) != 2:
                os.write(1, ("cd: too many arguments\n").encode())
            else:
                change_dir(args[1])
            continue # Go to next iteration
        
        # If bacground task
        no_bckgr_t = True
        if args[-1] == "&":
            no_bckgr_t = False
            del args[-1]
            
        # Creates child
        rc = os.fork()

        if rc < 0:
            os.write(2, ("Fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            # Checking if there is any Piping
            if "|" in args:
                piping(args)
            # Checking if there is any Redirection
            elif ">" in args:
                redirection(args, ">")
            elif "<" in args:
                redirection(args, "<")
            else:
                do_instr(args) # Execute normal instruction
        else:
            # If this is not a background task. Then need to wait for the command to execute
            if no_bckgr_t:
                print("We need to wait the CHILD")
                child_pid_code = os.wait() # Returns tuple containing PID and exit status
                os.write(1, (f'\tChild PID code: {child_pid_code}\n').encode())
                if child_pid_code[1] != 0:
                    os.write(2,(f'\nProgram terminated with exit code {child_pid_code[1]}\n').encode())
                
    os.write(1, ("\nThank your for using this SHELL!!\n").encode())
    sys.exit(0)

if __name__ == "__main__":
    main()
