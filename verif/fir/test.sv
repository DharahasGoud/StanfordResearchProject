module test(); 
   
   import constant_gpack::*;

   parameter integer data_depth = int'((test_gpack::num_of_codes - ffe_gpack::length+1)/ffe_gpack::width);

   logic clk;
   logic rstb;
   logic record;

   logic signed [code_precision-1:0] dataStream       [channel_width-1:0][data_depth-1:0];

   logic signed [ffe_gpack::weight_precision-1:0]  read_weights   [ffe_gpack::length-1:0];
   logic signed [ffe_gpack::weight_precision-1:0]  weights        [ffe_gpack::width-1:0][ffe_gpack::length-1:0];
   logic signed [ffe_gpack::input_precision-1:0]   data           [ffe_gpack::width-1:0];
   logic signed [ffe_gpack::output_precision-1:0]  out  	      [ffe_gpack::width-1:0];
   logic signed [ffe_gpack::output_precision-1:0]  serial_out     [data_depth*ffe_gpack::width-1:0];
   logic signed [ffe_gpack::output_precision-1:0]  record_out;


   ffe #(
   	.maxWeightLength(ffe_gpack::length),
	 	.numChannels(ffe_gpack::width),
	 	.codeBitwidth(ffe_gpack::input_precision),
	 	.weightBitwidth(ffe_gpack::weight_precision),
	 	.resultBitwidth(ffe_gpack::output_precision)
	) ffe_inst1 (
   	.clk(clk),
   	.rstb       (rstb),
   	.new_weights(weights),
   	.codes      (data),
   	.results    (out)
   );

   logic_recorder #(
      .n(ffe_gpack::output_precision),
      .filename(test_gpack::output_filename)
   ) ffe_recorder (
      .in (record_out),
      .clk(clk),
      .en (record)
   );


	integer ii,jj, pos;
   integer fid;

	initial begin
      clk        <= 0;
      pos        <= data_depth;
      record     <= 0;
      for(jj=0;jj<ffe_gpack::width;jj=jj+1) begin
         data[jj] <=0;
      end

      fid = $fopen(test_gpack::adapt_coef_filename, "r");
      for(ii=0; ii<ffe_gpack::length; ii=ii+1) begin
         void'($fscanf(fid, "%d\n", read_weights[ii]));
         for(jj=0; jj<ffe_gpack::width; jj=jj+1) begin
            weights[jj][ii] = read_weights[ii];
         end
      end
      repeat(ffe_gpack::width) toggle_clk(); //Load Data with Extra Cycles to drain the pipeline of X's

      fid = $fopen(test_gpack::adapt_code_filename, "r");
		for(ii=0;ii< data_depth;ii=ii+1) begin
         for(jj=0;jj<ffe_gpack::width;jj=jj+1) begin
            void'($fscanf(fid, "%d\n", dataStream[jj][ii]));
			   //dataStream[jj][ii] <= (jj + ii*dataWidth) >> ($clog2(test_gpack::num_of_codes*dataWidth) - 7); //$random();
         end
		end
         pos <= 0;
		repeat(data_depth) toggle_clk();
        record = 1;
        for(ii=0; ii<data_depth*ffe_gpack::width; ii=ii+1) begin
            record_out = serial_out[ii];
            toggle_clk();
        end
	end

	always @(posedge clk) begin
		if(pos < data_depth) begin 
            for(jj=0;jj<ffe_gpack::width;jj=jj+1) begin
  			    data[jj]  = dataStream[jj][pos];
                serial_out[jj + pos*ffe_gpack::width] = out[jj];
            end
		    pos   = pos + 1;
		end else begin
            for(jj=0;jj<ffe_gpack::width;jj=jj+1) begin
                data[jj]  = 0;
            end
        end
	end


	task toggle_clk;
		#1ns clk = 1;
		#1ns clk = 0;
	endtask

endmodule
