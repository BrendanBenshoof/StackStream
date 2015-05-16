StackStream Assembly
===================

StackStream Assembly is an attempt at contriving a byte-code level stack based assembly language to run on arbitrary length bytestrings.

This means it is well suited to managing large binary blobs of data.

## Bytestrings

The atomic unit in this assembly is a bytestring. Because bytestrings can be of arbitrary length (potentially of unbounded size!) we need a creative way to encode them:

So we use a simple approach that can be parsed in a streaming fashion:
```
[length of data][data]
```

This however leads to the issue, how many bytes long is the length value? Any fixed or bound number of bytes limits the bytestring size.
Essentially, this is solved by brute force.

A length value that would require n bits to represent is represented by:

```
'\0xff'*(n-1) + lengthbytes
```

with final output looking like:

```
'\0xff'*(n-1) + lengthbytes + data
```

This effectively doubles the number of bytes required to store a length. I'd love a better way to do this.

## The Stack

The basis of stack assembly languages is "the stack", which in this language is really just a binary "file-like" buffer.
Because the encoding stores their length, they can be blindly prepended to the buffer and read off safely.
Most opcodes read their arguments off the stack, which makes it a combination of working memory and inter-method communication

When a method is called, arguments may be passed to it via the stack, and values returned via the stack.

## The Memory (or the Context Stack)

A single stack is insufficient for Turning completeness. Rather than implementing a second stack and emulating a Turing machine, 
we provide a key-value based memory that effectively allows for variables.
To allow functions to avoid contaminating each other's memory layouts, we keep a stack of key-value memories.
This allows a function to safely start a new memory context, write to the memory, then discard the context when it is done.
When a value is written to the memory, it is stored to the top memory context only. 
When a value is read from the memory the stack of memory contexts is searched downward for a matching value.
This allows methods to safely read memory for input values if needed/wanted.

## The most basic operations

The following describes a minimal set of operations for dealing with the stack language.
Operations that modify bytestrings have not yet been included (I want to get these clear first)
Note that opcodes are stored as bytestrings, which means we have room for infinite opcodes.


| Operation     |        Opcode | Stack-args                |  inline-args  | stack output |  description                                      |
| ------------- | ------------- |---------------------------|---------------|--------------|---------------------------------------------------|
| PUT           | 0             |                           | bytestring    | byte-string  | Reads an in-line value and puts it on the stack   |
| OUTPUT        | 1             | bytestring                |               |              | Reads a bytestring off the stack and outputs it   |
| BURN          | 2             | bytestring                |               |              | Consumes and discards a value                     |
| START-CONTEXT | 3             |                           |               |              | Puts a new memory context on the memory stack     |
| END-CONTEXT   | 3             |                           |               |              | discards the top context of the memory stack      |
| STORE         | 4             | key, value                |               |              | stores value at key in top context                |
| READ          | 5             | key                       |               | value        | gets value stored at key in memory stack          |
| CMP           | 6             | val0, val1                | mode          | result       | preforms a comparison of the top two items        |
| JMP           | 7             | dest-byte, testval        |               |              | moves the program pointer to dest-byte if testval |
| CALL          | 8             | module-id                 |               | call results | looks up code at module-id and executes it        |

JMP and CALL are the most complex commands. JMP is complex because it may be difficult to assign values to the dest-bytes 
(variable length references change the length of the source).

CALL executes the new source code with the same stack and memory context (most polite functions will start and end a new memory context).
This means the called source has full reign to mutate the stack. Ideally it will only consume arguments and PUT results.


## Interpreting StackStream

The "source" of StackStream is a binary blob of bytes.
StackStream will start at the first byte, interpreting it as a bytestring opcode.
Because of it's streaming nature, execution of code can begin while it is still being read and code can be stored in burned literals.
This means de-compiling ByteStream code requires interpreting it (as the destination of JMP commands can be altered at runtime)
Adding commands to allow read-write to a DHT or Module Store would allow ByteStream to effectively self modify.
