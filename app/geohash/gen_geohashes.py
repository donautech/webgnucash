import json
import re

from descartes.patch import PolygonPatch
from polygon_geohasher.polygon_geohasher import geohashes_to_polygon
from shapely.geometry import mapping


def inc_char(text, chlist='0123456789bcdefghjkmnpqrstuvwxyz'):
    # Unique and sort
    if text == 'z':
        return '0'
    chlist = ''.join(sorted(set(str(chlist))))
    chlen = len(chlist)
    if not chlen:
        return ''
    text = str(text)
    # Replace all chars but chlist
    text = re.sub('[^' + chlist + ']', '', text)
    if not len(text):
        return chlist[0]
    # Increment
    inc = ''
    over = False
    for i in range(1, len(text) + 1):
        lchar = text[-i]
        pos = chlist.find(lchar) + 1
        if pos < chlen:
            inc = chlist[pos] + inc
            over = False
            break
        else:
            inc = chlist[0] + inc
            over = True
    if over:
        inc += chlist[0]
    result = text[0:-len(inc)] + inc
    return result


def get_diff(first, second, skip_amount=-1):
    diff = [i for i in range(len(first)) if first[i] != second[i]]
    print('ord_diff:', ord(first[diff[0]]) - ord(second[diff[0]]))

    if ord(first[diff[0]]) - ord(second[diff[0]]) == skip_amount:
        diff = diff[1]
    else:
        diff = diff[0]
    print('diff', diff)
    return diff


def generate(rentals_df):
    rentals_df['range'] = ''
    rentals_df = rentals_df[rentals_df['city_start_geofence_id'] == 52]
    # rentals_df = rentals_df[rentals_df['dist'] < 0.01]
    rentals_df.reset_index(drop=True, inplace=True)
    previous_rental = rentals_df.loc[0, :]
    geohashes_result = []
    for index, rental in rentals_df.iterrows():
        current_rental = rental['min_geohash']
        geohashes_result.append(current_rental)

        if index >= rentals_df.shape[0]:
            break

        print("1.index:", index)
        print("2.rentals_df.size", rentals_df.size)
        cur_hash = rentals_df['min_geohash'][index]
        if index == rentals_df.shape[0] - 1:
            next_hash = rentals_df['max_geohash'][index]
        else:
            next_hash = rentals_df['min_geohash'][index + 1]

        print(cur_hash, next_hash)

        diff = get_diff(cur_hash, next_hash) + 1
        geohashes = [cur_hash[:diff], next_hash[:diff]]
        print('3.geohashes', geohashes)
        while geohashes[0][-1] != geohashes[1][-1]:
            print(geohashes[0], geohashes[1])
            geohashes[0] = geohashes[0][:-1] + inc_char(geohashes[0][-1])
            geohashes_result.append(geohashes[0])

        geohashes_result.append(rentals_df['min_geohash'][index])
        previous_rental = rental
    polygons = geohashes_to_polygon(geohashes_result)
    icolor = 1
    geojson = {}
    geojson['type'] = 'FeatureCollection'

    features = []
    index = 0
    for polygon in polygons:
        R = (float(icolor) - 1.0) / len(polygons)
        G = 0
        B = 0
        coords = mapping(polygon)['coordinates'][0]

        #     coords = ((m(coords[0][1],coords[0][0])),(m(coords[1][1],coords[1][0])),
        #               (m(coords[2][1],coords[2][0])),(m(coords[3][1],coords[3][0])))
        patch = PolygonPatch(polygon, facecolor=[R, G, B], alpha=1.0, zorder=2)
        feature = {'geometry': mapping(polygon),
                   'type': 'Feature',
                   'properties': {'fill': '#ff7100',
                                  'fill-opacity': R,
                                  'description': str(rentals_df['r'][index])
                                  }}
        features.append(feature)
        # ax.add_patch(patch)
        icolor = icolor + 1
        index = index + 1

    # save json to file for furutre use
    geojson['features'] = features
    return geojson


def generate_and_save(rentals_df):
    geojson = generate(rentals_df)
    with open('geofences.json', 'w') as f:
        json.dump(geojson, f)
