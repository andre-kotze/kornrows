import os

wrong = '15'
right = '0'

checkdir = 'data/'
output = 'fixed/'

for txt in os.listdir(checkdir):
    if ".txt" in txt:
        with open(os.path.join(checkdir, txt)) as textfile:
            content = textfile.readlines()
            if content[0].startswith(wrong):
                print("fixing", txt)
                newcontent = [right + x[2:] for x in content]
                with open(os.path.join(output, txt), 'w') as newfile:
                    newfile.writelines(newcontent)
            else:
                print('skipping', txt)
            
