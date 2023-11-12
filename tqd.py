from tqdm import tqdm
from time import sleep


count = 56

with tqdm(total=count) as pbar:
    aa = 0
    while aa < count:
        sleep(0.1)
        pbar.update(1)
        aa += 1