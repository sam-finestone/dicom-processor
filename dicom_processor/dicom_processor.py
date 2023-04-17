import os
import pandas as pd
import numpy as np
import pydicom
from PIL import Image
import logging
import time
from typing import List, Tuple, Dict 
import logging
from pydicom.datadict import keyword_dict

class MissingMetadataError(Exception):
    """
    Custom exception raised when metadata is missing from a DICOM file
    """

    def __init__(self, tag: str):
        self.tag = tag
        self.message = f"Missing metadata for tag {tag}"
        super().__init__(self.message)

class DICOMProcessor:
    def __init__(self, dicom_file: str, output_folder: str) -> None:
        """
        DICOMProcessor class constructor
        
        Parameters:
        - path_to_dicom_folder (str): Path to the DICOM folder
        """
        self.dicom_file = dicom_file
        self.output_folder = output_folder

        # set up the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('dicom_processor.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info('Starting DICOM processing for file: {}'.format(self.dicom_file))
        
        self.dicom = pydicom.dcmread(self.dicom_file)
        self.logger.info('Loaded DICOM file: {}'.format(self.dicom_file))
        
        # run the preprocessing steps
        self.tags_df = self.extract_dicom_tags()
        self.logger.info('Extracted DICOM tags')
        self.pixel_data = self.get_numpy_array()
        self.logger.info('Extracted pixel data')
        self.convert_and_save_to_png()
        self.logger.info('Converted and saved DICOM file as PNG')
        self.metadata = self.extract_dicom_metadata()
        self.logger.info('Extracted metadata')


    def extract_dicom_tags(self) -> pd.DataFrame:
        """
        This method extracts the DICOM tags from the given DICOM file and returns them as a pandas DataFrame
        
        Parameters:
        - dicom_file (str): Path to the DICOM file
        
        Returns:
        - dicom_tags (pd.DataFrame): Pandas DataFrame containing the DICOM tags
        """
       # Extract all tags from the DICOM file and put them into a dictionary
        def dictify(ds):
            output = dict()
            for elem in ds:
                if elem.VR != 'SQ': 
                    output[elem.tag] = elem.value
                else:
                    output[elem.tag] = [dictify(item) for item in elem]
            return output
        
        tags_dict = dictify(self.dicom)
        
        # Convert the dictionary to a list of tuples
        tags_list = []
        for key, value in tags_dict.items():
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            tags_list.append((key, value))
        
        # Convert the list of tuples to a pandas dataframe
        tags_df = pd.DataFrame(tags_list, columns=['Tag', 'Value'])
        
        return tags_df
    
    def get_numpy_array(self) -> np.ndarray:
        """
        This method extracts the pixel data from the given DICOM file and returns it as a numpy array
        
        Parameters:
        - dicom_file (str): Path to the DICOM file
        
        Returns:
        - pixel_data (np.ndarray): Numpy array containing the pixel data
        """
        pixel_data = self.dicom.pixel_array
        return pixel_data

    def convert_and_save_to_png(self) -> str:
        """
        This method converts the given DICOM file to a PNG file and saves it to the specified output folder
        
        Parameters:
        - dicom_file (str): Path to the DICOM file to convert
        - output_folder (str): Path to the folder where the PNG file will be saved
        
        Returns:
        - str: Path to the saved PNG file
        """
        # extract the pixel data as a numpy array
        pixel_data = self.get_numpy_array()
        # create a PIL image from the numpy array
        img = Image.fromarray(pixel_data)
        output_img_file = os.path.join(self.output_folder, self.dicom_file.split('/')[-1].split('.')[0] + '.png')
        # save the image to the output file
        img.save(output_img_file)
    
    def extract_dicom_metadata(self) -> Dict[str,str]:
        """
        Extracts metadata from a DICOM file and returns it as a dictionary.

        Parameters:
        - dicom_file_path (str): Path to the DICOM file

        Returns:
        - metadata (dict): Dictionary containing metadata from the DICOM file
        """
        # Initialize an empty dictionary to hold the metadata
        metadata = {}

        # Loop over all data elements in the DICOM file
        for elem in self.dicom:
            # Skip image pixel data
            if elem.tag == pydicom.tag.Tag('7fe0', '0010'):
                continue
            
            # Get the keyword for the data element
            keyword = pydicom.datadict.keyword_for_tag(elem.tag)

            # If the keyword is not found, use the tag as the key
            if keyword is None:
                key = str(elem.tag)
            else:
                key = keyword

            # Get the value of the data element
            try:
                value = elem.value
            except:
                raise MissingMetadataError(f"Missing metadata value for {key} ({elem.tag})")

            # Add the key-value pair to the metadata dictionary
            metadata[key] = value

        return metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatientStudy:
    def __init__(self, path_to_dicom_folder: str, patient_id: str, output_img_folder: str) -> None:
        """
        This class processes all DICOM files of a patient
        
        Parameters:
        - path_to_dicom_folder (str): Path to the DICOM folder
        """
        self.patient_id = patient_id
        self.path_to_dicom_folder = path_to_dicom_folder

        self.study_series = os.path.join(path_to_dicom_folder, self.patient_id, 'study', 'series')
        if not os.path.isdir(self.study_series):
            raise ValueError(f"{self.study_series} is not a valid directory")
        
        # create a patient dicom image output folder a given patient id
        self.output_folder = os.path.join(output_img_folder, self.patient_id)
    
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # read all DICOM files of the patient
        self.dicom_file_series = self.read_dicom_folder()
        logger.info(f"Found {len(self.dicom_file_series)} DICOM files for patient {self.patient_id}")

        # extract the patient information for each DICOM file
        self.patient_info_df = self.get_patient_info()
    
    def read_dicom_folder(self) -> List[str]:
        """
        This method loads all DICOM files of a patient from the given folder path
        """
        dicom_files = []
        for (root, dirs, fileList) in os.walk(self.study_series):
                for filename in sorted(fileList):
                    if filename.endswith('.dcm'):
                        try:
                            study = os.path.join(self.study_series, filename)
                            dicom_files.append(study)
                        except pydicom.errors.InvalidDicomError:
                            print(f"Skipping {os.path.join(self.study_series, filename)}: not a valid DICOM file")
        if len(dicom_files) == 0:
            raise ValueError(f"No valid DICOM files found in {self.study_series}")
        return dicom_files
    
    def get_patient_info(self) -> pd.DataFrame:
        """
        This method extracts all DICOM tags from all DICOM files of a patient
        
        Returns:
        - pd.DataFrame: Pandas dataframe containing all DICOM tags
        """
        dicom_patient_data = pd.DataFrame(columns=['dcm_file_number', 'metadata', 'pixel_data'])
        for dicom_file in self.dicom_file_series:
            # extract the relevant DICOM information for each DICOM file
            dicom_prepared = DICOMProcessor(dicom_file, self.output_folder)
            # extracted DICOM tags to the dataframe
            # dicom_tags = dicom_prepared.extract_dicom_tags()
            # extract the pixel data as a numpy array
            dicom_pixel_data = dicom_prepared.get_numpy_array()
            # convert the pixel data to a PNG image and save it to the output folder
            dicom_prepared.convert_and_save_to_png()
            # extract the metadata as a dictionary
            dicom_metadata = dicom_prepared.extract_dicom_metadata()
            # Print the DICOM data for debugging purposes
            # print(dcm_data_dict)
            # append the extracted DICOM tags to the dataframe
            dcm_file_number = dicom_file.split('/')[-1].split('.')[0]
            dicom_patient_data = dicom_patient_data.append({'dcm_file_number':dcm_file_number, 'metadata': dicom_metadata, 'pixel_data': dicom_pixel_data}, ignore_index=True)
            print(f"Processed {dcm_file_number}")

        return dicom_patient_data


  





