from typing import List, Optional
from uuid import UUID, uuid4
from openai import AsyncOpenAI
from io import BytesIO
from collections import Counter
import PIL.Image as image
import requests

import os
import google.generativeai as genai

from urllib.request import urlopen
from bs4 import BeautifulSoup

def preprocess(text):

    html = text
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style", "span", "ul", "form", "label", "footer", "img"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    l = []
    for li in lines:
      if li not in l:
        l.append(li)
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in l for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def word_validate(text, words):
    word_list = words.split(",")
    word_count = Counter(text.split())
    final_word = []
    for w in word_list:
        if word_count[w.replace(" ","")] >= 3:
            final_word.append(w.replace(" ", ""))
    
    return ", ".join(final_word)


def post_process(output_dict: dict):

    real_output = {}
    for k in output_dict.keys():
        if k == "images":
            real_output[k] = output_dict[k]
            continue
        real_output[k]={}
        for j in range(0, len(output_dict[k])):
            real_output[k][str(j)] = output_dict[k][j]
    
    return real_output


class gemini():

    def __init__(self):
        genai.configure(api_key='key')
        self.model = genai.GenerativeModel('gemini-pro-vision')

    async def get_response(self, prompt, images):
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        if images is not None:
            generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192
            }
            self.model = genai.GenerativeModel(model_name='gemini-pro-vision',
                                               generation_config=generation_config
                                               )
            prompt = f"""You are an SEO Assistant to create more engagement. For the webpage with following content and images\n
            """+prompt
            prompt = [prompt]
            for img in images:
                my_res = requests.get(img.url)
                my_img = image.open(BytesIO(my_res.content))
                prompt.append(my_img)
        else:
             self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
             prompt = f"""For the webpage with following content\n
             """ + prompt

        chat_session = self.model.start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text


class openai():

    def __init__(self):
        self.client = AsyncOpenAI(api_key='key')

    async def get_response(self, prompt, images):
        if images is not None:
            prompt = f"""For the webpage with following content and images.
            """+prompt
            cont = [{
            "type": "text",
            "text": f"{prompt}",
            }]
            for img in images:
                cont.append({"type": "image_url", "image_url": {"url": img.url,},})
        else:
            prompt = f"""For the webpage with following content using the given focus words.\n"""+prompt
            cont = f"{prompt}"
        chat_completion = await self.client.chat.completions.create(
        messages=[
            {
             "role": "system",
            "content": "You are an SEO Assistant to create more engagement"
            },
            {
                "role": "user",
                "content": cont,
            }
        ],
        model="gpt-4o",
        temperature=1,
        top_p=1,
        frequency_penalty=2,
        presence_penalty=2
        )
        return chat_completion.choices[0].message.content


