import os
from converters import PDFToImageConverter, ImageToMarkdownConverter
from PIL import Image

"""
This script processes a PDF file by converting it to a JPEG image and then converting the image to markdown text.
"""
class PDFMarkdownProcessor:
    def __init__(self, pdf_converter = None, image_converter = None, md_output_dir = "markdown_output"):
        self.pdf_converter = pdf_converter or PDFToImageConverter()
        self.image_converter = image_converter or ImageToMarkdownConverter()
        self.md_output_dir = md_output_dir
        if not os.path.exists(self.md_output_dir):
            os.makedirs(self.md_output_dir)

    def process_pdf(self, pdf_path):
        """
        Process a PDF file by converting it to a JPEG image and then converting the image to markdown text.
        """
        image_path = self.pdf_converter.convert(pdf_path)
        markdown_texts = []

        for i, image_path in enumerate(image_path):
            page_num = i + 1
            md_file =os.path.join(self.md_output_dir, f"page_{page_num}.md")
            markdown_text = self.image_converter.convert(image_path, md_file)

            # Check if it is valid
            if markdown_text.startswith("Conversion failed"):
                print(f"Failed to process page {page_num}: {markdown_text}")
                markdown_texts.append(f"## Page {page_num}\n{markdown_text}\n")
            else:
                markdown_texts.append(f"## Page {page_num}\n{markdown_text}\n")

        # Write all markdown texts to a single file
        all_md_file = os.path.join(self.md_output_dir, "all_pages.md")
        with open(all_md_file, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_texts))
        print(f"All pages have been processed and saved to {all_md_file}")