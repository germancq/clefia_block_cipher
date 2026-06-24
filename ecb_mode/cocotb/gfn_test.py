#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : gfn_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 25.02.2025
# Last Modified Date: 25.02.2025
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


def setup_block_cipher(dut, blk_i, rk):
    print("setup block cipher")
    cocotb.start_soon(Clock(dut.clk, CLK_PERIOD, unit="ns").start())
    dut.rst.value = 0
    for i in range(0, dut.d.value):
        aux = random.getrandbits(32)
        dut.block_i[i].value = aux
        blk_i[i] = aux

    for i in range(0, int(int(dut.d.value) / 2) * int(dut.r.value)):
        aux = random.getrandbits(32)
        dut.round_keys[i].value = aux
        rk[i] = aux
        print(i)
        print(hex(aux))


async def rst_function_test(dut):
    print("rst function")
    dut.rst.value = 1
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.STEP_1.value
    ), f"ERROR STATE IN STEP_1, STATE={dut.current_state.value}"
    await n_cycles_clock(dut, 10)

    assert int(dut.current_state.value) == int(
        dut.STEP_1.value
    ), f"ERROR STATE IN STEP_1, STATE={dut.current_state.value}"

    assert (
        dut.dout_rounds_counter.value == 0
    ), f"ERROR STATE IN STEP_1, dout_rounds_counter={dut.current_state.value}, should be 0"

    for i in range(0, dut.d.value):
        print(i)
        assert (
            dut.T_dout[i].value == dut.block_i[i].value
        ), f"ERROR in STEP 1, T values incorrect"

    dut.rst.value = 0


async def step2_test(dut, expected_counter_value):
    print("step 2")
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.STEP_2.value
    ), f"ERROR STATE IN STEP_2, STATE={dut.current_state.value}"
    assert (
        dut.dout_rounds_counter.value == expected_counter_value
    ), f"ERROR STATE IN STEP_2, expected_value = {expected_counter_value}, counter_value={dut.dout_rounds_counter.value}"


async def step2_1_test(dut, clefia_sw, blk_i, rk, counter_value):
    print("step 2.1")
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.STEP_2_1.value
    ), f"ERROR STATE IN STEP_2_1, STATE={dut.current_state.value}"
    expected_f0_x_input_0 = blk_i[0]
    expected_f0_rk_input_0 = rk[(int(int(dut.d.value) / 2)) * counter_value]
    expected_f0_output_0 = clefia_sw.F0(expected_f0_rk_input_0, expected_f0_x_input_0)[
        0
    ]
    expected_next_T1 = clefia_sw.galois8.add(blk_i[1], expected_f0_output_0)
    blk_i[1] = expected_next_T1

    expected_f1_x_input_0 = blk_i[2]
    expected_f1_rk_input_0 = rk[(
        (int(int(dut.d.value) / 2)) * counter_value) + 1]
    expected_f1_output_0 = clefia_sw.F1(expected_f1_rk_input_0, expected_f1_x_input_0)[
        0
    ]
    expected_next_T3 = clefia_sw.galois8.add(blk_i[3], expected_f1_output_0)
    blk_i[3] = expected_next_T3

    assert hex(dut.f0_x_input[0].value) == hex(
        expected_f0_x_input_0
    ), f"ERROR IN STEP_2_1 f0_x_input expected = {hex(expected_f0_x_input_0)}, calculated = {hex(dut.f0_x_input[0].value)}"
    assert hex(dut.f0_rk_input[0].value) == hex(
        expected_f0_rk_input_0
    ), f"ERROR IN STEP_2_1 f0_rk_input expected = {hex(expected_f0_rk_input_0)}, calculated = {hex(dut.f0_rk_input[0].value)}"
    assert hex(dut.f0_y_output[0].value) == hex(
        expected_f0_output_0
    ), f"ERROR IN STEP_2_1 f0_y_output expected = {hex(expected_f0_output_0)}, calculated = {hex(dut.f0_y_output[0].value)}"
    assert hex(dut.T_din[1].value) == hex(
        expected_next_T1
    ), f"ERROR IN STEP_2_1 T1 expected = {hex(expected_next_T1)}, calculated = {hex(dut.T_din[1].value)}"

    assert hex(dut.f1_x_input[0].value) == hex(
        expected_f1_x_input_0
    ), f"ERROR IN STEP_2_1 f1_x_input expected = {hex(expected_f1_x_input_0)}, calculated = {hex(dut.f1_x_input[0].value)}"
    assert hex(dut.f1_rk_input[0].value) == hex(
        expected_f1_rk_input_0
    ), f"ERROR IN STEP_2_1 f1_rk_input expected = {hex(expected_f1_rk_input_0)}, calculated = {hex(dut.f1_rk_input[0].value)}"
    assert hex(dut.f1_y_output[0].value) == hex(
        expected_f1_output_0
    ), f"ERROR IN STEP_2_1 f1_y_output expected = {hex(expected_f1_output_0)}, calculated = {hex(dut.f1_y_output[0].value)}"
    assert hex(dut.T_din[3].value) == hex(
        expected_next_T3
    ), f"ERROR IN STEP_2_1 T3 expected = {hex(expected_next_T3)}, calculated = {hex(dut.T_din[3].value)}"

    if dut.d.value == 8:
        expected_f0_x_input_1 = blk_i[4]
        expected_f0_rk_input_1 = rk[(
            (int(int(dut.d.value) / 2)) * counter_value) + 2]
        expected_f0_output_1 = clefia_sw.F0(
            expected_f0_rk_input_1, expected_f0_x_input_1
        )[0]
        expected_next_T5 = clefia_sw.galois8.add(
            blk_i[5], expected_f0_output_1)
        blk_i[5] = expected_next_T5

        expected_f1_x_input_1 = blk_i[6]
        expected_f1_rk_input_1 = rk[(
            (int(dut.d.value / 2)) * counter_value) + 3]
        expected_f1_output_1 = clefia_sw.F1(
            expected_f1_rk_input_1, expected_f1_x_input_1
        )[0]
        expected_next_T7 = clefia_sw.galois8.add(
            blk_i[7], expected_f1_output_1)
        blk_i[7] = expected_next_T7

        assert hex(dut.f0_x_input[1].value) == hex(
            expected_f0_x_input_1
        ), f"ERROR IN STEP_2_1 f0_x_input expected = {hex(expected_f0_x_input_1)}, calculated = {hex(dut.f0_x_input[1].value)}"
        assert hex(dut.f0_rk_input[1].value) == hex(
            expected_f0_rk_input_1
        ), f"ERROR IN STEP_2_1 f0_rk_input expected = {hex(expected_f0_rk_input_1)}, calculated = {hex(dut.f0_rk_input[1].value)}"
        assert hex(dut.f0_y_output[1].value) == hex(
            expected_f0_output_1
        ), f"ERROR IN STEP_2_1 f0_y_output expected = {hex(expected_f0_output_1)}, calculated = {hex(dut.f0_y_output[1].value)}"
        assert hex(dut.T_din[5].value) == hex(
            expected_next_T5
        ), f"ERROR IN STEP_2_1 T5 expected = {hex(expected_next_T5)}, calculated = {hex(dut.T_din[5].value)}"

        assert hex(dut.f1_x_input[1].value) == hex(
            expected_f1_x_input_1
        ), f"ERROR IN STEP_2_1 f1_x_input expected = {hex(expected_f1_x_input_1)}, calculated = {hex(dut.f1_x_input[1].value)}"
        assert hex(dut.f1_rk_input[1].value) == hex(
            expected_f1_rk_input_1
        ), f"ERROR IN STEP_2_1 f1_rk_input expected = {hex(expected_f1_rk_input_1)}, calculated = {hex(dut.f1_rk_input[1].value)}"
        assert hex(dut.f1_y_output[1].value) == hex(
            expected_f1_output_1
        ), f"ERROR IN STEP_2_1 f1_y_output expected = {hex(expected_f1_output_1)}, calculated = {hex(dut.f1_y_output[1].value)}"
        assert hex(dut.T_din[7].value) == hex(
            expected_next_T7
        ), f"ERROR IN STEP_2_1 T7 expected = {hex(expected_next_T7)}, calculated = {hex(dut.T_din[7].value)}"

    return blk_i


