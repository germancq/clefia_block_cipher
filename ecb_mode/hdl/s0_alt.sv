/**
 * File              : s0.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 24.02.2025
 * Last Modified Date: 24.02.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */
module S0 (
    input  [7:0] x,
    output [7:0] y
);

  logic [3:0] SS0[15:0];
  assign SS0[0]  = 4'he;
  assign SS0[1]  = 4'h6;
  assign SS0[2]  = 4'hc;
  assign SS0[3]  = 4'ha;
  assign SS0[4]  = 4'h8;
  assign SS0[5]  = 4'h7;
  assign SS0[6]  = 4'h2;
  assign SS0[7]  = 4'hf;
  assign SS0[8]  = 4'hb;
  assign SS0[9]  = 4'h1;
  assign SS0[10] = 4'h4;
  assign SS0[11] = 4'h0;
  assign SS0[12] = 4'h5;
  assign SS0[13] = 4'h9;
  assign SS0[14] = 4'hd;
  assign SS0[15] = 4'h3;

  logic [3:0] SS1[15:0];
  assign SS1[0]  = 4'h6;
  assign SS1[1]  = 4'h4;
  assign SS1[2]  = 4'h0;
  assign SS1[3]  = 4'hd;
  assign SS1[4]  = 4'h2;
  assign SS1[5]  = 4'hb;
  assign SS1[6]  = 4'ha;
  assign SS1[7]  = 4'h3;
  assign SS1[8]  = 4'h9;
  assign SS1[9]  = 4'hc;
  assign SS1[10] = 4'he;
  assign SS1[11] = 4'hf;
  assign SS1[12] = 4'h8;
  assign SS1[13] = 4'h7;
  assign SS1[14] = 4'h5;
  assign SS1[15] = 4'h1;

  logic [3:0] SS2[15:0];
  assign SS2[0]  = 4'hb;
  assign SS2[1]  = 4'h8;
  assign SS2[2]  = 4'h5;
  assign SS2[3]  = 4'he;
  assign SS2[4]  = 4'ha;
  assign SS2[5]  = 4'h6;
  assign SS2[6]  = 4'h4;
  assign SS2[7]  = 4'hc;
  assign SS2[8]  = 4'hf;
  assign SS2[9]  = 4'h7;
  assign SS2[10] = 4'h2;
  assign SS2[11] = 4'h3;
  assign SS2[12] = 4'h1;
  assign SS2[13] = 4'h0;
  assign SS2[14] = 4'hd;
  assign SS2[15] = 4'h9;

  logic [3:0] SS3[15:0];
  assign SS3[0]  = 4'ha;
  assign SS3[1]  = 4'h2;
  assign SS3[2]  = 4'h6;
  assign SS3[3]  = 4'hd;
  assign SS3[4]  = 4'h3;
  assign SS3[5]  = 4'h4;
  assign SS3[6]  = 4'h5;
  assign SS3[7]  = 4'he;
  assign SS3[8]  = 4'h0;
  assign SS3[9]  = 4'h7;
  assign SS3[10] = 4'h8;
  assign SS3[11] = 4'h9;
  assign SS3[12] = 4'hb;
  assign SS3[13] = 4'hf;
  assign SS3[14] = 4'hc;
  assign SS3[15] = 4'h1;

  logic [3:0] t0, t1, u0, u1, y0, y1;
  logic [7:0] m0, m1;
  assign t1 = SS1[x[3:0]];
  assign t0 = SS0[x[7:4]];

  galois_multiplication #(
      .N(4)
  ) mul1 (
      .a(4'h2),
      .b(t1),
      .p(5'b10011),
      .s(m0)
  );
  galois_adder #(
      .N(4)
  ) a1 (
      .a(m0),
      .b(t0),
      .s(u0)
  );
  galois_multiplication #(
      .N(4)
  ) mul2 (
      .a(4'h2),
      .b(t0),
      .p(5'b10011),
      .s(m1)
  );
  galois_adder #(
      .N(4)
  ) a2 (
      .a(m1),
      .b(t1),
      .s(u1)
  );

  assign y[7:4] = SS2[u0];
  assign y[3:0] = SS3[u1];

endmodule : S0





