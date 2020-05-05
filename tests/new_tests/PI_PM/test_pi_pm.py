# general imports
import os
import numpy as np
import matplotlib.pyplot as plt
import pytest
from pathlib import Path
from sklearn import linear_model

# DragonPHY imports
from dragonphy import *

THIS_DIR = Path(__file__).parent.resolve()
BUILD_DIR = THIS_DIR / 'build'
if 'FPGA_SERVER' in os.environ:
    SIMULATOR = 'vivado'
else:
    SIMULATOR = 'ncsim'

# testing parameters
T_PER = 1/4e9
INL_LIM = 10e-12
GAIN_MIN = -1.9e-12
GAIN_MAX = -0.2e-12
MONOTONIC_LIM = -0.01e-12
RES_LIM = 3.5e-12
SIGN_FLIP = 125

# Set DUMP_WAVEFORMS to True if you want to dump all waveforms for this
# test.  The waveforms are stored in tests/new_tests/PI_PM/build/waves.shm
DUMP_WAVEFORMS = False

@pytest.mark.parametrize((), [pytest.param(marks=pytest.mark.slow) if SIMULATOR=='vivado' else ()])
def test_sim():
    deps = get_deps_cpu_sim_new(impl_file=THIS_DIR / 'test.sv')
    print(deps)

    def qwrap(s):
        return f'"{s}"'

    defines = {
        'PI_CTL_TXT': qwrap(BUILD_DIR / 'pi_ctl.txt'),
        'DELAY_TXT': qwrap(BUILD_DIR / 'delay.txt'),
        'SIGN_FLIP': SIGN_FLIP,
        'DAVE_TIMEUNIT': '1fs',
        'NCVLOG': None
    }

    flags = ['-unbuffered']
    if DUMP_WAVEFORMS:
        defines['DUMP_WAVEFORMS'] = None
        flags += ['-access', '+r']

    DragonTester(
        ext_srcs=deps,
        directory=BUILD_DIR,
        top_module='test',
        inc_dirs=[get_mlingua_dir() / 'samples', get_dir('inc/new_cpu')],
        defines=defines,
        simulator=SIMULATOR,
        flags=flags
    ).run()

    # read data from file
    pi_ctl = np.loadtxt(BUILD_DIR / 'pi_ctl.txt', dtype=int, delimiter=',')
    delay = np.loadtxt(BUILD_DIR / 'delay.txt', dtype=float, delimiter=',')

    # sort each column increasing order of pi_ctl codes
    for k in range(delay.shape[1]):
        idx_arr = pi_ctl[:, k].argsort()
        pi_ctl[:, k] = pi_ctl[idx_arr, k]
        delay[:, k] = delay[idx_arr, k]

    # correct phase measurement based on the sign
    # TODO: make this more robust
    for k in range(delay.shape[1]):
       delay[:, k] -= (T_PER/2)*(pi_ctl[:, k] >= SIGN_FLIP)

    # unwrap phase
    delay_unwrapped = np.zeros(delay.shape, dtype=float)
    for k in range(delay.shape[1]):
        # get original delay values
        delay_unwrapped[:, k] = delay[:, k]
        # convert to phase
        scale_factor = 2*np.pi/T_PER
        delay_unwrapped[:, k] *= scale_factor
        # unwrap with built-in function
        delay_unwrapped[:, k] = np.unwrap(delay_unwrapped[:, k])
        # convert back to time
        delay_unwrapped[:, k] /= scale_factor

    # plot results
    plot_data(pi_ctl, delay_unwrapped)

    # check each PI
    for k in range(pi_ctl.shape[1]):
        print(f'Checking PI #{k}...')
        check_pi(pi_ctl[:, k], delay_unwrapped[:, k])
        if k != (pi_ctl.shape[1]-1):
            print('')

def plot_data(pi_ctl, delay):
    fig = plt.figure(figsize=(10, 9))
    Nout = pi_ctl.shape[1]

    for k in range(Nout):
        ax = fig.add_subplot(Nout, 1, k+1)
        ax.plot(pi_ctl[:, k], 1e12*delay[:, k], '*')
        ax.set_title(f'PI Output #{k}')
        ax.set_xlabel('PI Code')
        ax.set_ylabel('Delay (ps)')

    fig.subplots_adjust(hspace=0.5)
    plt.tight_layout()

    plt.savefig(BUILD_DIR / 'pi.eps')

def check_pi(x, y):
    # create linear regression
    regr = linear_model.LinearRegression()
    regr.fit(x[:, np.newaxis], y)
    y_fit = regr.predict(x[:, np.newaxis])

    # INL
    inl = np.max(np.abs(y - y_fit))
    print(f'INL: {inl * 1e12:0.3f} ps.')

    # gain
    gain = regr.coef_[0]
    print(f'Gain: {gain * 1e12:0.3f} ps/LSB')

    # check results
    assert inl <= INL_LIM, \
        f'INL out of spec.  Worst-case code: {np.argmax(np.abs(y - y_fit))}.'
    assert GAIN_MIN <= gain <= GAIN_MAX, f'Gain out of spec.'