'''
 # @ Author: German Cano Quiveu, germancq
 # @ Create Time: 2023-11-30 11:52:21
 # @ Modified by: German Cano Quiveu, germancq
 # @ Modified time: 2023-11-30 11:52:25
 # @ Description:
 '''

import math
import numpy as np

class GaloisField:

    def __init__(self,n):
        #GF(2^n)
        self.n = n
        pass

    def inverse_mul(self,x,p):
        return self.polynomial_extended_euclidean_algorithm(p,x)[2]
        

    def polynomial_extended_euclidean_algorithm(self,a,b):
        #a y b son arrays
        q = np.zeros((np.shape(a)[0]),dtype=np.uint32)
        r0 = a
        r1 = b
        s0 = np.array([1],dtype=np.uint32)
        s1 = np.array([0],dtype=np.uint32)
        t0 = np.array([0],dtype=np.uint32)
        t1 = np.array([1],dtype=np.uint32)

        return self.pol_eea(r0,r1,s0,s1,t0,t1,q)

    #r_j = r_(i+1)
    def pol_eea(self,r_i,r_j,s_i,s_j,t_i,t_j,q):
        #print('pol_eea')
        #print(r_i)
        #print(r_j)
        #print(s_i)
        #print(s_j)
        #print(t_i)
        #print(t_j)
        #caso base r_i es 0
        if(not np.any(r_j)):
            return q,s_i,t_i,r_i
        #iteracion
        q = np.zeros((np.shape(r_i)[0]),dtype=np.uint32)
        q,r = self.polynomial_long_division(r_i,r_j,q)
        #q = np.flip(q)
        #q = np.trim_zeros(q,'f')
        
        s_q = np.flip(self.polynomial_multiplication(np.flip(s_j),q))
        t_q = np.flip(self.polynomial_multiplication(np.flip(t_j),q))
        

        
        s_q = np.trim_zeros(s_q,'f')
        t_q = np.trim_zeros(t_q,'f')

        

        if(not np.any(s_q)):
            s_k = s_i
        else:    
            size_sq = np.shape(s_q)[0]
            size_si = np.shape(s_i)[0]
            diff = abs(size_sq-size_si)
            z_append = np.zeros((diff),dtype=np.uint)
            if(size_si<size_sq):
                s_i = np.append(z_append,s_i)
            else:
                s_q = np.append(z_append,s_q)

            s_k = np.bitwise_xor(s_i,s_q)

        if(not np.any(t_q)):
            t_k = t_i    
        else:
            size_tq = np.shape(t_q)[0]
            size_ti = np.shape(t_i)[0]
            diff = abs(size_tq-size_ti)
            z_append = np.zeros((diff),dtype=np.uint)
            if(size_ti<size_tq):
                t_i = np.append(z_append,t_i)
            else:
                t_q = np.append(z_append,t_q)

            t_k = np.bitwise_xor(t_i,t_q)
        
        
        return self.pol_eea(r_j,r,s_j,s_k,t_j,t_k,q)

    
    def polynomial_long_division(self,a,b,q):
        #print('polinomial_long_division')
        #print(a)
        #print(b)
        #print(q)

        a = np.trim_zeros(a,'f')
        b = np.trim_zeros(b,'f')

        size_a = np.shape(a)[0]
        size_b = np.shape(b)[0]

        if(size_a < size_b):
            return q,a

        q_i = size_a - size_b
        q[q_i] = 1
        #print(q)
        z = np.zeros((q_i),dtype=np.uint32)
        b_q = np.append(b,z)
        #print(b_q)
        r = np.bitwise_xor(a,b_q)
        r = np.trim_zeros(r,'f')#trim front zeros
        #print(r)
        #return
        return self.polynomial_long_division(r,b,q)

        


    def scalar_by_matrix(self,M1,k,p):
        rows_a, cols_a = M1.shape



        result = np.zeros((rows_a,cols_a),dtype=np.uint32)
        for i in range(0,rows_a):
            for j in range(0,cols_a):
                #print(M1[i][j])
                result[i][j] = self.multiplication(M1[i][j],k,p)

        #print('scalar by matrix')
        #print(result)
        return result

    def matrix_add(self,A,B):
        try:
            rows_a,cols_a = np.shape(A)
        except ValueError as e:
            rows_a = np.shape(A)[0]
            cols_a = 1

        try:
            rows_b,cols_b = np.shape(B)
        except ValueError:
            rows_b = np.shape(B)[0]
            cols_b = 1

        if(rows_a != rows_b or cols_a != cols_b):
            return -1
        
        result = np.zeros((rows_a,cols_a),dtype=np.uint32)
        for i in range(0,rows_a):
            for j in range(0,cols_a):
                a = A[i]
                b = B[i]
                
                if(cols_a != 1):
                    a = A[i][j]
                
                if(cols_b != 1):
                    b = B[i][j]

                result[i][j] = self.add(a,b)

        return result

    def matrix_multiplication(self,A,B,p):

        try:
            rows_a,cols_a = np.shape(A)
        except ValueError as e:
            rows_a = np.shape(A)[0]
            cols_a = 1

        try:
            rows_b,cols_b = np.shape(B)
        except ValueError:
            rows_b = np.shape(B)[0]
            cols_b = 1

        #print(rows_b)
        #print(cols_a)
        if(cols_a != rows_b):
            #error
            return -1
        
        #print('matrix mult')
        #print(A)
        #print(B)
        result = np.zeros((rows_a,cols_b),dtype=np.uint32)

        for i in range(0,rows_a):
            for j in range(0,cols_b):
                ##print('get_cij')
                result[i][j] = self.get_c_ij(A,B,p,cols_a,cols_b,i,j)
                

        #print(result)
        #print('end matrix mult')
        return result
    

    def get_c_ij(self,A,B,p,cols_a,cols_b,i,j):
        result = 0
        for n in range(0,cols_a):
            a = A[i]
            b = B[n]
            
            if(cols_a != 1):
                a = A[i][n]
            
            if(cols_b != 1):
                b = B[n][j]
                    
            m = self.multiplication(a,b,p)
            
            ##print('mult')
            ##print(a)
            ##print(b)
            ##print(m)
            ##print('-------------------')
            
            result = self.add(m,result)

        return result

    '''
    def matrix_multiplication(self,M1,M2,p):
        rows_a = len(M1)
        rows_b = len(M2) # == colums_a
        colums_a = rows_b
        colums_b = rows_a
        if(type(M2[0]) is list) : 
            colums_b = len(M2[0])
        
        result = []
        

        for i in range(0,rows_a) :
            result.append([])
            for j in range(0,colums_b) :    
                result[i].append(0)
                for k in range(0,rows_b):
                    a_1 = result[i][j]

                    if(colums_b > 1):
                        a_3 = M2[k][j]
                    else :
                        a_3 = M2[k]

                    if(colums_a > 1) :
                        a_2 = M1[i][k]   
                    else :
                        a_2 = M1[k]
                        
                    #result[i][j] = (a_1 + (a_2 * a_3))
                    gf_1 = self.galois_multiplication(a_2,a_3,p)
                    
                    #print("==========================")
                    #print(i)
                    #print(j)
                    #print(hex(a_2))
                    #print(hex(a_3))
                    #print(hex(gf_1))
                    #print(hex(a_1))
                    #print("==========================")
                    
                    result[i][j] = self.galois_add(a_1,gf_1)

        return result
    '''
    def add(self,a,b) :
        return a ^ b
    
    def multiplication(self,a,b,p):
        t = 0
        for i in range(0,self.n):
            mask = 0x1 << i
            bit_b = b & mask
            b_i = 0 if bit_b == 0 else 1
            r = b_i*(a<<i)
            t = self.add(t,r)

        return self.reduced_polinomial(t,p)
    
    def polynomial_multiplication(self,a,b):
        ##print('polynomial_mult')
        ##print(a)
        ##print(b)
        size_a = np.shape(a)[0]
        size_b = np.shape(b)[0]
        t = np.zeros((size_a+size_b),dtype=np.uint32)
        for i in range(0,size_a):
            for j in range(0,size_b):
                if (a[i] == 1 and b[j] == 1):
                    t[i+j] = t[i+j] ^ 1
        ##print(t)
        ##print('end_mult')            
        return t    

    def reduced_polinomial(self,a,p):
        n = math.ceil(math.log(p,2))
        n = n - 1
        t = a
        for i in range((self.n*2)-1, self.n -1, -1 ):
            mask = 0x1 << i
            bit_t = t & mask
            t_i = 0 if bit_t == 0 else 1
            if(t_i):
                m = int(i-n)
                t = self.add(p<<m, t)

        return t