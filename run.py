from collections.abc import Callable, Iterable, Mapping
from typing import Any


        
from multiprocessing import Process




class HTTPServerFastData(Process):
    def __init__(self):
        super().__init__()
    
    def run(self) -> None:
        from receiver import app
        app.run()
        
    
def _main():
    HTTPServerFastData().start()
    

if __name__ == "__main__":
    _main()