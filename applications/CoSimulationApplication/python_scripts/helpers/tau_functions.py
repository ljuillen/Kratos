# -*- coding: utf-8 -*-
import re, glob, subprocess, time, os
import numpy as np
import tau_python
from tau_python import tau_msg
# import tau_python.tau_msg as tau_msg
import PyPara, PySurfDeflect
from scipy.io import netcdf

# GetFluidMesh is called only once at the beginning, after the first fluid solve
def GetFluidMesh(working_path, tau_path, step, para_path_mod):
    interface_file_name_surface = findSolutionAndConvert(working_path, tau_path, step, para_path_mod)
    interface_file_number_of_lines = findInterfaceFileNumberOfLines(interface_file_name_surface + '.dat')
    print 'interface_file_number_of_lines =', interface_file_number_of_lines
    NodesNr, ElemsNr, X, Y, Z, CP, P, elemTable, liste_number = readPressure(interface_file_name_surface + '.dat', interface_file_number_of_lines, 0, 20)
    nodal_coords, nodesID, elem_connectivities, element_types = interfaceMeshFluid(NodesNr, ElemsNr, elemTable, X, Y, Z)
    # In vtk format element connectivities start from 0, not from 1
    elem_connectivities -= 1
    return nodal_coords, elem_connectivities, element_types

def ComputeForces(working_path, tau_path, step, para_path_mod):
    interface_file_name_surface = findSolutionAndConvert(working_path, tau_path, step, para_path_mod)
    interface_file_number_of_lines = findInterfaceFileNumberOfLines(interface_file_name_surface + '.dat')
    print 'interface_file_number_of_lines =', interface_file_number_of_lines
    forces = caculatePressure(interface_file_name_surface, interface_file_number_of_lines, step)
    return forces

def ExecuteBeforeMeshDeformation(dispTau,step,para_path_mod,working_path,tau_path):
    global dispTauOld
    print "deformationstart"
    interface_file_name_surface = findSolutionAndConvert(working_path, tau_path, step, para_path_mod)
    interface_file_number_of_lines = findInterfaceFileNumberOfLines(interface_file_name_surface + '.dat')
    print 'interface_file_number_of_lines =', interface_file_number_of_lines

    NodesNr,ElemsNr,X,Y,Z,CP,P,elemTable,liste_number=readPressure( interface_file_name_surface + '.dat', interface_file_number_of_lines, 0, 20)

    nodes,nodesID,elems,element_types=interfaceMeshFluid(NodesNr,ElemsNr,elemTable,X,Y,Z)

    if(step==0):
        dispTauOld=np.zeros(3*NodesNr)
        dispTau_transpose = np.transpose(dispTau)
        print 'dispTau =', dispTau_transpose
    print 'dispTauOld = ', dispTauOld

    [ids,coordinates,globalID,coords]=meshDeformation(NodesNr,nodes,dispTau,dispTauOld,0,para_path_mod)
    PySurfDeflect.write_test_surface_file('deformation_file',coords[:,0:2],coords[:,3:5])
    print "afterPySurfDeflect"

    for i in xrange(0,3*NodesNr):
        dispTauOld[i]=dispTau[i]
    print "afterDeformation"


def FindOutputFile(working_path, step):
    outputs_path = working_path + "Outputs/"
    CheckIfPathExists(outputs_path)
    ouput_file_pattern = "airfoilSol.pval.unsteady_i="
    return FindFileName(outputs_path, ouput_file_pattern, step + 1)


def FindMeshFile(working_path, step):
    mesh_path = working_path + "Mesh/"
    CheckIfPathExists(mesh_path)
    if step == 0:
        pattern = 'airfoil_Structured_scaliert.grid'
        return FindInitialMeshFileName(mesh_path, pattern)
    else:
        pattern = 'airfoil_Structured_scaliert.grid.def.'
        return FindFileName(mesh_path, pattern, step)


# find the solution file name in '/Outputs' and convert in .dat
def findSolutionAndConvert(working_path, tau_path, step, para_path_mod):
    output_file_name = FindOutputFile(working_path, step)
    mesh_file_name = FindMeshFile(working_path, step)

    PrintBlockHeader("Start Writting Solution Data at time %s" %(str(time)))
    subprocess.call('rm ' +  working_path + '/Tautoplt.cntl' ,shell=True)
    readTautoplt(working_path + 'Tautoplt.cntl', working_path + 'Tautoplt_initial.cntl', mesh_file_name, output_file_name,working_path + para_path_mod)
    subprocess.call(tau_path + 'tau2plt ' + working_path + '/Tautoplt.cntl' ,shell=True)
    PrintBlockHeader("Stop Writting Solution Data at time %s" %(str(time)))

    if 'surface' not in output_file_name + '.dat':
        interface_file_name_surface = output_file_name[0:output_file_name.find('.pval')]+ '.surface.' + output_file_name[output_file_name.find('.pval')+1:len(output_file_name)]
    else:
        interface_file_name_surface = output_file_name

    return interface_file_name_surface


