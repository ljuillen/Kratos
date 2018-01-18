from __future__ import print_function, absolute_import, division #makes KratosMultiphysics backward compatible with python 2.6 and 2.7

from KratosMultiphysics import *
from KratosMultiphysics.FluidDynamicsApplication import *
from KratosMultiphysics.ExternalSolversApplication import *

######################################################################################
######################################################################################
######################################################################################

## Parse the ProjectParameters
parameter_file = open("ProjectParameters.json",'r')
ProjectParameters = Parameters( parameter_file.read())

## Get echo level and parallel type
echo_level = ProjectParameters["problem_data"]["echo_level"].GetInt()
parallel_type = ProjectParameters["problem_data"]["parallel_type"].GetString()

## Import KratosMPI if needed
if (parallel_type == "MPI"):
    from KratosMultiphysics.mpi import *
    from KratosMultiphysics.MetisApplication import *
    from KratosMultiphysics.TrilinosApplication import *

## Fluid model part definition
main_model_part = ModelPart(ProjectParameters["problem_data"]["model_part_name"].GetString())
main_model_part.ProcessInfo.SetValue(DOMAIN_SIZE, ProjectParameters["problem_data"]["domain_size"].GetInt())

## Solver construction
import python_solvers_wrapper_fluid
solver = python_solvers_wrapper_fluid.CreateSolver(main_model_part, ProjectParameters)

solver.AddVariables()

## Read the model - note that SetBufferSize is done here
solver.ImportModelPart()

## Add AddDofs
solver.AddDofs()

## Initialize GiD  I/O
output_post  = ProjectParameters.Has("output_configuration")
if (output_post == True):
    if (parallel_type == "OpenMP"):
        from gid_output_process import GiDOutputProcess
        gid_output = GiDOutputProcess(solver.GetComputingModelPart(),
                                      ProjectParameters["problem_data"]["problem_name"].GetString() ,
                                      ProjectParameters["output_configuration"])
    elif (parallel_type == "MPI"):
        from gid_output_process_mpi import GiDOutputProcessMPI
        gid_output = GiDOutputProcessMPI(solver.GetComputingModelPart(),
                                         ProjectParameters["problem_data"]["problem_name"].GetString() ,
                                         ProjectParameters["output_configuration"])

    gid_output.ExecuteInitialize()

## Creation of Kratos model (build sub_model_parts or submeshes)
FluidModel = Model()
FluidModel.AddModelPart(main_model_part)

## Get the list of the skin submodel parts in the object Model
for i in range(ProjectParameters["solver_settings"]["skin_parts"].size()):
    skin_part_name = ProjectParameters["solver_settings"]["skin_parts"][i].GetString()
    FluidModel.AddModelPart(main_model_part.GetSubModelPart(skin_part_name))

## Get the list of the no-skin submodel parts in the object Model (results processes and no-skin conditions)
for i in range(ProjectParameters["solver_settings"]["no_skin_parts"].size()):
    no_skin_part_name = ProjectParameters["solver_settings"]["no_skin_parts"][i].GetString()
    FluidModel.AddModelPart(main_model_part.GetSubModelPart(no_skin_part_name))

## Get the list of the initial conditions submodel parts in the object Model
for i in range(ProjectParameters["initial_conditions_process_list"].size()):
    initial_cond_part_name = ProjectParameters["initial_conditions_process_list"][i]["Parameters"]["model_part_name"].GetString()
    FluidModel.AddModelPart(main_model_part.GetSubModelPart(initial_cond_part_name))

## Get the gravity submodel part in the object Model
for i in range(ProjectParameters["gravity"].size()):
    gravity_part_name = ProjectParameters["gravity"][i]["Parameters"]["model_part_name"].GetString()
    FluidModel.AddModelPart(main_model_part.GetSubModelPart(gravity_part_name))

## Print model_part and properties
if (echo_level > 1) and ((parallel_type == "OpenMP") or (mpi.rank == 0)):
    print("")
    print(main_model_part)
    for properties in main_model_part.Properties:
        print(properties)

## Processes construction
import process_factory
# "list_of_processes" contains all the processes already constructed (boundary conditions, initial conditions and gravity)
# Note 1: gravity is firstly constructed. Outlet process might need its information.
# Note 2: conditions are constructed before BCs. Otherwise, they may overwrite the BCs information.
list_of_processes =  process_factory.KratosProcessFactory(FluidModel).ConstructListOfProcesses( ProjectParameters["gravity"] )
list_of_processes += process_factory.KratosProcessFactory(FluidModel).ConstructListOfProcesses( ProjectParameters["initial_conditions_process_list"] )
list_of_processes += process_factory.KratosProcessFactory(FluidModel).ConstructListOfProcesses( ProjectParameters["boundary_conditions_process_list"] )
list_of_processes += process_factory.KratosProcessFactory(FluidModel).ConstructListOfProcesses( ProjectParameters["auxiliar_process_list"] )

