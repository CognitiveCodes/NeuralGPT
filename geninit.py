# Import necessary modules
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow

# Import project modules
from NeuralGPT-0,1 import DualCoreLLM
from NeuralGPT-0,1 import module2
from NeuralGPT-0,1 import module3
from NeuralGPT-0,1 import module4
from NeuralGPT-0,1 import module5

# Define function to execute all modules
def execute_modules():
    DualCoreLLM.execute()
    module2.execute()
    module3.execute()
    module4.execute()
    module5.execute()

# Define main function to start GUI and execute modules
def main():
    # Start GUI
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()
    sys.exit(app.exec_())

    # Execute modules
    execute_modules()

if __name__ == '__main__':
    main()