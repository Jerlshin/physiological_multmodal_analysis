import argparse
from . import io

def main():
    p=argparse.ArgumentParser(description="BBBD 1.1 non-predictive audit")
    p.add_argument("command",choices=["inventory","download","verify","audit","summarize","storage","validate"])
    p.add_argument("--experiments",default="4,5,2,3,1")
    a=p.parse_args()
    if a.command=="inventory": io.inventory()
    elif a.command=="download": io.download(tuple(map(int,a.experiments.split(","))))
    elif a.command=="verify":
        for f in io.release()['files']:
            sha,md5=io.verify_file(io.DATA/'canonical_source'/f['key'],f)
            print(f['key'],sha,md5)
    elif a.command=="storage": print(io.storage_snapshot("manual"))
    elif a.command=="validate":
        from .validate import run
        run()
    elif a.command=="audit":
        from .audit import run
        run(tuple(map(int,a.experiments.split(","))))
    else:
        from .summary import run
        run()

if __name__=="__main__": main()
