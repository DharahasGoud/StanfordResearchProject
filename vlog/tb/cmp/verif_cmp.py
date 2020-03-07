from dragonphy import *
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import yaml
import math
from verif.fir.fir import Fir
from verif.analysis.histogram import *


def write_files(parameters, codes, weights, path="."):
    with open(path + '/' + "adapt_coeff.txt", "w+") as f:
        f.write("\n".join([str(int(w)) for w in weights]) + '\n')
    with open(path + '/' +  "adapt_codes.txt", "w+") as f:
        f.write("\n".join([str(int(c)) for c in codes]) + '\n')
    #f.write('mu: ' + str(parameters[2]) + '\n')

    #This is the most compatible way of writing for verilog - given its a fairly low level language

def deconvolve(weights, chan):
    plt.plot(chan(weights))
    plt.show()

def plot_adapt_input(codes, chan_out, n, plt_mode='normal'):
    if plt_mode == 'stem':
        plt.stem(codes[:n], markerfmt='C0o', basefmt='C0-')
        plt.stem(chan_out[:n], markerfmt='C1o', basefmt='C1-')
    else:
        plt.plot(codes[:n], 'o-')
        plt.plot(chan_out[:n], 'o-')
    plt.show()

def perform_wiener(ideal_input, chan, chan_out, M = 11, u = 0.1, pos=2, iterations=200000, build_dir='.'):
    adapt = Wiener(step_size = u, num_taps = M, cursor_pos=pos)
    for i in range(iterations-pos):
        adapt.find_weights_pulse(ideal_input[i-pos], chan_out[i])   
    
#   pulse_weights = adapt.weights   
#   for i in range(iterations-2):
#       adapt.find_weights_error(ideal_input[i-pos], chan_out[i])   
#   
#   pulse2_weights = adapt.find_weights_pulse2()

#   print(pulse_weights)
#   print(adapt.weights)
    
    #plt.plot(adapt.weights)
    #plt.show()

    #print(f'Filter input: {adapt.filter_in}')
    print(f'Adapted Weights: {adapt.weights}')

    #chan_out = chan_out[2:iterations+2]
    
    #deconvolve(adapt.weights, chan)

    #plt.plot(chan(np.reshape(pulse_weights, len(pulse_weights))))
    #plt.plot(chan(pulse2_weights[-1]))
    #plt.show()
    return adapt.weights

def execute_fir(ffe_config, quantized_weights, depth, quantized_chan_out):
    f = Fir(len(quantized_weights), quantized_weights, ffe_config["parameters"]["width"])
    
    # Only works when all channel weights are the same
    #single_matrix = []
    #for i in range(0, depth - len(quantized_weights) + 1, ffe_config["parameters"]["width"]):
    #    single_matrix.extend(f.single(quantized_chan_out, i).flatten())

    single_matrix = f(quantized_chan_out)
    # Works when all channel weights are different
    channel_matrix = f.channelized(quantized_chan_out)

    assert(compare(channel_matrix, single_matrix, length=500))
    # Format conv_matrix to match SV output
    return np.divide(np.array(single_matrix), 256)

def read_svfile(fname):
    with open(fname, "r") as f:
        f_lines = f.readlines()
        return np.array([int(x) for x in f_lines])

def convert_2s_comp(np_arr, width):
    signed_arr=[]
    for x in np_arr:
        if x - (2**(width-1)-1) > 0:
            x_new = x - (2**width)
            signed_arr.append(x_new)
        else:
            signed_arr.append(x)
    return signed_arr

def compare(arr1, arr2, arr2_trim=0, length=None, debug=False):
    equal = True
    arr2 = arr2[arr2_trim:-1]

    if debug:
        # Print out outputs
        print(f'Compare arr1: {arr1[:length]}')
        print(f'Compare arr2: {arr2[:length]}')

    min_len = min(len(arr1), len(arr2)) 
    length = min_len if length == None else min(min_len, length)

    for x in range(length):
        if arr1[x] != arr2[x]:
            equal = False
    return equal

