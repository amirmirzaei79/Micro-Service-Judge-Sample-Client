import mysql.connector, pika, minio
import sys, os, time

# Command Line Arguemtns <Submission_File_Path> <Submission_Language> <Testcases_File_Path> <Time_Limit(s)> <Memory_Limit(KB)>  <Tester_File_Path>(Optional)

# Parameters for connecting to other parts of system
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "rootpass")
DB_NAME = os.environ.get("DB_NAME", "testdb")
MINIO_HOST = os.environ.get("MINIO_HOST", "localhost")
MINIO_PORT = os.environ.get("MINIO_PORT", "9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "testbucket")
MQ_HOST = os.environ.get("MQ_HOST", "localhost")
MQ_PORT = int(os.environ.get("MQ_PORT", "5672"))
MQ_USER = os.environ.get("MQ_USER", "guest")
MQ_PASS = os.environ.get("MQ_PASS", "guest")
MQ_QUEUE = os.environ.get("MQ_QUEUE", "testqueue")


db_connection =  mysql.connector.connect(host=DB_HOST, 
                                         user=DB_USER, password=DB_PASS, 
                                         database=DB_NAME)
db_cursor = db_connection.cursor(buffered=True)
sql = f"CREATE TABLE IF NOT EXISTS Submission (\
        id int UNSIGNED AUTO_INCREMENT PRIMARY KEY,\
        status VARCHAR(40),\
        results_path VARCHAR(255),\
        log_path VARCHAR(255),\
        score FLOAT DEFAULT 0)"
db_cursor.execute(sql)
db_connection.commit()

sql = f"INSERT INTO Submission (status) VALUES ('In Queue')"
db_cursor.execute(sql)
db_connection.commit()
s_id = db_cursor.lastrowid

print("DB record created")

client = minio.Minio(
    MINIO_HOST + ":" + MINIO_PORT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

bucket_found = client.bucket_exists(MINIO_BUCKET)
if not bucket_found:
    client.make_bucket(MINIO_BUCKET)

client.fput_object(
    MINIO_BUCKET, f"submissions/{s_id}/{os.path.basename(sys.argv[1])}", sys.argv[1]
)
client.fput_object(
    MINIO_BUCKET, f"testcases/{s_id}/{os.path.basename(sys.argv[3])}", sys.argv[3]
)

print("Uploading to storage completed")

mq_credentials = pika.PlainCredentials(username=MQ_USER, password=MQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST, 
                                                               port=MQ_PORT, 
                                                               credentials=mq_credentials))
channel = connection.channel()
channel.queue_declare(queue=MQ_QUEUE, durable=True)
channel.basic_qos(prefetch_count=1)

if (len(sys.argv) > 6 and sys.argv[6] != '' and sys.argv[6] != 'Default' and sys.argv[6] != 'default'):
    tester_path = f"tester/{s_id}/{os.path.basename(sys.argv[6])}"
    client.fput_object(
    MINIO_BUCKET, tester_path, sys.argv[6]
    )
else:
    print("Using default tester")
    tester_path = "Default"

body = f"submissions/{s_id}/{os.path.basename(sys.argv[1])}" + "\0" + sys.argv[2] + "\0" + sys.argv[4] + "\0" + \
       sys.argv[5] + "\0" + f"testcases/{s_id}/{os.path.basename(sys.argv[3])}\0" + tester_path + "\0" + "Submission" + "\0" + str(s_id)
channel.basic_publish(exchange='',
                      routing_key=MQ_QUEUE, 
                      body=body)

print("Job Queued")
print("Job Details: (submission_path, language, time_limit(s), memory_limit(KB), testcases_path, tester, DB_table, DB_ID)")
print(body.split("\0"))
sql = "SELECT status FROM Submission WHERE id=%s"
values = (s_id,)
db_cursor.execute(sql, values)
db_connection.commit()
print(f"Submission ID: {s_id}")

records = db_cursor.fetchall()
status = records[0][0]

while status == "In Queue" or status == "Testing":
    time.sleep(1)
    sql = "SELECT status FROM Submission WHERE id=%s"
    values = (s_id,)
    db_cursor.execute(sql, values)
    db_connection.commit()

    records = db_cursor.fetchall()
    status = records[0][0]
    print(f"Current Status: {status}")
    if status == "In Queue" or status == "Testing":
        time.sleep(2)

sql = "SELECT status, score, results_path, log_path FROM Submission WHERE id=%s"
values = (s_id,)
db_cursor.execute(sql, values)
db_connection.commit()

records = db_cursor.fetchall()
status = records[0][0]
score = records[0][1]
print()
print("Result:")
print(f"{status} - score: {score}")

if len(records) > 0:
    if records[0][3] and len(records[0][3]) > 0:
        try:
            client.fget_object(MINIO_BUCKET, records[0][3], 'log.txt')
            print("Logs saved as log.txt")
        except minio.S3Error as exc:
            if (exc.code == "NoSuchKey"):
                print("Log File doesn't exist.")
            else:
                print("Error occured: ", exc)
    if records[0][2] and len(records[0][2]) > 0:
        try:
            client.fget_object(MINIO_BUCKET, records[0][2], 'results.txt')
            print("Results saved as log.txt")
        except minio.S3Error as exc:
            if (exc.code == "NoSuchKey"):
                print("Results File doesn't exist.")
            else:
                print("Error occured: ", exc)
