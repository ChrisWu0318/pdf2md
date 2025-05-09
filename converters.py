import os
import shutil
import torch
from pdf2image import convert_from_path
from transformers import AutoProcessor, AutoModelForCausalLM
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info
from PIL import Image

"""
This script converts a PDF file to a JPEG image with low resolution.
"""
class PDFToImageConverter:

    def __init__(self, output_dir = 'png_output', dpi = 200, fmt = 'jpeg', size = (1024, None)):
        self.output_dir = output_dir
        self.dpi = dpi
        self.fmt = fmt
        self.size = size
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def convert(self, pdf_path):
        print(f"Converting {pdf_path} to {self.output_dir} with{self.fmt}")
        image_paths = convert_from_path(
            pdf_path,
            dpi = self.dpi,
            fmt=self.fmt,
            output_floder = self.output_dir,
            size = self.size,
            path_only = True,
        )
        if not image_paths:
            raise ValueError(f"No images were created from {pdf_path}")
        for path in image_paths:
            print(f"Converted {path}")
        return image_paths
    
    def set_dpi(self, dpi):
        self.dpi = dpi
        print(f"DPI set to {self.dpi}")

"""
Use Qwen2.5-VL and vLLM, convert the image to markdown text
"""
class ImageToMarkdownConverter:

    def __init__(self, model_path = 'Qwen/Qwen2.5-VL-72B-Instruct', **kwargs):
        self.model_path = model_path
        # Determine the best available device
        if torch.cuda.is_available():
            self.device = 'cuda'
            print("Using NVIDIA GPU")
        elif torch.backends.mps.is_available():
            self.device = 'mps'
            print("Using Apple Silicon GPU")
        else:
            self.device = 'cpu'
            print("Using CPU")
        
        # Set default kwargs
        default_kwargs = {
            'dtype': 'auto',  # Let vLLM choose the best dtype
            'max_model_len': 8192 if self.device == 'cuda' else 4096,
            'trust_remote_code': True,
            'device': self.device,
        }
        default_kwargs.update(kwargs)

        # Use vLLm from local
        print(f"Loading model from {self.model_path}...")
        self.llm = LLM(
            model = self.model_path,
            quantization = None,
            **default_kwargs,
        )
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        print("Model loaded successfully")

    def convert(self, image_path, output_md_path, prompt = None, sampling_params = None):
        """
        Convert an image to markdown text, and save to output_md_path
        """
        if os.path.exists(output_md_path):
            print(f"Skipping {image_path}: {output_md_path} already exists.")
            with open(output_md_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content and not content.startswith("Conversion failed"):
                    return content
        
        print(f"Processing {image_path} on {self.device}...")
        image_path = os.path.abspath(image_path)

        if sampling_params is None:
            sampling_params = SamplingParams(
                temperature = 0.7,
                min_p = 0.1,
                max_tokens = 8192 if self.device == 'cuda' else 4096,
                stop_token_ids = []
            )

        if prompt is None:
            prompt = "Convert the image of a pdf document strictlt into markdown text,If there are mathematical formulas in the document, use Mathjax."

            message = [
                {"role": "system", "content": "You are a tool to parse documents."},
                {"role": "user", "content": [{"type": "image", "image": f"file://{image_path}"}, {"type": "text", "text": prompt}]},
            ]

            prompt_text = self.processor.apply_chat_template(message, tokenize = False, add_generation_prompt = True)
            image_input = process_vision_info(message)

            mm_data = {}
            if image_input is not None:
                if isinstance(image_input, list):
                    image_input = image_input[0]
                mm_data['image'] = image_input
            else:
                raise ValueError("No image input provided")
            
            llm_inputs = {"prompt": prompt_text, "multi_modal_data": mm_data}
            print(f"Input to LLM: {llm_inputs}")

            try:
                outputs = self.llm.generate([llm_inputs], sampling_params = sampling_params)
                markdown_text = outputs[0].outputs[0].text.strip()
                with open(output_md_path, "w", encoding="utf-8") as f:
                    f.write(markdown_text)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                markdown_text = f"Conversion failed: {e}"
            
            if not markdown_text or markdown_text == "```markdown" or markdown_text.isspace():
                markdown_text = "Conversion failed: No valid content generated."
            
            with open(output_md_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
                print(f"Saved Markdown to: {output_md_path}")
        
            return markdown_text