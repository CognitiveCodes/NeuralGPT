import pika

# connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# create a queue for each instance of the NeuralGPT agent
channel.queue_declare(queue='agent1')
channel.queue_declare(queue='agent2')
channel.queue_declare(queue='agent3')

# define a callback function to process incoming messages
def callback(ch, method, properties, body):
    # process message and execute appropriate task
    print("Received message: %r" % body)

# start consuming messages from the queue
channel.basic_consume(queue='agent1', on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue='agent2', on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue='agent3', on_message_callback=callback, auto_ack=True)

print('Waiting for messages...')
channel.start_consuming()