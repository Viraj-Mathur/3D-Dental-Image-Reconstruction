import vtk
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
import matplotlib.pyplot as plt

# Function to generate synthetic ground truth for evaluation
def generate_ground_truth(image_data):
    dims = image_data.GetDimensions()
    synthetic_data = np.random.randint(0, 256, size=(dims[2], dims[1], dims[0]), dtype=np.uint8)
    return synthetic_data

# Convert VTK image data to NumPy array
def vtk_to_numpy(image_data):
    dims = image_data.GetDimensions()
    numpy_data = vtk.util.numpy_support.vtk_to_numpy(image_data.GetPointData().GetScalars())
    numpy_data = numpy_data.reshape(dims[2], dims[1], dims[0])
    return numpy_data

# Create the DICOM reader
reader = vtk.vtkDICOMImageReader()
reader.SetDirectoryName('D:\\downloads\\GUI Code\\CAPSTONE\\DIcom gans\\Data\\raw')
reader.Update()

# Get the image data from the reader
image_data = reader.GetOutput()

# Resample the volume to your extracted voxel size using vtkImageReslice
resampler = vtk.vtkImageReslice()
resampler.SetInputData(image_data)
resampler.SetOutputSpacing(0.180311183, 0.180311183, 0.18031118)  # Voxel size from your log
resampler.SetInterpolationModeToLinear()
resampler.Update()

resampled_data = resampler.GetOutput()

# Convert resampled VTK data to NumPy array
resampled_numpy = vtk_to_numpy(resampled_data)

# Generate synthetic ground truth data for evaluation
ground_truth = generate_ground_truth(resampled_data)

# Evaluate metrics
accuracy = np.mean(resampled_numpy == ground_truth) * 100  # Simplified metric for demonstration
psnr_value = psnr(ground_truth, resampled_numpy, data_range=255)
ssim_value = ssim(ground_truth, resampled_numpy, data_range=255, multichannel=False)

print(f"Accuracy: {accuracy:.2f}%")
print(f"PSNR: {psnr_value:.2f}")
print(f"SSIM: {ssim_value:.4f}")

# Plotting the metrics
metrics = ["Accuracy", "PSNR", "SSIM"]
values = [accuracy, psnr_value, ssim_value]

plt.figure(figsize=(8, 6))
plt.bar(metrics, values, color=['blue', 'orange', 'green'])
plt.title("Model Evaluation Metrics")
plt.ylabel("Values")
plt.ylim(0, 100)
plt.show()

# Additional Notes:
# The ground truth here is synthetic and generated for evaluation purposes.
# Replace it with actual ground truth data if available for more accurate evaluation.
