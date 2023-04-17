import unittest

from test_dicom_processor import TestDICOMProcessor


def main():
    # create a test suite
    suite = unittest.TestSuite()

    # add the test cases to the test suite
    suite.addTest(TestDICOMProcessor("test_extract_dicom_tags"))
    suite.addTest(TestDICOMProcessor("test_get_numpy_array"))
    suite.addTest(TestDICOMProcessor("test_convert_and_save_to_png"))
    suite.addTest(TestDICOMProcessor("test_extract_dicom_metadata"))

    # create a test runner and run the test suite
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # print the test results
    print("\n\nTest Results:")
    print("Number of tests run:", result.testsRun)
    print("Number of failures:", len(result.failures))
    print("Number of errors:", len(result.errors))
    print("Number of skipped tests:", len(result.skipped))

    # return the exit code
    if len(result.failures) > 0 or len(result.errors) > 0:
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