async def step2_2_test(dut, clefia_sw, blk_i):
    print("step 2.2")
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.STEP_2_2.value
    ), f"ERROR STATE IN STEP_2_2, STATE={dut.current_state.value}"
    blk_i = np.roll(blk_i, -1)
    for i in range(0, dut.d.value):
        print(i)
        print(hex(blk_i[i]))
        print(hex(dut.T_din[i].value))
    for i in range(0, dut.d.value):
        assert hex(dut.T_din[i].value) == hex(
            blk_i[i]
        ), f"ERROR in STEP 2.2, T values incorrect, expected = {hex(blk_i[i])} calculated = {dut.T_din[i].value}"
    return blk_i


async def step3_test(dut, expected_result):
    print("step 3")
    await n_cycles_clock(dut, 1)
    assert int(dut.current_state.value) == int(
        dut.STEP_3.value
    ), f"ERROR STATE IN STEP_3 STATE={dut.current_state.value}"
    for i in range(0, dut.d.value):
        print(dut.T_dout[i].value)
        print(dut.block_o[i].value)
    for i in range(0, dut.d.value):
        assert hex(dut.block_o[i].value) == hex(
            expected_result[i]
        ), f"ERROR in STEP 3, T values incorrect"


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    clefia_sw = clefia.CLEFIA()

    await Timer(20, units="ns")
    blk_i = np.zeros(int(dut.d.value), dtype=np.uint32)
    rk = np.zeros(int(int(dut.d.value) / 2) *
                  int(dut.r.value), dtype=np.uint32)
    setup_block_cipher(dut, blk_i, rk)
    blk_i_cp = np.copy(blk_i)
    rk_cp = np.copy(rk)
    expected_result = clefia_sw.GFN(
        int(dut.d.value), int(dut.r.value), blk_i_cp, rk_cp)

    await rst_function_test(dut)
    print("final")
    print(blk_i)
    for i in range(0, dut.r.value):
        await step2_test(dut, i)
        blk_i = await step2_1_test(dut, clefia_sw, blk_i, rk, i)
        blk_i = await step2_2_test(dut, clefia_sw, blk_i)

    await step2_test(dut, dut.r.value)
    await step3_test(dut, expected_result)
