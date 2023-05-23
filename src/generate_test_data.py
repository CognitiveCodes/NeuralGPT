import random
import string

# Define a list of possible actions
actions = ['open', 'close', 'turn on', 'turn off', 'start', 'stop']

# Define a list of possible objects
objects = ['door', 'window', 'light', 'fan', 'TV', 'AC']

# Define a list of possible locations
locations = ['living room', 'bedroom', 'kitchen', 'bathroom', 'garage']

# Define a function to generate random test data
def generate_test_data():
    action = random.choice(actions)
    obj = random.choice(objects)
    location = random.choice(locations)
    message = f"{action} the {obj} in the {location}"
    return message

# Generate 10 random test messages
for i in range(10):
    test_message = generate_test_data()
    print(test_message)