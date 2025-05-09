# PDF to Markdown Converter

This project allows you to convert PDF files to Markdown format using the Qwen2.5-VL-3B-Instruct model.

## 1. Download the Model

First, install the required tool and download the Qwen2.5-VL-3B-Instruct model locally:

```bash
pip install modelscope
modelscope download --model Qwen/Qwen2.5-VL-3B-Instruct --local_dir ../local_models/Qwen2.5-VL-3B-Instruct
```

## 2. Convert PDF to Markdown

To convert a PDF file to Markdown, run the following command:

```bash
python main.py --pdf ./test_ocr.pdf --model ../local_models/Qwen2.5-VL-3B-Instruct --output output.md
```

- Replace `./test_ocr.pdf` with the path to your PDF file.
- The output will be saved as `output.md`.

## 3. Requirements

- Python 3.8 or higher
- [modelscope](https://modelscope.cn/) Python package

## 4. Notes

- Make sure you have enough disk space for the model download.
- The conversion process may require a GPU for optimal performance, but CPU is also supported.

## 5. Example

```bash
python main.py --pdf ./sample.pdf --model ../local_models/Qwen2.5-VL-3B-Instruct --output sample_output.md
```

This will convert `sample.pdf` to `sample_output.md` using the specified model.
