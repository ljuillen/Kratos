//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:		 BSD License
//					 Kratos default license: kratos/license.txt
//
//  Main authors:    Suneth Warnakulasuriya
//
//

// System includes
#include <functional>
#include <vector>

// External includes

// Project includes
#include "containers/model.h"
#include "testing/testing.h"

// Application includes
#include "custom_elements/evm_k_epsilon/evm_k_epsilon_adjoint_utilities.h"
#include "custom_processes/auxiliary_processes/rans_logarithmic_y_plus_calculation_process.h"
#include "custom_processes/auxiliary_processes/rans_logarithmic_y_plus_velocity_sensitivities_process.h"
#include "custom_utilities/rans_calculation_utilities.h"
#include "test_k_epsilon_utilities.h"
#include "custom_utilities/test_utilities.h"

namespace Kratos
{
namespace Testing
{
KRATOS_TEST_CASE_IN_SUITE(RansEvmKEpsilonGaussTKESensitivities, RANSEvModelsKEpsilonGaussMatrices)
{
    Model model;
    ModelPart& r_model_part = model.CreateModelPart("RansSensitivities");
    RansEvmKEpsilonModel::GenerateRansEvmKEpsilonTestModelPart(r_model_part,
                                                               "RANSEVMK2D3N");

    Parameters empty_parameters = Parameters(R"({
        "model_part_name" : "RansSensitivities"
    })");
    RansLogarithmicYPlusCalculationProcess y_plus_model_process(model, empty_parameters);

    auto perturb_variable = [](NodeType& rNode) -> double& {
        return rNode.FastGetSolutionStepValue(TURBULENT_KINETIC_ENERGY);
    };

    auto calculate_sensitivities = [](std::vector<Vector>& rValues,
                                      const ElementType& rElement,
                                      const Vector& rGaussShapeFunctions,
                                      const Matrix& rGaussShapeFunctionDerivatives,
                                      const ProcessInfo& rCurrentProcessInfo) {
        RansCalculationUtilities rans_calculation_utilities;

        const double c_mu = rCurrentProcessInfo[TURBULENCE_RANS_C_MU];

        const GeometryType& r_geometry = rElement.GetGeometry();
        const int number_of_nodes = r_geometry.PointsNumber();

        Vector nodal_y_plus(number_of_nodes);
        Vector nodal_tke(number_of_nodes);
        Vector nodal_epsilon(number_of_nodes);
        Vector nodal_nu_t(number_of_nodes);
        Vector nodal_f_mu(number_of_nodes);

        RansEvmKEpsilonModel::ReadNodalDataFromElement(
            nodal_y_plus, nodal_tke, nodal_epsilon, nodal_nu_t, nodal_f_mu, rElement);

        std::vector<double> primal_quantities;
        RansEvmKEpsilonModel::CalculatePrimalQuantities(
            primal_quantities, rElement, rGaussShapeFunctions,
            rGaussShapeFunctionDerivatives, rCurrentProcessInfo);

        const double nu_t = primal_quantities[0];
        const double Re_t = primal_quantities[3];
        const double f_mu = primal_quantities[5];
        const double nu = primal_quantities[6];
        const double epsilon = primal_quantities[7];
        const double tke = primal_quantities[8];

        Vector nodal_nu_t_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateNodalTurbulentViscosityTKESensitivities(
            nodal_nu_t_sensitivities, c_mu, nodal_tke, nodal_epsilon, nodal_f_mu);

        Vector gauss_nu_t_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateGaussSensitivities(
            gauss_nu_t_sensitivities, nodal_nu_t_sensitivities, rGaussShapeFunctions);

        BoundedMatrix<double, 2, 2> velocity_gradient_matrix;
        rans_calculation_utilities.CalculateGradient<2>(
            velocity_gradient_matrix, r_geometry, VELOCITY, rGaussShapeFunctionDerivatives);

        Vector gauss_production_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateProductionScalarSensitivities<2>(
            gauss_production_sensitivities, gauss_nu_t_sensitivities, velocity_gradient_matrix);

        Vector gauss_re_t_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateTurbulentReynoldsNumberTKESensitivity(
            gauss_re_t_sensitivities, tke, epsilon, nu, rGaussShapeFunctions);

        Vector gauss_theta_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateThetaTKESensitivity(
            gauss_theta_sensitivities, c_mu, f_mu, tke, nu_t,
            gauss_nu_t_sensitivities, rGaussShapeFunctions);

        Vector gauss_f2_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateF2ScalarSensitivity(
            gauss_f2_sensitivities, epsilon, Re_t, gauss_re_t_sensitivities);

        rValues.clear();
        rValues.push_back(gauss_nu_t_sensitivities);
        rValues.push_back(gauss_production_sensitivities);
        rValues.push_back(gauss_theta_sensitivities);
        rValues.push_back(gauss_re_t_sensitivities);
        rValues.push_back(gauss_f2_sensitivities);
    };

