import os
from KratosMultiphysics import *
import KratosMultiphysics.KratosUnittest as KratosUnittest
import test_MainKratosMPI

class ControlledExecutionScope:
    def __init__(self, scope):
        self.currentPath = os.getcwd()
        self.scope = scope

    def __enter__(self):
        os.chdir(self.scope)

    def __exit__(self, type, value, traceback):
        os.chdir(self.currentPath)

class TestCase(KratosUnittest.TestCase):

    def setUp(self):
        pass

    def createTest(self, parameter_file_name):
        with open(parameter_file_name + '_parameters.json', 'r') as parameter_file:
            project_parameters = Parameters(parameter_file.read())
            parameter_file.close()
        test = test_MainKratosMPI.MainKratos(project_parameters)
        return test

    def solve(self, parameter_file_name):
        test = self.createTest(parameter_file_name)
        test.Solve()

    def test_Cylinder(self):
        with ControlledExecutionScope(os.path.dirname(os.path.realpath(__file__))):
            # solve fluid
            self.solve('test_vms_sensitivity_2d/mpi_cylinder_test')
            # solve adjoint
            test = self.createTest('test_vms_sensitivity_2d/mpi_cylinder_test_adjoint')
            test.Solve()
            #Sensitivity = [[]]
            #Sensitivity[0].append(test.main_model_part.GetNode(1968).GetSolutionStepValue(SHAPE_SENSITIVITY_X))
            #Sensitivity[0].append(test.main_model_part.GetNode(1968).GetSolutionStepValue(SHAPE_SENSITIVITY_Y))


    def tearDown(self):
        pass

if __name__ == '__main__':
    KratosUnittest.main()
