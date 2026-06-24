#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : clefia_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 10.03.2025
# Last Modified Date: 10.03.2025
# Last Modified By  : German C.Quiveu <germancq@dte.us.es>
import os
import random
import sys

import clefia
import cocotb
import numpy as np
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer

CLK_PERIOD = 20


def setup_dut(dut, key, plaintext):
    print("setup block cipher")
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.key.value = key
    dut.block_i.value = plaintext
    dut.rq_data.value = 1


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    clefia_sw = clefia.CLEFIA()
    key = random.getrandbits(dut.KEY_LEN.value)
    plaintext = random.getrandbits(128)

    setup_dut(dut, key, plaintext)

    expected_wk, expected_rk = clefia_sw.key_schedule(
        key, int(dut.KEY_LEN.value))
    expected_result = clefia_sw.encrypt(plaintext, expected_wk, expected_rk)

    p_a = np.zeros(4, dtype=np.uint32)
    p_a[0] = plaintext >> 96 & 0xFFFFFFFF
    p_a[1] = plaintext >> 64 & 0xFFFFFFFF
    p_a[2] = plaintext >> 32 & 0xFFFFFFFF
    p_a[3] = plaintext & 0xFFFFFFFF
    print("--------------------------------------------")
    dut.rst.value = 1
    await n_cycles_clock(dut, 10)
    dut.rst.value = 0
    print("key_schedule")
    print(dut.end_key_generation.value)
    while dut.end_key_generation.value == 0:
        print("waiting for key_schedule")
        print(dut.encrypt_inst.current_state.value)
        await n_cycles_clock(dut, 1)

    await n_cycles_clock(dut, 1)
    dut.rq_data.value = 0

    while dut.end_signal.value == 0:
        print("waiting for encrypt")
        print(dut.encrypt_inst.current_state.value)
        await n_cycles_clock(dut, 1)

    await n_cycles_clock(dut, 1)

    for i in range(0, 36):
        assert hex(dut.round_keys[i].value) == hex(
            expected_rk[i]
        ), f"ERROR in WAIT_FOR_GFN, RK values incorrect, expected in RK{i} = {hex(expected_rk[i])}, calculated = {hex(dut.gfn_inst.round_keys[i].value)}"

    for i in range(0, 4):

        assert hex(dut.enc_block_i[i].value) == hex(
            p_a[i]
        ), f"ERROR in WAIT_FOR_GFN, plaintext values incorrect, expected in p{i} = {hex(p_a[i])}, calculated = {hex(dut.enc_block_i[i].value)}"

        assert hex(dut.wk[i].value) == hex(
            expected_wk[i]
        ), f"ERROR in WAIT_FOR_GFN, wk values incorrect, expected in wk{i} = {hex(expected_wk[i])}, calculated = {hex(dut.wk[i].value)}"

    print(hex(dut.result_enc[0].value))
    print(hex(dut.result_enc[1].value))
    print(hex(dut.result_enc[2].value))
    print(hex(dut.result_enc[3].value))
    assert hex(dut.block_o.value) == hex(
        expected_result
    ), f"ERROR IN RESULT expected={hex(expected_result)} calculated={hex(dut.block_o.value)}"
