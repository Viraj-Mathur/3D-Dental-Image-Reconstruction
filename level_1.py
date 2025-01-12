import numpy as np
import pydicom
from sklearn.cluster import KMeans
from skimage import morphology
from skimage.transform import resize
import pyvista as pv


# Step 1: Extract and Normalize DICOM Data
def extract_dicom_features(directory):
    """
    Extracts 3D volume and metadata from DICOM files in a directory.
    """
    import os

    # Read DICOM files
    files = sorted([os.path.join(directory, f) for f in os.listdir(directory)])
    slices = [pydicom.dcmread(file) for file in files]

    # Stack slices to form a 3D volume
    volume = np.stack([s.pixel_array for s in slices], axis=-1).astype(np.float32)

    # Extract metadata
    pixel_spacing = slices[0].PixelSpacing  # [x, y]
    slice_thickness = slices[0].SliceThickness  # z
    spacing = (*pixel_spacing, slice_thickness)  # Spacing for all three dimensions

    print(f"Pixel Spacing: {pixel_spacing}, Slice Thickness: {slice_thickness}")
    return volume, spacing


# Step 2: Normalize the Volume Data
def normalize_volume(volume):
    """
    Normalizes the volume intensities to the range [0, 1].
    """
    return (volume - np.min(volume)) / (np.max(volume) - np.min(volume))


# Step 3: Apply K-Means Clustering
def apply_kmeans(volume, n_clusters=3):
    """
    Applies K-Means clustering to the flattened volume data.
    """
    voxel_flat = volume.ravel().reshape(-1, 1)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(voxel_flat)
    clustered = kmeans.labels_.reshape(volume.shape)

    # Determine the cluster corresponding to teeth by intensity
    cluster_means = [volume[clustered == i].mean() for i in range(n_clusters)]
    teeth_cluster = np.argmax(cluster_means)

    # Create binary mask for teeth
    teeth_mask = (clustered == teeth_cluster).astype(np.uint8)
    return teeth_mask


# Step 4: Apply Morphological Operations
def refine_mask(mask):
    """
    Applies morphological operations to refine the segmentation mask.
    """
    mask = morphology.binary_closing(mask, morphology.ball(3))
    mask = morphology.binary_opening(mask, morphology.ball(2))
    return mask


# Step 5: Downsample the Volume
def downsample_volume(volume, scale_factor):
    """
    Downsamples the volume by a given scale factor.
    If the volume is boolean, it is cast to uint8 before resizing.
    """
    # Cast boolean volume to uint8
    if volume.dtype == np.bool_:
        volume = volume.astype(np.uint8)

    new_shape = (
        int(volume.shape[0] * scale_factor),
        int(volume.shape[1] * scale_factor),
        int(volume.shape[2] * scale_factor)
    )

    # Use interpolation order appropriate for the data type
    return resize(volume, new_shape, order=1, preserve_range=True, anti_aliasing=False)


# Step 6: Convert to PyVista Volume and Visualize
def visualize_volume(mask, spacing, scale_factor=0.5):
    """
    Visualizes the 3D volume using PyVista with downsampling to optimize memory usage.
    """
    # Downsample the mask for memory efficiency
    downsampled_mask = downsample_volume(mask, scale_factor)

    # Ensure the mask is normalized
    downsampled_mask = (downsampled_mask - downsampled_mask.min()) / (downsampled_mask.max() - downsampled_mask.min())

    # Adjust spacing for the downsampled data
    adjusted_spacing = [s * scale_factor for s in spacing[::-1]]

    # Create a PyVista ImageData
    grid = pv.ImageData()
    grid.dimensions = downsampled_mask.shape
    grid.spacing = adjusted_spacing  # Spacing corresponds to [z, y, x] in PyVista
    grid.point_data["Segmentation"] = downsampled_mask.ravel(order="F").astype(np.float32)

    # Debug information
    print(f"Grid dimensions: {grid.dimensions}")
    print(f"Grid spacing: {grid.spacing}")
    print(f"Unique values in the mask: {np.unique(downsampled_mask)}")

    # Render the volume
    plotter = pv.Plotter()
    plotter.add_volume(
        grid,
        cmap="viridis",  # Change to a preferred colormap
        opacity=[0, 1],  # Adjust opacity transfer function
        show_scalar_bar=True
    )
    plotter.show()




# Main Process
if __name__ == "__main__":
    # Step 1: Load DICOM Data
    dicom_directory = "D:\\downloads\\GUI Code\\CAPSTONE\\DIcom gans\\Data\\raw"  # Replace with your DICOM directory
    raw_volume, voxel_spacing = extract_dicom_features(dicom_directory)

    # Step 2: Normalize Volume
    normalized_volume = normalize_volume(raw_volume)

    # Step 3: Segment the Teeth Region
    teeth_mask = apply_kmeans(normalized_volume)

    # Step 4: Refine the Segmentation Mask
    refined_mask = refine_mask(teeth_mask)

    # Step 5: Visualize the 3D Mask with Downsampling
    visualize_volume(refined_mask, voxel_spacing, scale_factor=0.5)
