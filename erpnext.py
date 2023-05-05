import requests
import re

class Book():
  def __init__(self, title, author=None):
    self.title = title
    self.author = author
    self.chapters = []
    
  def save_to_html(self, filename="erpnext.html", section_titles=True):
    header = f"""<!DOCTYPE html>
<html lang="en">
<head>
<title>{self.title}</title>
<style>
  body {{
	text-align: left;
	width: 50%;
	margin: 0 auto;
  }}
</style>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>"""
    if filename is None:
      filename = self.title.lower().replace(" ","-") + ".html"
    filename = filename.replace(":", "_")
    filename = filename.replace("-", "_")
    with open(filename, "w", encoding="utf-8") as f:
      f.write(header)
      f.write(f"<h1>{title}</h1>\n")
      if self.author is not None:
        f.write(f"<p><i>By {self.author}</i></p>\n")
      for i, chapter in enumerate(self.chapters):
        f.write(f"<h2>Chapter {i+1}. {chapter.title}</h2>\n")
        for j, section in enumerate(chapter.sections):
          if section_titles:
            f.write(f"<h3>{i+1}.{j+1}. {section.title}</h3>\n")
          text = section.text.replace("\n", "<br>")
          f.write(f"<p>{text}</p>\n")

class Chapter():
  def __init__(self, title):
    self.title = title
    self.sections = []

class Section():
  def __init__(self, title):
    self.title = title
    self.text = None
    
class Generator():
  def __init__(self, api_key):
    self.api_key = api_key

  def generate(self) -> str:
    return str()

class OpenAIGenerator(Generator):
  def generate(self, model, **kwargs):
    headers = {"Authorization": f"Bearer {self.api_key}"}
    response = requests.post(
      "https://api.openai.com/v1/completions",
      headers=headers,
      json={"model": model, **kwargs},
    )
    r = response.json()
    try:
      return r["choices"][0]["text"]
    except:
      print(r)
   
  
# generation parameters
topic = "Enterprise resource planning, data science, business intellignece, sales consulting, digital marketing, and marketing automation"
author = "William Oakes"
n_chapters = 10

import getpass
openai_api_key = getpass.getpass("Enter OpenAI API key: ")

gpt3 = OpenAIGenerator(openai_api_key)

# generate title
prompt = f"We are writing a book about {topic}. Generate a name for the book. Do not use quotes:\n"
title = gpt3.generate(model="text-davinci-003", prompt=prompt, max_tokens=32)
title = title.strip()

book = Book(title, author)

# generation chapter names

prompt = f"We are writing a book about {topic}. We want to generate the titles of the chapters, and nothing more. The book has the following {n_chapters} chapters:\nChapter 1:"

output = gpt3.generate(model="text-davinci-003", prompt=prompt, temperature=1.4, max_tokens=128)

titles = output.split("\n")
titles = [titles[0].strip()] + [re.match("Chapter (.*)", title).group(1) for title in titles[1:] if re.match("Chapter (.*)", title) is not None ]
book.chapters = [Chapter(title) for title in titles]
for chapter in book.chapters:
  print(chapter.title)
  
# generate section titles

for i, chapter in enumerate(book.chapters):
  prompt = f"We are writing a book about {topic}. The book has the following chapter titles:\n" + "\n".join([f"Chapter {i+1}. {chapter.title}" for i, chapter in enumerate(book.chapters)]) + f"\nWe want to generate the sections of Chapter {i+1}. {chapter.title}, and nothing more. The chapter has the following sections:\nSection {i+1}.1:" 
  output = gpt3.generate(model="text-davinci-003", prompt=prompt, max_tokens=128, temperature=1.2, stop=f"Section {i+1}.1")
  
  titles = output.strip().split("\n")
  titles = [re.match(f"Section (.*)", title).group(1) for title in titles if re.match(f"Section (.*)", title) is not None ]
  chapter.sections = [Section(title) for title in titles]
  print(f"Chapter {i+1}. {chapter.title}")
  for j, section in enumerate(chapter.sections):
    print(f"Section {i+1}.{j+1}. {section.title}")
  print()
  
# generate section text

for i, chapter in enumerate(book.chapters):
  print(f"Generating text for Chapter {i+1}")
  for j, section in enumerate(chapter.sections):
    print(f"Generating text for Section {i+1}.{j+1}")
    prompt = f"We are writing a book about {topic}. The book has the following chapter titles:\n" + "\n".join([f"Chapter {i+1}: {chapter.title}" for i, chapter in enumerate(book.chapters)]) + f"\nWe want to generate a section for Chapter {i+1}: {chapter.title}, and nothing more. The chapter has the following sections:\n" + "\n".join([f"Section {i+1}.{j+1}: {section.title}" for i, chapter in enumerate(chapter.sections)]) + f"\nWe want to generate the text of Section {i+1}.{j+1}, and nothing more. Generate several lengthy paragraphs for the aforementioned section of the book. We want the sections to be verbose, and highly descriptive. Do not number the paragraphs, we just want the text itself:\n"
    
    output = gpt3.generate(model="text-davinci-003", prompt=prompt, max_tokens=512, temperature=1.2)
    
    section.text = output.strip()
    
book.save_to_html()
