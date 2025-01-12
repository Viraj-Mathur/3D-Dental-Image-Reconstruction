# **3D Reconstruction of 2D Dental DICOM Images**

### **Project Overview**
This project presents a cost-effective approach to generating high-quality 3D models of dentures using Dicom images as a dataset, eliminating the need for expensive CBCT machines. Integrating advanced deep learning techniques, data augmentation with GANs, and interactive visualization provides an efficient solution for dental imaging. The repository includes separate modules for different functionalities, while the DICOM dataset has been excluded for security reasons.

---

### **Features**
- **Multi-Level Model Pipeline**:
  - **Level 1 Model**: Basic 3D reconstruction.
  - **Level 2 Model**: Improved accuracy with enhanced feature extraction.
  - **Level 3 Model**: Best-performing model with optimized feature mapping and GAN-augmented training.
- **Feature Extraction**:
  - Extracts voxel size, volume shape, and other DICOM features for precise reconstruction.
- **GAN-Based Augmentation**:
  - Generates synthetic DICOM images to expand training datasets.
- **GUI**:
  - Provides an interactive interface for uploading DICOM images and visualizing reconstructed 3D models.

---


### **Usage**

#### **1. Running the Models**
- Run the **Level 1**, **Level 2**, or **Level 3** models based on your requirements:
  ```bash
  python Level1_Model.py
  python Level2_Model.py
  python Level3_Model.py
  ```

#### **2. Feature Extraction**
- Extract DICOM image features using `feature_extraction.py`:
  ```bash
  python feature_extraction.py
  ```

#### **3. GAN-Based Data Augmentation**
- Open `gans.ipynb` to generate new synthetic DICOM images:
  ```bash
  jupyter notebook gans.ipynb
  ```

#### **4. Interactive GUI**
- Launch the GUI for uploading DICOM images and visualizing 3D models:
  ```bash
  python GUI.py
  ```

---

### **Security Note**
- The DICOM dataset has been excluded from this repository to maintain data privacy and comply with ethical considerations. Replace the `Dataset` directory path in the code with your own DICOM dataset.

---

### **Sample Results**
- **Input**: 2D DICOM slices of dental anatomy.
- **Output**: High-quality interactive 3D volumetric models.

---

### **Future Enhancements**
- Automate model selection based on input quality.
- Extend the application to other medical imaging domains.
- Implement real-time reconstruction for clinical usability.



---

Feel free to fork and contribute to enhance this project!
