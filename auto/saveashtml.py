import os

# Path to the local clone of NeuralGPT repository
neuralgpt_path = "E:/AI/NeuralGPT/NeuralGPT"

# Content produced by Cognosys
content = "This is some content produced by Cognosys."

# Create the HTML file
filename = "content.html"
filepath = os.path.join(neuralgpt_path, filename)
with open(filepath, "w") as f:
    f.write("<html>\n")
    f.write("<head>\n")
    f.write("<title>Content from Cognosys</title>\n")
    f.write("</head>\n")
    f.write("<body>\n")
    f.write(f"<p>{content}</p>\n")
    f.write("</body>\n")
    f.write("</html>\n")

print(f"File saved to {filepath}")