#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : key_schedule_test.py
# Author            : German C.Quiveu <germancq@dte.us.es>
# Date              : 05.03.2025
# Last Modified Date: 05.03.2025
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


def setup_dut(dut, key):
    print("setup block cipher")
    cocotb.fork(Clock(dut.clk, CLK_PERIOD).start())
    dut.rst.value = 0
    dut.key.value = key


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

    assert (
        dut.dout_rounds_counter.value == 0
    ), f"ERROR STATE IN IDLE, dout_rounds_counter={dut.current_state.value}, should be 0"

    dut.rst.value = 0


async def gfn_test(
    dut,
    expected_l_value,
    expected_CON_values,
    expected_key128,
    expected_keyl,
    expected_keyr,
    expected_LL,
    expected_LR,
):
    print("wait for gfn test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.WAIT_FOR_GFN.value
    ), f"ERROR STATE IN WAIT_FOR_GFN, STATE={dut.current_state.value}"

    while (dut.gfn4_end_signal.value == 0) or (dut.gfn8_end_signal == 0):
        print(dut.current_state.value)
        await n_cycles_clock(dut, 1)

    print(hex(dut.LL_din[0].value))
    print(hex(dut.LL_din[1].value))
    print(hex(dut.LL_din[2].value))
    print(hex(dut.LL_din[3].value))
    print("-------------------")
    print(hex(dut.gfn4_block_o[0].value))
    print(hex(dut.gfn4_block_o[1].value))
    print(hex(dut.gfn4_block_o[2].value))
    print(hex(dut.gfn4_block_o[3].value))
    print("-------------------")
    print(hex(dut.gfn8_block_o[0].value))
    print(hex(dut.gfn8_block_o[1].value))
    print(hex(dut.gfn8_block_o[2].value))
    print(hex(dut.gfn8_block_o[3].value))
    print("-------------------")
    print(hex(dut.gfn8_block_i[0].value))
    print(hex(dut.gfn8_block_i[1].value))
    print(hex(dut.gfn8_block_i[2].value))
    print(hex(dut.gfn8_block_i[3].value))
    print(hex(dut.gfn8_block_i[4].value))
    print(hex(dut.gfn8_block_i[5].value))
    print(hex(dut.gfn8_block_i[6].value))
    print(hex(dut.gfn8_block_i[7].value))
    print("-------------------")
    print(hex(dut.gfn8_round_keys[0].value))
    print(expected_l_value)
    print(expected_key128)
    print(expected_keyl)
    print(hex(dut.key_l[0].value))
    print(hex(dut.key_l[1].value))
    print(hex(dut.key_l[2].value))
    print(hex(dut.key_l[3].value))

    print(expected_keyr)
    print(hex(dut.key_r[0].value))
    print(hex(dut.key_r[1].value))
    print(hex(dut.key_r[2].value))
    print(hex(dut.key_r[3].value))

    print(expected_LL)
    print(expected_LR)

    if dut.KEY_LEN.value == 128:
        for i in range(0, 4):
            print(i)
            assert hex(dut.key_r[i].value) == hex(
                expected_key128[i]
            ), f"ERROR gfn4_block_i"

        for i in range(0, 24):
            print(i)
            assert hex(dut.gfn4_round_keys[i].value) == hex(
                expected_CON_values[i]
            ), f"ERROR CON"
    for i in range(0, 4):

        assert hex(dut.LL_din[i].value) == hex(
            expected_l_value[i]
        ), f"ERROR in WAIT_FOR_GFN, LL values incorrect, expected in LL{i} = {hex(expected_l_value[i])}, calculated = {hex(dut.LL_din[i].value)}"
        if dut.KEY_LEN.value != 128:
            assert hex(dut.LR_din[i].value) == hex(
                expected_l_value[4 + i]
            ), f"ERROR in WAIT_FOR_GFN, LR values incorrect, expected in LR{i} = {hex(expected_l_value[4+i])}, calculated = {hex(dut.LR_din[i].value)}"


async def check_counter_test(dut, expected_counter_value):
    print("check_counter_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.CHECK_COUNTER.value
    ), f"ERROR STATE IN CHECK_COUNTER, STATE={dut.current_state.value}"

    assert hex(dut.dout_rounds_counter.value) == hex(
        expected_counter_value
    ), f"ERROR COUNTER value IN CHECK_COUNTER, expected={hex(expected_counter_value)} calculated={hex(dut.dout_rounds_counter.value)}"


async def gen_t_test(dut, expected_T):
    print("gen_t_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.GEN_T.value
    ), f"ERROR STATE IN GEN_T, STATE={dut.current_state.value}"

    for i in range(0, 4):
        assert hex(dut.T_din[i].value) == hex(
            expected_T[i]
        ), f"ERROR in T values, expected={hex(expected_T[i])} calculated={hex(dut.T_din[i].value)}"