def CheckIfPathExists(path):
    if not os.path.exists(path):
        raise Exception('Path: "{}" not found'.format(path))


def FindInitialMeshFileName(path, name):
    files_list = glob.glob(path + "*")
    for file in files_list:
        if file.startswith('%s' % path + '%s' % name):
            return file
    raise Exception('File: "{}" not found'.format(path + name))


def FindFileName(path, name, step):
    files_list = glob.glob(path + "*")
    for file in files_list:
        if file.startswith('%s' % path + '%s' % name + '%s' % step):
            return file
    raise Exception('File: "{}" not found'.format(path + name))

def findInterfaceFileNumberOfLines(fname):
    with open(fname,'r') as f:
        it = 0
        pattern = {'E+', 'E-'}
        for line in f:
            if 'E+' in line or 'E-' in line:
                it = it+1
    return it

def PrintBlockHeader(header):
    tau_python.tau_msg("\n" + 50 * "*" + "\n" + "* %s\n" %header + 50*"*" + "\n")

# read the solution file name in '/Outputs' and calculate the pressure
def caculatePressure(interface_file_name_surface, interface_file_number_of_lines, step):
    NodesNr,ElemsNr,X,Y,Z,CP,P,elemTable,liste_number=readPressure( interface_file_name_surface + '.dat', interface_file_number_of_lines, 0, 20)

    nodes,nodesID,elems,element_types=interfaceMeshFluid(NodesNr,ElemsNr,elemTable,X,Y,Z)

    # calculating cp at the center of each interface element
    pCell=calcpCell(ElemsNr,P,X,elemTable)

    # calculating element area and normal vector
    area,normal = calcAreaNormal(ElemsNr,elemTable,X,Y,Z,(step+1))

    # calculating the force vector
    forcesTauNP = calcFluidForceVector(ElemsNr,elemTable,NodesNr,pCell,area,normal,(step+1))

    return forcesTauNP

def readTautoplt(fname_mod, fname_o, mesh_file_name, interface_file_name, para_path_mod):
    fs = open(fname_o,'r+')
    fd = open(fname_mod,'w')
    line = fs.readline()
    while line:
        if 'Primary grid filename:' in line:
            line = 'Primary grid filename:' + mesh_file_name + ' \n'
            fd.write(line)
            print line
            line = fs.readline()
        if 'Boundary mapping filename:' in line:
            line = 'Boundary mapping filename:' + para_path_mod + ' \n'
            fd.write(line)
            print line
            line = fs.readline()
        if 'Restart-data prefix:' in line:
            line = 'Restart-data prefix:' + interface_file_name + ' \n'
            fd.write(line)
            print line
            line = fs.readline()
        else:
            line = fs.readline()
            fd.write(line)
    fd.close()
    fs.close()


# Read Cp from the solution file and calculate 'Pressure' on the nodes of TAU Mesh
def readPressure(interface_file_name,interface_file_number_of_lines,error,velocity):
    with open(interface_file_name,'r') as f:
        header1 = f.readline()  #liest document linie für linie durch
        header2 = f.readline()
        print "Careful ---- headers 2 = ", header2 #5 readline- Annahme fünf spalten
        header2_split = header2.split()
        pos_X = header2_split.index('"x"')
        pos_Y = header2_split.index('"y"')
        pos_Z = header2_split.index('"z"')
        pos_Cp = header2_split.index('"cp"')
        header3 = f.readline()
        header4 = f.readline()
        header5 = f.readline()

        d=[int(s) for s in re.findall(r'\b\d+\b', header4)]  #find all sucht muster im document
        NodesNr = d[0]
        ElemsNr = d[1]

        # write X,Y,Z,CP of the document in a vector = liste_number
        liste_number = []
        for i in xrange(interface_file_number_of_lines):
            line = f.readline()
            for elem in line.split():
                liste_number.append(float(elem))

        # write ElemTable of the document
        elemTable_Sol = np.zeros([ElemsNr,4],dtype=int)
        k = 0
        line = f.readline()
        while line:
            elemTable_Sol[k,0]=int(line.split()[0])
            elemTable_Sol[k,1]=int(line.split()[1])
            elemTable_Sol[k,2]=int(line.split()[2])
            elemTable_Sol[k,3]=int(line.split()[3])
            k=k+1
            line = f.readline()

        # reshape content in X, Y, Z, Cp
        X=liste_number[(pos_X-2)*NodesNr:(pos_X-2+1)*NodesNr]
        Y=liste_number[(pos_Y-2)*NodesNr:(pos_Y-2+1)*NodesNr]
        Z=liste_number[(pos_Z-2)*NodesNr:(pos_Z-2+1)*NodesNr]
        CP=liste_number[(pos_Cp-2)*NodesNr:(pos_Cp-2+1)*NodesNr]
        X=X[0:NodesNr-error]
        Y=Y[0:NodesNr-error]
        Z=Z[0:NodesNr-error]
        CP=CP[0:NodesNr-error]
        P=[x*velocity*velocity*0.5*1.2 for x in CP]
        P=np.array(P)

    return NodesNr,ElemsNr,X,Y,Z,CP,P,elemTable_Sol,liste_number


