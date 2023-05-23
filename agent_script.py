import os
import requests

# Create directory if it does not exist
if not os.path.exists("agent_scripts"):
    os.mkdir("agent_scripts")

# Get the content of the script from the URL
url = "https://app.cognosys.ai/agents/4641560f-1ba9-4df6-ad62-1842ef8a892d"
response = requests.get(url)
script_content = response.content

# Create the file and write the content to it
file_path = os.path.join("agent_scripts", "agent_4641560f-1ba9-4df6-ad62-1842ef8a892d.py")
with open(file_path, "wb") as f:
    f.write(script_content)