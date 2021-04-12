from paraview.simple import *
import numpy as np
import os
import sys

# Multiplies arrays contained in two seprate datasets

Disconnect()
Connect()

inDir = '/Users/Rishabh/Dropbox (MIT)/PUFFIN/Simulations/Gorgon/mag_ex_16_Al_2D-9/'
data1 = XMLImageDataReader(FileName=[inDir + 'x01_rnec-320' + '.vti'])  # read vti file
data2 = XMLImageDataReader(FileName=[inDir + 'x01_Ti-320' + '.vti'])  # read vti file

arrName1 = 'rnec'
arrName2 = 'Ti'
outName = 'neTi'
# Create programmable filter
PF1 = ProgrammableFilter(Input=[data1, data2])
PF1.Script = "import numpy as np \n" \
"a1 = inputs[0].CellData['" + arrName1 + "'] \n" \
"a2 = inputs[1].CellData['" + arrName2 + "'] \n" \
"out = np.multiply(a1,a2) \n" \
"output.CellData.append(out,'"+outName+"')"
