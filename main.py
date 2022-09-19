import os
import find_kornrows
import json
import pandas as pd
import argparse


def main(folder):
    geojson = []
    samples = os.listdir(folder)
    os.chdir(folder)
    samples = [s for s in samples if s.lower().endswith('.jpg')]
    for n, sample in enumerate(samples):
        print(f'[{n+1}/{len(samples)}] Processing {sample}')
        result = find_kornrows.analyse_field(sample)
        if result is not None:
            geojson.append(result)
        print('\n')
    with open('output.json', 'w') as output:
        json.dump(geojson, output, indent=2)
    df = pd.DataFrame(geojson)
    df.to_csv('output.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Target folder")
    parser.add_argument('--imgdir', required=True, help="Name of image directory")
    args = parser.parse_args()
    folder = args.imgdir
    main(folder)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 


'''
# read image xmp data
def get_alt(filename):
    rel_alt = None
    xmp = file_to_dict(filename)
    for i in xmp['http://www.dji.com/drone-dji/1.0/']:
        if 'RelativeAltitude' in i[0]:
            rel_alt = float(i[1])
    return rel_alt

rel_altitude = get_alt(img_file)

# read labels file here:
#   send points to oriente
#   send points to all_lines

# GROUND SAMPLING DISTANCE - GSD - mm/px
focal_length = 220
ar = 4 / 3
fov = 2 * arctan(35 / focal_length * 2)
'''
