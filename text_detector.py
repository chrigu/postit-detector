import io
import os
import urllib.request

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()


def detect_text(url):
    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__), url)
    print(url)
    # Loads the image into memory
    # with io.open(url, 'rb') as image_file:
    #     content = image_file.read()

    response = urllib.request.urlopen(url)
    content = response.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.document_text_detection(image=image)
    full_text = response.full_text_annotation

    if full_text:
        return full_text.text.replace('\n','')
    else:
        return ""
