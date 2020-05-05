`default_nettype none

interface dcore_debug_intf import const_pack::*; (
);

		logic en_ext_pi_ctl_cdr;
		logic [Npi-1:0] ext_pi_ctl_cdr;
		logic [Npi-1:0] ext_pi_ctl_offset [Nout-1:0];
		logic en_ext_pfd_offset;
		logic [Nadc-1:0] ext_pfd_offset [Nti-1:0];
		logic en_ext_pfd_offset_rep;
		logic [Nadc-1:0] ext_pfd_offset_rep [Nti_rep-1:0];
        logic en_ext_max_sel_mux;
 		logic [$clog2(Nunit_pi)-1:0] ext_max_sel_mux[Nout-1:0];	// to DCORE and JTAG
		logic en_pfd_cal;
		logic en_pfd_cal_rep;
		logic [Nrange-1:0] Navg_adc;
		logic [Nrange-1:0] Nbin_adc;
		logic [Nrange-1:0] DZ_hist_adc;
		logic [Nrange-1:0] Navg_adc_rep;
		logic [Nrange-1:0] Nbin_adc_rep;
		logic [Nrange-1:0] DZ_hist_adc_rep;
		logic signed [Nadc-1:0] adcout_avg [Nti-1:0];
		logic signed [23:0] adcout_sum [Nti-1:0];
		logic [2**Nrange-1:0] adcout_hist_center [Nti-1:0];
		logic [2**Nrange-1:0] adcout_hist_side   [Nti-1:0];
		logic signed [Nadc-1:0] pfd_offset [Nti-1:0];
		logic signed [Nadc-1:0] adcout_avg_rep [Nti_rep-1:0];
		logic signed [23:0] adcout_sum_rep [Nti_rep-1:0];
		logic [2**Nrange-1:0] adcout_hist_center_rep [Nti_rep-1:0];
		logic [2**Nrange-1:0] adcout_hist_side_rep [Nti_rep-1:0];
		logic signed [Nadc-1:0] pfd_offset_rep [Nti_rep-1:0];
		logic [3:0] Ndiv_clk_avg;
		logic [2:0] Ndiv_clk_cdr;
		logic int_rstb;
		logic [3:0]sel_outbuff;
    	logic [3:0]sel_trigbuff;
    	logic en_outbuff;
    	logic en_trigbuff;
   		logic [2:0]Ndiv_outbuff;
    	logic [2:0]Ndiv_trigbuff;
    	logic bypass_trig;
    	logic bypass_out;
    	logic sram_rstb;
    	logic cdr_rstb;
    	logic prbs_rstb;

    modport dcore ( 	
		input en_ext_pi_ctl_cdr,
		input ext_pi_ctl_cdr,
		input ext_pi_ctl_offset,
		input en_ext_pfd_offset,
		input ext_pfd_offset ,
		input en_ext_pfd_offset_rep,
		input ext_pfd_offset_rep,
 		input en_ext_max_sel_mux,	// to DCORE and JTAG
 		input ext_max_sel_mux,	// to DCORE and JTAG
		input en_pfd_cal,
		input en_pfd_cal_rep,
		input Navg_adc,
		input Nbin_adc,
		input DZ_hist_adc,
		input Navg_adc_rep,
		input Nbin_adc_rep,
		input DZ_hist_adc_rep,
		input Ndiv_clk_avg,
		input Ndiv_clk_cdr,
		input int_rstb,
		input sel_outbuff,
		input sel_trigbuff,
		input en_outbuff,
		input en_trigbuff,
		input Ndiv_outbuff,
		input Ndiv_trigbuff,
		input bypass_trig,
		input bypass_out,
		input sram_rstb,
		input cdr_rstb,
		input prbs_rstb,

		output adcout_avg ,
		output adcout_sum,
		output adcout_hist_center,
		output adcout_hist_side  ,
		output pfd_offset,
		output adcout_avg_rep ,
		output adcout_sum_rep ,
		output adcout_hist_center_rep ,
		output adcout_hist_side_rep ,
		output pfd_offset_rep 
    );
     modport jtag ( 	
		output en_ext_pi_ctl_cdr,
		output ext_pi_ctl_cdr,
		output ext_pi_ctl_offset,
		output en_ext_pfd_offset,
		output ext_pfd_offset ,
		output en_ext_pfd_offset_rep,
		output ext_pfd_offset_rep,
 		output en_ext_max_sel_mux,	// to DCORE and JTAG
 		output ext_max_sel_mux,	// to DCORE and JTAG
		output en_pfd_cal,
		output en_pfd_cal_rep,
		output Navg_adc,
		output Nbin_adc,
		output DZ_hist_adc,
		output Navg_adc_rep,
		output Nbin_adc_rep,
		output DZ_hist_adc_rep,
		output Ndiv_clk_avg,
		output Ndiv_clk_cdr,
		output int_rstb,
		output sel_outbuff,
		output sel_trigbuff,
		output en_outbuff,
		output en_trigbuff,
		output Ndiv_outbuff,
		output Ndiv_trigbuff,
		output bypass_trig,
		output bypass_out,
		output sram_rstb,
		output cdr_rstb,
		output prbs_rstb,

		input adcout_avg ,
		input adcout_sum,
		input adcout_hist_center,
		input adcout_hist_side  ,
		input pfd_offset,
		input adcout_avg_rep ,
		input adcout_sum_rep ,
		input adcout_hist_center_rep ,
		input adcout_hist_side_rep ,
		input pfd_offset_rep 
    );

endinterface 

`default_nettype wire