    RansModellingApplicationTestUtilities::RunGaussPointScalarSensitivityTest(
        r_model_part, y_plus_model_process,
        RansEvmKEpsilonModel::CalculatePrimalQuantities, calculate_sensitivities,
        RansEvmKEpsilonModel::UpdateVariablesInModelPartLowRe, perturb_variable, 1e-7, 1e-6);
}

KRATOS_TEST_CASE_IN_SUITE(RansEvmKEpsilonGaussEpsilonSensitivities, RANSEvModelsKEpsilonGaussMatrices)
{
    Model model;
    ModelPart& r_model_part = model.CreateModelPart("RansSensitivities");
    RansEvmKEpsilonModel::GenerateRansEvmKEpsilonTestModelPart(r_model_part,
                                                               "RANSEVMK2D3N");

    Parameters empty_parameters = Parameters(R"({
        "model_part_name" : "RansSensitivities"
    })");
    RansLogarithmicYPlusCalculationProcess y_plus_model_process(model, empty_parameters);

    auto perturb_variable = [](NodeType& rNode) -> double& {
        return rNode.FastGetSolutionStepValue(TURBULENT_ENERGY_DISSIPATION_RATE);
    };

    auto calculate_sensitivities = [](std::vector<Vector>& rValues,
                                      const ElementType& rElement,
                                      const Vector& rGaussShapeFunctions,
                                      const Matrix& rGaussShapeFunctionDerivatives,
                                      const ProcessInfo& rCurrentProcessInfo) {
        RansCalculationUtilities rans_calculation_utilities;

        const double c_mu = rCurrentProcessInfo[TURBULENCE_RANS_C_MU];

        const GeometryType& r_geometry = rElement.GetGeometry();
        const int number_of_nodes = r_geometry.PointsNumber();

        Vector nodal_y_plus(number_of_nodes);
        Vector nodal_tke(number_of_nodes);
        Vector nodal_epsilon(number_of_nodes);
        Vector nodal_nu_t(number_of_nodes);
        Vector nodal_f_mu(number_of_nodes);

        RansEvmKEpsilonModel::ReadNodalDataFromElement(
            nodal_y_plus, nodal_tke, nodal_epsilon, nodal_nu_t, nodal_f_mu, rElement);

        std::vector<double> primal_quantities;
        RansEvmKEpsilonModel::CalculatePrimalQuantities(
            primal_quantities, rElement, rGaussShapeFunctions,
            rGaussShapeFunctionDerivatives, rCurrentProcessInfo);

        const double nu_t = primal_quantities[0];
        const double Re_t = primal_quantities[3];
        const double f_mu = primal_quantities[5];
        const double nu = primal_quantities[6];
        const double epsilon = primal_quantities[7];
        const double tke = primal_quantities[8];

        Vector nodal_nu_t_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateNodalTurbulentViscosityEpsilonSensitivities(
            nodal_nu_t_sensitivities, c_mu, nodal_tke, nodal_epsilon, nodal_f_mu);

        Vector gauss_nu_t_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateGaussSensitivities(
            gauss_nu_t_sensitivities, nodal_nu_t_sensitivities, rGaussShapeFunctions);

        BoundedMatrix<double, 2, 2> velocity_gradient_matrix;
        rans_calculation_utilities.CalculateGradient<2>(
            velocity_gradient_matrix, r_geometry, VELOCITY, rGaussShapeFunctionDerivatives);

        Vector gauss_production_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateProductionScalarSensitivities<2>(
            gauss_production_sensitivities, gauss_nu_t_sensitivities, velocity_gradient_matrix);

        Vector gauss_theta_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateThetaEpsilonSensitivity(
            gauss_theta_sensitivities, c_mu, f_mu, tke, nu_t, gauss_nu_t_sensitivities);

        Vector gauss_re_t_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateTurbulentReynoldsNumberEpsilonSensitivity(
            gauss_re_t_sensitivities, tke, epsilon, nu, rGaussShapeFunctions);

        Vector gauss_f2_sensitivities(number_of_nodes);
        EvmKepsilonModelAdjointUtilities::CalculateF2ScalarSensitivity(
            gauss_f2_sensitivities, epsilon, Re_t, gauss_re_t_sensitivities);

        rValues.clear();
        rValues.push_back(gauss_nu_t_sensitivities);
        rValues.push_back(gauss_production_sensitivities);
        rValues.push_back(gauss_theta_sensitivities);
        rValues.push_back(gauss_re_t_sensitivities);
        rValues.push_back(gauss_f2_sensitivities);
    };

