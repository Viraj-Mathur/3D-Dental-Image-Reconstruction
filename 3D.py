import os
import vtk

# Directory containing the DICOM files
dicom_dir = 'D:\\DIcom gans\\Data\\raw'

# Create the DICOM reader
reader = vtk.vtkDICOMImageReader()

# Manually iterate over the files to identify problematic files
valid_files = []
for file in os.listdir(dicom_dir):
    if file.endswith('.dcm'):
        reader.SetFileName(os.path.join(dicom_dir, file))
        try:
            reader.Update()
            valid_files.append(os.path.join(dicom_dir, file))
        except Exception as e:
            print(f"Skipping problematic file: {file}, Error: {str(e)}")

if not valid_files:
    print("No valid DICOM files found or all files are problematic.")
    exit()

# Load the valid DICOM files
reader.SetDirectoryName(dicom_dir)
reader.Update()

# Check if the reader successfully loaded the data
imageData = reader.GetOutput()
if imageData.GetNumberOfPoints() == 0:
    print("Failed to load DICOM data. Please check the directory path.")
    exit()

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
