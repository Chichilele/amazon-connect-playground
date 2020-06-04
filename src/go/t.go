package main

import (
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/dynamodb"

	"fmt"
)

func main() {
	sess := session.Must(session.NewSessionWithOptions(session.Options{
		SharedConfigState: session.SharedConfigEnable,
	}))

	// Create DynamoDB client
	svc := dynamodb.New(sess)
	// snippet-end:[dynamodb.go.update_item.session]

	// Create item in table Movies
	my_table := "connect-user-hierarchy"
	user1 := "user_id02"
	hierarchy1 := "1859"

	input1 := &dynamodb.UpdateItemInput{
		ExpressionAttributeValues: map[string]*dynamodb.AttributeValue{
			":hgID": {
				S: aws.String(hierarchy1),
			},
		},
		TableName: aws.String(my_table),
		Key: map[string]*dynamodb.AttributeValue{
			"userID": {
				S: aws.String(user1),
			},
		},
		UpdateExpression: aws.String("set hierarchygroupID = :hgID"),
	}

	// input1 := &dynamodb.UpdateItemInput{
	// 	AttributeUpdates: map[string]*dynamodb.AttributeValueUpdate{
	// 		"hierarchygroupID": {
	// 			Value: &dynamodb.AttributeValue{
	// 				S: &hierarchy1,
	// 			},
	// 		},
	// 	},
	// 	TableName: aws.String(my_table),
	// 	Key: map[string]*dynamodb.AttributeValue{
	// 		"userID": {
	// 			S: aws.String(user1),
	// 		},
	// 	},
	// }

	r, err := svc.UpdateItem(input1)
	if err != nil {
		fmt.Println(err.Error())
		return
	}

	fmt.Println("Successfully updated '" + user1 + " hierarchy group id to " + hierarchy1)
	fmt.Println(r)
	// snippet-end:[dynamodb.go.update_item.call]
}

// snippet-end:[dynamodb.go.update_item]
