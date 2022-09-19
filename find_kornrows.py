'''
this algorithm is supposed to find the orientation of crop rows
given an input image and yolov5-labelled objects

The Procedure:
1. Read image exif data to find relative (above-ground) altitude
2. Read image labels.txt and plot centroids of objects
3. For each image, find the angle of lines with the lowest offset from all plants (objects)

'''
import os
import math
import argparse
import matplotlib.pyplot as plt
import PIL.Image as img
import numpy as np
from math import atan as arctan
from libxmp.utils import file_to_dict
from shapely.geometry import Point, LineString

VISUALISE = True
HIST_BINS = 40
ROW_TOLERANCE = 2
SPACE_TOLERANCE = 15

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    # For clockwise rotation, negate the angle:
    angle *= -1

    ox, oy = origin
    px, py = point

    sine = math.sin(angle)
    cosine = math.cos(angle)

    qx = ox + cosine * (px - ox) - sine * (py - oy)
    qy = oy + sine * (px - ox) + cosine * (py - oy)
    return qx, qy

def get_centroids(lbls, dims):
    '''
    Read Yolov5-format label files and return a list of centroid coordinate pairs
    '''
    centroids = []
    with open(lbls, 'r') as lbls_txt:
        for line in lbls_txt:
            obj_class, x, y, w, h = line.split(' ')
            # account for negative/reversed y-coords:
            centroids.append([float(x) * dims[0], (1 - float(y)) * dims[1]])
    return centroids

def scrape(start, end, step, dims, centroids):
    '''
    Iterate through orientations and return the orientation 
    that matches the lines in a point cloud    
    '''
    # p1 is centre image
    p1 = np.array(dims) / 2
    # p2 starts at top of image
    img_top = np.array(dims) * np.array([0.5, 1])
    orientation = [None]
    max_clust = [0]
    hist_data = [None]
    #output = open(f'output{step}.csv', 'w')
    #output.write('angle,empty_bins,non-empty_avg,discreteness\n')
    for angle in range(start,end,step):  # ADD TQDM LATER
        # plot a line of orientation "angle"
        #print(f'Scraping {angle:03d}°:\t',end='')
        # line drawn between two points, p1 (img_centre) and p2 (offset by angle):
        p2 = rotate(p1, img_top, math.radians(angle))
        distances = []
        for plant in centroids:
            # the distance from P3 perpendicular to a line drawn between P1 and P2
            p3 = np.array(plant)
            dist = np.abs(np.cross(p2-p1, p1-p3)) / np.linalg.norm(p2-p1)
            distances.append(dist)
        
        num_bins = HIST_BINS
        n, edges = np.histogram(distances, bins=num_bins)
        empties = np.count_nonzero(n==0)
        nonzero_mean = np.mean(n[np.nonzero(n)])
        discreteness = int(empties / num_bins * nonzero_mean * 100)
        if discreteness > max_clust[0]:
            max_clust = [discreteness]
            orientation = [angle]
            hist_data = [distances]
        elif discreteness == max_clust[0]:
            max_clust.append(discreteness)
            orientation.append(angle)
            hist_data.append(distances)
        #print(f'Empty bins: {empties}/{num_bins}\tAvg bin: {round(nonzero_mean,2)}\tDiscreteness: {discreteness}')
        #output.write(f'{angle},{empties},{round(nonzero_mean,2)},{discreteness}\n')
    #output.close()
    peak_width = len(max_clust)
    if peak_width > 1:
        max_clust = np.mean(max_clust)
        orientation = np.mean(orientation)
        hist_data = np.mean(hist_data, axis=0)
    else:
        max_clust = max_clust[0]
        orientation = orientation[0]
        hist_data = hist_data[0]

    print(f'\tMax discreteness ({max_clust}) at {orientation}°')
    return orientation, hist_data

def find_orientation(centroids, img, name):
    '''
    Coarse and fine scrape the image and return the best match orientation angle
    '''
    dims = img.size

    # course scrape through 180 degrees in x degree steps
    course, hist = scrape(0, 180, 5, dims, centroids)
    course = int(course)

    # fine scrape around course result in x degree steps
    fine, hist = scrape(course-5, course+5 ,1 , dims, centroids)

    if VISUALISE:
        plot_orientation(img, fine, centroids, hist, name)
        
    return fine

