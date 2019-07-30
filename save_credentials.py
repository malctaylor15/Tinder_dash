import pickle
import csv
keys = {}
# Open credentials from amazon
with open('credentials_tinder_s3_upload.csv', 'r') as hnd:
    reader = csv.reader(hnd)
    names = next(reader)
    row = next(reader)

# Access ID
keys[names[2]] = row[2]
# Secret Key
keys[names[3]] = row[3]
print(keys)
# Save credentials as pkl
with open('credentials.pkl', 'wb') as hnd:
    pickle.dump(keys, hnd)
