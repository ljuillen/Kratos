from KratosMultiphysics import *
import KratosMultiphysics.ConvectionDiffusionApplication
from KratosMultiphysics.ConvectionDiffusionApplication.convection_diffusion_analysis import ConvectionDiffusionAnalysis
import KratosMultiphysics.KratosUnittest as KratosUnittest

from math import *

class TestSymbolicEulerianConvectionDiffusionElement(KratosUnittest.TestCase):

    def testSymbolicEulerianConvectionDiffusionElementUnsteadyDOSS(self):
        project_parameters_file_name = "test_symbolic_eulerian_convection_diffusion_explicit_element/project_parameters_bar_DOSS.json"
        with open(project_parameters_file_name,'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())
        model = KratosMultiphysics.Model()
        bar_simulation = ConvectionDiffusionAnalysis(model, parameters)
        bar_simulation._GetSolver().main_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_AREA)
        bar_simulation.Run()
        # check L2 error via midpoint rule
        KratosMultiphysics.CalculateNodalAreaProcess(bar_simulation._GetSolver().main_model_part,2).Execute()
        error = 0
        model_part_name = bar_simulation.project_parameters["problem_data"]["model_part_name"].GetString()
        for node in bar_simulation.model.GetModelPart(model_part_name).Nodes:
            # L2 norm
            x = node.X
            y = node.Y
            u_analytical = x - sin(bar_simulation.time)
            u_numerical = node.GetSolutionStepValue(KratosMultiphysics.TEMPERATURE)
            error = error + (((u_analytical - u_numerical)**2)*node.GetSolutionStepValue(KratosMultiphysics.NODAL_AREA))
        error = sqrt(error)
        self.assertEqual(error,0.0017678016487473033)

    def testSymbolicEulerianConvectionDiffusionElementUnsteadyQOSS(self):
        project_parameters_file_name = "test_symbolic_eulerian_convection_diffusion_explicit_element/project_parameters_bar_QOSS.json"
        with open(project_parameters_file_name,'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())
        model = KratosMultiphysics.Model()
        bar_simulation = ConvectionDiffusionAnalysis(model, parameters)
        bar_simulation._GetSolver().main_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_AREA)
        bar_simulation.Run()
        # check L2 error via midpoint rule
        KratosMultiphysics.CalculateNodalAreaProcess(bar_simulation._GetSolver().main_model_part,2).Execute()
        error = 0
        model_part_name = bar_simulation.project_parameters["problem_data"]["model_part_name"].GetString()
        for node in bar_simulation.model.GetModelPart(model_part_name).Nodes:
            # L2 norm
            x = node.X
            y = node.Y
            u_analytical = x - sin(bar_simulation.time)
            u_numerical = node.GetSolutionStepValue(KratosMultiphysics.TEMPERATURE)
            error = error + (((u_analytical - u_numerical)**2)*node.GetSolutionStepValue(KratosMultiphysics.NODAL_AREA))
        error = sqrt(error)
        self.assertEqual(error,0.0017678016487243965)

    def testSymbolicEulerianConvectionDiffusionElementUnsteadyDASGS(self):
        project_parameters_file_name = "test_symbolic_eulerian_convection_diffusion_explicit_element/project_parameters_bar_DASGS.json"
        with open(project_parameters_file_name,'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())
        model = KratosMultiphysics.Model()
        bar_simulation = ConvectionDiffusionAnalysis(model, parameters)
        bar_simulation._GetSolver().main_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_AREA)
        bar_simulation.Run()
        # check L2 error via midpoint rule
        KratosMultiphysics.CalculateNodalAreaProcess(bar_simulation._GetSolver().main_model_part,2).Execute()
        error = 0
        model_part_name = bar_simulation.project_parameters["problem_data"]["model_part_name"].GetString()
        for node in bar_simulation.model.GetModelPart(model_part_name).Nodes:
            # L2 norm
            x = node.X
            y = node.Y
            u_analytical = x - sin(bar_simulation.time)
            u_numerical = node.GetSolutionStepValue(KratosMultiphysics.TEMPERATURE)
            error = error + (((u_analytical - u_numerical)**2)*node.GetSolutionStepValue(KratosMultiphysics.NODAL_AREA))
        error = sqrt(error)
        self.assertEqual(error,0.038797177945129026)

    def testSymbolicEulerianConvectionDiffusionElementUnsteadyQASGS(self):
        project_parameters_file_name = "test_symbolic_eulerian_convection_diffusion_explicit_element/project_parameters_bar_QASGS.json"
        with open(project_parameters_file_name,'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())
        model = KratosMultiphysics.Model()
        bar_simulation = ConvectionDiffusionAnalysis(model, parameters)
        bar_simulation._GetSolver().main_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_AREA)
        bar_simulation.Run()
        # check L2 error via midpoint rule
        KratosMultiphysics.CalculateNodalAreaProcess(bar_simulation._GetSolver().main_model_part,2).Execute()
        error = 0
        model_part_name = bar_simulation.project_parameters["problem_data"]["model_part_name"].GetString()
        for node in bar_simulation.model.GetModelPart(model_part_name).Nodes:
            # L2 norm
            x = node.X
            y = node.Y
            u_analytical = x - sin(bar_simulation.time)
            u_numerical = node.GetSolutionStepValue(KratosMultiphysics.TEMPERATURE)
            error = error + (((u_analytical - u_numerical)**2)*node.GetSolutionStepValue(KratosMultiphysics.NODAL_AREA))
        error = sqrt(error)
        self.assertEqual(error,0.17200571595025685)

    def testSymbolicEulerianConvectionDiffusionElementSteadyQASGS(self):
        project_parameters_file_name = "test_symbolic_eulerian_convection_diffusion_explicit_element/project_parameters_steady_state_explicit_solution_QASGS.json"
        with open(project_parameters_file_name,'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())
        model = KratosMultiphysics.Model()
        bar_simulation = ConvectionDiffusionAnalysis(model, parameters)
        bar_simulation._GetSolver().main_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_AREA)
        bar_simulation.Run()
        # check L2 error via midpoint rule
        KratosMultiphysics.CalculateNodalAreaProcess(bar_simulation._GetSolver().main_model_part,2).Execute()
        error = 0
        model_part_name = bar_simulation.project_parameters["problem_data"]["model_part_name"].GetString()
        for node in bar_simulation.model.GetModelPart(model_part_name).Nodes:
            # L2 norm
            x = node.X
            y = node.Y
            u_analytical = x - sin(bar_simulation.time)
            u_numerical = node.GetSolutionStepValue(KratosMultiphysics.TEMPERATURE)
            error = error + (((u_analytical - u_numerical)**2)*node.GetSolutionStepValue(KratosMultiphysics.NODAL_AREA))
        error = sqrt(error)
        self.assertAlmostEqual(error,0.5056562564233146,delta=1e-12)

    def testSymbolicEulerianConvectionDiffusionElementSteadyQOSS(self):
        project_parameters_file_name = "test_symbolic_eulerian_convection_diffusion_explicit_element/project_parameters_steady_state_explicit_solution_QOSS.json"
        with open(project_parameters_file_name,'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())
        model = KratosMultiphysics.Model()
        bar_simulation = ConvectionDiffusionAnalysis(model, parameters)
        bar_simulation._GetSolver().main_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.NODAL_AREA)
        bar_simulation.Run()
        # check L2 error via midpoint rule
        KratosMultiphysics.CalculateNodalAreaProcess(bar_simulation._GetSolver().main_model_part,2).Execute()
        error = 0
        model_part_name = bar_simulation.project_parameters["problem_data"]["model_part_name"].GetString()
        for node in bar_simulation.model.GetModelPart(model_part_name).Nodes:
            # L2 norm
            x = node.X
            y = node.Y
            u_analytical = x - sin(bar_simulation.time)
            u_numerical = node.GetSolutionStepValue(KratosMultiphysics.TEMPERATURE)
            error = error + (((u_analytical - u_numerical)**2)*node.GetSolutionStepValue(KratosMultiphysics.NODAL_AREA))
        error = sqrt(error)
        self.assertAlmostEqual(error,0.5056562564233146,delta=1e-12)

if __name__ == '__main__':
    KratosUnittest.main()