import h5py
import json




with open('fake_data.json', 'r') as f:
    initial :dict = json.load(f)


f = h5py.File('fake_data.hdf5', 'w')
print(type(f))
for k,i in initial.items():
    print(i)
    f.create_dataset(k, ('aezea'))

f.close()
