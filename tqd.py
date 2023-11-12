from tqdm import tqdm
from time import sleep


pbar = tqdm(total=56)
pbar.update(36)
pbar.refresh()
sleep(2)
pbar.update(37 - pbar.n)
sleep(2)