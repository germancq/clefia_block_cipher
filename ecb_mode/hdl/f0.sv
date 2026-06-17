/**
 * File              : f0.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 24.02.2025
 * Last Modified Date: 24.02.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module F0 (
    input  [31:0] rk,
    input  [31:0] x,
    output [31:0] y
);

  logic [7:0] T [ 3:0];
  wire  [7:0] s [ 3:0];

  logic [7:0] M0[15:0];
  assign M0[0]  = 8'h01;
  assign M0[1]  = 8'h02;
  assign M0[2]  = 8'h04;
  assign M0[3]  = 8'h06;
  assign M0[4]  = 8'h02;
  assign M0[5]  = 8'h01;
  assign M0[6]  = 8'h06;
  assign M0[7]  = 8'h04;
  assign M0[8]  = 8'h04;
  assign M0[9]  = 8'h06;
  assign M0[10] = 8'h01;
  assign M0[11] = 8'h02;
  assign M0[12] = 8'h06;
  assign M0[13] = 8'h04;
  assign M0[14] = 8'h02;
  assign M0[15] = 8'h01;

  S1 box0 (
      .x(rk[7:0] ^ x[7:0]),
      .y(T[0])
  );

  S0 box1 (
      .x(rk[15:8] ^ x[15:8]),
      .y(T[1])
  );
  S1 box2 (
      .x(rk[23:16] ^ x[23:16]),
      .y(T[2])
  );
  S0 box3 (
      .x(rk[31:24] ^ x[31:24]),
      .y(T[3])
  );

  matrix_multiplication #(
      .N(8),
      .COL_A(4),
      .COL_B(1),
      .ROW_A(4)
  ) mult (
      .a(M0),
      .b(T),
      .p(9'h11D),
      .s(s)
  );

  assign y = {s[3], s[2], s[1], s[0]};
endmodule






































