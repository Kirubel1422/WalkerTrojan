import os

def run(**args):
    files_list = list()
    print('[+] In walker.py')
    for root, _, fname in os.walk('/'):
        files_list.append(str(root) + "/" + fname)
    