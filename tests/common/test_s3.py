"""TestS3BucketCOnnectorMethods"""
import unittest
import boto3
import os

from moto import mock_aws #mock_s3 (https://stackoverflow.com/questions/77903321/importerror-cannot-import-name-mock-s3-from-moto)
from xetra.common.s3 import S3BucketConnector

class TestS3BucketConnectorMethods(unittest.TestCase):
    """
    Testing the S3BucketCOnnector class
    """

    def setUp(self):
        """
        Setting up the environment
        """
        # mocking s3 connection start
        self.mock_s3 = mock_aws#mock_s3()
        # self.mock_s3.start() # Avoid manually calling start() or stop() on the mock_s3 object when using it as a decorator or context manager. The moto decorators and context managers handle the starting and stopping of the mock environment automatically.
        # Defining the class arguments
        self.s3_access_key = 'AWS_ACCESS_KEY_ID' 
        self.s3_secret_key = 'AWS_SECRET_ACCESS_KEY'
        self.s3_endpoint_url = 'https://s3.eu-central-1.amazonaws.com'  # proposed from autocomplete 'http://localhost:4566'
        self.s3_bucket_name = 'test-bucket'
        # Creating s3 access keys as environemnt variabes
        os.environ[self.s3_access_key] = "K1"
        os.environ[self.s3_secret_key] = "K2"
        #Creating a bucket on the mocked s3
        self.s3  = boto3.resource(service_name='s3', endpoint_url=self.s3_endpoint_url) 
        self.s3.create_bucket(Bucket=self.s3_bucket_name,
                              CreateBucketConfiguration={
                                  'LocationConstraint': 'eu-central-1'
                                  })
        self.s3_bucket = self.s3.Bucket(self.s3_bucket_name)
        # Creatning a testing instance
        self.s3_bucket_conn = S3BucketConnector(self.s3_access_key,
                                                self.s3_secret_key,
                                                self.s3_endpoint_url,
                                                self.s3_bucket_name) 

    def tearDown(self):
        """
        Executing after unittests
        """
        # mocking s3 connection stop
        self.mock_s3.stop()

    def test_list_files_in_prefix_ok(self):
        """
        Test the list_files_in+_prefix method for getting 2 fle keys 
        as list on the mocked s3 bucket  
        """
        #Exected results 
        prefix_exp = 'prefix/'
        key1_exp = f'{prefix_exp}test1.csv'
        key2_exp = f'{prefix_exp}test2.csv'
        # Test init needed fpr special tests
        csv_content = """col1,col2
        valA, valB""" 
        self.s3_bucket.put_object(BOdy=csv_content, Key=key1_exp)
        self.s3_bucket.put_object(Body=csv_content, Key=key2_exp)
        # Method execiution
        list_result = self.s3_bucket_conn.list_files_in_prefix(prefix_exp)
        # Tests after method exection
        self.asserEqual(len(list_result),2)
        self.assertIn(key1_exp, list_result)
        self.assertIn(key2_exp, list_result) 
        # # CLean-up after tests
        self.s3_bucket.delete_objects(
            Delete={
                'Objects': [
                    {'Key': key1_exp},
                    {'Key': key2_exp}
                ]
            }
        )  
    # print("test") # for debuggin purposes 

    def test_list_files_on_prefx_wrong_prefix(self):
        """
        Test the list_files_in_prefix method in case of
        a wrong or not existing prefix
        """
        prefix_exp = 'no-prefix/'
        # Method execution
        list_result = self.s3_bucket_conn.list_files_in_prefix(prefix_exp)
        # Tests after method exection
        self.assertTrue(not list_result) 
        
if __name__ == '__main__':
    unittest.main()
    # down folows the testIns for debuggin gpurposes (they all got commented out eventually )
    #testIns = TestS3BucketConnectorMethods()
    #testIns.setUp()
    #testIns.test_list_files_in_prefix_ok()
    #testIns.tearDown()