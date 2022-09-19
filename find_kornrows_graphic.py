'''
this algorithm is supposed to find the orientation of crop rows
given an input image and yolov5-labelled objects

The Procedure:
1. Read image exif data to find relative (above-ground) altitude
2. Read image labels.txt and plot centroids of objects
3. For each image, find the angle of lines with the lowest offset from all plants (objects)

'''
import math
import argparse
import matplotlib.pyplot as plt
import PIL.Image as img
import numpy as np
from tqdm import tqdm

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    # For clockwise rotation, negate the angle
    #angle *= -1

    ox, oy = origin
    px, py = point

    sine = math.sin(angle)
    cosine = math.cos(angle)

    qx = ox + cosine * (px - ox) - sine * (py - oy)
    qy = oy + sine * (px - ox) + cosine * (py - oy)
    return qx, qy

def plot_centroids(lbls, dims):
    centroids = []
    with open(lbls, 'r') as lbls_txt:
        for line in lbls_txt:
            obj_class, x, y, w, h = line.split(' ')
            centroids.append([float(x) * dims[0], float(y) * dims[1]])
    return centroids

def find_orientation(centroids, img):
    '''
    At this stage, generate a dataset of measurements of offset from the plotted line
    From the histograms, a strategy can be devised to find the orientation
    '''
    dims = img.size
    orientation = None
    max_clust = 0
    result = {}
    p1 = np.array(dims) / 2
    #print(f'Position of p1 (img_centre): {list(p1)}')
    # p2 starts at top of image
    img_top = p1 * np.array([1, 0])
    #print(f'Position of img_top): {list(img_top)}')


    # PART TO WRAP ============
    for angle in range(0,180,5):  # ADD TQDM LATER
        # plot a line of orientation "angle"
        print(f'Plotting {angle}°')
        # line drawn between two points, p1 (img_centre) and p2 (offset by angle):
        p2 = rotate(p1, img_top, math.radians(angle))
        #print(f'Position of p2 (rotated {angle}° about p1)): {list(p2)}')
        distances = []
        for plant in centroids:
            # the distance from P3 perpendicular to a line drawn between P1 and P2
            p3 = np.array(plant)
            dist = np.abs(np.cross(p2-p1, p1-p3)) / np.linalg.norm(p2-p1)
            distances.append(dist)
        result[str(angle)] = distances
        fig, axs = plt.subplots(nrows=1, ncols=2,figsize=(14,6))
        

        # plot orientation angle
        axs[0].set_title('Angle')
        axs[0].imshow(img)
        #print(f'Plotting p1 ({list(p1)}) to p2 ({list(p2)})')
        axs[0].plot([p1[0],p2[0]],[p1[1],p2[1]], color="yellow")
        for plant in centroids:
            axs[0].plot(plant[0], plant[1], marker='o', color="blue")
        # plot distances
        axs[1].set_title('Distances')
        num_bins = 40
        n, bins, patches = axs[1].hist(distances, bins=num_bins)
        empties = np.count_nonzero(n==0)
        nonzero_mean = np.mean(n[np.nonzero(n)])
        discreteness = int(empties / num_bins * nonzero_mean * 100)
        if discreteness > max_clust:
            max_clust = discreteness
            orientation = angle
        fig.suptitle(f'Orientation: {angle}° | Plants: {len(centroids)}\nEmpty bins: {empties}/{num_bins} | Avg bin: {round(nonzero_mean,2)}')
        #plt.show()
        plt.savefig(f'kornrows/{angle}_{discreteness}.png', dpi=300)
    print(f'Max discreteness ({max_clust}) at {orientation}°')
    # PART TO WRAP ============



    #return orientation
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kornrow finder")
    parser.add_argument('--image_name', required=True, help="Name of the input image (with or without extension)")
    args = parser.parse_args()
    field = args.image_name
    if field.lower().endswith('.jpg'):
        field = field[:-4]
    image = field + '.JPG'
    lables = field + '.txt'
    rgb = img.open(image)
    #img_x, img_y = rgb.size
    plants = plot_centroids(lables, rgb.size)
    distances = find_orientation(plants, rgb)
    # export hists for orientations


    '''
    plt.imshow(rgb)
    for plant in plants:
        plt.plot(plant[0], plant[1], marker='o', color="blue")
    plt.show()
    '''




'''
labels.txt in the form:
0 0.063657 0.131173 0.062500 0.052469
0 0.635995 0.628086 0.075231 0.058642
0 0.968750 0.055041 0.062500 0.060700
which is: 
class x y width height

'''