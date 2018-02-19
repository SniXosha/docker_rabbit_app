import pika
import psycopg2
import time
import sys

timeout = 0.01
try:
	connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@rabbit:5672"))
except:
	success = False
	while not success:
		try:
			time.sleep(timeout)
			timeout *= 2
			connection = pika.BlockingConnection(pika.URLParameters("amqp://guest:guest@rabbit:5672"))
			success = True
		except:
			print("Err:", sys.exc_info()[0])
			success = False
print("connected to rabbit\n")

timeout = 0.01
conn_string = "host='database' dbname='rabdb' user='dockeruser'"
try:
	dbconn = psycopg2.connect(conn_string)
except:
	success = False
	while not success:
		try:
			time.sleep(timeout)
			timeout *= 2
			connection = psycopg2.connect(conn_string)
			success = True
		except:
			print("Err:",sys.exc_info()[0])
			success = False
dbconn.autocommit = True
cursor = dbconn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS rabdb_msg (id SERIAL PRIMARY KEY, msg TEXT NOT NULL);")

cursor.execute("SELECT * FROM rabdb_msg;")
row_count = 0
for row in cursor:
	row_count += 1
	print("row: %s    %s\n" % (row_count, row) )

channel = connection.channel()

channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
	rec = body.decode()
	cursor.execute("INSERT INTO rabdb_msg VALUES (DEFAULT,%s)",(rec,))
	print(" [x] Received %r" % rec)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
