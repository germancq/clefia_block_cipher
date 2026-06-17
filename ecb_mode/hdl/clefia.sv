/**
 * File              : clefia.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 20.02.2025
 * Last Modified Date: 20.02.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */


module clefia #(
    parameter KEY_LEN = 128
) (
    input clk,
    input rst,
    input [KEY_LEN-1:0] key,
    input [127:0] block_i,
    output [127:0] block_o,
    input rq_data,
    output end_key_generation,
    output end_signal

);

  localparam N_RK = 36 + ((KEY_LEN - 128) >> (3));
  logic [31:0] wk[3:0];
  logic [31:0] round_keys[N_RK-1:0];

  logic start_enc;
  logic [31:0] result_enc[3:0];
  logic end_enc;

  logic [31:0] enc_block_i[3:0];
  genvar i;
  for (i = 0; i < 4; i++) begin
    assign enc_block_i[3-i] = block_i[31+(i<<5):i<<5];

  end


  register #(
      .DATA_WIDTH(128)
  ) result (
      .clk(clk),
      .cl(rst || rq_data),
      .w(end_signal),
      .din({result_enc[0], result_enc[1], result_enc[2], result_enc[3]}),
      .dout(block_o)
  );

  key_schedule #(
      .KEY_LEN(KEY_LEN)
  ) key_sch_inst (
      .clk(clk),
      .rst(rst),
      .key(key),
      .wk(wk),
      .round_keys(round_keys),
      .end_signal(end_key_generation)
  );

  encrypt #(
      .KEY_LEN(KEY_LEN)
  ) encrypt_inst (
      .clk(clk),
      .rst(rst),
      .start(rq_data && end_key_generation),
      .wk(wk),
      .round_keys(round_keys),
      .block_i(enc_block_i),
      .block_o(result_enc),
      .end_signal(end_signal)
  );

endmodule : clefia


