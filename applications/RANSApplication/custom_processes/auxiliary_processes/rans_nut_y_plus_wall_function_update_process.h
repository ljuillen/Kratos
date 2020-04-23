//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:		 BSD License
//					 Kratos default license: kratos/license.txt
//
//  Main authors:    Suneth Warnakulasuriya (https://github.com/sunethwarna)
//

#if !defined(KRATOS_RANS_NUT_Y_PLUS_WALL_FUNCTION_UPDATE_PROCESS_H_INCLUDED)
#define KRATOS_RANS_NUT_Y_PLUS_WALL_FUNCTION_UPDATE_PROCESS_H_INCLUDED

// System includes
#include <string>

// External includes

// Project includes
#include "containers/model.h"
#include "processes/process.h"

namespace Kratos
{
///@addtogroup RANSApplication
///@{

///@name Kratos Globals
///@{

///@}
///@name Type Definitions
///@{

///@}
///@name  Enum's
///@{

///@}
///@name  Functions
///@{

///@}
///@name Kratos Classes
///@{

class KRATOS_API(RANS_APPLICATION) RansNutYPlusWallFunctionUpdateProcess : public Process
{
public:
    ///@name Type Definitions
    ///@{

    using NodeType = ModelPart::NodeType;
    using ConditionType = ModelPart::ConditionType;
    using ConditionGeometryType = ModelPart::ConditionType::GeometryType;

    /// Pointer definition of RansNutYPlusWallFunctionUpdateProcess
    KRATOS_CLASS_POINTER_DEFINITION(RansNutYPlusWallFunctionUpdateProcess);

    ///@}
    ///@name Life Cycle
    ///@{

    /// Constructor

    RansNutYPlusWallFunctionUpdateProcess(Model& rModel, Parameters rParameters);

    RansNutYPlusWallFunctionUpdateProcess(Model& rModel,
                                          const std::string& rModelPartName,
                                          const double Cmu,
                                          const double VonKarman,
                                          const double Beta,
                                          const double MinValue,
                                          const int EchoLevel);

    /// Destructor.
    ~RansNutYPlusWallFunctionUpdateProcess() override = default;

    ///@}
    ///@name Operators
    ///@{

    ///@}
    ///@name Operations
    ///@{

    int Check() override;

    void ExecuteInitialize() override;

    void ExecuteInitializeSolutionStep() override;

    void Execute() override;

    ///@}
    ///@name Access
    ///@{

    ///@}
    ///@name Inquiry
    ///@{

    ///@}
    ///@name Input and output
    ///@{

    /// Turn back information as a string.
    std::string Info() const override;

    /// Print information about this object.
    void PrintInfo(std::ostream& rOStream) const override;

    /// Print object's data.
    void PrintData(std::ostream& rOStream) const override;

    ///@}
    ///@name Friends
    ///@{

    ///@}

protected:
    ///@name Protected static Member Variables
    ///@{

    ///@}
    ///@name Protected member Variables
    ///@{

    ///@}
    ///@name Protected Operators
    ///@{

    ///@}
    ///@name Protected Operations
    ///@{

    ///@}
    ///@name Protected  Access
    ///@{

    ///@}
    ///@name Protected Inquiry
    ///@{

    ///@}
    ///@name Protected LifeCycle
    ///@{

    ///@}

private:
    ///@name Static Member Variables
    ///@{

    ///@}
    ///@name Member Variables
    ///@{

    Model& mrModel;
    std::string mModelPartName;
    double mCmu;
    double mVonKarman;
    double mBeta;
    double mMinValue;
    int mEchoLevel;
    bool mIsInitialized = false;

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

    void CalculateConditionNeighbourCount();

    ///@}
    ///@name Private  Access
    ///@{

    ///@}
    ///@name Private Inquiry
    ///@{

    ///@}
    ///@name Un accessible methods
    ///@{

    /// Assignment operator.
    RansNutYPlusWallFunctionUpdateProcess& operator=(RansNutYPlusWallFunctionUpdateProcess const& rOther);

    /// Copy constructor.
    RansNutYPlusWallFunctionUpdateProcess(RansNutYPlusWallFunctionUpdateProcess const& rOther);

    ///@}

}; // Class RansNutYPlusWallFunctionUpdateProcess

///@}

///@name Type Definitions
///@{

///@}
///@name Input and output
///@{

/// output stream function
inline std::ostream& operator<<(std::ostream& rOStream,
                                const RansNutYPlusWallFunctionUpdateProcess& rThis);

///@}

///@} addtogroup block

} // namespace Kratos.

#endif // KRATOS_RANS_NUT_Y_PLUS_WALL_FUNCTION_UPDATE_PROCESS_H_INCLUDED defined