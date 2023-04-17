import os
import glob
from dicom_processor import DICOMProcessor, PatientStudy
import pandas as pd

# Define the input directory containing the DICOM files
path_to_dicom_folder = '/Users/sam/Library/Mobile Documents/com~apple~CloudDocs/Projects/ML-projects/intracranial-hermorrhage-dcm/data/CT-intracranial-hemorrhage-dcm'

# Define the output directory to save the processed JPEG images
output_dir = "./output"

# Define the patient ID
patient_id = '050'

# create an instance of the PatientStudy class
# patient_data = PatientStudy(path_to_dicom_folder, patient_id, output_dir)

study_series = os.path.join(path_to_dicom_folder, patient_id, 'study', 'series')
output_folder = os.path.join(output_dir, patient_id)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# read a sepeific DICOM file of the patient_id
CT_file = '014.dcm'

# Get a list of all DICOM files in the input directory
dcm_file = os.path.join(path_to_dicom_folder, patient_id, 'study', 'series', CT_file)
print(f"Processing {dcm_file}")

# Create an instance of the DICOMProcessor class
dicom_prepared = DICOMProcessor(dcm_file, output_dir)

# extracted DICOM tags to the dataframe
dicom_tags = dicom_prepared.extract_dicom_tags()

# extract the pixel data as a numpy array
dicom_pixel_data = dicom_prepared.get_numpy_array()

# convert the pixel data to a PNG image and save it to the output folder
dicom_prepared.convert_and_save_to_png()

# extract the metadata as a dictionary
dcm_data_dict = dicom_prepared.extract_dicom_metadata()

# Print the DICOM data for debugging purposes
print(dcm_data_dict)

# Create an instance of the PatientStudy class
patient_050 = PatientStudy(path_to_dicom_folder, patient_id, output_dir)

# get the patient image pixel (as numpy) and metadata (as dictionary)
patient_050_info = patient_050.get_patient_info() 
print(patient_050_info.head())