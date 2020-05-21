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

def main():
    ## record details
    bucket = "connect-hierarchy-update"
    print("bucket: ", bucket, )

    ## write the file
    write_agent_update_file()

    ## get updates to apply
    update_data = get_user_updates(UPDATE_FILEPATH)    

    ## get each user's id
    response = connect_client.list_users(InstanceId=CONNECT_INSTANCE_ID)
    # update_data["id"] = [user["Id"] for user in response["UserSummaryList"] if user["Username"] in update_data['username']]
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
    
    with open('connect_jsons/update_user_hierarchy.json', 'w') as f:
        json.dump(response, f, indent=2)
    
    return response

## record details
bucket = "connect-hierarchy-update"
print("bucket: ", bucket, )

## write the file
write_agent_update_file()

## get updates to apply
update_data = get_user_updates(UPDATE_FILEPATH)    

## get each user's id
response = connect_client.list_users(InstanceId=CONNECT_INSTANCE_ID)
# update_data["id"] = [user["Id"] for user in response["UserSummaryList"] if user["Username"] in update_data['username']]
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

with open('connect_jsons/update_user_hierarchy.json', 'w') as f:
    json.dump(response, f, indent=2)

