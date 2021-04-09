from paraview.simple import *
import os
import sys
import numpy as np

# ~ This function loads the specified VTI data, gets a lineout and 
# ~ then saves the lineout data as a CSV file. p0 and p1 are the line origin
# ~ and end respectively.
# Usage:
# pvpython /path/to/file/getLineout.py

# New Session

Disconnect()
Connect()
		
def getLineout(fname,ln_origin,ln_end,inDir,outDir):
	# Inputs:
	# fname = VTI file name 
	# ln_origin = [1x3] point 1
	# ln_end = [1x3] point 2
	# inDir = input file directory
	# outDir = output file directory
	
	# Load data
	data = XMLImageDataReader(FileName=[inDir + fname])  # read vti file
	# Plot over line
	ln = PlotOverLine(Input=data,Source='High Resolution Line Source')
	ln.Source.Point1 = ln_origin
	ln.Source.Point2 = ln_end
	# Export as CSV:
	# First column is the scalar, Last  columns are the x, y and z positions
	# For vectors, first  columns are the x, y and z vector components
	if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
		os.mkdir(outDir)
	SaveData(outDir + fname[0:len(fname)-4] + '-lineout.csv', proxy=ln, FieldAssociation='Points')
	print ('Saved to ' + outDir + fname[0:len(fname)-4] + '-lineout.csv')

def getLineIntegratedVal(fname,dataName,ln_origin,ln_end,inDir,outDir,isVector):
	# Inputs:
	# fname = VTI file name 
	# ln_origin = [1x3] point 1
	# ln_end = [1x3] point 2
	# inDir = input file directory
	# outDir = output file directory
	# isVector = true for vector data
	
	# Load data
	data = XMLImageDataReader(FileName=[inDir + fname])  # read vti file
	# Plot over line
	ln = PlotOverLine(Input=data,Source='High Resolution Line Source')
	ln.Source.Point1 = ln_origin
	ln.Source.Point2 = ln_end
	# Integrate Over Line
	integrateVariables1 = IntegrateVariables(Input=ln)
	passArrays1 = PassArrays(Input=integrateVariables1)
	passArrays1.PointDataArrays = [dataName]    
	out = paraview.servermanager.Fetch(passArrays1)
	
	# Delete
	Delete(integrateVariables1)
	Delete(passArrays1)
	Delete(ln)
	Delete(data)
	del integrateVariables1, passArrays1, ln, data
	
	# Return result
	if isVector:
		u = [0, 0, 0]
		u[0] = out.GetPointData().GetArray(dataName).GetValue(0)
		u[1] = out.GetPointData().GetArray(dataName).GetValue(1)
		u[2] = out.GetPointData().GetArray(dataName).GetValue(2)
	else:
		u = [0]
		u[0] = out.GetPointData().GetArray(dataName).GetValue(0)
			
	return np.array(u)

def fn(fname,dataName,startx,endx,N,inDir,outDir,isVector):
	# Inputs:
	# fname = VTI file name 
	# startx, endx, N = starting x-pos, ending x-pos, number of points
	# inDir = input file directory
	# outDir = output file directory
	# isVector = true for vector data
	xx = np.linspace(startx,endx,N)
	# Storage arrays
	P0 = np.empty((0,3), dtype=float)
	P1 = np.empty((0,3), dtype=float)
	if isVector:
		U = np.empty((0,3), dtype=float)
	else:
		U = np.empty((0,1), dtype=float)
	for x in xx: # Iterate over all x
		p0 = [x, -0.03, 0.0]  # Position of Point 1
		p1 = [x,0.03,0.0] # Position of Point 2
		u = getLineIntegratedVal(fname,dataName,p0,p1,inDir,outDir,isVector) # Velocity
		# Append to arrays
		P0 = np.append(P0, np.array([p0]), axis=0)
		P1 = np.append(P1, np.array([p1]),axis=0)
		U = np.append(U,np.array([u]),axis=0)
	out =  np.column_stack((P0,P1,U))
	np.savetxt(outDir + fname[0:len(fname)-4] + '.csv' ,out,fmt='%1.5e', delimiter=',')
	print('Saved ' + fname[0:len(fname)-4] + '.csv')
	
	
	
# (1) 	Specify the directory which contains the .vti data output from GORGON
inDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_16_Al_2D-9/' # Input directory 
outDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_16_Al_2D-9/LineIntegratedValues/' # Output Directory
if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
	os.mkdir(outDir)

# (2) 	Next, specify the x-coordinates of the line
startx = 0.015
endx = 0.02
N = 5 # number of points

# (3) Extract and save Lineout Data of the specified time index
tvals = np.array([320]) # time indices of file we want to visualize

for ti in tvals: # Iterate over all time ids
	fn('x01_rnec-' + str(ti) + '.vti','rnec',startx,endx,N,inDir,outDir,0)
	fn('x01_Bvec-' + str(ti) + '.vti','Bvec',startx,endx,N,inDir,outDir,1)
	fn('x01_jvec-' + str(ti) + '.vti','jvec',startx,endx,N,inDir,outDir,1)
	fn('x01_vvec-' + str(ti) + '.vti','vvec',startx,endx,N,inDir,outDir,1)
	fn('x01_array_pres-' + str(ti) + '.vti','array_pres',startx,endx,N,inDir,outDir,0)
	fn('x01_Ti' + str(ti) + '.vti','Ti',startx,endx,N,inDir,outDir,0)
	fn('x01_Te' + str(ti) + '.vti','Te',startx,endx,N,inDir,outDir,0)
	

