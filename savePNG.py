from paraview.simple import *
import os
import sys
import numpy as np

# ~ This script loads 2D .vti  surface data output from GORGON into Paraview,
# ~ visualizes the number density on a log scale and saves the visualization as .PNG
# Usage:
# e.g. pvpython /path/to/file/savePNG.py 

Disconnect()
Connect()

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

def saveCurrentDataAsPNG(inputDir,fn,outDir):

	density = XMLImageDataReader(FileName=[inputDir + fn]) # Load the number density
	density.CellArrayStatus = ['rnec']
	# Show
	renderView1 = GetActiveViewOrCreate('RenderView')
	densityDisplay = Show(density, renderView1)
	ColorBy(densityDisplay, ('CELLS', 'rnec'))
	densityDisplay.SetRepresentationType('Surface')
	densityDisplay.SetScalarBarVisibility(renderView1, True)
	rnecLUT = GetColorTransferFunction('rnec')
	LoadPalette(paletteName='BlackBackground')
	rnecLUT.MapControlPointsToLogSpace()
	rnecLUT.UseLogScale = 1
	rnecLUT.RescaleTransferFunction(n_min, n_max)
	rnecLUT.ApplyPreset('Inferno (matplotlib)', True)
	
	# reset view to fit data
	renderView1.ResetCamera()
	camera=GetActiveCamera()
	
	# Save
	SaveScreenshot(outDir + fn[0:len(fn)-4]  + '.png', renderView1)
	print('Saved to ' + outDir + fn[0:len(fn)-4]  + '.png')
	
	Delete(density)
	del density
	

# ~ # (1) 	Specify the directory which contains the .vti data output from GORGON
# ~ # 		and the fnames of the density, velocity and magnetic field data
inputDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_20_Al_2D-2/' # Input directory 
outDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_20_Al_2D-2/images/' # Output Directory
tvals = np.arange(0,80,10) # time indices of file we want to visualize
n_min, n_max = 1e20, 1e25 # number density range to show

if (not os.path.isdir(outDir)): # create output dir if it doesn't exist
	os.mkdir(outDir)

for ti in tvals:
	fn = 'x00_rnec-' + str(ti) + '.vti' # Filename, number density
	saveCurrentDataAsPNG(inputDir,fn,outDir)




