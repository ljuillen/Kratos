from KratosMultiphysics import *
from KratosMultiphysics.RANSModellingApplication import *
from KratosMultiphysics.FluidDynamicsApplication import *

def run():
    Tester.SetVerbosity(Tester.Verbosity.FAILED_TESTS_OUTPUTS) # TESTS_OUTPUTS
    Tester.RunTestSuite("RANSYPlusModelSensitivities")
    Tester.RunTestSuite("RANSEvModelsKEpsilonNodalMatrices")
    Tester.RunTestSuite("RANSEvModelsKEpsilonGaussMatrices")
    Tester.RunTestSuite("RANSEvModelsKEpsilonElementResidualMatrices")
    # Tester.RunTestSuite("RANSEvModelsKEpsilonElementMethods")

if __name__ == '__main__':
    run()