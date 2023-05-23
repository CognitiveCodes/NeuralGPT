import os
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfFileReader(f)
        text = ''
        for page in pdf_reader.pages:
            text += page.extractText()
        return text
    
def main():
    directory = 'E:\AI\NeuralGPT\NeuralGPT'
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            text = extract_text_from_pdf(pdf_path)
            txt_path = os.path.splitext(pdf_path)[0] + '.txt'
            with open(txt_path, 'w') as f:
                f.write(text)

if __name__ == '__main__':
    main()