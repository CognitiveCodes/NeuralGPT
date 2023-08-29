import os
import json
import argparse
from flowise import FlowiseClient
from unified_model import UnifiedModel
def main(model_path):
 # Load pretrained model
 model = UnifiedModel(model_path)
 # Connect to FlowiseAI
 client = FlowiseClient()
 # Check for active instances of Neural AI
 active_instances = client.get_active_instances(model_name='NeuralGPT')
 if active_instances:
 # Communicate with other active instances
 instance_id = active_instances[0]['instance_id']
 chat_id = client.join_chat(instance_id)
 client.send_message(chat_id, 'Hello from another instance!')
 # Open chat window
 chat_id = client.create_chat(model_name='NeuralGPT')
 # Listen for messages
 while True:
 messages = client.get_messages(chat_id)
 for message in messages:
 if message['type'] == 'text':
 # Generate response
 response = model.generate_response(message['text'])
 # Send response
 client.send_message(chat_id, response)
if __name__ == '__main__':
 # Parse command line arguments
 parser = argparse.ArgumentParser()
 parser.add_argument('--model_path', type=str, required=True,
 help='Path to pretrained NeuralGPT model')
 args = parser.parse_args()
 # Check if model path exists
 if not os.path.exists(args.model_path):
 print(f"Error: Model path '{args.model_path}' does not exist.")
 exit()
 # Run main function
 main(args.model_path)