def plot_orientation(img, angle, centroids, hist, name):
    # plot scrape results
    fig, axs = plt.subplots(nrows=1, ncols=2,figsize=(14,6))
    # plot orientation angle
    axs[0].set_title('Angle')
    axs[0].imshow(img, origin='lower')
    # plot orientation line
    centre = np.array(img.size) / 2 # img_centre
    img_top = centre * np.array([1, 2])
    img_bot = centre * np.array([1, 0])
    p1 = rotate(centre, img_top, math.radians(angle))
    p2 = rotate(centre, img_bot, math.radians(angle))
    axs[0].plot([p1[0],p2[0]],[p1[1],p2[1]], color="yellow")
    for plant in centroids:
        axs[0].plot(plant[0], plant[1], marker='o', color="blue")
    # plot distances
    axs[1].set_title('Distances')
    axs[1].hist(hist, bins=HIST_BINS)
    filename = f'{name}_{angle}_plot'
    i = 0
    while os.path.isfile(f'{filename}_{i}'):
        i += 1
    plt.savefig(f'{filename}_{i}.png', dpi=300)
    fig.clear(True)
    plt.subplots()
    plt.close()
    



def azimuth(point1, point2):
    '''
    Azimuth between 2 shapely points (in the interval 0 - 180°)
    '''
    angle = math.atan2(point1, point2)
    return math.degrees(angle) if angle > 0 else math.degrees(angle) + 360

def get_p2p_lines(points, orientation, threshold):
    '''
    Get all point-to-point lines, filtered by threshold deviation from a given slope
    '''
    # get all point to point lines
    all_lines = []
    line_id = 0
    for point0 in points:
        for point1 in points:
            dx = point1.x - point0.x
            dy = point1.y - point0.y
            if dx * dy != 0:
                bearing = azimuth(dx, dy)
                if abs(bearing - orientation) < threshold:# or abs(bearing - (180 + orientation)) < threshold:
                    line = LineString([point0, point1])
                    if not any(p[1].equals(line) for p in all_lines):
                        all_lines.append((line_id, line))
                        line_id += 1
    uniqlines = []
    for id, line in all_lines:
        if not any(p[1].equals(line) for p in uniqlines):
            uniqlines.append((id, line))
    print(f'\tP2P Lines in interval {orientation - threshold} - {orientation + threshold}°: {len(all_lines)}')
    return uniqlines

def find_rows(lines):
    intersections = 0
    long_lines = []
    long_lines_ids = []
    for line0 in lines:
        crosses = 0
        for line1 in lines:
            if line0[1].touches(line1[1]):
                intersections += 1
                crosses += 1
                if line0[1].length > line1[1].length and line0[0] not in long_lines_ids:
                    long_lines.append(line0)
                    long_lines_ids.append(line0[0])

        if crosses == 0:
            long_lines.append(line0)
            long_lines_ids.append(line0[0])            
    if intersections == 0:
        long_lines = lines        
    #print(f'{intersections} intersections\t{len(long_lines)} lines')
    return intersections, long_lines



def find_single_lines(lines, row_buffers):
    intersections = 0
    short_lines_ids = []
    short_lines = []
    for line0 in lines:
        crosses = 0
        for line1 in lines:
            if line0[1].crosses(line1[1]):
                intersections += 1
                crosses += 1
                if line0[1].length < line1[1].length and line0[0] not in short_lines_ids:
                    intersected_rows = [row for row in row_buffers if line0[1].intersects(row)]
                    if len(intersected_rows) <= 1:
                        short_lines.append(line0)
                        short_lines_ids.append(line0[0])

        if crosses == 0:
            short_lines.append(line0)
            short_lines_ids.append(line0[0])            
    if intersections == 0:
        short_lines = lines        
    #print(f'{intersections} intersections\t{len(short_lines)} lines')
    return intersections, short_lines

