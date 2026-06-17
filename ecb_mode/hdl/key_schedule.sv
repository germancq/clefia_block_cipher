/**
 * File              : key_schedule.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 27.02.2025
 * Last Modified Date: 27.02.2025
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module key_schedule #(
    parameter KEY_LEN = 256
) (
    input clk,
    input rst,
    input [KEY_LEN-1:0] key,
    output [31:0] wk[3:0],
    output [31:0] round_keys[35+((KEY_LEN-128)>>(3)):0],
    output logic end_signal
);

  localparam N_RK = 36 + ((KEY_LEN - 128) >> (3));

  logic [31:0] key_r[3:0];
  assign key_r[3] = KEY_LEN == 128 ? key[31:0] : (KEY_LEN == 192 ? ~key[159:128] : key[31:0]);
  assign key_r[2] = KEY_LEN == 128 ? key[63:32] : (KEY_LEN == 192 ? ~key[191:160] : key[63:32]);
  assign key_r[1] = KEY_LEN == 128 ? key[95:64] : (KEY_LEN == 192 ? key[31:0] : key[95:64]);
  assign key_r[0] = KEY_LEN == 128 ? key[127:96] : (KEY_LEN == 192 ? key[63:32] : key[127:96]);
  logic [31:0] key_l[3:0];
  assign key_l[3] = KEY_LEN == 128 ? 0 : (KEY_LEN == 192 ? key[95:64] : key[159:128]);
  assign key_l[2] = KEY_LEN == 128 ? 0 : (KEY_LEN == 192 ? key[127:96] : key[191:160]);
  assign key_l[1] = KEY_LEN == 128 ? 0 : (KEY_LEN == 192 ? key[159:128] : key[223:192]);
  assign key_l[0] = KEY_LEN == 128 ? 0 : (KEY_LEN == 192 ? key[191:160] : key[255:224]);

  function [127:0] doubleSwap(input [127:0] block_i);
    return {block_i[120:64], block_i[6:0], block_i[127:121], block_i[63:7]};
  endfunction

  logic [31:0] number_rounds;
  generate
    case (KEY_LEN)
      128: begin
        assign number_rounds = 9;
      end
      192: begin
        assign number_rounds = 11;
      end
      default:
      begin
        assign number_rounds = 13;
      end
    endcase
  endgenerate

  //counter for rounds
  logic up_rounds_counter;
  logic rst_rounds_counter;
  logic [31:0] din_rounds_counter;
  logic [31:0] dout_rounds_counter;
  counter #(
      .DATA_WIDTH(32)
  ) rounds_counter (
      .clk (clk),
      .rst (rst_rounds_counter),
      .up  (up_rounds_counter),
      .down(1'b0),
      .din (din_rounds_counter),
      .dout(dout_rounds_counter)
  );

  //CON
  logic [31:0] CON_128[59:0];
  logic [31:0] CON_192[83:0];
  logic [31:0] CON_256[91:0];
  gen_con gen_con_inst (
      .CON_128(CON_128),
      .CON_192(CON_192),
      .CON_256(CON_256)
  );

  //gfn 4,12
  logic [31:0] gfn4_block_o[3:0];
  logic gfn4_end_signal;
  logic [31:0] gfn4_round_keys[23:0];

  genvar i;
  generate
    for (i = 0; i < 24; i++) begin
      assign gfn4_round_keys[i] = CON_128[i];

    end
  endgenerate
  gfn #(
      .d(4),
      .r(12)
  ) gfn_inst (
      .clk(clk),
      .rst(rst),
      .round_keys(gfn4_round_keys),
      .block_i(key_r),
      .block_o(gfn4_block_o),
      .end_signal(gfn4_end_signal)
  );
  // gfn 8,10
  logic [31:0] gfn8_block_o[7:0];
  logic gfn8_end_signal;
  logic [31:0] gfn8_block_i[7:0];
  logic [31:0] gfn8_round_keys[39:0];

  generate
    for (i = 0; i < 40; i++) begin
      assign gfn8_round_keys[i] = KEY_LEN <= 192 ? CON_192[i] : CON_256[i];
    end
    for (i = 0; i < 4; i++) begin
      assign gfn8_block_i[i]   = key_l[i];
      assign gfn8_block_i[i+4] = key_r[i];

    end
  endgenerate
  //  assign gfn8_block_i[3:0] = key_l;
  // assign gfn8_block_i[7:4] = key_r;
  gfn #(
      .d(8),
      .r(10)
  ) gfn_inst_8 (
      .clk(clk),
      .rst(rst),
      .round_keys(gfn8_round_keys),
      .block_i(gfn8_block_i),
      .block_o(gfn8_block_o),
      .end_signal(gfn8_end_signal)
  );

  //WK
  logic [31:0] WK_din[3:0];
  logic [31:0] WK_dout[3:0];
  logic [0:0] WK_w[3:0];
  logic [0:0] WK_cl[3:0];
  generate
    for (i = 0; i < 4; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_WK_i (
          .clk(clk),
          .cl(WK_cl[i]),
          .w(WK_w[i]),
          .din(WK_din[i]),
          .dout(WK_dout[i])
      );
      assign wk[i] = WK_dout[i];
    end
  endgenerate

  //register for T
  logic [31:0] T_din[3:0];
  logic [31:0] T_dout[3:0];
  logic [0:0] T_w[3:0];
  logic [0:0] T_cl[3:0];
  generate
    for (i = 0; i < 4; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_T_i (
          .clk(clk),
          .cl(T_cl[i]),
          .w(T_w[i]),
          .din(T_din[i]),
          .dout(T_dout[i])
      );
    end
  endgenerate
  //register for L
  logic [31:0] LL_din[3:0];
  logic [31:0] LL_dout[3:0];
  logic [0:0] LL_w[3:0];
  logic [0:0] LL_cl[3:0];
  generate
    for (i = 0; i < 4; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_LL_i (
          .clk(clk),
          .cl(LL_cl[i]),
          .w(LL_w[i]),
          .din(LL_din[i]),
          .dout(LL_dout[i])
      );
    end
  endgenerate
  logic [31:0] LR_din[3:0];
  logic [31:0] LR_dout[3:0];
  logic [0:0] LR_w[3:0];
  logic [0:0] LR_cl[3:0];
  generate
    for (i = 0; i < 4; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_LR_i (
          .clk(clk),
          .cl(LR_cl[i]),
          .w(LR_w[i]),
          .din(LR_din[i]),
          .dout(LR_dout[i])
      );
    end
  endgenerate
  //register for RK
  logic [31:0] RK_din[N_RK-1:0];
  logic [31:0] RK_dout[N_RK-1:0];
  logic [0:0] RK_w[N_RK-1:0];
  logic [0:0] RK_cl[N_RK-1:0];
  generate
    for (i = 0; i < N_RK; i++) begin
      register #(
          .DATA_WIDTH(32)
      ) r_RK_i (
          .clk(clk),
          .cl(RK_cl[i]),
          .w(RK_w[i]),
          .din(RK_din[i]),
          .dout(RK_dout[i])
      );
      assign round_keys[i] = RK_dout[i];
    end
  endgenerate

  logic [2:0] current_state, next_state;

  localparam IDLE = 0;
  localparam WAIT_FOR_GFN = 1;
  localparam CHECK_COUNTER = 2;
  localparam GEN_T = 3;
  localparam CHECK_ODD = 4;
  localparam GEN_RK = 5;
  localparam UPDATE_COUNTER = 6;
  localparam END_FSM_STATE = 7;

  logic [31:0] j;

  always_comb begin
    //default values
    next_state = current_state;

    up_rounds_counter = 0;
    rst_rounds_counter = 0;
    din_rounds_counter = 0;

    end_signal = 0;

    for (j = 0; j < 4; j++) begin
      WK_cl[j] = 0;
      WK_w[j] = 0;
      WK_din[j] = KEY_LEN == 128 ? key_r[j] : key_l[j] ^ key_r[j];

      T_cl[j] = 0;
      T_w[j] = 0;
      T_din[j] = 0;

      LL_cl[j] = 0;
      LL_w[j] = 0;
      LL_din[j] = 0;

      LR_cl[j] = 0;
      LR_w[j] = 0;
      LR_din[j] = 0;
    end

    for (j = 0; j < N_RK; j++) begin
      RK_cl[j]  = 0;
      RK_w[j]   = 0;
      RK_din[j] = 0;
    end
    case (current_state)
      IDLE: begin
        next_state = WAIT_FOR_GFN;

        rst_rounds_counter = 1;

        for (j = 0; j < 4; j++) begin
          WK_cl[j] = 1;

          T_cl[j]  = 1;

          LL_cl[j] = 1;
          LR_cl[j] = 1;

        end

        for (j = 0; j < N_RK; j++) begin
          RK_cl[j] = 1;
        end

      end
      WAIT_FOR_GFN: begin
        for (j = 0; j < 4; j++) begin
          WK_w[j] = 1;
        end
        if (gfn4_end_signal && gfn8_end_signal) begin
          next_state = CHECK_COUNTER;

          for (j = 0; j < 4; j++) begin

            LL_din[j] = KEY_LEN == 128 ? gfn4_block_o[j] : gfn8_block_o[j];
            LR_din[j] = KEY_LEN == 128 ? 0 : gfn8_block_o[4+j];

            LL_w[j]   = 1;
            LR_w[j]   = 1;

          end

        end
      end
      CHECK_COUNTER: begin
        next_state = GEN_T;
        if (dout_rounds_counter == number_rounds) begin
          next_state = END_FSM_STATE;
        end
      end
      GEN_T: begin
        next_state = CHECK_ODD;
        for (j = 0; j < 4; j++) begin
          T_w[j] = 1;
          case (KEY_LEN)
            128: begin
              T_din[j] = LL_dout[j] ^ CON_128[24+(dout_rounds_counter<<2)+j];
            end
            192: begin
              if (dout_rounds_counter % 4 < 2) begin
                T_din[j] = LL_dout[j] ^ CON_192[40+(dout_rounds_counter<<2)+j];
              end else begin
                T_din[j] = LR_dout[j] ^ CON_192[40+(dout_rounds_counter<<2)+j];
              end
            end
            default: begin
              if (dout_rounds_counter % 4 < 2) begin
                T_din[j] = LL_dout[j] ^ CON_256[40+(dout_rounds_counter<<2)+j];
              end else begin
                T_din[j] = LR_dout[j] ^ CON_256[40+(dout_rounds_counter<<2)+j];
              end
            end
          endcase

        end

      end
      CHECK_ODD: begin
        next_state = GEN_RK;

        for (j = 0; j < 4; j++) begin
          case (KEY_LEN)
            128: begin
              LL_w[3-j] = 1;
              LL_din[3-j] = doubleSwap({LL_dout[0], LL_dout[1], LL_dout[2], LL_dout[3]}) >>
                  (32 * j);
              if (dout_rounds_counter[0] == 1) begin
                T_w[j]   = 1;
                T_din[j] = T_dout[j] ^ key_r[j];
              end
            end
            default: begin
              if (dout_rounds_counter % 4 < 2) begin
                LL_w[3-j] = 1;
                LL_din[3-j] = doubleSwap({LL_dout[0], LL_dout[1], LL_dout[2], LL_dout[3]}) >>
                    (32 * j);
                if (dout_rounds_counter[0] == 1) begin
                  T_w[j]   = 1;
                  T_din[j] = T_dout[j] ^ key_r[j];
                end
              end else begin
                LR_w[3-j] = 1;
                LR_din[3-j] = doubleSwap({LR_dout[0], LR_dout[1], LR_dout[2], LR_dout[3]}) >>
                    (32 * j);
                if (dout_rounds_counter[0] == 1) begin
                  T_w[j]   = 1;
                  T_din[j] = T_dout[j] ^ key_l[j];
                end
              end
            end
          endcase
        end
      end
      GEN_RK: begin
        next_state = UPDATE_COUNTER;
        for (j = 0; j < 4; j++) begin
          RK_w[(dout_rounds_counter<<2)+j]   = 1;
          RK_din[(dout_rounds_counter<<2)+j] = T_dout[j];
        end

      end
      UPDATE_COUNTER: begin
        up_rounds_counter = 1;
        next_state = CHECK_COUNTER;
      end
      END_FSM_STATE: begin
        end_signal = 1;
      end


    endcase
  end

  always_ff @(posedge clk) begin

    if (rst) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end
  end
endmodule





















































