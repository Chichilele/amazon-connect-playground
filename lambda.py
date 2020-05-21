import csv
import json
import uuid
from urllib.parse import unquote_plus

import boto3

##load connect API
connect_client = boto3.client('connect')
s3_client = boto3.client('s3')

## connect instance ID
CONNECT_INSTANCE_ID = "3ab95c31-5dad-482b-9b7e-f6929d3b2619"


def get_user_updates(csv_path):
    '''read [csv_path] file and associate each column to a dict entry
    return csv_csv: dict
    '''
    csv_dict = {
        'username': [],
        'hierarchygroup': [],
    }

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['username'], row['hierarchygroup'])
            csv_dict['username'].append(row["username"])
            csv_dict['hierarchygroup'].append(row["hierarchygroup"])
    return csv_dict


def update_each_user(update_data, hierarchy_groups):
    response = {"sucess": {}, "fail": {}}
    for name, id, hg in zip(update_data['username'], update_data['id'], update_data['hierarchygroup']):
        print(f"{name:<10}\t{id}\t {hg}\t {hierarchy_groups[hg]}")
        ## List user hierarchy groups
        try:
            r = connect_client.update_user_hierarchy(
                HierarchyGroupId=hierarchy_groups[hg],
                UserId=id,
                InstanceId=CONNECT_INSTANCE_ID
            )
            response["success"][name] = r
        except Exception as e: 
            print(f"ERRPR \tcouldn't update {name}. The following error occured")
            print(e)
            response["fail"][name] = r
    
    return response

def lambda_handler(event, context):
    for record in event['Records']:
        ## get event record details
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        print(bucket, )
        
        ## get file path and download it
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        s3_client.download_file(bucket, key, download_path)
        
        ## get updates to apply
        update_data = get_user_updates(download_path)
        
        ## get each user's id
        response = connect_client.list_users(InstanceId=CONNECT_INSTANCE_ID)
        update_data["id"] = [user["Id"] for user in response["UserSummaryList"] if user["Username"] in update_data['username']]
        
        ## get each hierarchy group's id
        response = connect_client.list_user_hierarchy_groups(InstanceId=CONNECT_INSTANCE_ID,)
        hierarchy_groups = {group["Name"]: group["Id"] for group in response['UserHierarchyGroupSummaryList']}
        
        ## update connect 
        reponse = update_each_user(update_data, hierarchy_groups)
        
        return response


        
        