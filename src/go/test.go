package main

import (
	"log"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/connect"
	"github.com/aws/aws-sdk-go/service/s3"
)

var invokeCount = 0
var myObjects []*s3.Object
var uhg []*connect.HierarchyGroupSummary
var user *connect.User

func init() {
	s3svc := s3.New(session.New())
	connectsvc := connect.New(session.New())
	listObjInput := &s3.ListObjectsV2Input{
		Bucket: aws.String("connect-hierarchy-update"),
	}
	listObjResult, _ := s3svc.ListObjectsV2(listObjInput)
	myObjects = listObjResult.Contents

	listUHGInput := &connect.ListUserHierarchyGroupsInput{
		InstanceId: aws.String("3ab95c31-5dad-482b-9b7e-f6929d3b2619"),
	}
	listUHGResult, _ := connectsvc.ListUserHierarchyGroups(listUHGInput)
	uhg = listUHGResult.UserHierarchyGroupSummaryList

	describeUserInput := &connect.DescribeUserInput{
		InstanceId: aws.String("3ab95c31-5dad-482b-9b7e-f6929d3b2619"),
		UserId:     aws.String("4100e0d6-0418-4b14-8b6a-02d8669ed335"),
	}
	describeUserOutput, _ := connectsvc.DescribeUser(describeUserInput)
	user = describeUserOutput.User
}

func LambdaHandler() (int, error) {
	invokeCount = invokeCount + 1
	log.Print("objects: \n")
	log.Print(myObjects)
	log.Print("user hierarchy groups: \n")
	log.Print(uhg)
	log.Print("user: \n")
	log.Print(user)
	return invokeCount, nil
}

func main() {
	lambda.Start(LambdaHandler)
}
