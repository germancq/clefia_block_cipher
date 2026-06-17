/**
 * File              : gfn.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 20.02.2025
 * Last Modified Date: 20.02.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module gfn #(
    parameter d = 4,
    parameter r = 12
) (
    input clk,
    input rst,
    input [31:0] round_keys[((d>>1)*r)-1:0],
    input [31:0] block_i[d-1:0],
    output [31:0] block_o[d-1:0],
    output logic end_signal
);

  //counter for rounds
  logic up_rounds_counter;
  logic rst_rounds_counter;
  logic [$clog2(r):0] din_rounds_counter;
  logic [$clog2(r):0] dout_rounds_counter;
  counter #(
      .DATA_WIDTH($clog2(r) + 1)
  ) rounds_counter (
      .clk (clk),
      .rst (rst_rounds_counter),
      .up  (up_rounds_counter),
      .down(1'b0),
      .din (din_rounds_counter),
      .dout(dout_rounds_counter)
  );

  //registers for Ti
  genvar i;
  logic [31:0] T_din[d-1:0];
  logic [31:0] T_dout[d-1:0];
  logic [0:0] T_w[d-1:0];
  logic [0:0] T_cl[d-1:0];
  generate
    for (i = 0; i < d; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_T_i (
          .clk(clk),
          .cl(T_cl[i]),
          .w(T_w[i]),
          .din(T_din[i]),
          .dout(T_dout[i])
      );
      assign block_o[i] = i == 0 ? T_dout[d-1] : T_dout[(i-1)%d];
    end
  endgenerate

  logic [31:0] f0_rk_input[(d>>2)-1:0];
  logic [31:0] f0_x_input [(d>>2)-1:0];
  logic [31:0] f0_y_output[(d>>2)-1:0];
  logic [31:0] f1_rk_input[(d>>2)-1:0];
  logic [31:0] f1_x_input [(d>>2)-1:0];
  logic [31:0] f1_y_output[(d>>2)-1:0];
  generate
    for (i = 0; i < (d >> 2); i++) begin

      F0 f0_inst_i (
          .rk(f0_rk_input[i]),
          .x (f0_x_input[i]),
          .y (f0_y_output[i])
      );
      F1 f1_inst_i (
          .rk(f1_rk_input[i]),
          .x (f1_x_input[i]),
          .y (f1_y_output[i])
      );
    end
  endgenerate

  logic [2:0] current_state, next_state;

  localparam STEP_1 = 0;
  localparam STEP_2 = 1;
  localparam STEP_2_1 = 2;
  localparam STEP_2_2 = 3;
  localparam STEP_3 = 4;

  logic [31:0] j;
  always_comb begin

    next_state = current_state;
    //default values
    end_signal = 0;
    rst_rounds_counter = 1'b0;
    up_rounds_counter = 1'b0;
    din_rounds_counter = 0;
    for (j = 0; j < d; j++) begin
      T_w[j]   = 0;
      T_cl[j]  = 0;
      T_din[j] = 32'h0;
    end
    for (j = 0; j < (d << 2); j++) begin
      f0_x_input[j]  = 32'h0;
      f0_rk_input[j] = 32'h0;
      f1_x_input[j]  = 32'h0;
      f1_rk_input[j] = 32'h0;
    end

    case (current_state)
      STEP_1: begin

        rst_rounds_counter = 1;
        for (j = 0; j < d; j++) begin
          T_w[j]   = 1;
          T_din[j] = block_i[j];
        end
        next_state = STEP_2;
      end
      STEP_2: begin
        next_state = STEP_2_1;
        if (dout_rounds_counter == r) begin
          next_state = STEP_3;
        end
      end
      STEP_2_1: begin
        next_state = STEP_2_2;
        for (j = 0; j < (d >> 2); j++) begin
          f0_x_input[j]   = T_dout[(j<<2)];
          f0_rk_input[j]  = round_keys[(dout_rounds_counter<<(d>>2))+(j<<1)];
          f1_x_input[j]   = T_dout[(j<<2)+2];
          f1_rk_input[j]  = round_keys[(dout_rounds_counter<<(d>>2))+(j<<1)+1];
          T_w[(j<<2)+1]   = 1;
          T_din[(j<<2)+1] = T_dout[(j<<2)+1] ^ f0_y_output[j];
          T_w[(j<<2)+3]   = 1;
          T_din[(j<<2)+3] = T_dout[(j<<2)+3] ^ f1_y_output[j];
        end

      end
      STEP_2_2: begin
        next_state = STEP_2;
        up_rounds_counter = 1;
        for (j = 0; j < d; j++) begin
          T_w[j]   = 1;
          T_din[j] = T_dout[(j+1)%d];
        end
      end
      STEP_3: begin

        end_signal = 1;

      end
    endcase
  end
  always_ff @(posedge clk) begin

    if (rst) begin
      current_state <= STEP_1;
    end else begin
      current_state <= next_state;
    end
  end

endmodule : gfn


