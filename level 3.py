import vtk
import numpy as np
from skimage import filters, morphology
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import os
import matplotlib.pyplot as plt

# Load DICOM images
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName(r'D:\\downloads\\GUI Code\\CAPSTONE\\DIcom gans\\Data\\raw')  # Update with your DICOM folder path
reader.Update()

# Extract image data
imageData = reader.GetOutput()
extent = imageData.GetExtent()
spacing = imageData.GetSpacing()
dimensions = (extent[1] - extent[0] + 1, extent[3] - extent[2] + 1, extent[5] - extent[4] + 1)

# Convert image data to NumPy array
voxelData = vtk_to_numpy(imageData.GetPointData().GetScalars())
voxelData = voxelData.reshape(dimensions, order='F')

# Normalize voxel data
voxelData = (voxelData - np.min(voxelData)) / (np.max(voxelData) - np.min(voxelData))

# Apply intensity thresholding to isolate teeth (adjust thresholds)
low_threshold = 0.4  # Adjust based on intensity distribution for teeth
high_threshold = 0.8  # Adjust for the upper bound
teeth_mask = np.logical_and(voxelData > low_threshold, voxelData < high_threshold)

# Apply Gaussian smoothing to refine mask
smoothed_mask = filters.gaussian(teeth_mask, sigma=2.0) > 0.5  # Increase sigma for smoother transitions

# Apply morphological closing to fill small holes
refined_mask = morphology.binary_closing(smoothed_mask, morphology.ball(3))  # Increase size of structuring element

# Further morphological operations for refinement
refined_mask = morphology.binary_dilation(refined_mask, morphology.ball(1))  # Dilation to preserve structures

# Convert refined mask back to VTK
segmentedArray = refined_mask.astype(np.uint8)
segmentedVTKData = numpy_to_vtk(segmentedArray.ravel(order='F'), deep=True)
segmentedImageData = vtk.vtkImageData()
segmentedImageData.SetDimensions(dimensions)
segmentedImageData.SetSpacing(spacing)
segmentedImageData.GetPointData().SetScalars(segmentedVTKData)

# PSNR Calculation
def calculate_psnr(original, reconstructed):
    # Ensure the images are the same size
    assert original.shape == reconstructed.shape, "Original and reconstructed images must have the same dimensions"
    
    # Compute Mean Squared Error (MSE)
    mse = np.mean((original - reconstructed) ** 2)
    if mse == 0:
        return float('inf')  # No noise, perfect reconstruction
    
    # Compute PSNR
    max_pixel = 1.0  # Since the images are normalized between 0 and 1
    psnr_value = 10 * np.log10((max_pixel ** 2) / mse)
    return psnr_value

# Compute PSNR for the whole dataset
psnr_values = []
for i in range(dimensions[2]):  # Iterate over slices (z-axis)
    original_slice = voxelData[:, :, i]
    reconstructed_slice = refined_mask[:, :, i].astype(np.float32)  # Ensure the mask is float for PSNR calculation
    psnr_value = calculate_psnr(original_slice, reconstructed_slice)
    psnr_values.append(psnr_value)

# Plot PSNR Graph
plt.figure(figsize=(10, 6))
plt.plot(np.arange(dimensions[2]), psnr_values, marker='o', color='b')
plt.title("PSNR Values Across Slices")
plt.xlabel("Slice Number")
plt.ylabel("PSNR (dB)")
plt.grid(True)
plt.show()

# Volume Mapper for visualization
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputData(segmentedImageData)

# Volume Properties
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetInterpolationTypeToLinear()
volumeProperty.ShadeOn()

# Adjust opacity and color transfer functions
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(0, 0.0)  # Background is transparent
opacityTransferFunction.AddPoint(1, 1.0)  # Teeth are fully opaque

colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0, 0.0, 0.0, 0.0)  # Black for background
colorTransferFunction.AddRGBPoint(1, 1.0, 1.0, 1.0)  # White for teeth

volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.SetColor(colorTransferFunction)

# Volume Actor
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

# Renderer
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)
renderer.SetBackground(0, 0, 0)  # Black background

# Render Window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 800)

# Camera settings for better viewing
camera = renderer.GetActiveCamera()
camera.SetViewUp(0, 0, -1)
camera.SetPosition(-200, -200, 300)
camera.SetFocalPoint(0, 0, 0)
renderer.ResetCamera()

# Export rendering as PNG
export_folder = "./static/vtk"
if not os.path.exists(export_folder):
    os.makedirs(export_folder)

output_path = os.path.join(export_folder, "dental_structure.png")

exporter = vtk.vtkWindowToImageFilter()
exporter.SetInput(renderWindow)
exporter.Update()

writer = vtk.vtkPNGWriter()
writer.SetFileName(output_path)
writer.SetInputData(exporter.GetOutput())
writer.Write()

print(f"Dental structure 3D model saved as {output_path}.")

# Render Window Interactor for interactive visualization
renderWindow.Render()
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

print("Interactive model rendering started...")
renderWindowInteractor.Start()