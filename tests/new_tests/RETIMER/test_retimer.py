# general imports
import os
import pytest
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from pathlib import Path

# DragonPHY imports
from dragonphy import *

THIS_DIR = Path(__file__).parent.resolve()
BUILD_DIR = THIS_DIR / 'build'
if 'FPGA_SERVER' in os.environ:
    SIMULATOR = 'vivado'
else:
    SIMULATOR = 'ncsim'

# Set DUMP_WAVEFORMS to True if you want to dump all waveforms for this
# test.  The waveforms are stored in tests/new_tests/DC/build/waves.shm
DUMP_WAVEFORMS = True

@pytest.mark.parametrize((), [pytest.param(marks=pytest.mark.slow) if SIMULATOR=='vivado' else ()])
def test_sim():
    deps = get_deps_cpu_sim_new(impl_file=THIS_DIR / 'test.sv')
    print(deps)

    def qwrap(s):
        return f'"{s}"'

    defines = {
        'OUT_TXT' : qwrap(BUILD_DIR / 'ti_adc.txt'),
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

    y = np.loadtxt(BUILD_DIR / 'ti_adc.txt', dtype=int, delimiter=',')
    y = y.flatten()

    y_ = np.arange(256)

    assert(np.sum(y-y_) == 0)

if __name__ == "__main__":
    test_sim()
