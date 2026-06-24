#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : f0_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 24.02.2025
# Last Modified Date: 24.02.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>

import os
import random
import sys

import clefia
import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

M0 = np.array([[1, 2, 4, 6], [2, 1, 6, 4], [4, 6, 1, 2], [6, 4, 2, 1]])


def setup_block_cipher(dut, x, rk):
    dut.x.value = x
    dut.rk.value = rk


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    x = random.getrandbits(32)
    rk = random.getrandbits(32)

    clefia_sw = clefia.CLEFIA()
    expected_result = clefia_sw.F0(rk, x)
    setup_block_cipher(dut, x, rk)
    await Timer(20, units="ns")

    T_a = np.zeros((4, 1), dtype=np.uint32)
    T = clefia_sw.galois8.add(rk, x)
    T_n = np.zeros(4, dtype=np.uint32)
    for i in range(0, 4):
        T_n[i] = int((T >> (8 * i)) & 0xFF)
        if i % 2:
            T_n[i] = clefia_sw.S0(T_n[i])
        else:
            T_n[i] = clefia_sw.S1(T_n[i])
        T_a[i][0] = T_n[i]
    p = (1 << 8) + (1 << 4) + (1 << 3) + (1 << 2) + 1
    y = clefia_sw.galois8.matrix_multiplication(M0, T_a, p)

    print(expected_result)

    for i in range(0, 4):
        assert hex(dut.T[i].value) == hex(
            T_n[i]
        ), f"ERROR, EXPECTED value should be {hex(T[i])}, however hdl value is {hex(dut.T[i].value)}"

    assert hex(dut.y.value) == hex(
        expected_result[0]
    ), f"ERROR, EXPECTED value should be {expected_result}, however hdl value is {hex(dut.y.value)}"