def interfaceMeshFluid(NodesNr, ElemsNr, elemTable, X, Y, Z):
    # array to store the coordinates of the nodes in the fluid mesh: x1,y1,z1,x2,y2,z2,...
    nodes = np.zeros(NodesNr*3)
    # array to store the IDs of the nodes in the fluid mesh: IDnode1, IDnode2,...
    nodesID = np.zeros(NodesNr, dtype=int)
    elems = np.zeros(4*ElemsNr, dtype=int)  # array to store the element table
    element_types = np.zeros(ElemsNr, dtype=int)

    for i in xrange(0, NodesNr):
        nodesID[i] = i+1
        nodes[3*i+0] = X[i]
        nodes[3*i+1] = Y[i]
        nodes[3*i+2] = Z[i]

    for i in xrange(0, ElemsNr):
        elems[i*4+0] = elemTable[i, 0]
        elems[i*4+1] = elemTable[i, 1]
        elems[i*4+2] = elemTable[i, 2]
        elems[i*4+3] = elemTable[i, 3]
        element_types[i] = 9

    return nodes, nodesID, elems, element_types

# Calculate the Pressure on the elements from the pressure on the nodes
def calcpCell(ElemsNr,P,X,elemTable):
    pCell = np.zeros(ElemsNr); # cp for interface elements
    #print 'len(elemTable) = ', len(elemTable)
    with open('xp','w') as f:
        for i in xrange(0,ElemsNr):
            pCell[i] = 0.25* (P[elemTable[i,0]-1] + P[elemTable[i,1]-1] + P[elemTable[i,2]-1] + P[elemTable[i,3]-1]);
            x= 0.25* (X[elemTable[i,0]-1] + X[elemTable[i,1]-1] + X[elemTable[i,2]-1] + X[elemTable[i,3]-1]);
            f.write('%d\t%f\t%f\n'%(i,x,pCell[i]))

    return pCell


# Calculate the area and the normal of the area for each cell - element of TAU Mesh
def calcAreaNormal(ElemsNr,elemTable,X,Y,Z,fIteration):
    area = np.zeros(ElemsNr); # area of each interface element
    normal = np.zeros([ElemsNr,3]) # element normal vector
    A = np.zeros(3);
    B = np.zeros(3);
    for i in xrange(0,ElemsNr):
        A[0] = X[elemTable[i,2]-1] - X[elemTable[i,0]-1]
        A[1] = Y[elemTable[i,2]-1] - Y[elemTable[i,0]-1]
        A[2] = Z[elemTable[i,2]-1] - Z[elemTable[i,0]-1]
        B[0] = X[elemTable[i,3]-1] - X[elemTable[i,1]-1]
        B[1] = Y[elemTable[i,3]-1] - Y[elemTable[i,1]-1]
        B[2] = Z[elemTable[i,3]-1] - Z[elemTable[i,1]-1]
        a=np.cross(A,B)   #np quasi ein matematischer provider
        norm=np.linalg.norm(a)
        a=a/norm
        normal[i,0]=a[0]
        normal[i,1]=a[1]
        normal[i,2]=a[2]
        A[0] = X[elemTable[i,1]-1] - X[elemTable[i,0]-1]
        A[1] = Y[elemTable[i,1]-1] - Y[elemTable[i,0]-1]
        A[2] = Z[elemTable[i,1]-1] - Z[elemTable[i,0]-1]
        B[0] = X[elemTable[i,3]-1] - X[elemTable[i,0]-1]
        B[1] = Y[elemTable[i,3]-1] - Y[elemTable[i,0]-1]
        B[2] = Z[elemTable[i,3]-1] - Z[elemTable[i,0]-1]
        a=np.cross(A,B)
        norm=np.linalg.norm(a)
        area[i] =  norm # hold only for 2d case, MUST be modified for 3d interfaces
    f_name = 'Outputs/Area_'+str(fIteration)+'.dat'
    with open(f_name,'w') as fwrite:
        for i in xrange(0,len(area[:])):
            fwrite.write("%f\n" % (area[i]))
    return area, normal

