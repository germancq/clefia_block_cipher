"""
 # @ Author: German Cano Quiveu, germancq
 # @ Create Time: 2023-11-30 11:48:41
 # @ Modified by: German Cano Quiveu, germancq
 # @ Modified time: 2023-11-30 11:49:01
 # @ Description:
 """

import math

import galois_arithmetic
import numpy as np

np.set_printoptions(formatter={"int": hex})

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

MS_f = np.array(
    [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [0, 1, 1, 0, 0, 1, 0, 1],
        [0, 1, 0, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
    ]
)

MS_g = np.array(
    [
        [0, 0, 0, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0],
    ]
)

M0 = np.array([[1, 2, 4, 6], [2, 1, 6, 4], [4, 6, 1, 2], [6, 4, 2, 1]])

M1 = np.array([[1, 8, 2, 10], [8, 1, 10, 2], [2, 10, 1, 8], [10, 2, 8, 1]])


class CLEFIA:

    def __init__(self):
        self.galois16 = galois_arithmetic.GaloisField(16)
        self.galois8 = galois_arithmetic.GaloisField(8)
        self.galois4 = galois_arithmetic.GaloisField(4)

    def encrypt(self, plaintext, WK, RK):
        p_a = np.zeros(4, dtype=np.uint32)
        p_a[0] = plaintext >> 96 & 0xFFFFFFFF
        p_a[1] = plaintext >> 64 & 0xFFFFFFFF
        p_a[2] = plaintext >> 32 & 0xFFFFFFFF
        p_a[3] = plaintext & 0xFFFFFFFF

        print(
            "encrypt with p0 = {}; p1 = {}; p2 = {};p3 = {}".format(
                hex(p_a[0]), hex(p_a[1]), hex(p_a[2]), hex(p_a[3])
            )
        )
        print(WK)
        print("WK[0] = {}, WK[1] = {}".format(hex(WK[0]), hex(WK[1])))
        p_a[1] = p_a[1] ^ WK[0]
        p_a[3] = p_a[3] ^ WK[1]
        print("p1 = p1 ^ {} = {}".format(hex(WK[0]), hex(p_a[1])))
        print("p3 = p3 ^ {} = {}".format(hex(WK[1]), hex(p_a[3])))

        t = self.GFN(4, int(np.shape(RK)[0] / 2), p_a, RK)

        t[1] = t[1] ^ WK[2]
        t[3] = t[3] ^ WK[3]
        print(t)
        return (int(t[0]) << 96) + (int(t[1]) << 64) + (int(t[2]) << 32) + int(t[3])

    def key_schedule(self, key, key_len):
        key_a = np.zeros(int(key_len / 32), dtype=np.uint32)
        keyL_a = np.zeros(4, dtype=np.uint32)
        keyR_a = np.zeros(4, dtype=np.uint32)
        L_left = np.zeros(4, dtype=np.uint32)
        L_right = np.zeros(4, dtype=np.uint32)
        for i in range(0, int(key_len / 32)):
            key_a[int(key_len / 32) - 1 - i] = key >> (i * 32) & 0xFFFFFFFF
            print(hex(key_a[int(key_len / 32) - 1 - i]))
        # key_a[0] = key >> 96 & 0xFFFFFFFF
        # key_a[1] = key >> 64 & 0xFFFFFFFF
        # key_a[2] = key >> 32 & 0xFFFFFFFF
        # key_a[3] = key & 0xFFFFFFFF
        # key 128-bits
        print(key_a)
        for i in range(0, 4):
            keyL_a[i] = key_a[i]

        if key_len != 128:
            for i in range(0, 2):
                keyR_a[i] = key_a[i + 4]
            keyR_a[2] = key_a[6] if key_len == 256 else ~key_a[0]
            keyR_a[3] = key_a[7] if key_len == 256 else ~key_a[1]

        WK = np.zeros(4, dtype=np.uint32)
        RK = np.zeros(36, dtype=np.uint32)
        if key_len == 192:
            RK = np.zeros(44, dtype=np.uint32)
        if key_len == 256:
            RK = np.zeros(52, dtype=np.uint32)

        T_a, CON = self.generate_constants(0x428A, 30)
        if key_len == 192:
            T_a, CON = self.generate_constants(0x7137, 42)
        if key_len == 256:
            T_a, CON = self.generate_constants(0xB5C0, 46)

        L = self.GFN(4, 12, np.copy(key_a), CON[0:24])

        if key_len != 128:
            L = self.GFN(8, 10, np.concatenate((keyL_a, keyR_a)), CON[0:40])
            for i in range(0, 4):
                L_left[i] = L[i]
                L_right[i] = L[i + 4]
                WK[i] = keyR_a[i] ^ keyL_a[i]
        else:
            WK = np.copy(key_a)

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
        L_aux = np.zeros(4, dtype=np.uint32)
        K_aux = np.zeros(4, dtype=np.uint32)
        index = 8
        cte_index = 24
        if key_len != 128:
            index = 10 if key_len == 192 else 12
            cte_index = 40

        for i in range(0, index + 1):

            if key_len == 128:
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
                if i % 2 != 0:
                    print(
                        "T[{}] ^ K_aux[{}] = {} ^ {} = {} ".format(
                            j, j, hex(T[j]), hex(K_aux[j]), hex(T[j] ^ K_aux[j])
                        )
                    )
                    T[j] = T[j] ^ K_aux[j]

            # print(L)
            L = self.doubleSwap(L)
            if i % 4 < 2:
                L_left = self.doubleSwap(L_left)
            else:
                L_right = self.doubleSwap(L_right)

            # print(L)
            for j in range(0, 4):
                RK[(4 * i) + j] = T[j]
                print("RK[{}] = {}".format((4 * i) + j, hex(T[j])))

        return WK, RK

    def generate_constants(self, IV, l):
        T = np.zeros(l + 1, dtype=np.uint32)
        CON = np.zeros(2 * l, dtype=np.uint32)

        P = 0xB7E1
        Q = 0x243F

        p = (1 << 16) + (1 << 15) + (1 << 13) + (1 << 11) + (1 << 5) + (1 << 4) + 1
        p_a = np.array([1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1])

        T[0] = IV
        a = np.array([1, 0])
        b = self.galois16.inverse_mul(a, p_a)
        # print(b)
        c = 0
        for j in range(0, 16):
            c = c + int(b[15 - j] * math.pow(2, j))

        # print(hex(c))

        for i in range(0, l):
            # print(i)
            T_neg = ~T[i] & 0xFFFF
            CON[2 * i] = (self.galois16.add(T[i], P) << 16) + self.ROL(T_neg, 1, 16)
            # print(hex(CON[2*i]))
            CON[(2 * i) + 1] = (self.galois16.add(T_neg, Q) << 16) + self.ROL(
                T[i], 8, 16
            )
            # print(hex(CON[(2*i)+1]))
            T[i + 1] = self.galois16.multiplication(T[i], c, p)
            # print(hex(T[i+1]))

        return T, CON

    def gen_CON_values_for_sv(self, key_len):
        if key_len == 128:
            CON_128 = self.generate_constants(0x428A, 30)[1]
            for i in range(0, 60):
                value = CON_128[i]
                print(f"assign CON_128[{i}] = 32'h{hex(value)};")
        if key_len == 192:
            CON_192 = self.generate_constants(0x7137, 42)[1]
            for i in range(0, 84):
                value = CON_192[i]
                print(f"assign CON_192[{i}] = 32'h{hex(value)};")
        if key_len == 256:
            CON_256 = self.generate_constants(0xB5C0, 46)[1]
            for i in range(0, 92):
                value = CON_256[i]
                print(f"assign CON_256[{i}] = 32'h{hex(value)};")

    def doubleSwap(self, x_a):
        x_copy = x_a.astype(np.uint64)
        x_h = (x_copy[0] << 32) + (x_copy[1])
        x_l = (x_copy[2] << 32) + x_copy[3]
        print("-------------------------------------")
        print(type(x_h))
        # print(x_a)
        # print(hex(x_h))
        # print(hex(x_l))
        x0 = x_l & 0x7F
        x1 = (x_l >> 7) & 0x1FFFFFFFFFFFFFF
        x2 = (x_h) & 0x1FFFFFFFFFFFFFF
        x3 = (x_h >> (57)) & 0x7F
        # print(hex(x0))
        # print(hex(x1))
        # print(hex(x2))
        # print(hex(x3))

        y_h = (x2 << 7) + x0
        y_l = (x3 << 57) + x1
        y_a = np.zeros(4, dtype=np.uint32)

        for i in range(0, 2):
            y_a[i] = y_h >> (32 - 32 * i) & 0xFFFFFFFF
            y_a[i + 2] = y_l >> (32 - 32 * i) & 0xFFFFFFFF
        print("-------------------------------------------")
        return y_a

    def GFN(self, d, r, T_a, rk_a):
        print("///////////////////////")
        print("GFN d={} ,r={}".format(d, r))

        for i in range(0, r):
            print("GFN round {}; input = {}".format(i, T_a))
            for j in range(0, d, 4):
                print("---------------------------------------")
                # print(hex(T_a[j+1]))
                # print(hex(rk_a[(int(d/2)*i)]))
                # print(hex(T_a[j]))
                # print(hex(self.F0(rk_a[(int(d/2)*i)],T_a[j])[0]))
                print(
                    "T_a[{}] = {} ^ {}".format(
                        j + 1,
                        hex(T_a[j + 1]),
                        hex(self.F0(rk_a[(int(d / 2) * i) + int(j / 2)], T_a[j])[0]),
                    )
                )
                T_a[j + 1] = self.galois8.add(
                    T_a[j + 1], self.F0(rk_a[(int(d / 2) * i) + int(j / 2)], T_a[j])[0]
                )
                print("T_[{}] = {}".format(j + 1, hex(T_a[j + 1])))
                # print(hex(T_a[j+1]))
                print("--------------------------")

                # print(hex(T_a[j+3]))
                # print(hex(rk_a[(int(d/2)*i)+1]))
                # print(hex(T_a[j+2]))
                # print(hex(self.F1(rk_a[(int(d/2)*i)+1],T_a[j+2])[0]))
                print(
                    "T_a[{}] = T_a[{}] ^ {}".format(
                        j + 3,
                        T_a[j + 3],
                        self.F1(rk_a[(int(d / 2) * i) + (int(j / 2) + 1)], T_a[j + 2])[
                            0
                        ],
                    )
                )
                T_a[j + 3] = self.galois8.add(
                    T_a[j + 3],
                    self.F1(rk_a[(int(d / 2) * i) + (int(j / 2) + 1)], T_a[j + 2])[0],
                )

                # print(hex(T_a[j+3]))
                print("----------------------------------------------")

            # print(T_a)
            T_a = np.roll(T_a, -1)
            # print(T_a)

        return np.roll(T_a, 1)

    def F0(self, rk, x):
        print("**********F0*********")
        T_a = np.zeros((4, 1), dtype=np.uint32)
        T = self.galois8.add(rk, x)
        print("F0 input is = {}".format(hex(x)))
        print("F0 round key is = {}".format(hex(rk)))
        print("F0 after key add = {}".format(hex(T)))
        # print(hex(rk))
        # print(hex(x))
        # print(hex(T))
        T_n = np.zeros(4, dtype=np.uint32)
        for i in range(0, 4):
            T_n[i] = int((T >> (8 * i)) & 0xFF)
            if i % 2:
                T_n[i] = self.S0(T_n[i])
            else:
                T_n[i] = self.S1(T_n[i])
            T_a[i][0] = T_n[i]
            # print(i)
            # print(hex(T_n[i]))
            print("F0 after S = {} and i = {}".format(hex(T_n[i]), i))
        p = (1 << 8) + (1 << 4) + (1 << 3) + (1 << 2) + 1
        y = self.galois8.matrix_multiplication(M0, T_a, p)
        print("F0 after M = {}".format(y))
        print("**********************************")
        return (y[3] << 24) + (y[2] << 16) + (y[1] << 8) + y[0]

    def F1(self, rk, x):
        T_a = np.zeros((4, 1), dtype=np.uint32)
        T = self.galois8.add(rk, x)

        T_n = np.zeros(4, dtype=np.uint32)
        for i in range(0, 4):
            T_n[i] = (T >> (8 * i)) & 0xFF
            if i % 2:
                T_n[i] = self.S1(T_n[i])
            else:
                T_n[i] = self.S0(T_n[i])

            T_a[i][0] = T_n[i]

        p = (1 << 8) + (1 << 4) + (1 << 3) + (1 << 2) + 1
        y = self.galois8.matrix_multiplication(M1, T_a, p)
        return (y[3] << 24) + (y[2] << 16) + (y[1] << 8) + y[0]

    def S0(self, x):
        x1 = x & 0xF
        x0 = (x >> 4) & 0xF

        p = (1 << 4) + (1 << 1) + 1  # z4 + z + 1

        t0 = SS[0][x0]
        t1 = SS[1][x1]

        m0 = self.galois4.multiplication(2, t1, p)
        u0 = self.galois4.add(t0, m0)
        m1 = self.galois4.multiplication(2, t0, p)
        u1 = self.galois4.add(t1, m1)

        y0 = SS[2][u0]
        y1 = SS[3][u1]

        return (y0 << 4) + y1

    def S1(self, x):
        p = (1 << 8) + (1 << 4) + (1 << 3) + (1 << 2) + 1
        p_array = np.array([1, 0, 0, 0, 1, 1, 1, 0, 1])  #

        x_a = np.zeros((8, 1), dtype=np.uint32)
        for i in range(0, 8):
            x_a[7 - i] = (x >> i) & 0x01

        f = self.f_S1(x_a, p)
        f_inverse = self.galois8.inverse_mul(np.reshape(np.transpose(f), 8), p_array)
        # print(f)
        # print(f_inverse)
        padding = 8 - np.shape(f_inverse)[0]
        zero_padding = np.zeros(padding, dtype=np.uint)
        f_inverse = np.append(zero_padding, f_inverse)
        f_inverse = np.atleast_2d(f_inverse).T
        S1_array = self.g_S1(f_inverse, p)
        S1 = 0
        for i in range(0, 8):
            S1 = S1 + (S1_array[7 - i][0] * int(math.pow(2, i)))

        return S1

    def gen_S1_values_for_sv(self):

        for i in range(0, 256):
            value = self.S1(i)
            print(f"assign s1[{i}] = 8'h{hex(value)}")

    def f_S1(self, x, p):
        k = np.array([0, 0, 0, 1, 1, 1, 1, 0])  # 0x1e

        r = self.galois8.matrix_multiplication(MS_f, x, p)
        return self.galois8.matrix_add(r, k)

    def g_S1(self, x, p):
        k = np.array([0, 1, 1, 0, 1, 0, 0, 1])  # 0x69

        r = self.galois8.matrix_multiplication(MS_g, x, p)
        return self.galois8.matrix_add(r, k)

    def ROL(self, x, i, len_bits):
        j = len_bits - i
        return ((x << i) | (x >> j)) & (2**len_bits - 1)

    def ROR(self, x, i, len_bits):
        j = len_bits - i
        return ((x >> i) | (x << j)) & (2**len_bits - 1)


if __name__ == "__main__":
    cipher = CLEFIA()
    """
    a = np.array([1,0,0,0,1,1,0,1,1],dtype=np.uint32)
    b = np.array([1,0,1,0,0,1,1],dtype=np.uint32)
    q = np.zeros((9),dtype=np.uint32)
    gf = galois_arithmetic.GaloisField(8)
    #q,r = gf.polynomial_long_division(a,b,q)

    #print(q)
    #print(r)

    q,s,t,r = gf.polynomial_extended_euclidean_algorithm(a,b)
    #print(q)
    #print(s)
    #print(t)
    #print(r)

    #print(gf.inverse_mul(b,a))
    """
    a = 0x00010203
    rk = 0xF3E6CEF9
    # print(hex(cipher.F0(rk,a)[0]))
    # b  = 0x08090a0b
    # rk = 0x8df75e38
    # cipher.F1(rk,b)

    # cipher.generate_constants(0x428a,30)
    key = 0xFFEEDDCCBBAA99887766554433221100
    key_192 = 0xFFEEDDCCBBAA99887766554433221100F0E0D0C0B0A09080
    key_256 = 0xFFEEDDCCBBAA99887766554433221100F0E0D0C0B0A090807060504030201000

    # key = 0x3322110077665544bbaa9988ffeeddcc
    plaintext = 0x000102030405060708090A0B0C0D0E0F
    # plaintext = 0x0c0d0e0f08090a0b0405060700010203
    WK, RK = cipher.key_schedule(key, 128)
    print("/////////////////******************///////////////")
    c = cipher.encrypt(plaintext, WK, RK)

# cipher.gen_S1_values_for_sv()
# cipher.gen_CON_values_for_sv(128)
# cipher.gen_CON_values_for_sv(192)
# cipher.gen_CON_values_for_sv(256)
# print(hex(cipher.S0(0x10)))
# print(hex(cipher.S1(0x10)))
