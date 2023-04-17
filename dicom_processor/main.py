import os 
import pydicom

from dicom_processor import DICOMProcessor, PatientStudy

# path to the folder containing the dcm files
path_dcm_folder = '/Users/sam/Library/Mobile Documents/com~apple~CloudDocs/Projects/ML-projects/intracranial-hermorrhage-dcm/data/CT-intracranial-hemorrhage-dcm/'

# patient id
patient_id ='050'

# take a single dcm file from the folder given patient_id
dcm_file = '014.dcm'
dcm_file_path = os.path.join(path_dcm_folder, patient_id, 'study', 'series', dcm_file)

# create an output file for the CT images
output_dir = './output'

# create the output folder if it does not exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# create a DICOMProcessor object
dicom_processor = DICOMProcessor(dcm_file_path, output_dir)

# extract the DICOM tags
dicom_tags = dicom_processor.extract_dicom_tags()

# print the DICOM tags
print(dicom_tags)

# extract the pixel data as a numpy array
pixel_data = dicom_processor.get_numpy_array()

# convert the pixel data to a png image and save it to the output folder
dicom_processor.convert_and_save_to_png()

# extract metadata from the DICOM file
dicom_metadata = dicom_processor.extract_dicom_metadata()

# Let's look taking a patient stake of dcm studies 
# create a PatientStudy object for patient id
patient_study = PatientStudy(path_dcm_folder, patient_id, output_dir)

# get the patient information: numpy array of pixel data and metadata
patient_info = patient_study.get_patient_info()

print(patient_info.head())




