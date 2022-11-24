import pickle
from utils.log_entry import *
from colorama import init
from colorama import Fore, Back, Style
init()

labels = ['Normal', 'Anomalous']
# inp = '127.0.0.1 - jg [27/Apr/2012:11:27:36 +0700] "GET /regexcookbook.html HTTP/1.1" 200 2326'
log_path = 'D:/huyvo/CS429/LOG/access.log'
loaded_model = pickle.load(open('./rf_models/rfmodel-02.pkl', 'rb'))

if __name__ == '__main__':
    while True:
        row = input()
        if row.strip().lower() == 'exit':
            break
        inp = extract_info(row)
        if inp:
            # print(inp)
            ans = loaded_model.predict([inp])
            if int(ans[0]) == 0:
                print(Fore.GREEN + row + Fore.RESET)
            else:
                print(Fore.RED + row + Fore.RESET)
