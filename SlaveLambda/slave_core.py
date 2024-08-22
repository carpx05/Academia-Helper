from logger import LogType, log
<<<<<<< HEAD
from slave_utils import get_credentials_from_s3, process_credential
import json
import os
import concurrent.futures


TAG = "Academia_Attendance_Slave_Lambda"
S3_BUCKET = os.environ['db_name']
CREDENTIALS_FILE = os.environ['credentials_name']


def lambda_handler(event, context):
    try:
        credentials = get_credentials_from_s3(S3_BUCKET, CREDENTIALS_FILE)

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for cred in credentials:
                username = cred.get('username')
                password = cred.get('password')
                log(TAG, LogType.INFO, "Data retrieved for " + str(username))
                future = executor.submit(process_credential, username, password)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
    except Exception as e:
        log(TAG, LogType.ERROR, "Slave Lambda Error: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f"Lambda Error: {str(e)}")
        }
=======
from slave_utils import get_attendance
import json

TAG = "Academia_Attendance_Slave_Lambda"


def lambda_handler(event, context):
    # TODO implement
    username = event['username']
    password = event['password']
    try:
        attendance = get_attendance(username, password)
        log(TAG, LogType.INFO, "Data retrieved for " + str(username))
    except Exception as e:
        log(TAG, LogType.ERROR, "Error fetching data for " + str(username) + " : " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(f"Slave Lambda Error: {str(e)}")
        }
    return {
        'statusCode': 200,
        'body': json.dumps(attendance)
    }
>>>>>>> 7f9e03ca59eccd259df706c891b6c05ca7d6ebf0
