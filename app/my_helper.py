import re

def OPEN_FILE(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
def SAVE_FILE(content, filepath, append=False):
    mode = 'w'
    if append:
        mode = 'a'
    with open(filepath, mode, encoding='utf-8') as outfile:
        outfile.write(content)


def FIX_TEXT( text ):
    text = re.sub('\s+', ' ', text)
    text = text.strip()

    return text