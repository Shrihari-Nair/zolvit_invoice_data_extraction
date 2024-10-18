import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path
# from PIL import Image
# import numpy as np

def image_format(image_path):
    img = Path(image_path)

    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")

    image_parts = [
        {
            "mime_type": "image/png", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
            "data": img.read_bytes()
        }
    ]
    return image_parts

def gemini_output(model, image_path, system_prompt, user_prompt):

    image_info = image_format(image_path)
    input_prompt= [system_prompt, image_info[0], user_prompt]
    response = model.generate_content(input_prompt)
    return response.text

def gemini_response(image_path):
    load_dotenv()  # take environment variables from .env.

    os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    MODEL_CONFIG = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
    }

    ## Safety Settings of Model
    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
    ]
    model = genai.GenerativeModel(model_name = "gemini-1.5-flash",
                              generation_config = MODEL_CONFIG,
                              safety_settings = safety_settings)

    system_prompt = """
               You are a specialist in comprehending receipts.
               Input images in the form of receipts will be provided to you,
               and your task is to respond to questions based on the content of the input image.
               """
    #system_prompt = "Convert Invoice data into json format with appropriate json tags as required for the data in image "

    # user_prompt = """Convert Invoice data into json format with appropriate json tags as required for the data in image. 
    #                 Make sure the entire image is taken into account. Structure the table properly if available in the image"""

    user_prompt = """Show all the text visible in the image and make sure no word is missed. Create a json file such that key is the line number and value is the content of that line"""

    output = gemini_output(model, image_path, system_prompt, user_prompt)
    return output
