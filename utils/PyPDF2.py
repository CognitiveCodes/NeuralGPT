import os
import shutil
import PyPDF2

pdf_path = 'path/to/pdf/file.pdf'
save_path = 'E:/AI/NeuralGPT/NeuralGPT'

# Check if the save path exists, create it if it doesn't
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Open the PDF file in read-binary mode
with open(pdf_path, 'rb') as pdf_file:
    # Read the PDF file
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    # Get the first page of the PDF
    page = pdf_reader.getPage(0)
    # Create a new PDF writer object
    pdf_writer = PyPDF2.PdfFileWriter()
    # Add the page to the PDF writer object
    pdf_writer.addPage(page)
    # Create a new PDF file name
    pdf_file_name = os.path.splitext(os.path.basename(pdf_path))[0] + '.pdf'
    # Save the PDF file to the specified location
    with open(os.path.join(save_path, pdf_file_name), 'wb') as new_pdf_file:
        pdf_writer.write(new_pdf_file)