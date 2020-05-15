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
with open('users.json', 'w') as f:
    json.dump(response, f, indent=2)

for user in response["UserSummaryList"]:
    print(f"username: {user['Username']} \t{user['Id']}")

## list secu profiles
response = client.list_security_profiles(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('secu_profiles.json', 'w') as f:
    json.dump(response, f, indent=2)

## list Routing Profile
response = client.list_routing_profiles(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('route_profiles.json', 'w') as f:
    json.dump(response, f, indent=2)


## list HierarchyGroupId
response = client.list_user_hierarchy_groups(
    InstanceId=instance_id,
    # NextToken='string',
    # MaxResults=123
)
with open('hierarchy_groups.json', 'w') as f:
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
