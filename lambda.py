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
    csv_dict = {}

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_dict[row["username"]] = {"hg": row["hierarchygroup"]}
    return csv_dict

def update_each_user(update_data, hierarchy_groups):
    response = {"sucess": [], "fail": []}
    for name, user in update_data.items():
        request = {"username": f"{name:<10}", "user_id": f"{user.get('id', 'UNKOWN_USER_ID')}",
                "hierarchy_group": f"{user['hg']}", "hierarchy_group_id": f"{hierarchy_groups.get(user['hg'], 'UNKOWN_HG_ID')}"}
        
        try:
            r = connect_client.update_user_hierarchy(
                HierarchyGroupId=hierarchy_groups.get(user["hg"], "UNKOWN_HIERARCHY_GROUP_ID"),
                UserId=user.get("id", "UNKOWN_USER_ID"),
                InstanceId=CONNECT_INSTANCE_ID
            )
            response["sucess"].append({
                "request": request,
                "response": r
            })
        except Exception as e:
            print(f"Exception... {type(e).__name__}: {e}")
            response["fail"].append({
                "request": request,
                "response": r
            })
        response["counts"] = {
            "sucess": len(response["sucess"]),
            "fail": len(response["fail"])
        }   
    return response


def lambda_handler(event, context):
    for record in event['Records']:
        ## get event record details
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        print("bucket: ", bucket, )
        
        ## get file path and download it
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        s3_client.download_file(bucket, key, download_path)
        
        ## get updates to apply
        update_data = get_user_updates(download_path)
        
        ## get each user's id
        response = connect_client.list_users(InstanceId=CONNECT_INSTANCE_ID)
        for user in response["UserSummaryList"]:
            if user["Username"] in update_data.keys():
                update_data[user["Username"]]["id"] = user["Id"]
        
        ## get each hierarchy group's id
        response = connect_client.list_user_hierarchy_groups(InstanceId=CONNECT_INSTANCE_ID,)
        hierarchy_groups = {group["Name"]: group["Id"] for group in response["UserHierarchyGroupSummaryList"]}
        
        ## update connect 
        response = update_each_user(update_data, hierarchy_groups)
        
        ## log to CWL
        print(response)
        
        return response