if (echo_level > 1) and ((parallel_type == "OpenMP") or (mpi.rank == 0)):
    for process in list_of_processes:
        print(process)

## Processes initialization
for process in list_of_processes:
    process.ExecuteInitialize()

## Solver initialization
solver.Initialize()

## Stepping and time settings
# delta_time = ProjectParameters["problem_data"]["time_step"].GetDouble()
start_time = ProjectParameters["problem_data"]["start_time"].GetDouble()
end_time = ProjectParameters["problem_data"]["end_time"].GetDouble()

time = start_time
step = 0

if (output_post == True):
    gid_output.ExecuteBeforeSolutionLoop()

for process in list_of_processes:
    process.ExecuteBeforeSolutionLoop()

## Writing the full ProjectParameters file before solving
if ((parallel_type == "OpenMP") or (mpi.rank == 0)) and (echo_level > 0):
    f = open("ProjectParametersOutput.json", 'w')
    f.write(ProjectParameters.PrettyPrintJsonString())
    f.close()
'''   
def ForcingTerm(mp):
    for node in mp.GetSubModelPart("Parts_Parts_Auto1").Nodes:
        x = node.X
        y = node.Y
        for step in range(3):
            node.SetSolutionStepValue(BODY_FORCE_X,step,(0.4*((-0.25*x - 0.5*y - 0.4)**2 + (0.5*x + y + 0.8)**2)/(x + 2*y + 1.6)**2 - 0.4*(0.625*x + 1.25*y + 1.0)/(x + 2*y + 1.6) + 2.0)/(0.5*x + y + 0.8))
            node.SetSolutionStepValue(BODY_FORCE_Y,step,(0.8*((-0.25*x - 0.5*y - 0.4)**2 + (0.5*x + y + 0.8)**2)/(x + 2*y + 1.6)**2 - (-0.25*x - 0.5*y - 0.4)**2/(0.5*x + y + 0.8)**2 + (0.25*x + 0.5*y + 0.4)/(0.5*x + y + 0.8) + 1.75 - 0.4*(1.25*x + 2.5*y + 2.0)/(x + 2*y + 1.6))/(0.5*x + y + 0.8))
            node.SetSolutionStepValue(EXTERNAL_PRESSURE,step,((-0.25*x - 0.5*y - 0.4)*(0.8*((-0.25*x - 0.5*y - 0.4)**2 + (0.5*x + y + 0.8)**2)/(x + 2*y + 1.6)**2 + 7.0 - 0.4*(1.25*x + 2.5*y + 2.0)/(x + 2*y + 1.6))/(0.5*x + y + 0.8) - (-0.25*x - 0.5*y - 0.4)*(0.8*((-0.25*x - 0.5*y - 0.4)**2 + (0.5*x + y + 0.8)**2)/(x + 2*y + 1.6)**2 - (-0.25*x - 0.5*y - 0.4)**2/(0.5*x + y + 0.8)**2 + (0.25*x + 0.5*y + 0.4)/(0.5*x + y + 0.8) + 1.75 - 0.4*(1.25*x + 2.5*y + 2.0)/(x + 2*y + 1.6))/(0.5*x + y + 0.8) - (-0.25*x - 0.5*y - 0.4)*(7.0*x + 7.0*y - 0.4*((-0.25*x - 0.5*y - 0.4)**2 + (0.5*x + y + 0.8)**2)/(x + 2*y + 1.6) + 2.8)/(0.5*x + y + 0.8)**2 + 5.0 - 0.5*(7.0*x + 7.0*y - 0.4*((-0.25*x - 0.5*y - 0.4)**2 + (0.5*x + y + 0.8)**2)/(x + 2*y + 1.6) + 2.8)/(0.5*x + y + 0.8))/(0.5*x + y + 0.8))
           
        #for node in mp.GetSubModelPart("Parts_Parts_Auto1").Nodes:
            #node.Fix(BODY_FORCE_X)
            #node.Fix(BODY_FORCE_Y)
            #node.Fix(EXTERNAL_PRESSURE)   
'''            

