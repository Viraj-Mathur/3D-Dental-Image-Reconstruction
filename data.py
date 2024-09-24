import pydicom
import os
import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_dicom_info(filepath):
    try:
        ds = pydicom.dcmread(filepath)
        
        return {
            'SOPInstanceUID': ds.get('SOPInstanceUID', None),
            'SeriesInstanceUID': ds.get('SeriesInstanceUID', None),
            'StudyInstanceUID': ds.get('StudyInstanceUID', None),
            'PatientID': ds.get('PatientID', None),
            'Modality': ds.get('Modality', None),
            # Spatial Information
            'ImagePositionPatient': ds.get('ImagePositionPatient', None),
            'ImageOrientationPatient': ds.get('ImageOrientationPatient', None),
            'SliceLocation': ds.get('SliceLocation', None),
            'FrameOfReferenceUID': ds.get('FrameOfReferenceUID', None),
            'PositionReferenceIndicator': ds.get('PositionReferenceIndicator', None),
            # Dimension Information
            'PixelSpacing': ds.get('PixelSpacing', None),
            'SliceThickness': ds.get('SliceThickness', None),
            'SpacingBetweenSlices': ds.get('SpacingBetweenSlices', None),
            'Rows': ds.get('Rows', None),
            'Columns': ds.get('Columns', None),
            'NumberOfFrames': ds.get('NumberOfFrames', None),
            # Pixel Data and Value Interpretation
            'PixelData': ds.pixel_array,
            'BitsAllocated': ds.get('BitsAllocated', None),
            'BitsStored': ds.get('BitsStored', None),
            'HighBit': ds.get('HighBit', None),
            'PixelRepresentation': ds.get('PixelRepresentation', None),
            'RescaleIntercept': ds.get('RescaleIntercept', 0),
            'RescaleSlope': ds.get('RescaleSlope', 1),
            'RescaleType': ds.get('RescaleType', None),
            'WindowCenter': ds.get('WindowCenter', None),
            'WindowWidth': ds.get('WindowWidth', None),
            'PhotometricInterpretation': ds.get('PhotometricInterpretation', None),
            # Additional Information
            'InstanceNumber': ds.get('InstanceNumber', None),
            'AcquisitionNumber': ds.get('AcquisitionNumber', None),
            'PatientPosition': ds.get('PatientPosition', None),
            'DerivationDescription': ds.get('DerivationDescription', None),
            'TableHeight': ds.get('TableHeight', None),
            'GantryDetectorTilt': ds.get('GantryDetectorTilt', None),
        }
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {str(e)}")
        return None

def process_dicom_directory(directory):
    slices = defaultdict(list)
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.dcm'):
                filepath = os.path.join(root, filename)
                dicom_info = extract_dicom_info(filepath)
                if dicom_info:
                    series_uid = dicom_info['SeriesInstanceUID']
                    slices[series_uid].append(dicom_info)
    
    for series_uid in slices:
        slices[series_uid].sort(key=lambda x: float(x['SliceLocation'] or 0))
    
    return slices