async def check_odd_test(dut, expected_L, expected_T, expected_counter_value):
    print("check_odd_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.CHECK_ODD.value
    ), f"ERROR STATE IN CHECK_ODD, STATE={dut.current_state.value}"

    print(hex(dut.LL_din[0].value))
    print(hex(dut.LL_din[1].value))
    print(hex(dut.LL_din[2].value))
    print(hex(dut.LL_din[3].value))
    print(expected_L)
    print(hex(dut.T_din[0].value))
    print(hex(dut.T_din[1].value))
    print(hex(dut.T_din[2].value))
    print(hex(dut.T_din[3].value))
    print(expected_T)

    if dut.KEY_LEN.value == 128:
        for i in range(0, 4):
            assert hex(dut.LL_din[i].value) == hex(
                expected_L[i]
            ), f"ERROR in L values, expected={hex(expected_L[i])} calculated={hex(dut.LL_din[i].value)}"
            if expected_counter_value % 2:
                assert hex(dut.T_din[i].value) == hex(
                    expected_T[i]
                ), f"ERROR in T values, expected={hex(expected_T[i])} calculated={hex(dut.T_din[i].value)}"


async def gen_rk_test(dut, expected_RK, expected_counter_value):
    print("gen_rk_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.GEN_RK.value
    ), f"ERROR STATE IN GEN_RK, STATE={dut.current_state.value}"

    for i in range(0, 4):
        assert hex(dut.RK_din[expected_counter_value * 4 + i].value) == hex(
            expected_RK[expected_counter_value * 4 + i]
        ), f"ERROR in RK values, expected={hex(expected_RK[expected_counter_value*4 + i])} calculated={hex(dut.RK_din[expected_counter_value*4 + i].value)}"


async def update_counter_test(dut):
    print("update_counter_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.UPDATE_COUNTER.value
    ), f"ERROR STATE IN UPDATE_COUNTER, STATE={dut.current_state.value}"


async def end_fsm_state(dut, expected_RK, expected_WK):
    print("end_fsm_test")
    await n_cycles_clock(dut, 1)
    assert (
        dut.current_state.value == dut.END_FSM_STATE.value
    ), f"ERROR STATE IN END_FSM_STATE, STATE={dut.current_state.value}"

    assert dut.end_signal == 1, f"ERROR with end_signal"

    print(hex(dut.WK_din.value[0]))
    print(hex(dut.WK_din.value[1]))
    print(hex(dut.WK_din.value[2]))
    print(hex(dut.WK_din.value[3]))
    print(hex(dut.WK_dout.value[0]))
    print(hex(dut.WK_dout.value[1]))
    print(hex(dut.WK_dout.value[2]))
    print(hex(dut.WK_dout.value[3]))
    print(hex(dut.wk.value[0]))
    print(hex(dut.wk.value[1]))
    print(hex(dut.wk.value[2]))
    print(hex(dut.wk.value[3]))
    print(expected_RK)

    for i in range(0, 4):
        assert hex(dut.wk[i].value) == hex(
            expected_WK[i]
        ), f"ERROR in WK values, expected={hex(expected_WK[i])} calculated={hex(dut.wk[i].value)}"

    for i in range(0, dut.N_RK.value):
        assert hex(dut.round_keys[i].value) == hex(
            expected_RK[i]
        ), f"ERROR in RK values, expected={hex(expected_RK[i])} calculated={hex(dut.round_keys[i].value)}"


async def n_cycles_clock(dut, n):
    for i in range(0, n):
        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)