class seo_optimizer():

    def __init__(self, engine):

        if engine == 'gemini pro vision' or engine is None:
            self.client = gemini()
        
        if engine == 'chat gpt':
            self.client = openai()

    
    async def get_composite(self, text:str, focus_words:str =None, images=None):
        out_str = []
        fn_dict = {"meta_title":"generate a list with 3 versions of meta titles here with less 50 characters in length with more engagement",
                   "meta_description": "generate a list with 3 versions of meta descriptions here with less than 140 characters in length"}
        outputs = ["meta_title", "meta_description"]
        for f in outputs:
            out_str.append("'"+f+"'"+":"+fn_dict[f])
        output_json = "Please create and output only the response in the following format:\n"+"{"+",\n".join(out_str)+"}"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        for i in range(0, len(response)):
            if response[i] == "{":
                s = i
                break

        for i in range(1, len(response)):
            if response[len(response)-i] == "}":
                e = len(response)-i
                break
        response_dict = eval(response[s:e+1]) 
        return post_process(response_dict)

    
    async def get_meta_title(self, text:str, focus_words:str=None, images=None):
        output_json = "Please generate and output a list with 3 versions of meta titles with maximum of 50 characters and the format of output ['title1', 'title2', 'title3'] only"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        response = response.replace("<title>","").replace("</title>","").replace("\"","").replace("\n","")
        return post_process({'meta_title': eval(response)})
    

    async def get_meta_description(self, text:str, focus_words:str = None, images=None):
        output_json = "Generate and output a list with 3 versions of meta description with one sentence and maximum of 140 characters and the format of output ['description1', 'description2', 'description3'] only"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        return post_process({'meta_description': eval(response.replace("\"","").replace("\n",""))})
    

    async def get_alt_tags(self, text:str=None, images=None):
        output_json = "generate a list with 3 different versions of ALT Image Tags for the image with maximum of 120 characters and the format of output ['alt_tag1', 'alt_tag2', 'alt_tag3'] only"
        if text != None:
            text = preprocess(text)
            prompt = f"""Content: {text}
            """ + output_json
        else:
            prompt = output_json
        response = await self.client.get_response(prompt, images)
        image_id = images[0].id
        response_dict = {}
        response_dict[image_id] = eval(response)
        response_dict = post_process(response_dict)
        return {"images": response_dict}


    async def get_fb_og_title(self, text:str, focus_words:str = None, images=None):
        output_json = "Please generate and output a list with 3 versions of og titles for sharing the website on facebook with maximum of 50 characters and the format of output ['title1', 'title2', 'title3'] only"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        response = response.replace("<title>","").replace("</title>","").replace("\"","").replace("\n","")
        return post_process({'fb_og_title': eval(response)})
    

    async def get_fb_og_description(self, text:str, focus_words:str = None, images=None):
        output_json = "Generate and output a list with 3 versions of og descriptions for sharing the website on facebook, with maximum of 60 characters and the format of output ['description1', 'description2', 'description3'] only"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        return post_process({'fb_og_description': eval(response.replace("\"","").replace("\n",""))})


    async def get_fb_composite(self, text:str, focus_words:str=None, images=None):
        out_str = []
        fn_dict = {"fb_og_title":"generate a list with 3 versions of og titles for sharing the website on facebook with maximum of 50 characters",
                   "fb_og_description": "generate a list with 3 versions of og descriptions for sharing the website on facebook, with maximum of 60 characters"}
        outputs = ['fb_og_title', 'fb_og_description']
        for f in outputs:
            out_str.append("'"+f+"'"+":"+fn_dict[f])
        output_json = "Please create and output only the response in the following format:\n"+"{"+",\n".join(out_str)+"}"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        
        for i in range(0, len(response)):
            if response[i] == "{":
                s = i
                break

        for i in range(1, len(response)):
            if response[len(response)-i] == "}":
                e = len(response)-i
                break
        response_dict = eval(response[s:e+1])
        return post_process(response_dict)
    

    async def get_x_og_title(self, text:str, focus_words:str=None, images=None):
        output_json = "Output only a list with 3 versions of og titles for sharing the website on twitter with maximum of 60 characters and the format of output should be ['title1', 'title2', 'title3'] without any other text"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        response = response.replace("<title>","").replace("</title>","").replace("\"","").replace("\n","")
        return post_process({'x_og_title': eval(response)})
    

    async def get_x_og_description(self, text:str, focus_words:str=None, images=None):
        output_json = "Output only a list with 3 versions of og descriptions for sharing the website on twitter, with maximum of 150 characters and the format of output ['description1', 'description2', 'description3'] without any other text"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        return post_process({'x_og_description': eval(response.replace("\"","").replace("\n",""))})


    async def get_x_composite(self, text:str, focus_words:str = None, images=None):
        out_str = []
        fn_dict = {"x_og_title":"generate a list with 3 versions og titles for sharing the website on twitter with maximum of 60 characters and hashtags",
                   "x_og_description": "generate a list with 3 versions of og descriptions for sharing the website on twitter, with maximum of 150 characters and hashtags"}
        outputs = ['x_og_title', 'x_og_description']
        for f in outputs:
            out_str.append("'"+f+"'"+":"+fn_dict[f])
        output_json = "Please create and output only the response in the following format:\n"+"{"+",\n".join(out_str)+"}"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        
        for i in range(0, len(response)):
            if response[i] == "{":
                s = i
                break

        for i in range(1, len(response)):
            if response[len(response)-i] == "}":
                e = len(response)-i
                break
        response_dict = eval(response[s:e+1])
        return post_process(response_dict)
        

    async def get_social_composite(self, text:str, focus_words:str=None, images=None):
        out_str = []
        fn_dict = {"fb_og_title":"generate a list with 3 versions og titles for sharing the website on facebook with maximum of 50 characters",
                   "fb_og_description": "generate a list with 3 versions of og descriptions for sharing the website on facebook, with maximum of 60 characters",
                   "x_og_title":"generate a list with 3 versions of og titles for sharing the website on twitter with maximum of 60 characters and hashtags",
                   "x_og_description": "generate a list with 3 versions of og descriptions for sharing the website on twitter, with maximum of 150 characters"}
        outputs = ['fb_og_title', 'fb_og_description', 'x_og_title', 'x_og_description']
        for f in outputs:
            out_str.append("'"+f+"'"+":"+fn_dict[f])
        output_json = "Please create and output only the response in the following format:\n"+"{"+",\n".join(out_str)+"}"
        text = preprocess(text)
        if focus_words is not None:
            focus_str = word_validate(text, focus_words)
            focus_prompt = f"""Use atleast one of these focus words: {focus_str} in the outputs"""
        else:
            focus_prompt = ""
        prompt = f"""Content: {text}
        """ + focus_prompt + output_json
        response = await self.client.get_response(prompt, images)
        for i in range(0, len(response)):
            if response[i] == "{":
                s = i
                break

        for i in range(1, len(response)):
            if response[len(response)-i] == "}":
                e = len(response)-i
                break
        response_dict = eval(response[s:e+1])
        return post_process(response_dict)
        