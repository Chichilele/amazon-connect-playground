import boto3
import json

client = boto3.client('connect')
instance_id = "3ab95c31-5dad-482b-9b7e-f6929d3b2619"

## list users
response = client.list_users(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('connect_jsons/users.json', 'w') as f:
    json.dump(response, f, indent=2)

for user in response["UserSummaryList"]:
    print(f"username: {user['Username']} \t{user['Id']}")

## describe user
response = client.describe_user(
    UserId="846523c4-80d2-4ee1-a3aa-78e6baaf8a77",
    InstanceId=instance_id
)
with open('connect_jsons/user_g-agent.json', 'w') as f:
    json.dump(response, f, indent=2)



## list secu profiles
response = client.list_security_profiles(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('connect_jsons/security_profiles.json', 'w') as f:
    json.dump(response, f, indent=2)

## list Routing Profile
response = client.list_routing_profiles(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('connect_jsons/routing_profiles.json', 'w') as f:
    json.dump(response, f, indent=2)



#############################
######## HIERARCHY ##########
#############################

## Describe the user hierarchy structure
response = client.describe_user_hierarchy_structure(
    InstanceId=instance_id
)
with open('connect_jsons/user_hierarchy_structure.json', 'w') as f:
    json.dump(response, f, indent=2)

## List user hierarchy
response = client.list_user_hierarchy_groups(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('connect_jsons/user_hierarchy_groups.json', 'w') as f:
    json.dump(response, f, indent=2)

## Describe user hierarchy group
response = client.describe_user_hierarchy_group(
    # HierarchyGroupId='0d3f9236-c93a-4f4a-b178-bb5297293275',
    # HierarchyGroupId='cfa72c7a-4009-4e4e-92eb-31ab5361d33b',
    HierarchyGroupId='5d2450fb-324d-4763-9d99-fc8a012e06a0',
    InstanceId=instance_id
)
# with open('connect_jsons/london_user_hierarchy_group.json', 'w') as f:
# with open('connect_jsons/bristol_user_hierarchy_group.json', 'w') as f:
with open('connect_jsons/unitedkingdom_user_hierarchy_group.json', 'w') as f:
    json.dump(response, f, indent=2)

## List user hierarchy groups
response = client.update_user_hierarchy(
    HierarchyGroupId='string',
    UserId='string',
    InstanceId='string'
)
with open('connect_jsons/update_user_hierarchy.json', 'w') as f:
    json.dump(response, f, indent=2)





############################
## add users
# response = []
# for i in range(3):
i = 1
r = client.create_user(
    Username=f"agent-{i:03}",
    Password='Testpassword1',
    IdentityInfo={
        'FirstName': f"Agent-{i:03}",
        'LastName': 'Connect',
        'Email': f"agent-{i:03}.connect@email.co.uk"
    },
    PhoneConfig={
        'PhoneType': 'SOFT_PHONE',
        'AutoAccept': False,
        'AfterContactWorkTimeLimit': 120,
        # 'DeskPhoneNumber': 'string'
    },
    # DirectoryUserId='string',
    SecurityProfileIds=[
        'd076dd88-f192-461b-9b8e-4c0790362624',
    ],
    RoutingProfileId='453cf9c8-b936-4f06-876a-654b701db548',
    HierarchyGroupId='0d3f9236-c93a-4f4a-b178-bb5297293275',
    InstanceId=instance_id,
)
    # response.append(r)
