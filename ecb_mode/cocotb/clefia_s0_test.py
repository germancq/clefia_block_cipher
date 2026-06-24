import os
import random
import sys

import clefia
import cocotb
import galois_arithmetic
import numpy as np
from cocotb.clock import Clock
from cocotb.regression import TestFactory
from cocotb.triggers import FallingEdge, RisingEdge, Timer

SS = np.array(
    [
        [
            0xE,
            0x6,
            0xC,
            0xA,
            0x8,
            0x7,
            0x2,
            0xF,
            0xB,
            0x1,
            0x4,
            0x0,
            0x5,
            0x9,
            0xD,
            0x3,
        ],
        [
            0x6,
            0x4,
            0x0,
            0xD,
            0x2,
            0xB,
            0xA,
            0x3,
            0x9,
            0xC,
            0xE,
            0xF,
            0x8,
            0x7,
            0x5,
            0x1,
        ],
        [
            0xB,
            0x8,
            0x5,
            0xE,
            0xA,
            0x6,
            0x4,
            0xC,
            0xF,
            0x7,
            0x2,
            0x3,
            0x1,
            0x0,
            0xD,
            0x9,
        ],
        [
            0xA,
            0x2,
            0x6,
            0xD,
            0x3,
            0x4,
            0x5,
            0xE,
            0x0,
            0x7,
            0x8,
            0x9,
            0xB,
            0xF,
            0xC,
            0x1,
        ],
    ]
)


def setup_block_cipher(dut, x):
    dut.x.value = x


@cocotb.test()
@cocotb.parametrize(index=range(0, 256))
async def test(dut, index=0):

    x = index

    galois4 = galois_arithmetic.GaloisField(4)
    clefia_sw = clefia.CLEFIA()
    expected_result = clefia_sw.S0(x)
    setup_block_cipher(dut, x)
    await Timer(10, units="ns")

    x1 = x & 0xF
    x0 = (x >> 4) & 0xF

    p = (1 << 4) + (1 << 1) + 1  # z4 + z + 1

    t0 = SS[0][x0]
    t1 = SS[1][x1]

    m0 = galois4.multiplication(2, t1, p)
    u0 = galois4.add(t0, m0)
    m1 = galois4.multiplication(2, t0, p)
    u1 = galois4.add(t1, m1)

    y0 = SS[2][u0]
    y1 = SS[3][u1]

    print(hex(x))
    print(hex(x0))
    print(hex(x1))
    assert hex(dut.t0.value) == hex(
        t0
    ), f"ERROR, EXPECTED value should be {hex(t0)}, however hdl value is {hex(dut.t0.value)}"

    assert hex(dut.t1.value) == hex(
        t1
    ), f"ERROR, EXPECTED value should be {hex(t1)}, however hdl value is {hex(dut.t1.value)}"

    assert hex(dut.m0.value) == hex(
        m0
    ), f"ERROR, EXPECTED value should be {hex(m0)}, however hdl value is {hex(dut.m0.value)}"

    assert hex(dut.m1.value) == hex(
        m1
    ), f"ERROR, EXPECTED value should be {hex(m1)}, however hdl value is {hex(dut.m1.value)}"

    assert hex(dut.u0.value) == hex(
        u0
    ), f"ERROR, EXPECTED value should be {hex(u0)}, however hdl value is {hex(dut.u0.value)}"

    assert hex(dut.u1.value) == hex(
        u1
    ), f"ERROR, EXPECTED value should be {hex(u1)}, however hdl value is {hex(dut.u1.value)}"

    assert hex(dut.y.value) == hex(
        expected_result
    ), f"ERROR, EXPECTED value should be {hex(expected_result)}, however hdl value is {hex(dut.y.value)}"
