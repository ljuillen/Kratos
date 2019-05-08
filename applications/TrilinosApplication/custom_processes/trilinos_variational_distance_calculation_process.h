//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:		 BSD License
//					 Kratos default license: kratos/license.txt
//
//  Main authors:    Jordi Cotea
//                   Riccardo Rossi
//                   Ruben Zorrilla
//

#if !defined(KRATOS_TRILINOS_VARIATIONAL_DISTANCE_CALCULATION_PROCESS_INCLUDED )
#define  KRATOS_TRILINOS_VARIATIONAL_DISTANCE_CALCULATION_PROCESS_INCLUDED

// System includes

// External includes
#include "Epetra_MpiComm.h"

// Project includes
#include "custom_strategies/builder_and_solvers/trilinos_block_builder_and_solver.h"
#include "processes/variational_distance_calculation_process.h"
#include "solving_strategies/schemes/residualbased_incrementalupdate_static_scheme.h"

namespace Kratos
{

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

/// Short class definition.
/**takes a model part full of SIMPLICIAL ELEMENTS (triangles and tetras) and recomputes a signed distance function
mantaining as much as possible the position of the zero of the function prior to the call.

This is achieved by minimizing the function  ( 1 - norm( gradient( distance ) )**2
with the restriction that "distance" is a finite elment function
*/
template< unsigned int TDim, class TSparseSpace, class TDenseSpace, class TLinearSolver >
class TrilinosVariationalDistanceCalculationProcess
    : public VariationalDistanceCalculationProcess<TDim,TSparseSpace,TDenseSpace,TLinearSolver>
{
public:

    KRATOS_DEFINE_LOCAL_FLAG(CALCULATE_EXACT_DISTANCES_TO_PLANE);

    ///@name Type Definitions
    ///@{

    typedef VariationalDistanceCalculationProcess<TDim, TSparseSpace, TDenseSpace, TLinearSolver> BaseType;
    typedef typename TLinearSolver::Pointer LinearSolverPointerType;
    typedef typename BaseType::SchemeType::Pointer SchemePointerType;
    typedef typename BuilderAndSolver<TSparseSpace, TDenseSpace, TLinearSolver>::Pointer BuilderSolverPointerType;

    ///@}
    ///@name Pointer Definitions
    ///@{

    /// Pointer definition of TrilinosVariationalDistanceCalculationProcess
    KRATOS_CLASS_POINTER_DEFINITION(TrilinosVariationalDistanceCalculationProcess);

    ///@}
    ///@name Life Cycle
    ///@{

    TrilinosVariationalDistanceCalculationProcess(
        Epetra_MpiComm &rComm,
        ModelPart &base_model_part,
        LinearSolverPointerType plinear_solver,
        unsigned int max_iterations = 10,
        Flags Options = NOT_CALCULATE_EXACT_DISTANCES_TO_PLANE,
        std::string AuxPartName = "RedistanceCalculationPart" )
        : VariationalDistanceCalculationProcess<TDim, TSparseSpace, TDenseSpace, TLinearSolver>(base_model_part, max_iterations, Options, AuxPartName ),
        mrComm(rComm),
        mAuxModelPartName( AuxPartName )
    {

        KRATOS_TRY

        this->ValidateInput();

        // Generate an auxilary model part and populate it by elements of type DistanceCalculationElementSimplex
        this->ReGenerateDistanceModelPart(base_model_part);

        // Builder and Solver
        const int RowSizeGuess = (TDim == 2 ? 15 : 40);
        BuilderSolverPointerType pBuilderSolver = Kratos::make_shared<TrilinosBlockBuilderAndSolver<TSparseSpace, TDenseSpace, TLinearSolver > >(
            mrComm,
            RowSizeGuess,
            plinear_solver);

        this->InitializeSolutionStrategy(plinear_solver, pBuilderSolver);

        KRATOS_CATCH("")
    }

    /// Destructor.
    virtual ~TrilinosVariationalDistanceCalculationProcess() {};

    ///@}
    ///@name Operators
    ///@{

    ///@}base_model_part
    ///@nbase_model_part
    ///@{base_model_part

    ///@}base_model_part
    ///@name Input and output
    ///@{

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

    Epetra_MpiComm& mrComm;

    std::string mAuxModelPartName;

    ///@}
    ///@name Private Operators
    ///@{

    ///@}
    ///@name Private Operations
    ///@{

    void CommunicateBoundaryFlagToOwner(ModelPart& rModelPart)
    {
        int rank;
        MPI_Comm_rank(MPI_COMM_WORLD, &rank);

        int destination = 0;

        Communicator::NeighbourIndicesContainerType& neighbours_indices = rModelPart.GetCommunicator().NeighbourIndices();

        std::vector<int*> recv_buffers(neighbours_indices.size());
        std::vector<int>  recv_sizes(neighbours_indices.size());

        for (unsigned int i_color = 0; i_color < neighbours_indices.size(); i_color++)
            if ((destination = neighbours_indices[i_color]) >= 0)
            {
                Communicator::NodesContainerType& r_local_nodes = rModelPart.GetCommunicator().InterfaceMesh(i_color).Nodes();
                Communicator::NodesContainerType& r_ghost_nodes = rModelPart.GetCommunicator().InterfaceMesh(i_color).Nodes();

                unsigned int send_size = r_ghost_nodes.size();
                unsigned int recv_size = r_local_nodes.size();

                if ( (send_size == 0) && (recv_size == 0) )
                    continue; // Nothing to transfer

                int* send_buffer = new int[send_size];
                recv_buffers[i_color] = new int[recv_size];
                recv_sizes[i_color] = recv_size;

                // Fill the send buffer
                unsigned int i = 0;
                for (ModelPart::NodeIterator i_node = r_ghost_nodes.begin(); i_node != r_ghost_nodes.end(); ++i_node)
                {
                    send_buffer[i++] = i_node->Is(BOUNDARY); // bool to int! (should be safe)
                }

                if (i > send_size)
                    std::cout << rank << " Error in estimating send buffer size...." << std::endl;

                MPI_Status status;

                int send_tag = i_color;
                int receive_tag = i_color;

                MPI_Sendrecv(send_buffer, send_size, MPI_INT, destination, send_tag,
                             recv_buffers[i_color], recv_size, MPI_INT, destination, receive_tag,
                             MPI_COMM_WORLD, &status);

                delete [] send_buffer;
            }

        // Write in nodes
        for (unsigned int i_color = 0; i_color < neighbours_indices.size(); i_color++)
            if ((destination = neighbours_indices[i_color]) >= 0)
            {
                Communicator::NodesContainerType& r_local_nodes = rModelPart.GetCommunicator().InterfaceMesh(i_color).Nodes();

                int* recv_buffer = recv_buffers[i_color];

                unsigned int i = 0;
                for (ModelPart::NodeIterator i_node = r_local_nodes.begin(); i_node != r_local_nodes.end(); ++i_node)
                {
                    i_node->Set(BOUNDARY, bool(recv_buffer[i++]) || i_node->Is(BOUNDARY) ); // OR with received value
                }

                if ((int)i > recv_sizes[i_color])
                    std::cout << rank << " Error in estimating receive buffer size...." << std::endl;

                delete[] recv_buffer;
            }
    }

    void CommunicateBoundaryFlagFromOwner(ModelPart& rModelPart)
    {
        int rank;
        MPI_Comm_rank(MPI_COMM_WORLD, &rank);

        int destination = 0;

        Communicator::NeighbourIndicesContainerType& neighbours_indices = rModelPart.GetCommunicator().NeighbourIndices();

        std::vector<int*> recv_buffers(neighbours_indices.size());
        std::vector<int>  recv_sizes(neighbours_indices.size());

        for (unsigned int i_color = 0; i_color < neighbours_indices.size(); i_color++)
            if ((destination = neighbours_indices[i_color]) >= 0)
            {
                Communicator::NodesContainerType& r_local_nodes = rModelPart.GetCommunicator().InterfaceMesh(i_color).Nodes();
                Communicator::NodesContainerType& r_ghost_nodes = rModelPart.GetCommunicator().InterfaceMesh(i_color).Nodes();

                unsigned int send_size = r_local_nodes.size();
                unsigned int recv_size = r_ghost_nodes.size();

                if ( (send_size == 0) && (recv_size == 0) )
                    continue; // Nothing to transfer

                int* send_buffer = new int[send_size];
                recv_buffers[i_color] = new int[recv_size];
                recv_sizes[i_color] = recv_size;

                // Fill the send buffer
                unsigned int i = 0;
                for (ModelPart::NodeIterator i_node = r_local_nodes.begin(); i_node != r_local_nodes.end(); ++i_node)
                {
                    send_buffer[i++] = i_node->Is(BOUNDARY); // bool to int! (should be safe)
                }

                if (i > send_size)
                    std::cout << rank << " Error in estimating send buffer size...." << std::endl;

                MPI_Status status;

                int send_tag = i_color;
                int receive_tag = i_color;

                MPI_Sendrecv(send_buffer, send_size, MPI_INT, destination, send_tag,
                             recv_buffers[i_color], recv_size, MPI_INT, destination, receive_tag,
                             MPI_COMM_WORLD, &status);

                delete [] send_buffer;
            }

        // Write in nodes
        for (unsigned int i_color = 0; i_color < neighbours_indices.size(); i_color++)
            if ((destination = neighbours_indices[i_color]) >= 0)
            {
                Communicator::NodesContainerType& r_ghost_nodes = rModelPart.GetCommunicator().InterfaceMesh(i_color).Nodes();

                int* recv_buffer = recv_buffers[i_color];

                unsigned int i = 0;
                for (ModelPart::NodeIterator i_node = r_ghost_nodes.begin(); i_node != r_ghost_nodes.end(); ++i_node)
                {
                    i_node->Set(BOUNDARY, bool(recv_buffer[i++]) );
                }

                if ((int)i > recv_sizes[i_color])
                    std::cout << rank << " Error in estimating receive buffer size...." << std::endl;

                delete[] recv_buffer;
            }
    }

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
    TrilinosVariationalDistanceCalculationProcess& operator=(TrilinosVariationalDistanceCalculationProcess const& rOther);

    /// Copy constructor.
    TrilinosVariationalDistanceCalculationProcess(TrilinosVariationalDistanceCalculationProcess const &rOther);

    ///@}

}; // Class TrilinosVariationalDistanceCalculationProcess

///@}

///@name Type Definitions
///@{

///@}
///@name Input and output
///@{

///@}
}  // namespace Kratos.

#endif // KRATOS_TRILINOS_VARIATIONAL_DISTANCE_CALCULATION_PROCESS_INCLUDED  defined
