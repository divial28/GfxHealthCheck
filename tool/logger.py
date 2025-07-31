import pprint

def log(title, content=None):
    print("="*60)
    print(title)
    if content:
        pprint.pprint(content)
    print("="*60)
