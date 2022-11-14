# Microservice Judge Sample Client

[Jump to Instructions](#Instructions)

[Check out Microservice Judge](https://github.com/amirmirzaei79/microservice-judge)

This is a sample client for **Microservice** Judge project to provide an implementation and help with testing the judge.

Note that this is just a sample client and should not be used in production; as it uploads testcases and tester (if specified) to storage for each submission. It is not the typical use case  for such a program and in production it should be sufficient to upload one testcase file and one tester (if necessary) for each group of submission (each problem).

## Instructions

0. Spin up MySQL, RabbitMQ, MinIO & Microservice Judge

1. Set the following environmental variables or change their default value in first section of code.

   ```
   DB_HOST (Host address of database)
   DB_PORT (Port for database connection)
   DB_USER (database user (must have write access))
   DB_PASS (password for database user)
   DB_NAME (name of the database that is used)
   MINIO_HOST (Host address of MinIO)
   MINIO_PORT (Port for MinIO connection)
   MINIO_ACCESS_KEY (MinIO Access Key (username))
   MINIO_SECRET_KEY (MinIO Secret Key (password))
   MINIO_BUCKET (name of the MinIO bucket that is used)
   MQ_HOST (Host address of RabbitMQ)
   MQ_PORT (Port for RabbitMQ connection)
   MQ_USER (RabbitMQ user)
   MQ_PASS (password for RabbitMQ user)
   MQ_NAME (name of the queue that is used)
   ```

2. Run the program, give it following command line arguments

   ```bash
   python3 judge_client.py <Submission_File_Path> <Submission_Language> <Testcases_File_Path> <Time_Limit(s)> <Memory_Limit(KB)>
   ```

   to use default tester or 

   ```bash
   python3 judge_client.py <Submission_File_Path> <Submission_Language> <Testcases_File_Path> <Time_Limit(s)> <Memory_Limit(KB)> <Tester_File_Path>
   ```

   to specify a custom tester.

   Replace each <> with appropriate values; for example

   ```bash
   python3 judge_client.py ./power.py Python3 ./power_testcases.zip 1 64000
   ```

