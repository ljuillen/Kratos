//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:		 BSD License
//					 Kratos default license: kratos/license.txt
//
//  Main authors:    Vicente Mataix Ferrandiz
//

// System includes

// External includes

// Project includes
#include "includes/define.h"
#include "factories/base_factory.h"
#include "factories/standard_convergence_criteria_factory.h"
#include "spaces/ublas_space.h"

// Convergence criterias
#include "solving_strategies/convergencecriterias/convergence_criteria.h"
#include "solving_strategies/convergencecriterias/displacement_criteria.h"
#include "solving_strategies/convergencecriterias/residual_criteria.h"
#include "solving_strategies/convergencecriterias/and_criteria.h"
#include "solving_strategies/convergencecriterias/or_criteria.h"

namespace Kratos
{
    void RegisterConvergenceCriterias()
    {
        typedef TUblasSparseSpace<double> SpaceType;
        typedef TUblasDenseSpace<double> LocalSpaceType;

        typedef DisplacementCriteria<SpaceType,  LocalSpaceType> DisplacementCriteriaType;
        typedef ResidualCriteria<SpaceType,  LocalSpaceType> ResidualCriteriaType;
        typedef And_Criteria<SpaceType,  LocalSpaceType> And_CriteriaType;
        typedef Or_Criteria<SpaceType,  LocalSpaceType> Or_CriteriaType;

        //NOTE: here we must create persisting objects for the linear solvers
        static DisplacementCriteriaType msDisplacementCriteria;
        static ResidualCriteriaType msResidualCriteria;
        static And_CriteriaType msAnd_Criteria;
        static Or_CriteriaType msOr_Criteria;

        // Registration of convergence solvers
        KRATOS_REGISTER_CONVERGENCE_CRITERIA(DisplacementCriteriaType::Name(), msDisplacementCriteria);
        KRATOS_REGISTER_CONVERGENCE_CRITERIA(ResidualCriteriaType::Name(), msResidualCriteria);
        KRATOS_REGISTER_CONVERGENCE_CRITERIA(And_CriteriaType::Name(), msAnd_Criteria );
        KRATOS_REGISTER_CONVERGENCE_CRITERIA(Or_CriteriaType::Name(), msOr_Criteria );
    };
} // Namespace Kratos
