# This file re-organizes election data from the precinct level to the block level, using a conversion file that assigns census blocks to 
# precincts. For each precinct, votes are allocated to blocks in the precinct based on the share of the precinct's registered voters 
# that reside in each block. Example: Precinct X has 1000 votes, and includes blocks X1, X2, X3, and X4. X1 has 43% of the block's
# registered voters, X2 has 11%, X3 has 18%, and X4 has 28%. In this case, block X1 would be allocated 430 votes, block X2 would be 
# allocated 110 votes, X3 would be allocated 180 votes, and X4 would be allocated 280 votes. In cases where the values calculated are non-
# integers, they are rounded down, and the Hamilton method is used to allocate the remaining votes.

# For census blocks spanning multiple precincts, the conversion file provides registered voter counts for each block-precinct segment. The 
# block's total votes are the sum of votes from all its precinct segments.

import csv
from collections import defaultdict

def hamilton(values: dict, remainders: dict): # implements Hamilton method
    total_remainder = round(sum(remainders.values()))
    largest_remainders = [block for block, _ in sorted(remainders.items(), key=lambda item: item[1], reverse=True)[:total_remainder]]
    for b in largest_remainders:
        values[b] += 1

election_file = 'Precinct Results.csv' # election results by precinct
conversion_file = 'Conversion.csv' # block-precinct conversion file
output_file = 'Block Results.csv' # election results by block

# The precinct_results file is a dictionary that matches each precinct's key (SRPREC_KEY) to a list of two integers.
# The integers are the number of Democratic votes and the number of Republican votes, respectively.
precinct_results = defaultdict(lambda: [0, 0])
block_results = defaultdict(lambda: [0, 0])

block_by_precinct_d = defaultdict(lambda: defaultdict(lambda: 0)) # D votes by precinct-block segment
block_by_precinct_r = defaultdict(lambda: defaultdict(lambda: 0)) # R votes by precinct-block segment
block_remainders_d = defaultdict(lambda: defaultdict(lambda: 0.0)) # D remainders by precinct-block segment (used for Hamilton method)
block_remainders_r = defaultdict(lambda: defaultdict(lambda: 0.0)) # R remainders by precinct-block segment (used for Hamilton method)

with open(election_file, 'r') as file:
    r0 = csv.reader(file)
    h0 = next(r0)

    for row in r0:
        cur_row = dict(zip(h0, row))
        precinct_id = cur_row['SRPREC_KEY']
        d_votes = int(cur_row['GOVDEM01'])
        r_votes = int(cur_row['GOVREP01'])
        precinct_results[precinct_id] = [d_votes, r_votes]

with open(conversion_file, 'r') as file:
    r1 = csv.reader(file)
    h1 = next(r1)

    for row in r1:
        cur_row = dict(zip(h1, row))
        block = cur_row['BLOCK_KEY']
        prec = cur_row['SRPREC_KEY']

        if prec != '' and block != '':
            blockreg = float(cur_row['BLKREG'])
            totreg = float(cur_row['SRTOTREG'])
            block_dem = precinct_results[prec][0] * blockreg / totreg
            block_rep = precinct_results[prec][1] * blockreg / totreg

            block_dem_i = int(block_dem)
            block_rep_i = int(block_rep)

            block_by_precinct_d[prec][block] = block_dem_i
            block_by_precinct_r[prec][block] = block_rep_i
            block_remainders_d[prec][block] = block_dem - block_dem_i
            block_remainders_r[prec][block] = block_rep - block_rep_i

for b in block_by_precinct_d:
    hamilton(block_by_precinct_d[b], block_remainders_d[b])
for b in block_by_precinct_r:
    hamilton(block_by_precinct_r[b], block_remainders_r[b])

for p in block_by_precinct_d:
    for b in block_by_precinct_d[p]:
        block_results[b][0] += block_by_precinct_d[p][b]
for p in block_by_precinct_r:
    for b in block_by_precinct_r[p]:
        block_results[b][1] += block_by_precinct_r[p][b]

# Sort block_results by key
block_results = dict(sorted(block_results.items(), key=lambda item: item[0]))

# Write block_results to CSV file
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['GEOID20', 'Tot', 'D', 'R'])
    for b in block_results.keys():
        block_group = b[:12] # first 12 characters of block ID
        if block_group[11] != '0': # block groups ending in 0 are water-only
            d_votes = int(block_results[b][0])
            r_votes = int(block_results[b][1])
            tot_votes = d_votes + r_votes
            row = [b, tot_votes, d_votes, r_votes]
            writer.writerow(row)

# Evaluate statewide total votes in output file.
statewide_votes_output = [0, 0, 0]
with open(output_file, 'r') as file:
    r2 = csv.reader(file)
    h2 = next(r2)
    for row in r2:
        cur_row = dict(zip(h2, row))
        d_votes = int(cur_row['D'])
        r_votes = int(cur_row['R'])
        tot_votes = int(cur_row['Tot'])
        statewide_votes_output[0] += d_votes
        statewide_votes_output[1] += r_votes
        statewide_votes_output[2] += tot_votes

print(f'File {output_file} written successfully')
print(f'Total votes: {statewide_votes_output[2]} ({statewide_votes_output[0]} D, {statewide_votes_output[1]} R)')