import os
import datetime

now = datetime.datetime.now()
print(now)
# os.mkdir(f'{now:%Y%m%d_%H%M%S}')
os.mkdir('/home/' + now.strftime('%Y_%m_%d_%H_%M_%S'))
