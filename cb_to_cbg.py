import csv
from collections import defaultdict

input_file = 'Block Results.csv'
output_file = 'Block Group Results.csv'

cbg_dict = defaultdict(lambda: [0, 0]) # Each dictionary entry of format {<block group>: [<D votes>, <R votes>]}

with open(input_file, 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)

    for row in reader:
        cur_row = dict(zip(headers, row))
        cbg = cur_row['GEOID20'][:12]
        d = int(cur_row['D'])
        r = int(cur_row['R'])
        cbg_dict[cbg][0] += d
        cbg_dict[cbg][1] += r

cbg_dict = dict(sorted(cbg_dict.items(), key=lambda item: item[0]))

with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['GEOID20', 'Tot', 'D', 'R'])
    for bg in cbg_dict.keys():
        d = cbg_dict[bg][0]
        r = cbg_dict[bg][1]
        t = d + r
        writer.writerow([bg, t, d, r])

print(f'File {output_file} written successfully')