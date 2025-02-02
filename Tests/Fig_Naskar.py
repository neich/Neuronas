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
import matplotlib.pyplot as plt

# ============== models
import WholeBrain.Models.Naskar as Naskar
import WholeBrain.Models.DynamicMeanField as DMF #Para graficar la curva sin FIC

# ============== chose and setup an integrator
import WholeBrain.Integrators.Euler as scheme
scheme.sigma = 0.001
import WholeBrain.Integrators.Integrator as integrator
integrator.integrationScheme = scheme
integrator.verbose = False

# ============== FIC mechanism
import WholeBrain.Utils.FIC.Balance_Herzog2022 as Herzog2022Mechanism
import WholeBrain.Utils.FIC.BalanceFIC as BalanceFIC
BalanceFIC.integrator = integrator


np.random.seed(42)  # Fix the seed for debug purposes...

def plotMaxFrecForAllWe(C, wStart=0, wEnd=6+0.001, wStep=0.05,
                        extraTitle='', precompute=True, fileName=None):
    # Integration parms...
    dt = 0.1
    tmax = 9 * 60 * 1000.
    Tmaxneuronal = int((tmax+dt))
    # all tested global couplings (G in the paper):
    wes = np.arange(wStart, wEnd, wStep)  # warning: the range of wes depends on the conectome.
    N = C.shape[0]

    ########### Para graficar la curva sin FIC
    # Integration parms...
    integrator.neuronalModel = DMF
    scheme.neuronalModel = DMF
    DMF.setParms({'SC': C})
    DMF.couplingOp.setParms(C)
    BalanceFIC.balancingMechanism = Herzog2022Mechanism

    print("======================================")
    print("=    simulating E-E (no FIC)         =")
    print("======================================")
    maxRateNoFIC = np.zeros(len(wes))
    DMF.setParms({'J': np.ones(N)})  # E-E = Excitatory-Excitatory, no FIC...
    for kk, we in enumerate(wes):  # iterate over the weight range (G in the paper, we here)
        print("Processing: {}".format(we), end='')
        DMF.setParms({'we': we})
        integrator.recompileSignatures()
        v = integrator.warmUpAndSimulate(dt, Tmaxneuronal, TWarmUp=60 * 1000)[:, 1,
            :]  # [1] is the output from the excitatory pool, in Hz.
        maxRateNoFIC[kk] = np.max(np.mean(v, 0))
        print(" => {}".format(maxRateNoFIC[kk]))
    ee, = plt.plot(wes, maxRateNoFIC)
    ee.set_label("E-E")

    integrator.neuronalModel = Naskar
    scheme.neuronalModel = Naskar
    Naskar.setParms({'SC': C})
    Naskar.couplingOp.setParms(C)

    print("======================================")
    print("=    simulating Naskar               =")
    print("======================================")
    maxRateFIC = np.zeros(len(wes))
    for kk, we in enumerate(wes):  # iterate over the weight range (G in the paper, we here)
        print("\nProcessing: {}  ".format(we), end='')
        Naskar.setParms({'G': we})
        #integrator.recompileSignatures()
        v = integrator.warmUpAndSimulate(dt, Tmaxneuronal, TWarmUp=60*1000)[:,1,:]  # [1] is the output from the excitatory pool, in Hz.
        maxRateFIC[kk] = np.max(np.mean(v, axis=0))  # the original code from [DecoEtAl_2014]
        #maxRateFIC[kk] = np.mean(np.max(v, axis=0))  # this is what is implemented in the code [NaskarEtAl_2018].
        print("maxRateFIC => {}".format(maxRateFIC[kk]))
    fic, = plt.plot(wes, maxRateFIC)
    fic.set_label("MDMF")


    plt.title("Large-scale network (MDMF)" + extraTitle)
    plt.ylabel("Maximum rate (Hz)")
    plt.xlabel("Global Coupling (G = we)")
    plt.legend()
    plt.show()


# ==========================================================================
# ==========================================================================
# ========================================================================== --EOF