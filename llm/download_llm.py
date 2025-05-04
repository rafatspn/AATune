import os
import torch
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set your custom model directory
MODEL_DIR = "/lus/grand/projects/EE-ECP/araf/llms/starcoder_v2_15b"  # Change to your preferred directory
CACHE_DIR = "/lus/grand/projects/EE-ECP/araf/llms/cache"  # Specify cache directory

# Create the cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

# If the directory does not exist, download the model

print("Downloading model... This might take a while.")

# Retry strategy setup
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# Increase the timeout for the request
timeout = 300  # 5 minutes timeout

MODEL_NAME = "bigcode/starcoder2-15b"  # Change to the desired model name

# Download the model and tokenizer using the custom cache directory and retry mechanism
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, device_map="auto", cache_dir=CACHE_DIR, timeout=timeout)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR, timeout=timeout)
print("Model downloaded successfully!")

print("Model loaded successfully!")