for node in main_model_part.GetSubModelPart("Parts_Parts_Auto1").Nodes:
    x = node.X
    y = node.Y
    for step in range(3):
        node.SetSolutionStepValue(MOMENTUM_X,step,24.0*x + 48*y + 38.4 )
        node.SetSolutionStepValue(MOMENTUM_Y,step,-12.0*x - 24*y - 19.2)
        node.SetSolutionStepValue(DENSITY,step,0.5*x+y+0.8)
        node.SetSolutionStepValue(TOTAL_ENERGY,step,1000*x +500*y +30000)
     
for node in main_model_part.GetSubModelPart("AutomaticInlet2D_Automatic_inlet_velocity_Auto2").Nodes:
    x = node.X
    y = node.Y
    node.SetSolutionStepValue(MOMENTUM_X, 24.0*x + 48*y + 38.4 )
    node.SetSolutionStepValue(MOMENTUM_Y, -12.0*x - 24*y - 19.2)
    node.SetSolutionStepValue(DENSITY, 0.5*x+y+0.8)
    node.SetSolutionStepValue(TOTAL_ENERGY, 1000*x +500*y +30000)
    node.Fix(MOMENTUM_X)
    node.Fix(MOMENTUM_Y)
    node.Fix(DENSITY)
    node.Fix(TOTAL_ENERGY)
    
for node in main_model_part.GetSubModelPart("Slip2D_Slip_Auto1").Nodes:
    x = node.X
    y = node.Y
    node.SetSolutionStepValue(MOMENTUM_X, 24.0*x + 48*y + 38.4 )
    node.SetSolutionStepValue(MOMENTUM_Y, -12.0*x - 24*y - 19.2)
    node.SetSolutionStepValue(DENSITY, 0.5*x+y+0.8)
    node.SetSolutionStepValue(TOTAL_ENERGY, 1000*x +500*y +30000)
    node.Fix(MOMENTUM_X)
    node.Fix(MOMENTUM_Y)
    node.Fix(DENSITY)
    node.Fix(TOTAL_ENERGY)
    
for node in main_model_part.GetSubModelPart("NoSlip2D_No_Slip_Auto1").Nodes:
    x = node.X
    y = node.Y
    node.SetSolutionStepValue(MOMENTUM_X, 24.0*x + 48*y + 38.4 )
    node.SetSolutionStepValue(MOMENTUM_Y, -12.0*x - 24*y - 19.2)
    node.SetSolutionStepValue(DENSITY, 0.5*x+y+0.8)
    node.SetSolutionStepValue(TOTAL_ENERGY, 1000*x +500*y +30000)
    node.Fix(MOMENTUM_X)
    node.Fix(MOMENTUM_Y)
    node.Fix(DENSITY)
    node.Fix(TOTAL_ENERGY)
  
for node in main_model_part.GetSubModelPart("Outlet2D_Outlet_pressure_Auto1").Nodes:
    x = node.X
    y = node.Y
    node.SetSolutionStepValue(MOMENTUM_X, 24.0*x + 48*y + 38.4 )
    node.SetSolutionStepValue(MOMENTUM_Y, -12.0*x - 24*y - 19.2)
    node.SetSolutionStepValue(DENSITY, 0.5*x+y+0.8)
    node.SetSolutionStepValue(TOTAL_ENERGY, 1000*x +500*y +30000)
    node.Fix(MOMENTUM_X)
    node.Fix(MOMENTUM_Y)
    node.Fix(DENSITY)
    node.Fix(TOTAL_ENERGY)

while(time <= end_time):

    delta_time = solver.ComputeDeltaTime()
    step += 1
    time = time + delta_time
    main_model_part.CloneTimeStep(time)

    if (parallel_type == "OpenMP") or (mpi.rank == 0):
        print("")
        print("STEP = ", step)
        print("TIME = ", time)

    for process in list_of_processes:
        process.ExecuteInitializeSolutionStep()
    
    if (output_post == True):
        gid_output.ExecuteInitializeSolutionStep()

    if(step >= 3):
        
        solver.Solve()
    #else:
       # ForcingTerm(main_model_part)

    #applica le BCs
    for process in list_of_processes:
        process.ExecuteFinalizeSolutionStep()

    if (output_post == True):
        gid_output.ExecuteFinalizeSolutionStep()

    for process in list_of_processes:
        process.ExecuteBeforeOutputStep()

    if (gid_output.IsOutputStep()) and (output_post == True):
        gid_output.PrintOutput()

    for process in list_of_processes:
        process.ExecuteAfterOutputStep()

for process in list_of_processes:
    process.ExecuteFinalize()

if (output_post == True):
    gid_output.ExecuteFinalize()
