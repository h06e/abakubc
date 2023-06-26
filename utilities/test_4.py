from PIL import Image
import matplotlib.pyplot as plt
import json


# with open('utilities/img_database', 'w') as bin_file:
#     pass
# test_id_list = [f'carre_7_0_0_{i}' for i in range(7)]

# for test_id in test_id_list:
#     with open('utilities/img_database', 'ba') as bin_file:
#         with open(f'utilities/test/{test_id}/geo.png', 'br') as img_file:
#             bin_file.write(f'\n{test_id}\n'.encode('UTF-8'))
#             bin_file.writelines(img_file.readlines())

# images_dict={}
# with open('utilities/img_database', 'br') as f:
#     previous_line=None
#     i=0
#     for line in f:
#         if line == b'\x89PNG\r\n':
#             images_dict[previous_line.decode('UTF-8')[:-1]]=i
#         previous_line = line
#         i+=1

# print(images_dict)
# with open('utilities/img_database', 'br') as f:
#     line=f.readlines(images_dict['carre_7_0_0_0'])
#     file=[f.readline()]
#     while line != b'\x89PNG\r\n':
#         line=f.readline()
#         file.append(line)
#     with open('utilities/tmp_img.png', 'bw') as img_file:
#         img_file.writelines(file)
##########################

with open('tmp.png', 'br') as f:
    data = f.readlines()
print(data[0])
full={'key':[i.decode() for i in data]}
with open('tmp.json', 'w') as fp:
    json.dump(full, fp)