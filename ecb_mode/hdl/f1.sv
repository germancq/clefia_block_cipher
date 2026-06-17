/**
 * File              : f1.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 25.02.2025
 * Last Modified Date: 25.02.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module F1 (
    input  [31:0] rk,
    input  [31:0] x,
    output [31:0] y
);

  logic [7:0] T [ 3:0];
  wire  [7:0] s [ 3:0];

  logic [7:0] M1[15:0];
  assign M1[0]  = 8'h01;
  assign M1[1]  = 8'h08;
  assign M1[2]  = 8'h02;
  assign M1[3]  = 8'h0a;
  assign M1[4]  = 8'h08;
  assign M1[5]  = 8'h01;
  assign M1[6]  = 8'h0a;
  assign M1[7]  = 8'h02;
  assign M1[8]  = 8'h02;
  assign M1[9]  = 8'h0a;
  assign M1[10] = 8'h01;
  assign M1[11] = 8'h08;
  assign M1[12] = 8'h0a;
  assign M1[13] = 8'h02;
  assign M1[14] = 8'h08;
  assign M1[15] = 8'h01;

  S0 box0 (
      .x(rk[7:0] ^ x[7:0]),
      .y(T[0])
  );

  S1 box1 (
      .x(rk[15:8] ^ x[15:8]),
      .y(T[1])
  );
  S0 box2 (
      .x(rk[23:16] ^ x[23:16]),
      .y(T[2])
  );
  S1 box3 (
      .x(rk[31:24] ^ x[31:24]),
      .y(T[3])
  );

  matrix_multiplication #(
      .N(8),
      .COL_A(4),
      .COL_B(1),
      .ROW_A(4)
  ) mult (
      .a(M1),
      .b(T),
      .p(9'h11D),
      .s(s)
  );

  assign y = {s[3], s[2], s[1], s[0]};
endmodule
















































