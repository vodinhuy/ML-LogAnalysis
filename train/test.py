import pickle
from utils.log_entry import *
from colorama import init
from colorama import Fore, Back, Style
import time
init()

labels = ['Anomalous', 'Normal']
# inp = '127.0.0.1 - jg [27/Apr/2012:11:27:36 +0700] "GET /regexcookbook.html HTTP/1.1" 200 2326'
log_path = 'D:/huyvo/CS429/LOG/access.log'
loaded_model = pickle.load(open('./testmodel.pkl', 'rb'))
# pred = loaded_model.predict([
#     [30,0,1,3,0],
#     [17,16,7,34,1]
# ])
# print(pred)
# for x in pred:
#     print(labels[x])

with open(log_path, 'r') as f:
    for _ in range(1000):
        row = f.readline()
        inp = get_input_test(row)
        # print(row)
        if inp:
            ans = loaded_model.predict([inp])
            if int(ans[0]) == 0: # Anomalous
                print(Fore.RED + row + Fore.RESET)
            else:
                print(row)

# print('BEGIN')
# while True:
#     s = input('INPUT:')
#     if s.strip().lower() == 'exit':
#         break
#     inp = get_input_test(s)
#     if inp:
#         ans = loaded_model.predict([inp])
#         if int(ans[0]) == 0: # Anomalous
#             print(Fore.RED + s + Fore.RESET)
#         else:
#             print(row)