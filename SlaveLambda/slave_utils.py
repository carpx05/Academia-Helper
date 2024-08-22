from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from headless_chrome import create_driver


def perform_login(username, password):
    driver.switch_to.frame('zohoiam')
    driver.find_element(By.ID, "login_id").send_keys(username) 
    driver.find_element(By.ID, "nextbtn").click()
    password_element = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "password")))
    password_element.send_keys(password)
    button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "nextbtn")))
    button.click()


def get_attendance(username, password):
    driver = webdriver.Chrome()
    # driver = create_driver()
    driver.get("https://academia.srmist.edu.in/#Page:My_Attendance")
    perform_login(username, password)
    driver.get("https://academia.srmist.edu.in/#Page:My_Attendance")
    table = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//table)[5]")))
    attendance = table.text
    return attendance

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from headless_chrome import create_driver
import os
import psycopg2
import boto3
import json


def perform_login(username, password):
    driver.switch_to.frame('zohoiam')
    driver.find_element(By.ID, "login_id").send_keys(username) 
    driver.find_element(By.ID, "nextbtn").click()
    password_element = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "password")))
    password_element.send_keys(password)
    button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "nextbtn")))
    button.click()


def get_attendance(username, password):
    driver = webdriver.Chrome()
    # driver = create_driver()
    driver.get("https://academia.srmist.edu.in/#Page:My_Attendance")
    perform_login(username, password)
    driver.get("https://academia.srmist.edu.in/#Page:My_Attendance")
    table = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//table)[5]")))
    attendance = table.text
    return attendance


def get_credentials_from_s3(bucket, file_key):
    response = s3_client.get_object(Bucket=bucket, Key=file_key)
    credentials = json.loads(response['Body'].read().decode('utf-8'))
    return credentials


def process_credential(username, password):
    attendance_data = get_attendance(username, password)
    parsed_data = []
    for data in attendance_data:
        course_code, course_title, details, faculty_name, slot, hours_conducted, hours_absent, attendance_percentage, university_practical_details = data
        parsed_data.append((course_code, course_title, details[0], faculty_name, slot,
                            hours_conducted, hours_absent, attendance_percentage, university_practical_details))

    # Insert data into PostgreSQL
    insert_data_to_postgresql(parsed_data)
    return {
        'statusCode': 200,
        'body': json.dumps("Data successfully inserted")
    }


def insert_data_to_postgresql(parsed_data):
    conn = psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT']
    )
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO attendance (course_code, course_title, category, faculty_name, slot, 
                            hours_conducted, hours_absent, attendance_percentage, 
                            university_practical_details)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, parsed_data)
    conn.commit()

    cursor.close()
    conn.close()


def parse_attendance_data(attendance_data):
    lines = attendance_data.strip().split('\n')
    lines = lines[1:]
    parsed_data = []

    for i in range(0, len(lines), 2):  
        course_code = lines[i].strip()
        details = lines[i+1].split()

        if "Theory" in details:
            course_type = "Theory"
        elif "Practical" in details:
            course_type = "Practical"
        else:
            raise ValueError("Course type not found in data")

        course_title = ' '.join(details[1:details.index(course_type)])

        start_index = details.index(course_type) + 1
        end_index = [j for j, s in enumerate(details) if ')' in s][0] + 1
        faculty_name = ' '.join(details[start_index:end_index])

        category = details[0]
        slot = details[end_index] 
        hours_conducted = int(details[end_index + 1])
        hours_absent = int(details[end_index + 2])
        attendance_percentage = float(details[end_index + 3])

        parsed_data.append((course_code, course_title, category, faculty_name, slot,
                            hours_conducted, hours_absent, attendance_percentage))

        return parsed_data
