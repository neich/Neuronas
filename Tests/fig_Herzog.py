# ================================================================================================================
#
# This prog. plots the max frec for varying global couplings (G)
#
# see:
# [D*2014]  Deco et al. (2014) J Neurosci.
#           http://www.jneurosci.org/content/34/23/7886.long
#
# By Gustavo Patow
#
# Optimized by Facundo Faragó
# ================================================================================================================

# ============== import libraries
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import multiprocessing
from tqdm import tqdm

# ============== chose a model
import WholeBrain.Models.DynamicMeanField as DMF

# ============== chose and setup an integrator
import WholeBrain.Integrators.EulerMaruyama as scheme
scheme.neuronalModel = DMF
import WholeBrain.Integrators.Integrator as integrator
integrator.integrationScheme = scheme
integrator.neuronalModel = DMF
integrator.verbose = False

# ============== chose a FIC mechanism
import WholeBrain.Utils.FIC.BalanceFIC as BalanceFIC
BalanceFIC.integrator = integrator
import WholeBrain.Utils.FIC.Balance_Herzog2022 as Herzog2022Mechanism
BalanceFIC.balancingMechanism = Herzog2022Mechanism  # default behaviour for this project


def plotMaxFrecForAllWe(C, wStart=0, wEnd=6 + 0.001, wStep=0.05,
                        extraTitle='', precompute=True, fileName=None):

    # Integration parms...
    dt = 0.1
    tmax = 10000.
    Tmaxneuronal = int((tmax + dt))
    # all tested global couplings (G in the paper):
    wes = np.arange(wStart, wEnd, wStep)  # warning: the range of wes depends on the conectome.
    # wes = np.arange(2.0, 2.11, 0.1)  # only for debug purposes...
    # numW = wes.size  # length(wes);
    N = C.shape[0]

    DMF.setParms({'SC': C})
    DMF.couplingOp.setParms(C)

    print("======================================")
    print("=    simulating E-E (no FIC)         =")
    print("======================================")
    maxRateNoFIC = np.zeros(len(wes))
    DMF.setParms({'J': np.ones(N)})  # E-E = Excitatory-Excitatory, no FIC...
    for kk, we in enumerate(wes):  # iterate over the weight range (G in the paper, we here)
        print("Processing: {}".format(we), end='')
        DMF.setParms({'we': we})
        # integrator.recompileSignatures()
        v = integrator.simulate(dt, Tmaxneuronal)[:, 1, :]  # [1] is the output from the excitatory pool, in Hz.
        maxRateNoFIC[kk] = np.max(np.mean(v, 0))
        print(" => {}".format(maxRateNoFIC[kk]))
    ee, = plt.plot(wes, maxRateNoFIC)
    ee.set_label("E-E")

    print("======================================")
    print("=    simulating FIC                  =")
    print("======================================")
    # DMF.lambda = 0.  # make sure no long-range feedforward inhibition (FFI) is computed
    maxRateFIC = np.zeros(len(wes))
    if precompute:
        BalanceFIC.Balance_AllJ9(C, wes, baseName=fileName)
    for kk, we in enumerate(wes):  # iterate over the weight range (G in the paper, we here)
        print("\nProcessing: {}  ".format(we), end='')
        DMF.setParms({'we': we})
        balancedJ = BalanceFIC.Balance_J9(we, C, fileName.format(np.round(we, decimals=2)))['J'].flatten()
        integrator.neuronalModel.setParms({'J': balancedJ})
        # integrator.recompileSignatures()
        v = integrator.simulate(dt, Tmaxneuronal)[:, 1, :]  # [1] is the output from the excitatory pool, in Hz.
        maxRateFIC[kk] = np.max(np.mean(v, 0))
        print("maxRateFIC => {}".format(maxRateFIC[kk]))
    fic, = plt.plot(wes, maxRateFIC)
    fic.set_label("FDMF")

    # for line, color in zip([1.47, 4.45], ['r', 'b']):
    #     plt.axvline(x=line, label='line at x = {}'.format(line), c=color)
    plt.title("Large-scale network (FDMF)" + extraTitle)
    plt.ylabel("Maximum rate (Hz)")
    plt.xlabel("Global Coupling (G = we)")
    plt.legend()
    plt.show()






















# ================================================================================================================
# ================================================================================================================
# ================================================================================================================EOF