@cocotb.test()
@cocotb.parametrize(index=range(0, 10))
async def test(dut, index=0):

    clefia_sw = clefia.CLEFIA()
    key = random.getrandbits(dut.KEY_LEN.value)

    expected_wk, expected_rk = clefia_sw.key_schedule(
        key, int(dut.KEY_LEN.value))

    await Timer(20, units="ns")

    setup_dut(dut, key)
    await rst_function_test(dut)

    key_a = np.zeros(int(dut.KEY_LEN.value / 32), dtype=np.uint32)
    keyL_a = np.zeros(4, dtype=np.uint32)
    keyR_a = np.zeros(4, dtype=np.uint32)
    L_left = np.zeros(4, dtype=np.uint32)
    L_right = np.zeros(4, dtype=np.uint32)
    for i in range(0, int(dut.KEY_LEN.value / 32)):
        key_a[int(dut.KEY_LEN.value / 32) - 1 -
              i] = key >> (i * 32) & 0xFFFFFFFF
        print(hex(key_a[int(dut.KEY_LEN.value / 32) - 1 - i]))
    # key 128-bits
    print(key_a)
    for i in range(0, 4):
        keyL_a[i] = key_a[i]

    if dut.KEY_LEN.value != 128:
        for i in range(0, 2):
            keyR_a[i] = key_a[i + 4]
        keyR_a[2] = key_a[6] if dut.KEY_LEN.value == 256 else ~key_a[0]
        keyR_a[3] = key_a[7] if dut.KEY_LEN.value == 256 else ~key_a[1]

    WK = np.zeros(4, dtype=np.uint32)
    RK = np.zeros(36, dtype=np.uint32)
    if dut.KEY_LEN.value == 192:
        RK = np.zeros(44, dtype=np.uint32)
    if dut.KEY_LEN.value == 256:
        RK = np.zeros(52, dtype=np.uint32)

    T_a, CON = clefia_sw.generate_constants(0x428A, 30)
    if dut.KEY_LEN.value == 192:
        T_a, CON = clefia_sw.generate_constants(0x7137, 42)
    if dut.KEY_LEN.value == 256:
        T_a, CON = clefia_sw.generate_constants(0xB5C0, 46)
    cp_key_a = np.copy(key_a)
    L = clefia_sw.GFN(4, 12, np.copy(key_a), CON[0:24])

    if dut.KEY_LEN.value != 128:
        L = clefia_sw.GFN(8, 10, np.concatenate((keyL_a, keyR_a)), CON[0:40])
        for i in range(0, 4):
            L_left[i] = L[i]
            L_right[i] = L[i + 4]
            WK[i] = keyR_a[i] ^ keyL_a[i]
    else:
        WK = np.copy(key_a)

    ############# TESTBENCH COCOTB####################
    await gfn_test(dut, L, CON, cp_key_a, keyL_a, keyR_a, L_left, L_right)

    #################################################
    # print(hex(L[0]))
    # print(hex(L[1]))
    # print(hex(L[2]))
    # print(hex(L[3]))
    print(key_a)
    print(WK)
    print(keyL_a)
    print(keyR_a)
    print(L_left)
    print(L_right)

    # print(hex(CON[58]))
    # print(hex(CON[59]))

    T = np.zeros(4, dtype=np.uint32)
    T_copy = np.zeros(4, dtype=np.uint32)
    L_aux = np.zeros(4, dtype=np.uint32)
    K_aux = np.zeros(4, dtype=np.uint32)
    index = 8
    cte_index = 24
    if dut.KEY_LEN.value != 128:
        index = 10 if dut.KEY_LEN.value == 192 else 12
        cte_index = 40

    for i in range(0, index + 1):
        ############# TESTBENCH COCOTB####################
        await check_counter_test(dut, i)

        #################################################

        if dut.KEY_LEN.value == 128:
            L_aux = np.copy(L)
            K_aux = np.copy(WK)
        else:
            if i % 4 < 2:
                L_aux = np.copy(L_left)
                K_aux = np.copy(keyR_a)
            else:
                L_aux = np.copy(L_right)
                K_aux = np.copy(keyL_a)

        for j in range(0, 4):
            c = CON[cte_index + (4 * i) + j]
            print(
                "L_aux[{}] ^ c = {} ^ {} = {} ".format(
                    j, hex(L_aux[j]), hex(c), hex(L_aux[j] ^ c)
                )
            )
            T[j] = c ^ L_aux[j]
            T_copy[j] = c ^ L_aux[j]
            if i % 2 != 0:
                print(
                    "T[{}] ^ K_aux[{}] = {} ^ {} = {} ".format(
                        j, j, hex(T[j]), hex(K_aux[j]), hex(T[j] ^ K_aux[j])
                    )
                )
                T[j] = T[j] ^ K_aux[j]

        ############# TESTBENCH COCOTB####################
        await gen_t_test(dut, T_copy)

        #################################################
        # print(L)
        L = clefia_sw.doubleSwap(L)
        print(L)
        if i % 4 < 2:
            L_left = clefia_sw.doubleSwap(L_left)
        else:
            L_right = clefia_sw.doubleSwap(L_right)

        ############# TESTBENCH COCOTB####################
        await check_odd_test(dut, L, T, i)

        #################################################
        # print(L)
        for j in range(0, 4):
            RK[(4 * i) + j] = T[j]
            print("RK[{}] = {}".format((4 * i) + j, hex(T[j])))

        ############# TESTBENCH COCOTB####################
        await gen_rk_test(dut, RK, i)
        await update_counter_test(dut)

        #################################################
    await check_counter_test(dut, index + 1)
    await end_fsm_state(dut, expected_rk, expected_wk)
