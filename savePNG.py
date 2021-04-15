from paraview.simple import *
import os
import sys
import numpy as np

# ~ This script loads 2D or 3D .vti  surface data output from GORGON into Paraview,
# ~ visualizes the number density on a log scale and saves the visualization as .PNG
# Usage:
# e.g. pvpython /path/to/file/savePNG.py 

Disconnect()
Connect()

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

def saveCurrentDataAsPNG(inputDir,fn,repType,outDir):
	# inputDir = input directoru
	# fn = file name
	# repType = representation type, 'Volume' for 3D, 'Surface' for 2D

	density = XMLImageDataReader(FileName=[inputDir + fn]) # Load the number density
	density.CellArrayStatus = ['rnec']
	# Show
	renderView1 = GetActiveViewOrCreate('RenderView')
	renderView1.ViewSize = [800,800]
	densityDisplay = Show(density, renderView1)
	ColorBy(densityDisplay, ('CELLS', 'rnec'))
	densityDisplay.SetRepresentationType(repType)
	densityDisplay.SetScalarBarVisibility(renderView1, True)
	rnecLUT = GetColorTransferFunction('rnec')
	LoadPalette(paletteName='BlackBackground')
	rnecLUT.MapControlPointsToLogSpace()
	rnecLUT.UseLogScale = 1 # Toggle for log scale or linear scale
	rnecLUT.RescaleTransferFunction(n_min, n_max)
	rnecLUT.ApplyPreset('Inferno (matplotlib)', True)
	
	if (repType == 'Volume'):
		# Camera 
		renderView1.ResetCamera()
		camera=GetActiveCamera()
		camera.SetFocalPoint(0,0,0)
		# End-On
		camera.SetPosition(0,0,0.2)
		camera.SetViewUp(0,1,0)
		# ~ # Side-On # Uncomment for side-on
		# ~ camera.Pitch(90)
		# Ortho
		camera.Pitch(45)  # Un-comment for orthogonal
		
		ResetCamera()
		camera.Dolly(1.5)
	Render()
	
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
	saveCurrentDataAsPNG(inputDir,fn,'Volume',outDir)




