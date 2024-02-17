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

def lambda_handler(event, context):
    try:
        # Valore della variabile
        job_id = event['CodePipeline.job']['id']
        job_data = event['CodePipeline.job']['data']
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        
        ssm_client = boto3.client('ssm')
            
        username = (ssm_client.get_parameter(Name='/hawkbit/username', WithDecryption=True))['Parameter']['Value']
        password = (ssm_client.get_parameter(Name='/hawkbit/password', WithDecryption=True))['Parameter']['Value']
        server_ip = (ssm_client.get_parameter(Name='/hawkbit/ip_address', WithDecryption=True))['Parameter']['Value']
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        auth_header = f"Basic {encoded_credentials}"
        
        distribution_set = json.loads(user_parameters.replace("'", "\"").replace("F", "f").replace("T", "t"))
        
        url = f"http://{server_ip}:8080/rest/v1/targets"
        payload = ""
        headers = {
            'Authorization': auth_header
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"Error in the Target retrieve creation!  Error: {response.status_code}")
            traceback.print_exc()
            put_job_failure(job_id, 'Function exception: ')
            return
        print("Target retrieve completed")
        
        content = response.json()['content']
        target_names = ""
        for name in content:
            print(f"distribution_set: {distribution_set['name']} target_names: {name['name']}")
            if distribution_set['name'] in name['name']:
                target_names = name['name']
        
        url = f"http://{server_ip}:8080/rest/v1/rollouts"
        payload = json.dumps({
            "createdBy": "Reply",
            "createdAt": int(datetime.now().timestamp()),
            "lastModifiedBy": "Reply",
            "lastModifiedAt": int(datetime.now().timestamp()),
            "name": f"{distribution_set['name']}{distribution_set['version']}",
            "description": "Rollout on Lorenzo_Device",
            "targetFilterQuery": f"id=={target_names}*",
            "distributionSetId": distribution_set['id'],
            "amountGroups": 1,
            "type": "forced"
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_header
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 201:
            print(f"Error in the Rollout creation!  Error: {response.status_code}")
            traceback.print_exc()
            put_job_failure(job_id, 'Function exception: ')
            return
        print(response.text)
        
        rollout_id = response.json()['id']
        status = ""
        while status != "ready":
            url = f"http://{server_ip}:8080/rest/v1/rollouts/{rollout_id}"
            payload = ""
            headers = {
                'Authorization': auth_header
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            status = response.json()['status']
            print(status)
        
        print(rollout_id)
        url = f"http://{server_ip}:8080/rest/v1/rollouts/{rollout_id}/start"
        payload = ""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_header
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        put_job_success(job_id, 'Rollout completed')
        
    except Exception as e:
        # We're expecting the user parameters to be encoded as JSON
        # so we can pass multiple values. If the JSON can't be decoded
        # then fail the job with a helpful message.
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ')

def put_job_success(job, message):
    """Notify CodePipeline of a successful job
    
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
        
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
    
    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)
  
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
 
def setup_s3_client(job_data):
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']
    
    session = Session(aws_access_key_id=key_id,
        aws_secret_access_key=key_secret,
        aws_session_token=session_token)
    return session.client('s3', config=botocore.client.Config(signature_version='s3v4'))
    
def json_from_previus_lambda(s3, artifact):
    bucket = artifact['location']['s3Location']['bucketName']
    key = artifact['location']['s3Location']['objectKey']
    with tempfile.NamedTemporaryFile() as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        file_list = zip.namelist()
        for file_name in file_list:
                # read and write file content in new zip
                print(f"{zip.read(file_name)}")
        

    # Il contenuto potrebbe essere un JSON
    data_from_previous_lambda = json.loads(content)
    print(f"data: {data_from_previous_lambda}")