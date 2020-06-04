// main.go
package main

import (
	"context"
	"encoding/csv"
	"log"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/connect"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"

	"os"
)

var instance_id = aws.String(os.Getenv("CONNECT_INSTANCE_ID"))

// read csv file and outputs a 2d list of string
func csvReader(filepath string) [][]string {
	// 1. Open the file
	recordFile, err := os.Open(filepath)
	if err != nil {
		log.Println("An error encountered ::", err)
	}
	// 2. Initialize the reader
	reader := csv.NewReader(recordFile)

	// 3. Read all the records
	records, _ := reader.ReadAll()

	return records
}

func handler(ctx context.Context, s3Event events.S3Event) ([]*connect.UpdateUserHierarchyOutput, error) {
	for _, record := range s3Event.Records {
		s3rec := record.S3
		log.Printf("[%s - %s] Bucket = %s, Key = %s \n", record.EventSource, record.EventTime, s3rec.Bucket.Name, s3rec.Object.Key)

		// read the updated file
		downloader := s3manager.NewDownloader(session.New())
		connectsvc := connect.New(session.New())

		// prepare file
		file, err := os.Create("/tmp/" + s3rec.Object.Key)
		if err != nil {
			exitErrorf("Unable to open file %q, %v", s3rec.Object.Key, err)
		}

		defer file.Close()

		numBytes, err := downloader.Download(file,
			&s3.GetObjectInput{
				Bucket: aws.String(s3rec.Bucket.Name),
				Key:    aws.String(s3rec.Object.Key),
			})
		if err != nil {
			exitErrorf("Unable to download item %q, %v", s3rec.Object.Key, err)
		}

		log.Println("Downloaded", file.Name(), numBytes, "bytes")
		records := csvReader(file.Name())

		// build UpdateUserHierarchyInput
		updates := make([]connect.UpdateUserHierarchyInput, len(records)-1)
		res := make([]*connect.UpdateUserHierarchyOutput, len(records)-1)
		for i, r := range records[1:] {
			updates[i] = connect.UpdateUserHierarchyInput{
				HierarchyGroupId: aws.String(r[1]),
				InstanceId:       instance_id,
				UserId:           aws.String(r[0]),
			}
			log.Println(updates[i])
			res[i], err = connectsvc.UpdateUserHierarchy(&updates[i])
			if err != nil {
				log.Println("Unable to update: ", err)
			}
		}
		return res, nil

	}
	return nil, nil
}

func main() {
	// Make the handler available for Remote Procedure Call by AWS Lambda
	lambda.Start(handler)
}

// Downloads an item from an S3 Bucket in the region configured in the shared config
// or AWS_REGION environment variable.

func exitErrorf(msg string, args ...interface{}) {
	log.Printf(msg+"\n", args...)
	// os.Exit(1)
}

// import (
// 	"log"

// 	"github.com/aws/aws-lambda-go/lambda"
// 	"github.com/aws/aws-sdk-go/aws"
// 	"github.com/aws/aws-sdk-go/aws/session"
// 	"github.com/aws/aws-sdk-go/service/connect"
// 	"github.com/aws/aws-sdk-go/service/s3"
// )

// var invokeCount = 0
// var myObjects []*s3.Object
// var uhg []*connect.HierarchyGroupSummary
// var user *connect.User

// func init() {
// 	s3svc := s3.New(session.New())
// 	connectsvc := connect.New(session.New())
// 	listObjInput := &s3.ListObjectsV2Input{
// 		Bucket: aws.String("connect-hierarchy-update"),
// 	}
// 	listObjResult, _ := s3svc.ListObjectsV2(listObjInput)
// 	myObjects = listObjResult.Contents

// 	listUHGInput := &connect.ListUserHierarchyGroupsInput{
// 		InstanceId: instance_id,
// 	}
// 	listUHGResult, _ := connectsvc.ListUserHierarchyGroups(listUHGInput)
// 	uhg = listUHGResult.UserHierarchyGroupSummaryList

// 	describeUserInput := &connect.DescribeUserInput{
// 		InstanceId: instance_id,
// 		UserId:     aws.String("4100e0d6-0418-4b14-8b6a-02d8669ed335"),
// 	}
// 	describeUserOutput, _ := connectsvc.DescribeUser(describeUserInput)
// 	user = describeUserOutput.User
// }

// func LambdaHandler() (int, error) {
// 	invokeCount = invokeCount + 1
// 	log.Print("objects: \n")
// 	log.Print(myObjects)
// 	log.Print("user hierarchy groups: \n")
// 	log.Print(uhg)
// 	log.Print("user: \n")
// 	log.Print(user)
// 	return invokeCount, nil
// }

// func main() {
// 	lambda.Start(LambdaHandler)
// }
