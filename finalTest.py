import vtk
import numpy as np
from sklearn.cluster import KMeans
from skimage import morphology
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import time

# Function to estimate and display time left during execution
def long_running_task(total_steps):
    print("Task started...")
    start_time = time.time()  # Record the start time

    for step in range(1, total_steps + 1):
        elapsed_time = time.time() - start_time
        remaining_time = (elapsed_time / step) * (total_steps - step)
        print(f"Step {step}/{total_steps} completed. Estimated time left: {remaining_time:.2f} seconds")

    print("Task completed!")

# DICOM Reader
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName('D:\\DIcom gans\\Data\\raw')
reader.Update()

# Start long-running task for DICOM reading
long_running_task(1)  # Single step for loading data

# Get the image data
imageData = reader.GetOutput()

# Extract voxel data as a NumPy array
extent = imageData.GetExtent()
spacing = imageData.GetSpacing()
dimensions = (extent[1] - extent[0] + 1, extent[3] - extent[2] + 1, extent[5] - extent[4] + 1)
voxelData = vtk_to_numpy(imageData.GetPointData().GetScalars())
voxelData = voxelData.reshape(dimensions, order='F')

# Normalize the voxel intensities
voxelData = (voxelData - np.min(voxelData)) / (np.max(voxelData) - np.min(voxelData))

# Reshape voxel data for K-means clustering
voxelFlat = voxelData.ravel().reshape(-1, 1)

# Apply K-means clustering to separate intensities into teeth and background
kmeans = KMeans(n_clusters=3, random_state=0)  # Adjust clusters based on data
kmeans.fit(voxelFlat)
clustered = kmeans.labels_.reshape(voxelData.shape)

# Determine the cluster corresponding to teeth by intensity mean
cluster_means = [voxelData[clustered == i].mean() for i in range(3)]
teeth_cluster = np.argmax(cluster_means)  # Cluster with highest intensity

# Create a binary mask for teeth
teeth_mask = (clustered == teeth_cluster).astype(np.uint8)

# Apply morphological operations to refine the mask
teeth_mask = morphology.binary_closing(teeth_mask, morphology.ball(3))
teeth_mask = morphology.binary_opening(teeth_mask, morphology.ball(2))

# Convert the processed mask back to VTK format
segmentedArray = teeth_mask.astype(np.uint8)
segmentedVTKData = numpy_to_vtk(num_array=segmentedArray.ravel(order='F'), deep=True)
segmentedImageData = vtk.vtkImageData()
segmentedImageData.SetDimensions(dimensions)
segmentedImageData.SetSpacing(spacing)
segmentedImageData.GetPointData().SetScalars(segmentedVTKData)

# Start long-running task for rendering and resampling
long_running_task(3)  # Simulating multi-step task

# Resample the volume for better resolution
resampler = vtk.vtkImageReslice()
resampler.SetInputData(segmentedImageData)
resampler.SetOutputSpacing(0.180311183, 0.180311183, 0.18031118)
resampler.SetInterpolationModeToLinear()
resampler.Update()

resampledData = resampler.GetOutput()

# Volume Mapper for visualization
volumeMapper = vtk.vtkSmartVolumeMapper()
volumeMapper.SetInputData(resampledData)

# Volume Properties
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetInterpolationTypeToLinear()
volumeProperty.ShadeOn()

# Adjust opacity and color functions for teeth visualization
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(0, 0.0)
opacityTransferFunction.AddPoint(1, 1.0)  # Teeth regions are 1 after segmentation

colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0, 0.0, 0.0, 0.0)  # Background is black
colorTransferFunction.AddRGBPoint(1, 1.0, 1.0, 1.0)  # Teeth are white

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

# Interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Camera settings
camera = renderer.GetActiveCamera()
camera.SetViewUp(0, 0, -1)
camera.SetPosition(-500, -500, 500)
camera.SetFocalPoint(0, 0, 0)
renderer.ResetCamera()

# Start rendering
renderWindow.Render()
renderWindowInteractor.Start()

print("Rendering completed.")
