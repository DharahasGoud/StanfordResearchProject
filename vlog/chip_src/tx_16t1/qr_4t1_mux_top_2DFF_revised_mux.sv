`timescale 100ps/1ps   //  unit_time / time precision

`default_nettype none

module qr_4t1_mux_top_2DFF_revised_mux (
    input wire logic clk_Q,
    input wire logic clk_QB,
    input wire logic clk_I,
    input wire logic clk_IB, // Four phase clock input from PI+MDLL
    input wire logic [3:0] din,
    input wire logic rst,
    output logic data
);

logic[3:0] sel;

// Instantiate the data path for Q clk path, use the Q clock as the reference clock
wire D0DQ;
wire D1MQ;
ff_c dff_Q0 (.D(din[3]), .CP(clk_Q), .Q(D0DQ));

// Instantiate the data path for I clk path
wire D0DI;
wire D1MI;
ff_c dff_I0 (.D(din[2]), .CP(clk_I), .Q(D0DI));

// Instantiate the data path for QB clk path
wire D0DQB;
wire D1DQB;
wire D2MQB;
ff_c dff_QB0 (.D(din[1]), .CP(clk_Q), .Q(D0DQB)); // data captured using Q clk and gradually passed to QB clk.
ff_c dff_QB1 (.D(D0DQB), .CP(clk_QB), .Q(D1DQB));

// Instantiate the data path for QB clk path
wire D0DIB;
wire D1DIB;
wire D2MIB;
ff_c dff_IB0 (.D(din[0]), .CP(clk_I), .Q(D0DIB)); // data captured using Q clk and gradually passed to IB clk.
ff_c dff_IB1 (.D(D0DIB), .CP(clk_IB), .Q(D1DIB));

// 4 to 1 mux
assign sel[3] = (clk_Q  & clk_I);
assign sel[2] = (clk_I  & clk_QB);
assign sel[1] = (clk_QB & clk_IB);
assign sel[0] = (clk_IB & clk_Q);


always_comb begin
    case (sel)
    4'b0001: data = D1DQB;
    4'b0010: data = D0DI;
    4'b0100: data = D0DQ;
    4'b1000: data = D1DIB;
    endcase
end

endmodule

`default_nettype wire
