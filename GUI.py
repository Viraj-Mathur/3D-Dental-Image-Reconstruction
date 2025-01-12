import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
from model_creation import process_dicom
from featureExtraction import main
import os

class App:

    def __init__(self):
        self.root = ctk.CTk()  
        self.root.title("DICOM Image 3D Model Maker")
        
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode("dark")

        self.headingFont = ("Arial", 34, "bold")
        self.labelFont = ("Arial", 18, "bold")
        self.buttonFont = ("Arial", 16, "bold")
        self.entryFont = ("Arial", 16, "bold")

        self.headingLabel = ctk.CTkLabel(self.root, text="DICOM IMAGE 3D MODEL MAKER", font=self.headingFont, padx=20, pady=40)
        self.headingLabel.pack()

        self.gif_frame = tk.Frame(self.root)
        self.gif_frame.pack()

        self.gif_label = tk.Label(self.gif_frame)
        self.gif_label.pack()

        self.load_gif("Animation.gif", width=700, height=600)

        self.browseFrame = ctk.CTkFrame(self.root)
        self.browseFrame.pack(pady=30)

        self.browseEntry = ctk.CTkEntry(self.browseFrame, font=self.entryFont, width=400)
        self.browseEntry.grid(row=0, column=0, padx=10)

        self.browseButton = ctk.CTkButton(self.browseFrame, text="Browse", font=self.buttonFont, command=self.browse_folder)
        self.browseButton.grid(row=0, column=1, padx=10)

        self.processingBtnFrame = ctk.CTkFrame(self.root)
        self.processingBtnFrame.pack()

        self.extarctFeatureButton = ctk.CTkButton(self.processingBtnFrame, text="Extract Features", font=self.buttonFont, command=self.extractFeatures)
        self.extarctFeatureButton.grid(row=1, column=0, padx=10, pady=20)

        self.processButton = ctk.CTkButton(self.processingBtnFrame, text="Process DICOM", font=self.buttonFont, command=self.process_dicom)
        self.processButton.grid(row=1, column=1, padx=10, pady=20)

        self.root.mainloop()

    def load_gif(self, gif_path, width=None, height=None):
        self.gif_frames = []  
        self.gif_index = 0  

        gif = Image.open(gif_path)
        for frame in range(0, gif.n_frames):
            gif.seek(frame)
            frame_image = gif.copy()

            if width and height:
                frame_image = frame_image.resize((width, height), Image.LANCZOS)

            self.gif_frames.append(ImageTk.PhotoImage(frame_image))

        self.update_gif()

    def update_gif(self):
        if self.gif_frames:
            self.gif_label.config(image=self.gif_frames[self.gif_index])
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.root.after(100, self.update_gif)

    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            
            self.browseEntry.delete(0, tk.END)
            self.browseEntry.insert(0, folder_path)

    import os

    def has_only_dcm_files(self, directory_path):
        if not os.path.isdir(directory_path):
            messagebox.showerror('Folder Error', 'Error: Browse folder is empty!')
            return False
        
        for file_name in os.listdir(directory_path):
            # Ignore subdirectories
            if os.path.isdir(os.path.join(directory_path, file_name)):
                return False
            # Check file extension
            if not file_name.lower().endswith('.dcm'):
                messagebox.showerror('File Error', 'Error: All files are not dicom file!')
                return False
        
        return True

    def extractFeatures(self):

        filePresent = self.has_only_dcm_files(self.browseEntry.get())
    
        if(filePresent):
            self.featureWindow = tk.Toplevel(self.root)
            self.featureWindow.title("Extracted Features")

            self.panelFrameLabel = ctk.CTkFrame(self.featureWindow, width=1500)
            self.panelFrameLabel.pack(pady=20)  
            
            self.leftPanelLabel = ctk.CTkLabel(self.panelFrameLabel, text="DICOM Features", font=self.labelFont, width=400)
            self.leftPanelLabel.grid(row=0, column=0)

            self.rightPanelLabel = ctk.CTkLabel(self.panelFrameLabel, text="Feature Image Preview", font=self.labelFont, width=700)
            self.rightPanelLabel.grid(row=0, column=1)

            self.mainFrame = ctk.CTkFrame(self.featureWindow, width=1500)
            self.mainFrame.pack(padx=5)

            self.leftPanel = ctk.CTkFrame(self.mainFrame, width=400)
            self.leftPanel.grid(row=0, column=0)

            self.rightPanel = ctk.CTkFrame(self.mainFrame, width=700)
            self.rightPanel.grid(row=0, column=1)

            self.gridFrame = ctk.CTkFrame(self.rightPanel, width=700)
            self.gridFrame.pack(fill="x", expand=True)

            self.dicom_features = {}

            self.dicom_features = main(self.browseEntry.get())
            if self.dicom_features is not None:
                self.add_image_grid()
                
                self.update_features_table()  

    def process_dicom(self):
        filePresent = self.has_only_dcm_files(self.browseEntry.get())

        if(filePresent):
            folder_path = self.browseEntry.get()
            
            try:
                self.featureWindow.destroy()
            except:
                pass

            self.root.destroy()

            process_dicom(folder_path)
        
    def add_image_grid(self):
        image_paths = ["axial.png", "coronal.png", "sagittal.png", "surface_normals_axial.png"]

        for index, image_path in enumerate(image_paths):
            
            image = Image.open(image_path).resize((350, 350))
            photo = ImageTk.PhotoImage(image)

            img_label = ctk.CTkLabel(self.gridFrame, image=photo, text="")
            img_label.image = photo  
            img_label.grid(row=index // 2, column=index % 2, padx=1, pady=1)

    def update_features_table(self):
        self.dicom_features.pop("FrameOfReferenceUID", None)

        for widget in self.leftPanel.winfo_children():
            widget.destroy()

        table_frame = ctk.CTkFrame(self.leftPanel)
        table_frame.pack(padx=10, pady=10, fill="x", expand=True)

        for i, (key, value) in enumerate(self.dicom_features.items()):
            key_label = ctk.CTkLabel(table_frame, text=key, font=("Arial", 14), width=200, height=40, corner_radius=10, fg_color="lightgray", text_color="black")
            key_label.grid(row=i + 1, column=0, padx=5, pady=5)

            value_label = ctk.CTkLabel(table_frame, text=str(value), font=("Arial", 14), width=200, height=40, corner_radius=10, fg_color="lightgray", text_color="black")
            value_label.grid(row=i + 1, column=1, padx=2, pady=5)

GUI = App()