#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : gen_con_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 26.02.2025
# Last Modified Date: 26.02.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>
import os
import random
import sys

import clefia
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer


@cocotb.test()
@cocotb.parametrize(index=range(0, 1))
async def test(dut, index=0):

    await Timer(10, units="ns")

    clefia_sw = clefia.CLEFIA()
    iv = 0x428A
    l = 30
    expected_result = clefia_sw.generate_constants(iv, l)[1]
    for i in range(0, 60):
        print(i)

        assert hex(dut.CON_128[i].value) == hex(
            expected_result[i]
        ), f"ERROR, EXPECTED value should be {hex(expected_result[i])}, however hdl value is {hex(dut.CON_128[i].value)}"

    clefia_sw = clefia.CLEFIA()
    iv = 0x7137
    l = 42
    expected_result = clefia_sw.generate_constants(iv, l)[1]
    for i in range(0, 84):
        print(i)

        assert hex(dut.CON_192[i].value) == hex(
            expected_result[i]
        ), f"ERROR, EXPECTED value should be {hex(expected_result[i])}, however hdl value is {hex(dut.CON_192[i].value)}"

    clefia_sw = clefia.CLEFIA()
    iv = 0xB5C0
    l = 46
    expected_result = clefia_sw.generate_constants(iv, l)[1]
    for i in range(0, 92):
        print(i)

        assert hex(dut.CON_256[i].value) == hex(
            expected_result[i]
        ), f"ERROR, EXPECTED value should be {hex(expected_result[i])}, however hdl value is {hex(dut.CON_256[i].value)}"
