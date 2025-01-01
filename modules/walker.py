import os

def run(**args):
    files_list = list()
    
    for root, _, fname in os.walk('/'):
        files_list.append(str(root) + "/" + fname)
    