def main():
    build_dir = 'verif/cmp/build_cmp'
    pack_dir  = 'verif/cmp/pack'

    system_config = Configuration('system')
    test_config   = Configuration('test_verif_cmp', 'verif/cmp')

    #Associate the correct build directory to the python collateral
    test_config['parameters']['ideal_code_filename'] = str(Path(build_dir + '/' + test_config['parameters']['ideal_code_filename']).resolve())
    test_config['parameters']['adapt_code_filename'] = str(Path(build_dir + '/' + test_config['parameters']['adapt_code_filename']).resolve())
    test_config['parameters']['adapt_coef_filename'] = str(Path(build_dir + '/' + test_config['parameters']['adapt_coef_filename']).resolve())
    test_config['parameters']['output_filename'] = str(Path(build_dir + '/' + test_config['parameters']['output_filename']).resolve())

    #
    cmp_config = system_config['generic']['comp']

    # Get config parameters from system.yml file
    ffe_config = system_config['generic']['ffe']

    # Number of iterations of Wiener Steepest Descent
    iterations  = 200000
    depth = 1000
    test_config['parameters']['num_of_codes'] = depth

    #Create Package Generator Object 
    generic_packager   = Packager(package_name='constant', parameter_dict=system_config['generic']['parameters'], path=pack_dir)
    testbench_packager = Packager(package_name='test',     parameter_dict=test_config['parameters'], path=pack_dir)
    ffe_packager       = Packager(package_name='ffe',      parameter_dict=ffe_config['parameters'], path=pack_dir)
    cmp_packager       = Packager(package_name='cmp',      parameter_dict=cmp_config['parameters'], path=pack_dir)
    #Create package file from parameters specified in system.yaml under generic
    generic_packager.create_package()
    testbench_packager.create_package()
    ffe_packager.create_package()
    cmp_packager.create_package()

    #Create TestBench Object
    tester   = Tester(
                        top       = 'test',
                        testbench = ['verif/cmp/test_cmp.sv'],
                        libraries = ['src/fir/syn/ffe.sv', 'src/dig_comp/syn/comparator.sv' ,'verif/tb/beh/logic_recorder.sv'],
                        packages  = [generic_packager.path, testbench_packager.path, ffe_packager.path, cmp_packager.path],
                        flags     = ['-sv', '-64bit', '+libext+.v', '+libext+.sv', '+libext+.vp'],
                        build_dir = build_dir,
                        overload_seed=True,
                        wave=True
                    )

    # Cursor position with the most energy 
    pos = 2
    resp_len = 125

    ideal_codes = np.random.randint(2, size=iterations)*2 - 1

    chan = Channel(channel_type='skineffect', normal='area', tau=2, sampl_rate=5, cursor_pos=pos, resp_depth=resp_len)
    chan_out = chan(ideal_codes)

    #plot_adapt_input(ideal_codes, chan_out, 100)
    qc = Quantizer(width=ffe_config["parameters"]["input_precision"], signed=True)
    quantized_chan_out = qc.quantize_2s_comp(chan_out)

    weights = []
    if ffe_config["adaptation"]["type"] == "wiener":
        weights = perform_wiener(ideal_codes, chan, chan_out, ffe_config['parameters']["length"], \
            ffe_config["adaptation"]["args"]["mu"], pos, iterations, build_dir=build_dir)
    else: 
        print(f'Do Nothing')

    check_bits = 300
    quantized_chan_out_t = quantized_chan_out[check_bits:check_bits+depth]

    print(f'Quantized Chan: {quantized_chan_out}')
    print(f'Chan: {chan_out}')
    qw = Quantizer(width=ffe_config["parameters"]["weight_precision"], signed=True)
    quantized_weights = qw.quantize_2s_comp(weights)
    print(f'Weights: {weights}')
    print(f'Quantized Weights: {quantized_weights}')
    write_files([depth, ffe_config['parameters']["length"], ffe_config["adaptation"]["args"]["mu"]], quantized_chan_out_t, quantized_weights, 'verif/cmp/build_cmp')   
         
    #Execute TestBench Object
    tester.run()
    
    Packager.delete_pack_dir(path=pack_dir)

    #Execute ideal python FIR 
    py_arr = execute_fir(ffe_config, quantized_weights, depth, quantized_chan_out_t)

    # Plot a window of the ideal vs ffe output
    plot_comparison(py_arr, ideal_codes, length=150, scale=50, delay_ffe=pos, delay_ideal=check_bits)
    # Histogram Plot
    plot_histogram(py_arr, ideal_codes, delay_ffe=pos, delay_ideal=check_bits, save_dir=build_dir) 
    
    py_arr = np.array([1 if int(np.floor(py_val)) >= 0 else 0 for py_val in py_arr])

    # Read in the SV results file
    sv_arr = read_svfile('verif/cmp/build_cmp/cmp_results.txt')
    # Compare
    sv_trim = (3+ffe_config['parameters']["length"]) * ffe_config["parameters"]["width"] - (ffe_config["parameters"]["length"]-1)
    # This trim needs to be fixed - I think the current approach is ""hacky""
    comp_len = math.floor((depth - ffe_config["parameters"]["length"] + 1) \
        /ffe_config["parameters"]["width"]) * ffe_config["parameters"]["width"]

    # Print ideal codes
    ideal_in = ideal_codes[pos:pos+check_bits]
    print(f'Ideal Codes: {ideal_in}')

    # Comparison
    result = compare(py_arr, sv_arr, sv_trim, check_bits, True)
    if result:
        print('TEST PASSED')
    else: 
        print('TEST FAILED')
    assert(result)


# Used for testing 
if __name__ == "__main__":
    main()