    RansModellingApplicationTestUtilities::RunGaussPointScalarSensitivityTest(
        r_model_part, y_plus_model_process,
        RansEvmKEpsilonModel::CalculatePrimalQuantities, calculate_sensitivities,
        RansEvmKEpsilonModel::UpdateVariablesInModelPartLowRe, perturb_variable, 1e-7, 3e-5);
}

KRATOS_TEST_CASE_IN_SUITE(RansEvmKEpsilonGaussVelocitySensitivities, RANSEvModelsKEpsilonGaussMatrices)
{
    Model model;
    ModelPart& r_model_part = model.CreateModelPart("RansSensitivities");
    RansEvmKEpsilonModel::GenerateRansEvmKEpsilonTestModelPart(r_model_part,
                                                               "RANSEVMK2D3N");

    Parameters empty_parameters = Parameters(R"({
        "model_part_name" : "RansSensitivities"
    })");
    RansLogarithmicYPlusVelocitySensitivitiesProcess y_plus_model_sensitivities_process(
        model, empty_parameters);
    RansLogarithmicYPlusCalculationProcess y_plus_model_process(model, empty_parameters);

    y_plus_model_process.Check();
    y_plus_model_process.Execute();

    y_plus_model_sensitivities_process.Check();
    y_plus_model_sensitivities_process.Execute();

    auto perturb_variable = [](NodeType& rNode, const int Dim) -> double& {
        array_1d<double, 3>& r_vector = rNode.FastGetSolutionStepValue(VELOCITY);
        return r_vector[Dim];
    };

    auto calculate_sensitivities = [](std::vector<Matrix>& rValues,
                                      const ElementType& rElement,
                                      const Vector& rGaussShapeFunctions,
                                      const Matrix& rGaussShapeFunctionDerivatives,
                                      const ProcessInfo& rCurrentProcessInfo) {
        RansCalculationUtilities rans_calculation_utilities;

        const double c_mu = rCurrentProcessInfo[TURBULENCE_RANS_C_MU];
        const int domain_size = rCurrentProcessInfo[DOMAIN_SIZE];

        const GeometryType& r_geometry = rElement.GetGeometry();
        const int number_of_nodes = r_geometry.PointsNumber();

        Vector nodal_y_plus(number_of_nodes);
        Vector nodal_tke(number_of_nodes);
        Vector nodal_epsilon(number_of_nodes);
        Vector nodal_nu_t(number_of_nodes);
        Vector nodal_f_mu(number_of_nodes);

        RansEvmKEpsilonModel::ReadNodalDataFromElement(
            nodal_y_plus, nodal_tke, nodal_epsilon, nodal_nu_t, nodal_f_mu, rElement);

        std::vector<double> primal_quantities;
        RansEvmKEpsilonModel::CalculatePrimalQuantities(
            primal_quantities, rElement, rGaussShapeFunctions,
            rGaussShapeFunctionDerivatives, rCurrentProcessInfo);

        const double nu_t = primal_quantities[0];
        const double f_mu = primal_quantities[5];
        const double tke = primal_quantities[8];
        const double y_plus = primal_quantities[9];

        BoundedMatrix<double, 2, 2> velocity_gradient_matrix;
        rans_calculation_utilities.CalculateGradient<2>(
            velocity_gradient_matrix, r_geometry, VELOCITY, rGaussShapeFunctionDerivatives);

        const Matrix& y_plus_sensitivities =
            rElement.GetValue(RANS_Y_PLUS_VELOCITY_DERIVATIVES);

        Matrix nodal_f_mu_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateNodalFmuVectorSensitivities(
            nodal_f_mu_sensitivities, nodal_y_plus, y_plus_sensitivities);

        Matrix nodal_nu_t_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateNodalTurbulentViscosityVectorSensitivities(
            nodal_nu_t_sensitivities, c_mu, nodal_tke, nodal_epsilon, nodal_f_mu_sensitivities);

        Matrix gauss_f_mu_velocity_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateGaussFmuVectorSensitivities(
            gauss_f_mu_velocity_sensitivities, y_plus, y_plus_sensitivities, rGaussShapeFunctions);

        Matrix gauss_nu_t_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateGaussSensitivities(
            gauss_nu_t_sensitivities, nodal_nu_t_sensitivities, rGaussShapeFunctions);

        Matrix gauss_y_plus_velocity_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateGaussSensitivities(
            gauss_y_plus_velocity_sensitivities, y_plus_sensitivities, rGaussShapeFunctions);

        Matrix gauss_production_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateProductionVelocitySensitivities<2>(
            gauss_production_sensitivities, nu_t, gauss_nu_t_sensitivities,
            velocity_gradient_matrix, rGaussShapeFunctionDerivatives);

        Matrix gauss_theta_sensitivities(number_of_nodes, domain_size);
        EvmKepsilonModelAdjointUtilities::CalculateThetaVelocitySensitivity(
            gauss_theta_sensitivities, c_mu, f_mu, tke, nu_t,
            gauss_f_mu_velocity_sensitivities, gauss_nu_t_sensitivities);

        // empty matrices to skip sensitivity check since they are always zero
        Matrix gauss_Re_t_sensitivities(0, 0);
        Matrix gauss_f2_sensitivities(0, 0);

        rValues.clear();
        rValues.push_back(gauss_nu_t_sensitivities);
        rValues.push_back(gauss_production_sensitivities);
        rValues.push_back(gauss_theta_sensitivities);
        rValues.push_back(gauss_Re_t_sensitivities);
        rValues.push_back(gauss_f2_sensitivities);
        rValues.push_back(gauss_f_mu_velocity_sensitivities);
    };

    RansModellingApplicationTestUtilities::RunGaussPointVectorSensitivityTest(
        r_model_part, y_plus_model_process,
        RansEvmKEpsilonModel::CalculatePrimalQuantities, calculate_sensitivities,
        RansEvmKEpsilonModel::UpdateVariablesInModelPartLowRe, perturb_variable, 1e-6, 1e-6);
}
} // namespace Testing
} // namespace Kratos