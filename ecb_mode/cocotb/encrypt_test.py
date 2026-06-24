#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : encrypt_test.py
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


def setup_dut(dut, blk_i, rk, wk):
    print("setup block cipher")
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    dut.start.value = 1
    for i in range(0, 4):
        aux = random.getrandbits(32)
        dut.block_i[i].value = int(blk_i[i])

    for i in range(0, 4):
        aux = random.getrandbits(32)
        dut.wk[i].value = int(wk[i])

    for i in range(0, dut.N_RK.value):
        aux = random.getrandbits(32)
        dut.round_keys[i].value = int(rk[i])


async def rst_function_test(dut):
    print("rst function")
    dut.rst.value = 1
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN IDLE, STATE={dut.current_state.value}"
    await n_cycles_clock(dut, 5)

    assert (
        dut.current_state.value == dut.IDLE.value
    ), f"ERROR STATE IN IDLE, STATE={dut.current_state.value}"

    dut.rst.value = 0


async def gfn_test(dut, expected_block_i, expected_rk, expected_output):
    print("wait for gfn test")
    print(dut.start.value)
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.WAIT_FOR_GFN.value
    ), f"ERROR STATE IN WAIT_FOR_GFN, STATE={dut.current_state.value}"

    while dut.gfn_end_signal.value == 0:
        print(dut.current_state.value)
        await n_cycles_clock(dut, 1)

    print(hex(dut.gfn_block_i[0].value))
    print(hex(dut.gfn_block_i[1].value))
    print(hex(dut.gfn_block_i[2].value))
    print(hex(dut.gfn_block_i[3].value))

    print(hex(expected_block_i[0]))
    print(hex(expected_block_i[1]))
    print(hex(expected_block_i[2]))
    print(hex(expected_block_i[3]))

    for i in range(0, dut.N_RK.value):
        print(i)
        assert hex(dut.gfn_inst.round_keys[i].value) == hex(
            expected_rk[i]
        ), f"ERROR in WAIT_FOR_GFN, RK values incorrect, expected in RK{i} = {hex(expected_rk[i])}, calculated = {hex(dut.gfn_inst.round_keys[i].value)}"

    for i in range(0, 4):

        assert hex(dut.gfn_block_i[i].value) == hex(
            expected_block_i[i]
        ), f"ERROR in WAIT_FOR_GFN, block_i values incorrect, expected in LL{i} = {hex(expected_block_i[i])}, calculated = {hex(dut.gfn_block_i[i].value)}"

        assert hex(dut.gfn_block_o[i].value) == hex(
            expected_output[i]
        ), f"ERROR in WAIT_FOR_GFN, block_o values incorrect, expected in LR{i} = {hex(expected_output[i])}, calculated = {hex(dut.gfn_block_o[i].value)}"


async def write_output_test(dut, expected_result):
    print("write_output_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.WRITE_OUTPUT.value
    ), f"ERROR STATE IN WRITE_OUTPUT, STATE={dut.current_state.value}"

    for i in range(0, 4):
        assert hex(dut.out_din[i].value) == hex(
            expected_result[i]
        ), f"ERROR in result values, expected={hex(expected_result[i])} calculated={hex(dut.out_din[i].value)}"


async def end_fsm_state(dut, expected_result):
    print("end_fsm_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.END_STATE.value
    ), f"ERROR STATE IN END_STATE, STATE={dut.current_state.value}"

    assert dut.end_signal == 1, f"ERROR with end_signal"

    for i in range(0, 4):
        assert hex(dut.block_o[i].value) == hex(
            expected_result[i]
        ), f"ERROR in result values, expected={hex(expected_result[i])} calculated={hex(dut.block_o[i].value)}"


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

    expected_wk, expected_rk = clefia_sw.key_schedule(key, dut.KEY_LEN.value)
    expected_result = clefia_sw.encrypt(plaintext, expected_wk, expected_rk)

    p_a = np.zeros(4, dtype=np.uint32)
    p_a[0] = plaintext >> 96 & 0xFFFFFFFF
    p_a[1] = plaintext >> 64 & 0xFFFFFFFF
    p_a[2] = plaintext >> 32 & 0xFFFFFFFF
    p_a[3] = plaintext & 0xFFFFFFFF

    setup_dut(dut, p_a, expected_rk, expected_wk)
    await rst_function_test(dut)

    print(
        "encrypt with p0 = {}; p1 = {}; p2 = {};p3 = {}".format(
            hex(p_a[0]), hex(p_a[1]), hex(p_a[2]), hex(p_a[3])
        )
    )
    print(expected_wk)
    print(
        "expected_wk[0] = {}, expected_wk[1] = {}".format(
            hex(expected_wk[0]), hex(expected_wk[1])
        )
    )
    p_a[1] = p_a[1] ^ expected_wk[0]
    p_a[3] = p_a[3] ^ expected_wk[1]
    print("p1 = p1 ^ {} = {}".format(hex(expected_wk[0]), hex(p_a[1])))
    print("p3 = p3 ^ {} = {}".format(hex(expected_wk[1]), hex(p_a[3])))
    cp_p = np.copy(p_a)

    t = clefia_sw.GFN(4, int(np.shape(expected_rk)[0] / 2), p_a, expected_rk)

    await gfn_test(dut, cp_p, expected_rk, t)

    t[1] = t[1] ^ expected_wk[2]
    t[3] = t[3] ^ expected_wk[3]
    print(t)
    await write_output_test(dut, t)
    await end_fsm_state(dut, t)
