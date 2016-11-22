# The Aqua instruction set

## Overview

The Aqua is a CPU with 16 4-bit registers.
However, it has a 16 bit address bus, a 16 bit program counter and an 8 bit data bus.
It resolves this conflict by mapping these to multiple registers.

## Register overview

### `0x0`: `REG_IMMEDIATE`

This register holds any immediate that is loaded.
The method of loading immediate values is discussed in the instruction set summary

### `0x1`: `REG_CONTROL`

This is a control/flags register.
This controls branching.
Details of branching are discussed in the instruction set summary.

### `0x2-0x3`: `REG_MEMORY_LOW`, `REG_MEMORY_HIGH`

    REG_MEMORY = {REG_MEMORY_HIGH, REG_MEMORY_LOW};

These two registers hold any data that will be written into the memory, or any data that is read from the memory.
Details of memory access are discussed in the instruction set summary.

### `0x4-0x7`: `REG_ALU_A`, `REG_ALU_B`, REG_ALU_OP`, `REG_ALU_RES`

    REG_ALU_RES = alu(REG_ALU_A, REG_ALU_B, REG_ALU_OP);

These four registers control the ALU.
The ALU is some, as of now, undefined combinational function of the operands and the operator.
Since the entire ALU can be represented by 16k bits, the ALU can conveniently be implemented using a 32k bit parallel ROM.
An image of such a ROM can be found in the file `alu.rom`, along with the python script used to generate it.

### `0x8-0xB`: `REG_ADD_0` - `REG_ADD_3`

    REG_ADDRESS = {REG_ADD_3, REG_ADD_2, REG_ADD_1, REG_ADD_0};

These four registers hold the address to be used for the next memory operation.
Details of memory access are discussed in the instruction set summary.
These special registers can also be incremented and decremented.
For details of this functionality, please see again the instrution set summary.

### `0xC-0xF`: `REG_A` - `REG_D`

These are four general purpose registers.
These are probably going to be used as a stack pointer, when the calling convention is defined.

## Instruction set summary

### `0x??`: `mov`

Most instructions are simple copy operations between the 16 registers.

```verilog
if(INSTR[3:0] != 'h0 && INSTR[3:0] != 'h7)
    reg[INSTR[3:0]] <= reg[INSTR[7:4]];
```

However, there are two read-only registers that form an exception:

* You can not copy into `REG_IMMEDIATE`
* You can not copy into `REG_ALU_RES`

Writing into these registers means a different operation

### `0x?0`: `ldi`

The `ldi` instruction allows one to set `REG_IMMEDIATE` to any value.

```verilog
if(INSTR[3:0] != 'h0)
    REG_IMMEDIATE <= INSTR[7:4];
```

### `0x07`: `ld`

This instruction performs loads into the memory registers whatever is pointed at by the address registers.

```verilog
if(INSTR = 'h07')
    REG_MEMORY <= mem[REG_ADDRESS];
```

### `0x17`: `st`

This instruction stores whatever is in the memory registers to a location determined by the address register.

```verilog
if(INSTR = 'h17')
    mem[REG_ADDRESS] = REG_MEMORY;
```

### `0x27`: `inc`

This instruction increments the address register.

```verilog
if(INSTR = 'h27')
    REG_ADDRESS <= REG_ADDRESS + 1;
```

### `0x37`: `dec`

This instruction increments the address register.

```verilog
if(INSTR = 'h37')
    REG_ADDRESS <= REG_ADDRESS - 1;
```

### `0x47`: `jmp`

This instructions jumps to wherever the address registers point.

```verilog
if(INSTR = 'h47')
    PC <= REG_ADDRESS;
```

### `0x57`: `jmpif`

This instructions jumps to wherever the address registers point, but only if the control register is 0.

```verilog
if(INSTR = 'h57' and REG_STATUS == 0)
    PC <= REG_ADDRESS;
```

### `0x67`: `jal`

This instructions jumps to wherever the address registers point, and stores the previous value of the program counter in the address registers.

```verilog
if(INSTR = 'h67') begin
    PC <= REG_ADDRESS;
    REG_ADDRESS <= PC;
end;
```

### `0x77`: `nop`

This instruction does nothing.

### `0xE7`: `break`

This instruction executes some implementation-defined debugging action, or nothing at all.
It must not affect the state of the registers or main memory in any way, unless user action has been taken.

    if(INSTR = 'hE7')
        $display ("");

### `0xF7`: `halt`

This instruction stops the CPU from executing any further instructions.

## Calling convention

Yet to be defined.

