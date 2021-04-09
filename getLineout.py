from paraview.simple import *
import os
import sys

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

# (1) 	Specify the directory which contains the .vti data output from GORGON
inDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_20_Al_2D-3/' # Input directory 
outDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_20_Al_2D-3/LineOut/' # Output Directory
if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
	os.mkdir(outDir)

# (2) 	Next, specify the origina nd end points of the line
p0 = [0.012, 0.0, 0.0]  # Position of Point 1
p1 =  [0.03,0.0,0.0] # Position of Point 2

# (3) Extract and save Lineout Data 
tvals = np.array([80,160,240,320,400]) # time indices of file we want to visualize

for ti in tvals:
	getLineout('x01_rnec-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Number denisty
	getLineout('x01_vvec-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Velocity
	getLineout('x01_Bvec-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Magnetic Field	
	getLineout('x01_array_pres-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Pressure	
	getLineout('x01_rho-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Mass density
	getLineout('x01_Ti-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Ion Temp.
	getLineout('x01_Te-' + str(ti) + '.vti',p0,p1,inDir,outDir) # Electron Temp.