# Calculate the Vector Force
def calcFluidForceVector(ElemsNr,elemTable,NodesNr,pCell,area,normal,fIteration):
    forcesTauNP = np.zeros(NodesNr*3)
    for i in xrange(0,ElemsNr):
        #p= cpCell[i] * q
        p=pCell[i]
        Fx = p * area[i] * normal[i,0]
        Fy = p * area[i] * normal[i,1]
        Fz = p * area[i] * normal[i,2]
        #print 'test Fx, Fy, Fz', Fx, Fy, Fz
        forcesTauNP[3*(elemTable[i,0]-1)+0] += 0.25 * Fx
        forcesTauNP[3*(elemTable[i,0]-1)+1] += 0.25 * Fy
        forcesTauNP[3*(elemTable[i,0]-1)+2] += 0.25 * Fz
        forcesTauNP[3*(elemTable[i,1]-1)+0] += 0.25 * Fx
        forcesTauNP[3*(elemTable[i,1]-1)+1] += 0.25 * Fy
        forcesTauNP[3*(elemTable[i,1]-1)+2] += 0.25 * Fz
        forcesTauNP[3*(elemTable[i,2]-1)+0] += 0.25 * Fx
        forcesTauNP[3*(elemTable[i,2]-1)+1] += 0.25 * Fy
        forcesTauNP[3*(elemTable[i,2]-1)+2] += 0.25 * Fz
        forcesTauNP[3*(elemTable[i,3]-1)+0] += 0.25 * Fx
        forcesTauNP[3*(elemTable[i,3]-1)+1] += 0.25 * Fy
        forcesTauNP[3*(elemTable[i,3]-1)+2] += 0.25 * Fz
    f_name = 'Outputs/ForcesTauNP_'+str(fIteration)+'.dat'
    with open(f_name,'w') as fwrite:
        for i in xrange(0,len(forcesTauNP[:])):
            fwrite.write("%f\n" % (forcesTauNP[i]))
    return forcesTauNP

# Execute the Mesh deformation of TAU
def meshDeformation(NodesNr,nodes,dispTau,dispTauOld,error, para_path_mod):

    disp=np.zeros([NodesNr,3])#NodesNr
    for i in xrange(0,NodesNr):#NodesNr
        disp[i,0]=1*(dispTau[3*i+0]-dispTauOld[3*i+0])
        disp[i,1]=1*(dispTau[3*i+1]-dispTauOld[3*i+1])
        disp[i,2]=1*(dispTau[3*i+2]-dispTauOld[3*i+2])
    Para = PyPara.Parafile(para_path_mod)
    ids, coordinates = PySurfDeflect.read_tau_grid(Para)
    coords=np.zeros([NodesNr-error,6])#NodesNr

    for i in xrange(0,NodesNr-error):
        coords[i,0]=coordinates[0,i]
        coords[i,1]=coordinates[1,i]
        coords[i,2]=coordinates[2,i]

    globalID = np.zeros(NodesNr-error)
    for i in xrange(0,NodesNr-error):
        xi = coords[i,0]
        yi = coords[i,1]
        zi = coords[i,2]
        for k in xrange(0,NodesNr-error):
            xk = nodes[3*k+0]
            yk = nodes[3*k+1]
            zk = nodes[3*k+2]
            dist2 = (xi-xk)*(xi-xk) + (yi-yk)*(yi-yk) + (zi-zk)*(zi-zk)

            if dist2 < 0.00001:
                #K=k
                globalID[i] = k
            globalID = globalID.astype(int)
        #print "%d found %d" % (i,K)
        coords[i, 3] = disp[globalID[i], 0]
        coords[i, 4] = disp[globalID[i], 1]
        coords[i, 5] = disp[globalID[i], 2]

    fname_new = 'interface_deformfile.nc'
    ncf = netcdf.netcdf_file(fname_new, 'w')
    # define dimensions
    nops = 'no_of_points'
    number_of_points = len(ids[:])
    ncf.createDimension(nops, number_of_points)
    # define variables
    gid = ncf.createVariable('global_id', 'i', (nops,))
    ncx = ncf.createVariable('x', 'd', (nops,))
    ncy = ncf.createVariable('y', 'd', (nops,))
    ncz = ncf.createVariable('z', 'd', (nops,))
    ncdx = ncf.createVariable('dx', 'd', (nops,))
    ncdy = ncf.createVariable('dy', 'd', (nops,))
    ncdz = ncf.createVariable('dz', 'd', (nops,))
    # write data
    gid[:] = ids
    ncx[:] = coords[:,0]
    ncy[:] = coords[:,1]
    ncz[:] = coords[:,2]
    ncdx[:] = coords[:,3]
    ncdy[:] = coords[:,4]
    ncdz[:] = coords[:,5]
    ncf.close()

    return ids, coordinates, globalID, coords
