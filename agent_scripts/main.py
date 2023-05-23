from database import DatabaseModule
from sqlite_example import SqliteExample

from script_executor import ScriptExecutor
from script_executor_example import ScriptExecutorExample

# Create a new instance of the DatabaseModule class
database = DatabaseModule("mydatabase.db")

# Create a new instance of the ScriptExecutor class
script_executor = ScriptExecutor("myscript.py")

# Use the database object to store some data
data = "Hello, world!"
table_name = "mytable"
database.store_data(data, table_name)

# Retrieve the stored data
query = "Hello, world!"
retrieved_data = database.retrieve_data(query, table_name)

# Use the script_executor object to execute a script
input_data = b"Hello, world!"
output = script_executor.get_script_output(input_data)

# Print the retrieved data and script output
print(retrieved_data)
print(output)
