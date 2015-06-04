#stackstream is a keyword action language, so assembling it is simple:

import binascii

def bytes2int(bytes):
    if type(bytes) is int:
        return bytes
    return int(binascii.hexlify(bytes), 16) 

def int2bytes(i):
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

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

def writeVal(val):#adds length identifier to bytestring
    l = len(val)
    lengthBytes = int2bytes(l)
    return b'\xff'*(len(lengthBytes)-1)+lengthBytes+val

#(command byte, expected number of arguments)
command_map = {
    b"PUT":(b'\x00',1),
    b"OUTPUT":(b'\x01',0),
    b"BURN":(b'\x02',0),
    b"STARTC":(b'\x03',0),
    b"ENDC":(b'\x04',0),
    b"STORE":(b'\x05',0),
    b"READ":(b'\x06',0),
    b"CMP":(b'\x07',1),
    b"JMP":(b'\x08',1),
    b"CALL":(b'\x09',0),
    b"DUMP":(b'\x0A',1),
    b"ADD":(b'\x0B',0),
    b"SUB":(b'\x0C',0),
    b"MUL":(b'\x0D',0),
    b"DIV":(b'\x0E',0),
    b"MOD":(b'\x0F',0),
}


#values are packed in form ('type',val)
def parseVal(val):
    valType, raw = val
    if valType == "int":
        intbytes = int2bytes(raw)
        return writeVal(intbytes)
    if valType == "bytes":
        return writeVal(raw)
    if valType == "flag":
        intbytes = int2bytes(flags[raw])
        print(raw,intbytes)
        return writeVal(intbytes)
flags = {}

def assemble(code):#code is a list of commands and vals
    global flags
    next_vals = 0
    output = []
    bytes_out = 0
    block_id = 0
    for c in code:
        print c
        if next_vals == 0:
            if c[0] == b"#":#this is a flag
                flags[c] = bytes_out
                continue
            cmd, arglen = command_map[c]
            output.append(cmd)
            bytes_out+=len(cmd)
            next_vals = arglen
        else:
            valbytes = parseVal(c)
            output.append(valbytes)
            bytes_out+=len(valbytes)
            next_vals-=1

    return b''.join(output)

testcode = [
    b'PUT',('bytes',b'hello.ss'),
    b'CALL',
    b'PUT', ('int',0),
    b'PUT', ('bytes',b'a'),
    b'STORE',
    b'PUT', ('int',1),
    b'PUT', ('bytes',b'b'),
    b'STORE',
    b'#LOOPHEAD',
    b'PUT', ('bytes',b'a'),
    b'READ',
    b'PUT', ('bytes',b'b'),
    b'READ',
    b'ADD',
    b'PUT', ('bytes',b'c'),
    b'STORE',
    b'PUT', ('bytes',b'b'),
    b'READ',
    b'PUT', ('bytes',b'a'),
    b'STORE',
    b'PUT', ('bytes',b'c'),
    b'READ',
    b'PUT', ('bytes',b'b'),
    b'STORE',
    b'PUT', ('bytes',b'c'),
    b'READ',
    b'OUTPUT',
    b'PUT', ('bytes',b'True'),
    b'JMP', ('flag',b'#LOOPHEAD')

]

helloworld = [
    b'DUMP',('bytes',b'Hello World'),
]
"""


"""

code = assemble(testcode)
print(repr(code))