def analyse_field(field):
    if field.lower().endswith('.jpg'):
        field = field[:-4]
    image = field + '.JPG'
    lables = field + '.txt'
    if not os.path.isfile(lables):
        lables = 'labels/' + lables
        if not os.path.isfile(lables):
            print(f'No plants detected in {image}')
            return None
    rgb = img.open(image)
    rgb = rgb.transpose(img.FLIP_TOP_BOTTOM)
    img_x, img_y = rgb.size
    result = {'img_name':field}
    dims = (img_x, img_y)
    rel_alt = None
    #plt.imshow(rgb, origin='lower')
    #plt.imshow(rgb, origin='lower', extent=(0,5184,0,3888))
    plants = get_centroids(lables, dims)
    orientation = find_orientation(plants, rgb, field)
    result['plant_count'] = len(plants)
    result['row_orientation'] = orientation

    xmp = file_to_dict(image)
    for i in xmp['http://www.dji.com/drone-dji/1.0/']:
        if 'RelativeAltitude' in i[0]:
            rel_alt = float(i[1])
        elif 'GpsLatitude' in i[0]:
            result['latitude'] = float(i[1])
        elif 'GpsLongitude' in i[0]:
            result['longitude'] = float(i[1])
        else:
            pass
    if rel_alt is not None:
        gsd = (7.6 * rel_alt * 100) / (47.6 * img_x) # in cm per pixel
        area = gsd**2 * img_x * img_y / 10e4
        result['rel_alt'] = rel_alt
        result['area_m2'] = area
        plants_ha = (len(plants) / area) * 10e4
        result['plants_per_ha'] = plants_ha

    plt.imshow(rgb, origin='lower')
    points = [Point(plant) for plant in plants]
    print(f'\tFound {len(points)} plant centroids')

    all_lines = get_p2p_lines(points, orientation, ROW_TOLERANCE)
    intersections, rows = find_rows(all_lines)
    while intersections > 0:
        intersections, rows = find_rows(rows)
    uniqlines = []
    for id, line in rows:
        if not any(p[1].equals(line) for p in uniqlines):
            uniqlines.append((id, line))
    print(f'\tUnique corn rows: {len(uniqlines)}')
    result['rows_detected'] = len(uniqlines)

    buff_cornrows = [line[1].buffer(100) for line in uniqlines]
    

    #ax.plot(line.xy[0], line.xy[1])
    for poly in buff_cornrows:
        plt.plot(*poly.exterior.xy, color='yellow', alpha=0.85)
        #plt.plot(line[1].xy[0], line[1].xy[1], color='yellow') # Equivalent

    # put the both in one big-ass graph
    plt.savefig(f'{field}_rows.png', dpi=300)

    all_lines = get_p2p_lines(points, orientation, SPACE_TOLERANCE)
    intersections, short_lines = find_single_lines(all_lines, buff_cornrows)
    while intersections > 0:
        intersections, short_lines = find_single_lines(short_lines, buff_cornrows)

    # filter
    slines = []
    for id, line in short_lines:
        line_area = line.buffer(100)
        contained_plants = [plant for plant in points if line_area.contains(plant)]
        if len(contained_plants) < 3 and any(row.contains(line) for row in buff_cornrows):
            slines.append((id, line))
    print(f'\tUnique corn plant spaces: {len(slines)}')

    short_lines = slines
    distances = [line[1].length for line in short_lines]
    cov = np.std(distances) / np.mean(distances) * 100
    print(f'\n\tCV: {cov}')
    result['cv'] = cov

    for line in short_lines:
        plt.plot(line[1].xy[0], line[1].xy[1]) # Equivalent

    #print('Plants coords:')
    #for plant in points:
    #    plt.plot(plant.x, plant.y, marker='o', color="blue")
    #plt.title(field)
    plt.suptitle(f'CoV: {round(cov,2)}% | Plants: {len(plants)} | Rows: {len(uniqlines)}\nOrientation: {orientation} | Plants/ha: {int(plants_ha)}')
    plt.savefig(f'{field}_spaces.png', dpi=300)
    plt.close()

    return result

#img_file = 'runs/detect/exp12/DJI_20220211065928_0026_Z.JPG'
#img_file = 'kornrows/DJI_20220211065254_0005_Z.JPG'
#img_file = 'kornrows/DJI_20220211071229_0062_Z.JPG'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Plant spacing measurement")
    parser.add_argument('--image_name', required=True, help="Name of the input image (with or without extension)")
    args = parser.parse_args()
    img_file = args.image_name
    analyse_field(img_file)