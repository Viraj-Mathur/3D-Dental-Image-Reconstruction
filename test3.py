import vtk

# Create the DICOM reader
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName('D:\\DIcom gans\\Data\\raw')
reader.Update()

# Get the image data from the reader
imageData = reader.GetOutput()

# Resample the volume to match your extracted voxel size using vtkImageReslice
resampler = vtk.vtkImageReslice()
resampler.SetInputData(imageData)
resampler.SetOutputSpacing(0.180311183, 0.180311183, 0.18031118)  # Voxel size from your data
resampler.SetInterpolationModeToLinear()
resampler.Update()

resampledData = resampler.GetOutput()

# Set up the volume mapper
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputData(resampledData)

# Configure volume properties
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# Opacity and color transfer functions
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

# Create the volume actor
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

# Renderer setup
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)
renderer.SetBackground(0, 0, 0)  # Black background

# Render window setup
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 800)

# Render window interactor setup
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Create clipping planes for X, Y, and Z axes
xPlane = vtk.vtkPlane()
xPlane.SetOrigin(0, 0, 0)
xPlane.SetNormal(1, 0, 0)  # Normal along the X axis

yPlane = vtk.vtkPlane()
yPlane.SetOrigin(0, 0, 0)
yPlane.SetNormal(0, 1, 0)  # Normal along the Y axis

zPlane = vtk.vtkPlane()
zPlane.SetOrigin(0, 0, 0)
zPlane.SetNormal(0, 0, 1)  # Normal along the Z axis

# Add all clipping planes to the volume mapper
volumeMapper.AddClippingPlane(xPlane)
volumeMapper.AddClippingPlane(yPlane)
volumeMapper.AddClippingPlane(zPlane)

# Function to update clipping planes
def update_clipping_planes():
    volumeMapper.RemoveAllClippingPlanes()
    volumeMapper.AddClippingPlane(xPlane)
    volumeMapper.AddClippingPlane(yPlane)
    volumeMapper.AddClippingPlane(zPlane)

# Set up implicit plane widgets for X, Y, and Z axes
xPlaneWidget = vtk.vtkImplicitPlaneWidget2()
xPlaneRep = vtk.vtkImplicitPlaneRepresentation()
xPlaneRep.SetPlaceFactor(1.25)
xPlaneRep.PlaceWidget(volume.GetBounds())
xPlaneRep.SetNormal(1, 0, 0)
xPlaneWidget.SetRepresentation(xPlaneRep)
xPlaneWidget.SetInteractor(renderWindowInteractor)

yPlaneWidget = vtk.vtkImplicitPlaneWidget2()
yPlaneRep = vtk.vtkImplicitPlaneRepresentation()
yPlaneRep.SetPlaceFactor(1.25)
yPlaneRep.PlaceWidget(volume.GetBounds())
yPlaneRep.SetNormal(0, 1, 0)
yPlaneWidget.SetRepresentation(yPlaneRep)
yPlaneWidget.SetInteractor(renderWindowInteractor)

zPlaneWidget = vtk.vtkImplicitPlaneWidget2()
zPlaneRep = vtk.vtkImplicitPlaneRepresentation()
zPlaneRep.SetPlaceFactor(1.25)
zPlaneRep.PlaceWidget(volume.GetBounds())
zPlaneRep.SetNormal(0, 0, 1)
zPlaneWidget.SetRepresentation(zPlaneRep)
zPlaneWidget.SetInteractor(renderWindowInteractor)

# Callback functions for updating clipping planes
def x_plane_callback(widget, event):
    xPlaneRep.GetPlane(xPlane)
    update_clipping_planes()

def y_plane_callback(widget, event):
    yPlaneRep.GetPlane(yPlane)
    update_clipping_planes()

def z_plane_callback(widget, event):
    zPlaneRep.GetPlane(zPlane)
    update_clipping_planes()

# Add observers to update clipping planes when interacting with the widgets
xPlaneWidget.AddObserver("InteractionEvent", x_plane_callback)
yPlaneWidget.AddObserver("InteractionEvent", y_plane_callback)
zPlaneWidget.AddObserver("InteractionEvent", z_plane_callback)

# Enable the plane widgets
xPlaneWidget.On()
yPlaneWidget.On()
zPlaneWidget.On()

# Camera settings for a better view angle
camera = renderer.GetActiveCamera()
camera.SetViewUp(0, 0, -1)
camera.SetPosition(-500, -500, 500)
camera.SetFocalPoint(0, 0, 0)
renderer.ResetCamera()

# Start the interaction
renderWindow.Render()
renderWindowInteractor.Start()