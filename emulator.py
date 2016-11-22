#!/usr/bin/env python3
# -*- coding: utf-8 -*-

REG_IMMEDIATE = 0x0 # immediate register
REG_CONTROL   = 0x1 # control register
REG_MEM_LOW   = 0x2 # memory low
REG_MEM_HIGH  = 0x3 # memory memory high # little eindian???
REG_ALU_A     = 0x4 # ALU operand A
REG_ALU_B     = 0x5 # ALU operand B
REG_ALU_OP    = 0x6 # ALU instruction
REG_ALU_RES   = 0x7 # ALU result
REG_ADD_0     = 0x8 # address low
REG_ADD_1     = 0x9 # address
REG_ADD_2     = 0xA # address
REG_ADD_3     = 0xB # address high
REG_A         = 0xC # general purpose
REG_B         = 0xD # general purpose
REG_C         = 0xE # general purpose
REG_D         = 0xF # general purpose

import sys
from subprocess import run

def get_low(byte):
    return byte & 0x0f

def get_high(byte):
    return (byte & 0xf0) >> 4

def construct_address(A = 0, B = 0, C = 0, D = 0):
    return get_low(A) | (get_low(B) << 4) | (get_low(C) << 8) | (get_low(D) << 12)

def hexdump(data):
    run(["hd"], input=data)

"""A class responsible for emulating this CPU"""
class CPU():

    def is_ram(self, address):
        return True

    def __init__(self, alu_rom = None, rom = None):
        if alu_rom is None:
            self.alu_rom = bytearray(0x1000)
        elif hasattr(alu_rom, "read"):
            alu_rom = alu_rom.read(0x1000)
            self.alu_rom = bytearray(alu_rom.ljust(0x1000, b'\x00'))
        else:
            self.alu_rom = bytearray(alu_rom[:0x1000].ljust(0x1000, b'\x00'))

        if rom is None:
            self.memory = bytearray(0x10000)
        elif hasattr(rom, "read"):
            rom = rom.read(0x10000)
            self.memory = bytearray(rom.ljust(0x10000, b'\x00'))
        else:
            self.memory = bytearray(rom[:0x10000].ljust(0x10000, b'\x00'))

        self.pc = 0
        self.registers = bytearray(0x10)

    @property
    def address(self):
        return construct_address(self.registers[REG_ADD_0],
                                 self.registers[REG_ADD_1],
                                 self.registers[REG_ADD_2],
                                 self.registers[REG_ADD_3])

    @address.setter
    def address(self, address):
        self.registers[REG_ADD_0] = (address >> 0) & 0xf
        self.registers[REG_ADD_1] = (address >> 4) & 0xf
        self.registers[REG_ADD_2] = (address >> 8) & 0xf
        self.registers[REG_ADD_3] = (address >> 12) & 0xf

    def cmd_memory_read(self):
        byte = self.memory[self.address]
        self.registers[REG_MEM_LOW] = get_low(byte)
        self.registers[REG_MEM_HIGH] = get_high(byte)

    def cmd_memory_write(self):
        if not self.is_ram(self.address): return
        byte = construct_address(self.registers[REG_MEM_LOW], self.registers[REG_MEM_HIGH])
        self.memory[self.address] = byte

    def cmd_increment_address(self):
        self.address += 1

    def cmd_decrement_address(self):
        self.address -= 1

    def cmd_jmp(self):
        self.pc = self.address

    def cmd_jmpif(self):
        #print("Conditional jump at address 0x{:04X}".format(self.pc))
        if self.registers[REG_CONTROL] == 0:
            self.cmd_jmp()

    def cmd_jal(self):
        self.pc, self.addres = self.address, self.pc

    def cmd_break(self):
        print("Break at address 0x{0:04X}".format(self.pc))
        hexdump(self.registers)

    def cmd_halt(self):
        print("Halt at address 0x{0:04X}".format(self.pc))
        hexdump(self.registers)
        hexdump(self.memory)
        sys.exit()

    def cmd_noop(self):
        pass

    commands = \
    (
      cmd_memory_read,       # 0x0
      cmd_memory_write,      # 0x1
      cmd_increment_address, # 0x2
      cmd_decrement_address, # 0x3
      cmd_jmp,               # 0x4
      cmd_jmpif,             # 0x5
      cmd_jal,               # 0x6
      cmd_noop,              # 0x7
      cmd_noop,              # 0x8
      cmd_noop,              # 0x9
      cmd_noop,              # 0xA
      cmd_noop,              # 0xB
      cmd_noop,              # 0xC
      cmd_noop,              # 0xD
      cmd_break,             # 0xE
      cmd_halt,              # 0xF
    )

    def cycle(self):
        # fetch
        instruction = self.memory[self.pc]
        self.pc += 1
        self.pc &= 0xffff
        # decode
        src = get_high(instruction)
        dst = get_low(instruction)
        # execute
        if dst == REG_IMMEDIATE:
           self.registers[REG_IMMEDIATE] = src
        elif dst == REG_ALU_RES:
           self.commands[src](self)
        else:
           if src == REG_ALU_RES:
              src_val = self.alu_rom[construct_address(self.registers[REG_ALU_A], self.registers[REG_ALU_B], self.registers[REG_ALU_OP])]
           else:
              src_val = self.registers[src]
           self.registers[dst] = src_val

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: emulator.py alu.rom <binary>")
        sys.exit(1)
    alu_rom = open(sys.argv[1], "rb")
    rom = open(sys.argv[2], "rb")
    instance = CPU(alu_rom, rom)
    del alu_rom
    del rom
    while True:
        instance.cycle()

