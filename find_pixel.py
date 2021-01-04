import re

def isolate_pixel(comment):
    pixel = re.findall('\{.*?\}',comment)
    print(pixel)
    return pixel




