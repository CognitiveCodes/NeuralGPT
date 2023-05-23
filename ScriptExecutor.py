import subprocess

class ScriptExecutor:
    def __init__(self, script_path):
        self.script_path = script_path

    def execute_script(self, input_data):
        try:
            # Run the script in a sandboxed environment
            output = subprocess.check_output(['python', self.script_path], input=input_data, timeout=10, stderr=subprocess.STDOUT)
            return output.decode('utf-8')
        except subprocess.TimeoutExpired:
            return "Script execution timed out"
        except subprocess.CalledProcessError as e:
            return f"Script execution failed with error code {e.returncode}: {e.output.decode('utf-8')}"
        except Exception as e:
            return f"Script execution failed with exception: {str(e)}"

# Example usage
executor = ScriptExecutor('path/to/script.py')
result = executor.execute_script(b'input data')
print(result)