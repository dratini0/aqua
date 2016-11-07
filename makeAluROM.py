#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def get_low(byte):
    return byte & 0x0f

def get_high(byte):
    return (byte & 0xf0) >> 4

def construct_address(A = 0, B = 0, C = 0, D = 0):
    return get_low(A) | (get_low(B) << 4) | (get_low(C) << 8) | (get_low(D) << 12)

aluROM = bytearray(0x1000)

alu_ops = (
  lambda a, b: get_low(a + b),
  lambda a, b: get_high(a + b),
  lambda a, b: get_low(a * b),
  lambda a, b: get_high(a * b),
  lambda a, b: a & b,
  lambda a, b: a | b,
  lambda a, b: a ^ b,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: 0,
  lambda a, b: alu_unary_ops[b](a),
)

alu_unary_ops = (
  lambda a: 0 if a != 0 else 1,
  lambda a: get_low(~a),
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
  lambda a: 0,
)

for op in range(0x10):
    for B in range(0x10):
        for A in range(0x10):
           aluROM[construct_address(A, B, op)] = alu_ops[op](A, B)

open(sys.argv[1], "wb").write(aluROM)

