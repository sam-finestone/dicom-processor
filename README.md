# Take-home Exercise: DICOM Image Processing Library


## Background
There are 10 samples of brain CT scans that need to be read and processed further upstream. These images are all in the medical imaging DICOM format (wiki), and need to be processed to retrieve the raw image pixel data, alongside the metadata data about the scan itself (patient name, acquisition date etc). DICOM files are often stored in a folder structure known as the DICOM study structure (example here), and might contain multiple DICOM slices in a series that stack up into a 3D image.

## Tasks
- Your task is to prepare a DICOM processing library that can read, store and process information from DICOM images. This is broken down into smaller chunks:
- Load DICOM images (given the study structure)
- Extract DICOM Tags into a Pandas Dataframe
- Extract pixel data into a Numpy array
- Convert and save these images to JPG image
- Retrieve the numpy array data and a dictionary of the metadata
- Test the functionality of each feature

A skeleton repository has been provided, including a very simple dummy test script and folder. There are no strict requirements to the project structure or functions, so feel free to modify the skeleton function declarations outside of the given types and names. 

As for libraries, the expected libraries like numpy, pillow, pandas, and pydicom are included in the requirements.txt file. Any newly installed libraries should be added to the requirements folder, and a short description of the package + the purpose of the package added to the read me. 

When completed, provide your source code as a zip file or private Github repository.

## Data

#### DICOM Data:
https://drive.google.com/file/d/1SsLf_TvESnXTj8yMjWY6XHELCUmMXHZ_

