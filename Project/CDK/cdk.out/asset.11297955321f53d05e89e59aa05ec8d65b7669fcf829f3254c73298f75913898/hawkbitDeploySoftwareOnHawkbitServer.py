import requests
import json
import boto3
import traceback
import botocore
import zipfile
import tempfile
import os
import base64
from datetime import datetime
from boto3.session import Session

cf = boto3.client('cloudformation')
code_pipeline = boto3.client('codepipeline')
#server_ip = "3.254.159.167"

def lambda_handler(event, context):
    try:
        # Valore della variabile
        job_id = event['CodePipeline.job']['id']
        job_data = event['CodePipeline.job']['data']
        input_artifacts = job_data['inputArtifacts']
        output_artifacts = job_data['outputArtifacts']
        project_name = job_data['actionConfiguration']['configuration']['UserParameters']
        project_version = datetime.now().strftime("%y.%m.%d.%H.%M.%S")
        ssm_client = boto3.client('ssm')
        
        username = (ssm_client.get_parameter(Name='/hawkbit/username', WithDecryption=True))['Parameter']['Value']
        password = (ssm_client.get_parameter(Name='/hawkbit/password', WithDecryption=True))['Parameter']['Value']
        server_ip = (ssm_client.get_parameter(Name='/hawkbit/ip_address', WithDecryption=True))['Parameter']['Value']
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        auth_header = f"Basic {encoded_credentials}"
        
        # Get the artifact details
        input_artifact_data = input_artifacts[0]
        s3 = setup_s3_client(job_data)
        # Get the JSON template file out of the artifact
        file_path = get_file(s3, input_artifact_data, "Lorenzo_Device")
        
        url = f"http://{server_ip}:8080/rest/v1/softwaremodules"
        payload = json.dumps([{
            "name": project_name,
            "version": project_version,
            "type": "Application",
            "description": "Hawkbit device simulator module from codecommit",
            "vendor": "Reply",
            "encrypted": False
        }])

        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_header
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 201:
            print(f"Error in the Software Module creation!  Error: {response.status_code}")
            traceback.print_exc()
            put_job_failure(job_id, 'Function exception: ')
            return
        #put_job_success(job_id, 'Software Module creation completed', {"SoftwareModule": f"{response.json()}"})
        print('Software Module creation completed')
        
        json_data = response.json()
        softwaremodule_id = json_data[0]['id']
        url = f"http://{server_ip}:8080/rest/v1/softwaremodules/{softwaremodule_id}/artifacts"
        payload = {}
        files=[
            ('file',("Lorenzo_Device.zip", open(file_path,'rb'),'application/zip'))
        ]
        headers = {
            'Authorization': auth_header
        }
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        os.remove(file_path)
        if response.status_code != 201:
            print(f"Error in the upload Artifact!  Error: {response.status_code}")
            traceback.print_exc()
            put_job_failure(job_id, 'Function exception: ')
            return
        #put_job_success(job_id, 'Upload artifact completed', {"Artifact": f"{response.json()}"})
        print('Upload artifact completed')
        
        url = f"http://{server_ip}:8080/rest/v1/distributionsets"
        payload = json.dumps([{
            "name": project_name,
            "description": "A Device simulator of hawkbit client",
            "version": project_version,
            "requiredMigrationStep": False,
            "modules": [{
                "id": softwaremodule_id
            }],
            "type": "app"
        }])
        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_header
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 201:
            print(f"Error in the Distribution Set creation! Error: {response.status_code}")
            traceback.print_exc()
            put_job_failure(job_id, 'Function exception: ')
            return
        print('Creation of distributionsets completed')
        
        return put_job_success(job_id, 'Deployment completed', {"DistributioSet": f"{response.json()[0]}"})
        
        
    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ')
        
def setup_s3_client(job_data):
    """Creates an S3 client
    
    Uses the credentials passed in the event by CodePipeline. These
    credentials can be used to access the artifact bucket.
    
    Args:
        job_data: The job data structure
        
    Returns:
        An S3 client with the appropriate credentials
        
    """
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']
    
    session = Session(aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token)
    return session.client('s3', config=botocore.client.Config(signature_version='s3v4'))
    
def get_file(s3, artifact, folder_to_extract):
    """Gets the template artifact
    Downloads the artifact from the S3 artifact store to a temporary file
    then extracts the zip and returns the file containing the CloudFormation
    template.
    Args:
        artifact: The artifact to download
        file_in_zip: The path to the file within the zip containing the template
    Returns:
        The CloudFormation template as a string
    Raises:
        Exception: Any exception thrown while downloading the artifact or unzipping it
    """
    #tmp_file = tempfile.NamedTemporaryFile()
    bucket = artifact['location']['s3Location']['bucketName']
    key = artifact['location']['s3Location']['objectKey']
    extraction_directory = tempfile.mkdtemp()
    
    with tempfile.NamedTemporaryFile() as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        # Open the original ZIP file
        with zipfile.ZipFile(tmp_file.name, 'r') as zip:
            #FIleName in the archive
            file_list = zip.namelist()
            # Create a new ZIP file containing the extracted folder and its contents
            new_zip_path = f"/tmp/{folder_to_extract}.zip"
            new_zip_file = zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED)
            for file_name in file_list:
                # read and write file content in new zip
                file_content = zip.read(file_name)
                new_zip_file.writestr(file_name, file_content)
                
            # Close the new ZIP file
            new_zip_file.close()
            print(f"File {folder_to_extract}.zip creation completed")
            return new_zip_path
        
            
def put_job_success(job, message, output_result):
    """Notify CodePipeline of a successful job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    
    """
    print('Putting job success')
    print(message)
    
    #code_pipeline.put_job_success_result(jobId=job)
    return code_pipeline.put_job_success_result(
        jobId=job,
        outputVariables=output_result
    )
  
def put_job_failure(job, message):
    """Notify CodePipeline of a failed job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
    
    """
    print('Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})
 