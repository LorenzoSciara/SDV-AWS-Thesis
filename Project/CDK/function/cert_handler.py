import json
import time
from botocore.exceptions import ClientError
import boto3
import os

SECRET_NAME = "hawkbit-iot-cert-and-key-5"

iot = boto3.client('iot', region_name='eu-west-1')

def on_create(thing_name):
    response = iot.create_keys_and_certificate(setAsActive=True)
    certificate_id = response['certificateId']
    certificate_pem = response['certificatePem']
    key_pair = response['keyPair']
    
    if not certificate_id or not certificate_pem or not key_pair:
        raise ValueError('Failed to create keys and certificate')
    
    directory_path="./certificates"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    file_path = os.path.join(directory_path, f"{thing_name}.private.key")
    with open(file_path, 'w') as file:
        file.write(key_pair['PrivateKey'])
    file_path = os.path.join(directory_path, f"{thing_name}.public.key")
    with open(file_path, 'w') as file:
        file.write(key_pair['PublicKey'])
    file_path = os.path.join(directory_path, f"{thing_name}.cert.pem")
    with open(file_path, 'w') as file:
        file.write(certificate_pem)
    time.sleep(2)
    return {
        'PhysicalResourceId': certificate_id,
        'Data': {
            'certificateId': certificate_id
        }
    }
 
def cert_handler(thing_name):
    '''if contest.node.try_get_context("is_deploy"):
        return on_create(contest)
    elif contest.node.try_get_context("is_destroy"):
        return on_delete(contest)
    raise ValueError('Unknown request type')'''
    return on_create(thing_name)

if __name__ == "__main__":
    on_create()
