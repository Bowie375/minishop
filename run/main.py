import os
import sys

import subprocess
import multiprocessing

from minishop.backend.server import Server

def start_frontend():
    with open("outputs/frontend.log", "w") as f:
        subprocess.run(['npm', 'run', '--prefix=minishop/frontend', 'dev'], 
                       stdout=f, stderr=f, shell=True)

def start_backend():
    sys.stdout = open("outputs/backend.log", "w")
    sys.stderr = sys.stdout

    db_url = 'minishop/data/e_commerce.db'
    server = Server(os.path.abspath(db_url))
    server.run()

def main():
    # start backend server
    p_backend = multiprocessing.Process(target=start_backend)
    p_backend.start()

    # start frontend server
    p_frontend = multiprocessing.Process(target=start_frontend)
    p_frontend.start()
    
    # wait for the processes to finish
    p_backend.join()
    p_frontend.join()


if __name__ == '__main__':
    main()
