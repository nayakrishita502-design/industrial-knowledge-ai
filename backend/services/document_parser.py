import os
import pandas as pd

from pypdf import PdfReader
from docx import Document


class DocumentParser:

    def extract_text(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            return self._read_pdf(file_path)

        elif extension == ".docx":
            return self._read_docx(file_path)

        elif extension == ".txt":
            return self._read_txt(file_path)

        elif extension == ".csv":
            return self._read_csv(file_path)

        elif extension == ".xlsx":
            return self._read_excel(file_path)

        else:
            raise Exception(f"Unsupported file type: {extension}")

    def _read_pdf(self, file_path):

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

        return text

    def _read_docx(self, file_path):

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:
            paragraphs.append(paragraph.text)

        return "\n".join(paragraphs)

    def _read_txt(self, file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _read_csv(self, file_path):

        dataframe = pd.read_csv(file_path)

        return dataframe.to_string(index=False)

    def _read_excel(self, file_path):

        dataframe = pd.read_excel(file_path)

        return dataframe.to_string(index=False)