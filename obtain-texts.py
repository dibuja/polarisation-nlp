'''
This script takes as input a file the metadata obtained with harvesting.py and obtains the texts present in the Diario de Sesiones
of the Congreso de los Diputados in Spain. The script: (1) downloads the correspoding pdf, (2) extracts the text depending on
the type of document, (3) cleans the text, (4) transforms it into a dictionary and merges interventions for the same day, topic
and speaker, and finally (5) turns the interventions into a string that becomes the column feature 'text' in the dataframe.

Usage: python obtain-texts.py [input file] [output file]
'''

import pandas as pd
import pdfplumber
import requests
import re
from timeit import default_timer as timer
import sys
from pathlib import Path

# Function to download a PDF file given an url and leave it in a temporary directory.
def download_pdf(url):
    session_obj = requests.Session()
    response = session_obj.get(url, headers={"User-Agent": "Mozilla/5.0"})
    file = response.content

    # Putting the file in a temporary directory.
    filename = Path('./tmp/temp.pdf')
    filename.write_bytes(file)

def pdf2text(legislature):
    with pdfplumber.open('./tmp/temp.pdf') as pdf:
        text = "" # Temporary string where all text goes.
        tp = len(pdf.pages) # Total number of pages.
        start = timer()

        if legislature > 10:
            for i in range(tp):
                page = pdf.pages[i]
                # Crop the area of the page corresponding to the text itself.
                page = page.crop((0, 0.12 * float(page.height), 0.90 * float(page.width), 0.93 * float(page.height)))

                # Extract the text from the selected area.
                new_text = page.extract_text() + '\n'
                
                text += new_text

        elif legislature > 5 & legislature < 10:
            for i in range(tp):
                page = pdf.pages[i]
                # Crop the area of the page corresponding to the text itself.
                left_half = page.crop((0, 0.08 * float(page.height), 0.5 * float(page.width), 0.93 * float(page.height)))
                right_half = page.crop((0.50 * float(page.width), 0.08 * float(page.height), 0.95 * float(page.width), 0.93 * float(page.height)))

                # Extract the text from the selected area.
                new_text = left_half.extract_text() + '\n'
                new_text += right_half.extract_text() + '\n'
                text += new_text

        else:
            print('Warning: Invalid legislature. The code does not support PDF scrapping for legislatures 1 until 5.')

    end = timer()
    print(f'Time for PDF2Text extract_text(): {end - start} seconds')
    return text

def cleantext(text):

    # Sanitize "\u2002" by changing them for " ".
    text = text.replace('\u2002', ' ')

    # Eliminate double spaces.
    text = text.replace('  ', ' ')

    # Eliminate hyphens that separate two paragraphs.
    regex = "[a-zA-ZñáéíóúüàèìòùçÑÁÉÍÓÚÜÀÈÌÒÙÇ](\-\n)"
    text = re.sub(regex, '', text)
    
    return text

