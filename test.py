import vtk

# Create the DICOM reader
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName('D:\\DIcom gans\\Data\\raw')
reader.Update()

# Get the image data from the reader
imageData = reader.GetOutput()

# Resampling the volume to your extracted voxel size using vtkImageReslice
resampler = vtk.vtkImageReslice()
resampler.SetInputData(imageData)
resampler.SetOutputSpacing(0.180311183, 0.180311183, 0.18031118)  # Voxel size from your log
resampler.SetInterpolationModeToLinear()
resampler.Update()

resampledData = resampler.GetOutput()

# Set up the volume mapper using the resampled data
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputData(resampledData)

# Volume properties for visualization, adjusted to your specific data characteristics
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# Opacity and color transfer functions, which may need to be fine-tuned to your data
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
renderer.SetBackground(0, 0, 0)  # Black background

# Render window setup
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 800)

# Render window interactor setup
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Add an implicit plane to clip the volume
plane = vtk.vtkPlane()
plane.SetOrigin(0, 0, 0)
plane.SetNormal(1, 0, 0)  # Adjust normal direction to control the slicing plane

# Create an implicit plane widget
planeWidget = vtk.vtkImplicitPlaneWidget2()
planeRep = vtk.vtkImplicitPlaneRepresentation()
planeRep.SetPlaceFactor(1.25)  # Control how far the plane can be moved
planeRep.PlaceWidget(volume.GetBounds())
planeRep.SetOrigin(0, 0, 0)
planeRep.SetNormal(1, 0, 0)
planeWidget.SetRepresentation(planeRep)
planeWidget.SetInteractor(renderWindowInteractor)

# Function to update the clipping plane
def clip_volume_callback(widget, event):
    planeRep.GetPlane(plane)
    volumeMapper.RemoveAllClippingPlanes()
    volumeMapper.AddClippingPlane(plane)

# Add observer to update the clipping plane
planeWidget.AddObserver("InteractionEvent", clip_volume_callback)
planeWidget.On()

# Camera settings for a better view angle
camera = renderer.GetActiveCamera()
camera.SetViewUp(0, 0, -1)
camera.SetPosition(-500, -500, 500)
camera.SetFocalPoint(0, 0, 0)
renderer.ResetCamera()

# Start the interaction
renderWindow.Render()
renderWindowInteractor.Start()