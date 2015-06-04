#!/bin/python3

"""

    This is a draft of a stackstream implementation:
    I'm making the executive choice of using 1-byte opcodes (this allows 256 opcodes)
    This could easily be extended by taking in "mode" or "operation" argument

    values referred to as "arguments" follow the command in source code.
    further input is popped off the stack and results are pushed to the stack

    | OPCODE    | Description
    |  0 PUT    | put the following value on the stack
    |  1 OUTPUT | pop the stack and output/print the result
    |  2 BURN   | discard the top stack value
    |  3 STARTC | Start a new variable scope context
    |  4 ENDC   | End the current variable context
    |  5 STORE  | pops a key and value off the stack, stores value to key in the variable context
    |  6 READ   | pops a key and reads the value from the current memory onto the stack
    |  7 CMP    | takes a mode argument, pops two values off the stack and compares them
    |  8 JMP    | takes in a byte-number argument. pops a value off the stack. if it is not-null it moves the program pointer to it
    |  9 CALL   | pops a source identifier off the stack and calls it
    | 10 DUMP   | writes the argument to output


    BASIC MATH <here things get sketchy>

    | 11 ADD   | adds top two stack items
    | 12 SUB   | subtracts top two stack item: 2nd - TOP
    | 13 MUL   | multiplies top two stack items
    | 14 DIV   | divides top two stack item: 2nd / TOP
    | 15 MOD   | divides top two stack item: 2nd % TOP

"""

import binascii
import io

def bytes2int(bytes):
    if type(bytes) is int or type(bytes) is long:
        return bytes
    hexval = binascii.hexlify(bytes)



    return int(hexval,16) 



def readval(sourceStream):
    inital_length = sourceStream.read(1)
    bytes_length = 1
    if inital_length == b'\x00':
        return sourceStream.readall()
    while inital_length == b'\xff':
        inital_length = sourceStream.read(1)
        bytes_length+=1
    if bytes_length > 1:
        inital_length = sourceStream.read(bytes_length)
    length = bytes2int(inital_length)
    return sourceStream.read(length)



def readline(sourceStream):
    op = sourceStream.read(1)
    if op == b'':
        return None, None
    arg = None
    """
        ops that take arguments: PUT, CMP, JMP
    """
    if op in b'\x00\x07\x08\x0A':
        arg = readval(sourceStream)

    return op, arg

f = io.BytesIO(b'\x00\x01\x0f\x00\x01I\x05\x00\x01\x00\x00\x01A\x05\x00\x01\x01\x00\x01B\x05\x00\x01A\x06\x00\x01B\x06\x0A\x00\x01C\x05\x00\x01B\x06\x00\x01A\x05\x00\x01C\x06\x00\x01B\x05\x00\x01C\x06\x01\x00\x01I\x06\x00\x01\x01\x0B\x00\x01\x00\x07\x01\x00\x08\x01\x15')

"""
A <= 0
B <= 1
C <= 1

while TRUE:
    C <= A + B
    output C
    A <= B
    B <= C



PUT 16\x00\x01\x0F
PUT I \x00\x01I
STORE \x05

PUT 0 \x00\x01\x00
PUT A \x00\x01A
STORE \x05
PUT 1 \x00\x01\x01
PUT B \x00\x01B
STORE \x05
PUT 1 \x00\x01\x01

#JMP FLAG #byte 15

PUT A \x00\x01A
GET   \x06
PUT B \x00\x01B
GET   \x06
ADD   \x0A
PUT C \x00\x01C
STORE \x05
PUT B \x00\x01B
GET   \x06
PUT A \x00\x01A
STORE \x05
PUT C \x00\x01C
GET   \x06
PUT B \x00\x01B
STORE \x05
PUT C \x00\x01C
GET   \x06
OUTPUT\x01

PUT I \x00\x01I
GET   \x06
PUT 1 \x00\x01\x01
SUB   \x0B
PUT 0 \x00\x01\x00
CMP   \x07


JMP 22 \x08\x01\x18



"""


def run(sourceStream):
    memory = [{}]
    stack = []
    fileStack = [sourceStream]
    op, arg = readline(fileStack[-1])
    opcount = 1000
    while(op or len(fileStack)>0):
        if opcount <= 0:
            break
        if not op:
            fp = fileStack.pop()
            fp.close()
            if len(fileStack) < 0:
                break
            op, arg = readline(fileStack[-1])
            continue
        opcount-=1
        #print(op,arg)
        if op == b'\x00': #PUT
            stack.append(arg)
        elif op == b'\x01': #OUTPUT
            stack_input = stack.pop()
            yield stack_input
        elif op == b'\x02': #BURN
            stack.pop()
        elif op == b'\x03': #OPEN CONTEXT
            memory.append({})
        elif op == b'\x04': #CLOSE CONTEXT
            memory.pop()
        elif op == b'\x05': #MEMORY STORE
            key = stack.pop()
            val = stack.pop()
            memory[-1][key] = val
        elif op == b'\x06': #MEMORY READ
            key = stack.pop()
            try:
                val = memory[-1][key] 
                stack.append(val)
            except Exception:
                stack.append(b'\x00')
        elif op == b'\x07': #CMP
            arg1 = bytes2int(stack.pop())
            arg2 = bytes2int(stack.pop())
            if arg1 != arg2:
                stack.append(b'\x01')
            else:
                stack.append(b'\x00')
        elif op == b'\x08': #JMP
            test = stack.pop()
            if test != b'\x00':
                index = bytes2int(arg)
                fileStack[-1].seek(index)

        elif op == b'\x09': #CALL
            fname = stack.pop()
            fp = open(fname,'r')
            fileStack.append(fp)


        elif op == b'\x0A': #DUMP
            print("DUMPING",arg)
            yield arg

        elif op == b'\x0B': #ADD
            arg1 = bytes2int(stack.pop())
            arg2 = bytes2int(stack.pop())
            stack.append(arg2+arg1)
        elif op == b'\x0C': #SUB
            arg1 = bytes2int(stack.pop())
            arg2 = bytes2int(stack.pop())
            stack.append(arg2-arg1)
        elif op == b'\x0D': #MUL
            arg1 = bytes2int(stack.pop())
            arg2 = bytes2int(stack.pop())
            stack.append(arg2*arg1)
        elif op == b'\x0E': #DIV
            arg1 = bytes2int(stack.pop())
            arg2 = bytes2int(stack.pop())
            stack.append(arg2/arg1)
        elif op == b'\x0F': #MOD
            arg1 = bytes2int(stack.pop())
            arg2 = bytes2int(stack.pop())
            stack.append(arg2%arg1)
        else:
            print(op,arg,memory[0],stack)
            raise Exception()
            
        op, arg = readline(fileStack[-1])

for l in run(io.BytesIO(b'\x00\x08hello.ss\t\x00\x01\x00\x00\x01a\x05\x00\x01\x01\x00\x01b\x05\x00\x01a\x06\x00\x01b\x06\x0b\x00\x01c\x05\x00\x01b\x06\x00\x01a\x05\x00\x01c\x06\x00\x01b\x05\x00\x01c\x06\x01\x00\x04True\x08\x01\x19')):
    print(l)
