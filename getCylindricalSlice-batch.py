# ~ This script loads .vti or .vtk 3D volume data at specified time-instances into Paraview,
# ~ creates cylindrical slices, and integrates the values over the slice area to determine the
# ~ average value at the radial position. 
# ~ For vector data, an addition step calculates the magnitude of the vector first.
# Usage:
# pvpython getCylindricalSlice-batch.py dataSet dname isVector 
# e.g. pvpython /path/to/file/getCylindricalSlice-batch.py 
from paraview.simple import *
import numpy as np
import os
import sys

def processAtSlice(data,arrName,r):
	# This function:
	# (1) creates a cylindrical slice of radius r 
	# (2) Clips the cylindrical slice in the axial direction to [z_lower, z_upper]
	# (3) Integrates the data over the slice and divides by area
	# (4) Returns value averaged over slice
	slice1 = Slice(Input=data)
	slice1.SliceType = 'Plane'
	slice1.SliceType.Origin = [0.0, 0.0, 0.0]
	slice1.SliceType = 'Cylinder'
	slice1.SliceType.Axis = [0.0, 0.0, 1.0]
	slice1.SliceType.Radius = r
	#Clip 
	clip1 = Clip(Input=slice1)
	clip1.ClipType = 'Plane'
	clip1.Scalars = ['CELLS', arrName]
	clip1.ClipType.Normal = [0.0, 0.0, 1.0]
	clip1.ClipType.Origin = [0.0, 0.0, z_upper]
	#Clip 
	clip2 = Clip(Input=clip1)
	clip2.ClipType = 'Plane'
	clip2.Scalars = ['CELLS', arrName]
	clip2.ClipType.Normal = [0.0, 0.0, -1.0]
	clip2.ClipType.Origin = [0.0, 0.0, z_lower]
	# Integrate
	integrateVariables1 = IntegrateVariables(Input=clip2)
	integrateVariables1.DivideCellDataByVolume = 1
	out = paraview.servermanager.Fetch(integrateVariables1)
	# destroy 
	Delete(slice1)
	Delete(clip1)
	Delete(clip2)
	Delete(integrateVariables1)
	del slice1,clip1,clip2,integrateVariables1
	# Return result
	return (out.GetCellData().GetArray(arrName).GetValue(0)) # Averaged result
def processAllSlices(data,arrName):
	# This function calculates raddi at which to create slices
	# then calculates the verage value at each slice
	r = np.linspace(rmin,rmax,N) # radii to process
	val = np.zeros(r.size) # array conating averaged data
	for ii in range(N):
		print('Processing slice ' + str(ii+1) + '/' + str(N) + '...')
		val[ii] = processAtSlice(data,arrName,r[ii])
	return r,val
def getVectorMagnitude(data,dataSet):
	# calculate vector magnitude
	calculator1 = Calculator(Input=data)
	calculator1.AttributeType = 'Cell Data'
	calculator1.ResultArrayName = 'Vmag' # Outputs the magnitude of the vector
	calculator1.Function = 'mag(' + dataSet + ')'
	return calculator1	
def fn(dataSet,dname,isVector,ftype):
	for jj in tid:
		fname = 'x01_' + dataSet + '-' + str(jj) # file to open
		print('Reading ' + fname + '....')
		
		# Load data
		if (ftype == '.vtk'):
			data = LegacyVTKReader(FileNames=[inDir + fname + ftype]) # read vtk data
		elif (ftype == '.vti'):
			data = XMLImageDataReader(FileName=[inDir + fname + ftype])  # read vti file
		else:
			print("Error: Invalid file type")
		
		if isVector: # caculate vector magnitude if vector data
			Vmag = getVectorMagnitude(data,dataSet)
			r,val = processAllSlices(Vmag,'Vmag') # Process slices for vector magnitude
			Delete(Vmag)
			del Vmag
		else:
			r,val = processAllSlices(data,dataSet) # Process slices for scalar data	
				
		# Save as csv
		if (not os.path.isdir(outDir + dname + '/')): # create output dir if it doesn't exist
			os.mkdir(outDir + dname + '/')
		out = np.column_stack((r,val))
		np.savetxt(outDir + dname + '/'+ fname + '.csv' ,out,fmt='%1.5e', delimiter=',')
		# Delete current data
		Delete(data)
		del data
	print('Done')

# Input and Output directory
inDir = '/path/to/file/Macros/paraview-post-process/'  # Input dir
outDir = '/path/to/file/Other/'  # Output dir
if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
	os.mkdir(outDir)

# Global Parameters
z_lower, z_upper = 6e-3, 50-3 # bottom and top of cylinder
rmin, rmax = 10e-3, 48e-3 # min and max radii
N = 10  # number of slices
tid = np.array([0,1]) # time id
fn('rnec','Electron Density',0,'.vti') # fn(dataSetName, dataType, isVector = 0 or 1, filetype = 'vti' or '.vtk')
fn('rho','Mass Density',0,'.vti')
fn('array_pres','Pressure',0,'.vti')
fn('vvec','Velocity',1,'.vti')
fn('Bvec','Magnetic Field',1,'.vti')
fn('jvec','Current Density',1,'.vti')
fn('Ti','Ti',0,'.vti')
fn('Te','Te',0,'.vti')
