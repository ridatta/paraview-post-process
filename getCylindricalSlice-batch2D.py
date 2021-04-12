# ~ This script loads .vti or .vtk 3D volume data at specified time-instances into Paraview,
# ~ creates cylindrical slices, and integrates the values over the slice area to determine the
# ~ azimuthal average value at the radial position. 
# ~ For vector data, an addition step calculates the magnitude of the vector first.
# ~ You can also choose to keep the right half or left half of image
# Usage:
# pvpython getCylindricalSlice-batch.py dataSet dname isVector 
# e.g. pvpython getCylindricalSlice-batch2D.py 
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
		
	# Integrate
	slice1 = Slice(Input=data)
	slice1.SliceType = 'Plane'
	slice1.SliceType.Origin = [0.0, 0.0, 0.0]
	slice1.SliceType = 'Cylinder'
	slice1.SliceType.Axis = [0.0, 0.0, 1.0]
	slice1.SliceType.Radius = r
	
	#Clip 
	if clip_half:
		clip1 = Clip(Input=slice1)
		clip1.ClipType = 'Plane'
		clip1.Scalars = ['CELLS', arrName]
		clip1.ClipType.Normal = [1.0, 0.0, 0.0] # 1 to keep left half, -1 to keep right half
		clip1.ClipType.Origin = [0.0, 0.0, 0.0]
		temp = clip1
	else:
		temp = slice1
	
	integrateVariables1 = IntegrateVariables(Input=temp)
	integrateVariables1.DivideCellDataByVolume = 1
	out = paraview.servermanager.Fetch(integrateVariables1)
	# destroy 
	Delete(slice1)
	Delete(integrateVariables1)
	Delete(temp)
	del slice1,integrateVariables1,temp
	if clip_half:
		Delete(clip1)
		del clip1
	
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
		# Load data - for weighted dataSets
		if (dataSet == 'neTi'):
			fname_ne = 'x01_' + 'rnec' + '-' + str(jj) # file to open
			fname_Ti = 'x01_' + 'Ti' + '-' + str(jj) # file to open
			fname = 'x01_' + dataSet + '-' + str(jj) # file to open
			print('Reading ' + fname_ne + '....')
			print('Reading ' + fname_Ti + '....')
			if (ftype == '.vtk'):
				data1 = LegacyVTKReader(FileNames=[inDir + fname_ne + ftype]) # read vtk data
				data2 = LegacyVTKReader(FileNames=[inDir + fname_Ti + ftype]) # read vtk data
			elif (ftype == '.vti'):
				data1 = XMLImageDataReader(FileName=[inDir + fname_ne + ftype])  # read vti file
				data2 = XMLImageDataReader(FileName=[inDir + fname_Ti + ftype])  # read vti file
			else:
				print("Error: Invalid file type")
			data = multiplyDatasets(data1,data2,'rnec','Ti','neTi')  # get multiplied dataSet
			
		elif (dataSet == 'neTe'):
			fname_ne = 'x01_' + 'rnec' + '-' + str(jj) # file to open
			fname_Te = 'x01_' + 'Te' + '-' + str(jj) # file to open
			fname = 'x01_' + dataSet + '-' + str(jj) # file to open
			print('Reading ' + fname_ne + '....')
			print('Reading ' + fname_Te + '....')
			if (ftype == '.vtk'):
				data1 = LegacyVTKReader(FileNames=[inDir + fname_ne + ftype]) # read vtk data
				data2 = LegacyVTKReader(FileNames=[inDir + fname_Te + ftype]) # read vtk data
			elif (ftype == '.vti'):
				data1 = XMLImageDataReader(FileName=[inDir + fname_ne + ftype])  # read vti file
				data2 = XMLImageDataReader(FileName=[inDir + fname_Te + ftype])  # read vti file
			else:
				print("Error: Invalid file type")
			data = multiplyDatasets(data1,data2,'rnec','Te','neTe')  # get multiplied dataSet
			
		else:  # Load for single dataset
			fname = 'x01_' + dataSet + '-' + str(jj) # file to open
			print('Reading ' + fname + '....')
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
def multiplyDatasets(data1,data2,arrName1,arrName2,outName):
	# ~ Inputs:
		# ~ data1 = data set 1
		# ~ data2 = data set 2
		# ~ arrName1 = array in data1 we want 
		# ~ arrName2 = array in data2 we want
		# ~ outName = name of output array
	# Create programmable filter
	PF1 = ProgrammableFilter(Input=[data1, data2])
	PF1.Script = "import numpy as np \n" \
	"a1 = inputs[0].CellData['" + arrName1 + "'] \n" \
	"a2 = inputs[1].CellData['" + arrName2 + "'] \n" \
	"out = np.multiply(a1,a2) \n" \
	"output.CellData.append(out,'"+outName+"')"
	return PF1
	
Disconnect()
Connect()
# Input and Output directory
inDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_16_Al_2D-9/'  # Input dir
outDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_16_Al_2D-9/CSV/'  # Output dir
if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
	os.mkdir(outDir)

# Global Parameters
rmin, rmax = 10e-3, 30e-3 # min and max radii
N = 10  # number of slices
tid = np.array([320]) # time id
clip_half = 1 # Set to true if you want to keep only the left half
fn('Ti','Ti',0,'.vti')
fn('neTi','neTi',0,'.vti')
fn('rnec','Electron Density',0,'.vti')
