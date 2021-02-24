from paraview.simple import *
import os
import sys

# ~ This function loads the specified VTI data, creates a planar slice and 
# ~ then saves the slice data as a CSV file. p0 and n0 are the slice origin
# ~ and normal respectively.
# Usage:
# pvpython /path/to/file/getPlanarSliceData.py

# New Session

Disconnect()
Connect()

def saveSliceAsCSV(fname,slice_origin,slice_nrm,inDir,outDir):
	 # Inputs:
	 # fname = VTI file name 
	 # slice_origin = [3x1] origin of slice
	 # slice_nrm = [3x1] slice normal
	 # inDir = input file directory
	 # outDir = output file directory
		 
	# Load data
	data = XMLImageDataReader(FileName=[inDir + fname])  # read vti file
	# Create the slice
	slice1 = Slice(Input=data)
	slice1.SliceType = 'Plane'
	slice1.SliceOffsetValues = [0.0]
	slice1.SliceType.Origin = slice_origin
	slice1.SliceType.Normal = slice_nrm
	# Convert to point data
	out = CellDatatoPointData(Input=slice1)
	# Export slice data
	if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
		os.mkdir(outDir)
	SaveData(outDir + fname[0:len(fname)-4] + '-slice.csv', proxy=out, FieldAssociation='Points')
	print ('Saved to ' + outDir + fname[0:len(fname)-4] + '-slice.csv')
		
# (1) 	Specify the directory which contains the .vti data output from GORGON
#  		and the fnames of the density, velocity and magnetic field data
inDir = '/path/to/VTIfiles/' # Input directory 
outDir = '/path/to/save/CSV/' # Output Directory
if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
	os.mkdir(outDir)

# (2) 	Next, specify the location and direction of the slice we want
p0 = [0.0, 0.0, 0.017]  # Location of slice
n0 =  [0.0,0.0,1.0] # slice normal

# (3) Save Slice Data 
saveSliceAsCSV('x01_rnec-240.vti',p0,n0,inDir,outDir) 
saveSliceAsCSV('x01_vvec-240.vti',p0,n0,inDir,outDir)
saveSliceAsCSV('x01_Bvec-240.vti',p0,n0,inDir,outDir)