def reconstruct_3d_volume(slices):
    rows = slices[0]['Rows']
    cols = slices[0]['Columns']
    num_slices = len(slices)
    
    volume = np.zeros((rows, cols, num_slices))
    
    for i, slice_data in enumerate(slices):
        pixel_array = slice_data['PixelData']
        rescale_slope = slice_data['RescaleSlope']
        rescale_intercept = slice_data['RescaleIntercept']
        volume[:,:,i] = pixel_array * rescale_slope + rescale_intercept
    
    pixel_spacing = slices[0]['PixelSpacing']
    slice_thickness = slices[0]['SliceThickness']
    spacing_between_slices = slices[0].get('SpacingBetweenSlices')
    
    # If SpacingBetweenSlices is not available, use SliceThickness
    if spacing_between_slices is None:
        spacing_between_slices = slice_thickness
    
    # Ensure all values are available and valid
    if pixel_spacing and slice_thickness and spacing_between_slices:
        voxel_size = (float(pixel_spacing[0]), float(pixel_spacing[1]), float(spacing_between_slices))
    else:
        logging.warning("Unable to determine voxel size. Using default (1,1,1)")
        voxel_size = (1, 1, 1)
    
    metadata = {
        'PatientPosition': slices[0].get('PatientPosition'),
        'FrameOfReferenceUID': slices[0].get('FrameOfReferenceUID'),
        'ImageOrientationPatient': slices[0].get('ImageOrientationPatient'),
        'ImagePositionPatient': slices[0].get('ImagePositionPatient'),
        'WindowCenter': slices[0].get('WindowCenter'),
        'WindowWidth': slices[0].get('WindowWidth'),
        'RescaleType': slices[0].get('RescaleType'),
        'PhotometricInterpretation': slices[0].get('PhotometricInterpretation'),
        'DerivationDescription': slices[0].get('DerivationDescription'),
        'TableHeight': slices[0].get('TableHeight'),
        'GantryDetectorTilt': slices[0].get('GantryDetectorTilt'),
    }
    
    return volume, voxel_size, metadata

def resample_volume(volume, voxel_size, target_voxel_size=(1, 1, 1)):
    zoom_factors = [old / new for old, new in zip(voxel_size, target_voxel_size)]
    resampled_volume = zoom(volume, zoom_factors, order=1)
    return resampled_volume

def visualize_3d_volume(volume, metadata):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    window_center = metadata['WindowCenter']
    window_width = metadata['WindowWidth']
    if isinstance(window_center, pydicom.multival.MultiValue):
        window_center = window_center[0]
    if isinstance(window_width, pydicom.multival.MultiValue):
        window_width = window_width[0]
    
    vmin = window_center - window_width // 2
    vmax = window_center + window_width // 2
    
    axes[0].imshow(volume[:, :, volume.shape[2]//2], cmap='gray', vmin=vmin, vmax=vmax)
    axes[0].set_title('Axial')
    
    axes[1].imshow(volume[:, volume.shape[1]//2, :], cmap='gray', vmin=vmin, vmax=vmax)
    axes[1].set_title('Coronal')
    
    axes[2].imshow(volume[volume.shape[0]//2, :, :], cmap='gray', vmin=vmin, vmax=vmax)
    axes[2].set_title('Sagittal')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    dicom_directory = '/home/matrix/Downloads/DIcom gans/Data/raw'
    
    logging.info("Processing DICOM files...")
    series_slices = process_dicom_directory(dicom_directory)
    
    if not series_slices:
        logging.warning("No valid DICOM files found.")
    else:
        logging.info(f"Processed {len(series_slices)} series.")
        
        for series_uid, slices in series_slices.items():
            logging.info(f"\nProcessing series {series_uid}")
            logging.info(f"Number of slices: {len(slices)}")
            
            logging.info("Reconstructing 3D volume...")
            volume, voxel_size, metadata = reconstruct_3d_volume(slices)
            logging.info(f"Volume shape: {volume.shape}")
            logging.info(f"Voxel size: {voxel_size}")
            
            logging.info("Resampling volume...")
            resampled_volume = resample_volume(volume, voxel_size)
            logging.info(f"Resampled volume shape: {resampled_volume.shape}")
            
            logging.info("Visualizing volume...")
            visualize_3d_volume(resampled_volume, metadata)
            
            logging.info("Additional Metadata:")
            for key, value in metadata.items():
                logging.info(f"{key}: {value}")
            
            logging.info("Derived Information:")
            logging.info(f"Derivation Description: {metadata['DerivationDescription']}")
            logging.info(f"Rescale Type: {metadata['RescaleType']}")
            
            logging.info("Additional Spatial Information:")
            logging.info(f"Table Height: {metadata['TableHeight']}")
            logging.info(f"Gantry/Detector Tilt: {metadata['GantryDetectorTilt']}")