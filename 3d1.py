import vtk

# Create the DICOM reader
reader = vtk.vtkDICOMImageReader()
# reader.SetDirectoryName('/home/matrix/Viraj pc/Prev Sem/6TH SEM/CAPSTONE/CBCD DICOM 2/SHWETA')
reader.SetDirectoryName('D:\\DIcom gans\\Data\\raw')
# reader.SetDirectoryName('/home/matrix/Downloads/DIcom gans/Data/VOL_2')
reader.Update()

# Get the image data from the reader
imageData = reader.GetOutput()

# Set up the volume mapper using the raw image data
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputData(imageData)

# Volume properties for basic visualization
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# Simple opacity and color transfer functions
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(0, 0.0)
opacityTransferFunction.AddPoint(500, 0.15)
opacityTransferFunction.AddPoint(1000, 0.85)
opacityTransferFunction.AddPoint(1150, 1.0)

colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(500, 1.0, 0.5, 0.3)
colorTransferFunction.AddRGBPoint(1000, 1.0, 1.0, 0.9)
colorTransferFunction.AddRGBPoint(1150, 1.0, 1.0, 1.0)

volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.SetColor(colorTransferFunction)

# Set up the volume actor
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

# Renderer setup
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)
renderer.SetBackground(1, 1, 1)  # White background

# Render window setup
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 800)

# Render window interactor setup
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Camera settings for a better view angle
camera = renderer.GetActiveCamera()
camera.SetViewUp(0, 0, -1)
camera.SetPosition(-500, -500, 500)  # Far enough back to see the entire volume
camera.SetFocalPoint(0, 0, 0)
renderer.ResetCamera()

# Start the interaction
renderWindow.Render()
renderWindowInteractor.Start()