def text2dict(cleaned):
    '''
    Convers the clean text obtained from the PDF into a dictionary with structure: {topic} : {{speaker} : {text}}.
    Cleans several errors such as double spaces and new lines. The dictionary omits the titles of the topics but keeps their id.
    '''

    # Split by topic excluding the titles of the topics (capitalized words starting with a hiphen, ending with the file number).
    splitted_by_topic = re.split(
        '[—–\-A-Z /\\n\n,.\d?¿:;!¡ÑÇÁÉÍÓÚÜÀÈÌÒÙ)(]{30,1000}\([NúÚmMeErRoOdDxXpPiInNtT \n\\n]{21,26}([\d]{3}/[\d]{6})[\).]{0,2}[\n\\n]{0,4}', cleaned)

    # TODO: the way the algorithm works does not account for situations in which there are several topics discussed at the same time. It could be adjusted
    # to include those cases, but then the logic would change a lot since it would not be possible to use dictionaries.
    # '[—–\-A-Z /\\n\n,.\d?¿:;!¡ÑÑÇÁÉÍÓÓÚÚÜÀÈÌÒÙ)(]{3,1000}\([NúúÚmMeErRoOdDxXpPiIntT \n\\n]{21,26}([\d]{3}/[\d]{6})\)[;\n.]{1,2}[\n\\n]{0,4}', cleaned)

    # Remove the first item, which is always the summary of the session.
    splitted_by_topic.pop(0)

    # Split for each new speaker.
    splitted_topic_speaker = [re.split(
        '([ ]{0,3}[ElLa]{2} señor[\w]{0,1} [A-ZÑÁÉÍÓÚÜÀÈÌÒÙÇ\n\-, ]{2,150}[() A-Za-zñáéíóúüàèìòùç\-\n,]{0,50}:)', line) 
        for line in splitted_by_topic]

    # Turn the splitted lists into a dictionary {topic} : {rest}
    keys = []
    values = []
    for i in range(0, len(splitted_topic_speaker), 2):
        keys.append((splitted_topic_speaker[i][0]))
        values.append(splitted_topic_speaker[i+1])

    # dic = dict(zip(keys, values))
    # Changed the way the dictionary was created due to topics being tackled twice in the same session (debate & voting).
    dic = {}

    for i in range(len(keys)):
        if keys[i] in dic.keys():
            # We extend from 1: in order to avoid the initial empty value due to the regex split.
            dic[keys[i]].extend(values[i][1:])
        else:
            dic[keys[i]] = values[i]

    # Cleaning up the texts.
    for key, value in dic.items():
        # Remove all the first elements from the values in the dictionary, which are empty.
        dic[key].pop(0)

        
        for i in range(0, len(value) - 1):
            if len(dic[key][i]) > 0:
                # Remove all the newlines from each intervention.
                dic[key][i] = value[i].replace('\n', ' ')

                # Remove the double spaces generated from the previous replacement.
                dic[key][i] = value[i].replace('  ', ' ')

                # If the beginning of the sentence is an empty string, then remove it.
                if dic[key][i][0] == ' ':
                    dic[key][i] = value[i][1:]

                # If the end of the sentence is an empty string, then remove it.
                li = len(dic[key][i]) - 1
                if dic[key][i][li] == ' ':
                    dic[key][i] = value[i][:li]

    # Merging interventions by speaker for the same topic and turning them into a dict.
    # {topic} : {{speaker} : {text}}
    for key in dic:
        speakers = []
        texts = []
        results = {}

        for i in range(len(dic[key])):
            if (i % 2) == 0:
                speakers.append(dic[key][i])
            else:
                texts.append(dic[key][i])

        for i in range(len(speakers)):
            if speakers[i] in results.keys():
                results[speakers[i]] = results[speakers[i]] + '\n' + texts[i]
            else:
                results[speakers[i]] = texts[i]

        dic[key] = results

    return dic

def obtain_texts(data):
    texts = []
    previous_url = ''

    for row in range(len(data)):
        # The speaker's surname, topic id and url of the intervention.
        surname = data.loc[row]['orador'].split(',')[0].lower()
        topic = data.loc[row]['numero_expediente'][0:10]
        url = data.loc[row]['enlace_pdf']
        legislatura = data.loc[row]['legislatura']

        if url != previous_url:
            # Perform all the necessary steps.
            download_pdf(url)
            pdf_text = pdf2text(legislatura)
            cleaned = cleantext(pdf_text)
            processed = text2dict(cleaned)
            previous_url = url

        count = 0
        text = ''

        if topic in processed.keys():
            for item in processed[topic].keys():
                if surname in item.lower():
                    text = processed[topic][item]
                    count += 1

        # Making sure there are no duplicates in the interventions.
        if count > 1: print(f'A speaker appeared two times in row {row}')

        texts.append(text)

    return texts

def main():
    # Import data. In this case legislatures X to XIV.

    assert len(sys.argv) == 3, 'Usage: python obtain-texts.py [input file] [output file]'

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    data = pd.read_csv(input_file)
    texts = obtain_texts(data)
    data['text'] = texts
    data.to_csv(output_file, index=False)

    print('Succesfully extracted texts!')

main()
