import csv
import json

import boto3
## load connect API
connect_client = boto3.client('connect')

#################################################################
########################### CONSTANTS ###########################
#################################################################

## connect instance ID
CONNECT_INSTANCE_ID = "3ab95c31-5dad-482b-9b7e-f6929d3b2619"

## users to update csv file
UPDATE_FILEPATH = "user_hierarchy_updates.csv"

#################################################################
#################################################################


def write_agent_update_file(path="user_hierarchy_updates.csv"):
    with open(path, 'w') as f:
        f.writelines("username,hierarchygroup\n")
        for i in range(1, 21):
            f.writelines(f"agent-{i:03},London\n")


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
    response = []
    for name, id, hg in zip(update_data['username'], update_data['id'], update_data['hierarchygroup']):
        print(f"{name:<10}\t{id}\t {hg}\t {hierarchy_groups[hg]}")
        # List user hierarchy groups
        r = connect_client.update_user_hierarchy(
            HierarchyGroupId=hierarchy_groups[hg],
            UserId=id,
            InstanceId=CONNECT_INSTANCE_ID
        )
        response.append(r)
    
    return response

## write the file
write_agent_update_file()

## get updates to apply
update_data = get_user_updates(UPDATE_FILEPATH)

## get each user's id
response = connect_client.list_users(InstanceId=CONNECT_INSTANCE_ID)
update_data["id"] = [user["Id"] for user in response["UserSummaryList"] if user["Username"] in update_data['username']]

## get each hierarchy group's id
response = connect_client.list_user_hierarchy_groups(InstanceId=CONNECT_INSTANCE_ID,)
hierarchy_groups = {group["Name"]: group["Id"] for group in response['UserHierarchyGroupSummaryList']}

## update connect 
response = update_each_user(update_data, hierarchy_groups)

with open('connect_jsons/update_user_hierarchy.json', 'w') as f:
    json.dump(response, f, indent=2)
