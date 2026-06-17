/**
 * File              : encrypt.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 10.03.2025
 * Last Modified Date: 10.03.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module encrypt #(
    parameter KEY_LEN = 256
) (
    input clk,
    input rst,
    input start,
    input [31:0] wk[3:0],
    input [31:0] round_keys[35+((KEY_LEN-128)>>(3)):0],
    input [31:0] block_i[3:0],
    output [31:0] block_o[3:0],
    output logic end_signal
);

  localparam N_RK = 36 + ((KEY_LEN - 128) >> (3));
  localparam R = N_RK >> (1);


  //gfn 4,R
  logic [31:0] gfn_block_o[3:0];
  logic gfn_end_signal;
  logic [31:0] gfn_block_i[3:0];
  assign gfn_block_i[0] = block_i[0];
  assign gfn_block_i[1] = block_i[1] ^ wk[0];
  assign gfn_block_i[2] = block_i[2];
  assign gfn_block_i[3] = block_i[3] ^ wk[1];
  logic rst_gfn;

  gfn #(
      .d(4),
      .r(R)
  ) gfn_inst (
      .clk(clk),
      .rst(rst_gfn),
      .round_keys(round_keys),
      .block_i(gfn_block_i),
      .block_o(gfn_block_o),
      .end_signal(gfn_end_signal)
  );


  //output register
  genvar i;
  logic [31:0] out_din[3:0];
  logic [31:0] out_dout[3:0];
  logic [0:0] out_w[3:0];
  logic [0:0] out_cl[3:0];
  generate
    for (i = 0; i < 4; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_WK_i (
          .clk(clk),
          .cl(out_cl[i]),
          .w(out_w[i]),
          .din(out_din[i]),
          .dout(out_dout[i])
      );
      assign block_o[i] = out_dout[i];
    end
  endgenerate


  logic [31:0] j;
  logic [1:0] current_state, next_state;
  localparam IDLE = 0;
  localparam WAIT_FOR_GFN = 1;
  localparam WRITE_OUTPUT = 2;
  localparam END_STATE = 3;


  always_comb begin
    next_state = current_state;
    end_signal = 0;
    rst_gfn = 0;
    for (j = 0; j < 4; j++) begin
      out_cl[j]  = 0;
      out_w[j]   = 0;
      out_din[j] = 0;
    end
    case (current_state)
      IDLE: begin
        rst_gfn = 1;
        if (start == 1) begin
          next_state = WAIT_FOR_GFN;
        end
        for (j = 0; j < 4; j++) begin
          out_cl[j] = 1;
        end

      end
      WAIT_FOR_GFN: begin
        if (gfn_end_signal == 1) begin
          next_state = WRITE_OUTPUT;
        end

      end
      WRITE_OUTPUT: begin
        for (j = 0; j < 4; j++) begin
          out_w[j] = 1;
        end
        out_din[0] = gfn_block_o[0];
        out_din[1] = gfn_block_o[1] ^ wk[2];
        out_din[2] = gfn_block_o[2];
        out_din[3] = gfn_block_o[3] ^ wk[3];

        next_state = END_STATE;

      end
      END_STATE: begin
        end_signal = 1;
      end

    endcase


  end


  always_ff @(posedge clk) begin
    if (rst == 1) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end

  end
endmodule
