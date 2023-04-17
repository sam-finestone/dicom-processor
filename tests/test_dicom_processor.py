import os
import unittest
import pandas as pd
import numpy as np
import pydicom
from PIL import Image
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import generate_uid
import sys
sys.path.append('../dicom_processor')
from dicom_processor import DICOMProcessor

class TestDICOMProcessor(unittest.TestCase):

    def setUp(self):
        # create a temporary folder to store test files
        self.temp_folder = './test_folder'
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        # create a test DICOM file with known properties
        self.dicom_file = os.path.join(self.temp_folder, 'test.dcm')
        self.test_image = np.random.randint(0, 256, size=(512, 512)).astype('uint16')
        ds = Dataset()
        ds.PatientName = 'Test Patient'
        ds.Modality = 'CT'
        ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        ds.SOPInstanceUID = generate_uid()
        ds.StudyDate = '20220101'
        ds.StudyTime = '120000'
        ds.Manufacturer = 'Manufacturer Inc.'
        ds.PixelSpacing = [0.5, 0.5]
        ds.Rows = self.test_image.shape[0]
        ds.Columns = self.test_image.shape[1]
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = 'MONOCHROME2'
        ds.PixelData = self.test_image.tobytes()
        ds.is_little_endian = True
        ds.is_implicit_VR = False
        ds.PixelRepresentation = 0  # unsigned

        # Set the file meta information
        file_meta = FileMetaDataset()
        file_meta.FileMetaInformationVersion = b'\x00\x01'
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'
        file_meta.ImplementationClassUID = '1.3.6.1.4.1.12345.6.7.8.9'
        file_meta.ImplementationVersionName = 'Test DICOM Processor'
        
        # Set the file meta dataset
        ds.file_meta = file_meta
        # Save the dataset to a file
        ds.save_as(self.dicom_file, write_like_original=False)

    def tearDown(self):
        # remove the temporary folder and all files in it
        for file in os.listdir(self.temp_folder):
            os.remove(os.path.join(self.temp_folder, file))
        os.rmdir(self.temp_folder)

    def test_extract_dicom_tags(self):
        # create a DICOM processor for the test file
        processor = DICOMProcessor(self.dicom_file, self.temp_folder)

        # extract the DICOM tags
        dicom_tags = processor.extract_dicom_tags()

        # check that the extracted tags match the expected values
        self.assertIsInstance(dicom_tags, pd.DataFrame)
        self.assertCountEqual(dicom_tags.columns, ['Tag', 'Value'])
        self.assertTrue(dicom_tags['Tag'].dtype == np.int64)
        self.assertEqual(dicom_tags.shape[0], 17)
        self.assertEqual(dicom_tags.loc[0, 'Tag'], 524310)
        self.assertEqual(dicom_tags.loc[6, 'Value'], 'Test Patient') 

    def test_get_numpy_array(self):
        # create a DICOM processor for the test file
        processor = DICOMProcessor(self.dicom_file, self.temp_folder)

        # extract the pixel data as a numpy array
        pixel_data = processor.get_numpy_array()

        # check that the extracted pixel data matches the expected values
        self.assertEqual(pixel_data.shape, self.test_image.shape)
        self.assertTrue(np.array_equal(pixel_data, self.test_image))

    def test_convert_and_save_to_png(self):
        # create a DICOM processor for the test file
        processor = DICOMProcessor(self.dicom_file, self.temp_folder)

        # convert the DICOM file to a PNG file and save it
        processor.convert_and_save_to_png()
        # check that the PNG file was created and has the expected properties
        png_file = os.path.join(self.temp_folder, 'test.png')
        # check that the PNG file was created and has the expected properties
        self.assertTrue(os.path.exists(png_file))
        with Image.open(png_file) as img:
            self.assertEqual(img.size, self.test_image.shape[::-1])

    def test_extract_dicom_metadata(self):
        # create a DICOM processor for the test file
        processor = DICOMProcessor(self.dicom_file, self.temp_folder)

        # extract the metadata
        metadata = processor.extract_dicom_metadata()

       # check that the extracted metadata matches the expected values
        self.assertEqual(metadata['PatientName'], 'Test Patient')
        self.assertEqual(metadata['Modality'], 'CT')
        self.assertEqual(metadata['PixelSpacing'], [0.5, 0.5])
        self.assertEqual(metadata['Rows'], self.test_image.shape[0])
        self.assertEqual(metadata['Columns'], self.test_image.shape[1])
        self.assertEqual(metadata['BitsAllocated'], 16)
        self.assertEqual(metadata['BitsStored'], 16)
        self.assertEqual(metadata['HighBit'], 15)
        self.assertEqual(metadata['SamplesPerPixel'], 1)
        self.assertEqual(metadata['PhotometricInterpretation'], 'MONOCHROME2')
        




