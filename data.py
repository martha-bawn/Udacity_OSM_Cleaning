
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import csv
import codecs

import csv_schema

import cerberus

OSMFILE = "sample.osm"
# OSMFILE = "denver-boulder_colorado.osm"

###################
#  STREET NAMES   #
###################

## Audit the street names (adapted from Udacity exercises)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


def audit_street_type(street_types, street_name):
    """ Pulls out street type (e.g. Avenue, Boulevard) from street name and adds it to dict of street_types

    Args: dict street_types found, with street names as values
          street_name str

    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    """ Returns True if element is describing a street name, and False otherwise.

    Arg: ET element
    Returns: Boolean

    """
    return elem.attrib['k'] == "addr:street"


def st_audit(osmfile):
    """ Returns dict with street types in file as keys, and street names with each type as values.

    Arg: XML filename
    Returns: Dict {street type: set(street names) }

    """

    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


expected = ["Street", "Avenue", "Boulevard", "Broadway", "Drive", "Center", "Circle", "Commons", "Court", "Highway",
            "Place", "Square", "Lane", "Loop", "Mall", "Road", "Trail", "Parkway", "Place", "Point", "Ramp", "Way",
            "Terrace", "Plaza", "Crescent"]

mapping = { "St": "Street", "st": "Street", "Strret": "Street", "STreet": "Street",
            "Ave": "Avenue", "ave": "Avenue", "Av": "Avenue",
            "Blvd": 'Boulevard',
            "Ct": "Court", "ct": "Court",
            "Cir": "Circle", "circle": "Circle",
            "Dr": "Drive", "drive": "Drive",
            "Hwy": "Highway",
            "Pkwy": "Parkway", "Pky": "Parkway",
            "Pl": "Place",
            "Rd": "Road", "rd": "Road", "Raod": "Road",
            "SH": 'State Highway',
            "SR": "State Road",
            "E": "East", "W": "West", "S": "South", "N": "North",
            "Main": "Main Street", "Mainstreet": "Main Street",
            "US": "US Highway",
            "Co": "Colorado", "CO": "Colorado",
            "lane": "Lane", "Ln": "Lane"
            }


def update_st_name(name, mapping):
    """ Cleans street name

     Args: str name for cleaning
           dict mapping for errors to corrected version
     Returns: cleaned name str

    """

    name = name.replace('.', '')
    name = name.replace(',', '')
    name = name.replace('-', ' ')

    if 'Baselin' in name:
        return 'Baseline Road'

    if name == 'East Colfax':
        return 'East Colfax Avenue'

    name = name.split(' ')
    for i, name_word in enumerate(name):

        if any(unit == name_word for unit in ['Suite', 'suite', 'ste', 'Ste', 'Suit', 'Unit', 'unit']) \
                or '#' in name_word:
            name = name[:i]

        if name_word in mapping.keys():
            name[i] = mapping[name_word]

    name = ' '.join(name)

    return name


def street_name_test():
    """ Audits street name field, prints result, applies update_st_name to all street names and prints result """
    st_types = st_audit(OSMFILE)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_st_name(name, mapping)
            print name, "=>", better_name


################
#   ZIPCODES   #
################

def zip_audit(osmfile):
    """ Counts instances of each unique zipcode value in osm file

    Arg: osm file name
    Returns: dict of each zipcode value in file, with counts as values

    """
    osm_file = open(osmfile, "r")
    zip_count = {}

    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if tag.attrib['k'] in ('addr:postcode', 'zip_left', 'zip_right'):
                    v = tag.attrib['v']
                    if v in zip_count.keys():
                        zip_count[v] += 1
                    else:
                        zip_count[v] = 1


    osm_file.close()
    return zip_count

def is_valid_zip(zip):
    """ Checks format of zipcode string, returns boolean """

    # return len(zip) == 5 and str.isdigit(zip) and int(zip) in range(80000, 80700)
    return re.match(r'^\d{5}$', zip)

def update_zip(zip):
    ''' Cleans zipcode string

    Arg: str zip
    Returns: cleaned str zip

    '''

    if '-' in zip:
        zip = zip.split('-')
        zip = zip[0]
    elif ' ' in zip:
        zip = zip.split(' ')
        zip = zip[-1]
    elif 'CO' in zip:   # for format 'CO88888'
        zip = zip[2:]

    if is_valid_zip(zip):
        return zip
    elif is_valid_zip(zip[:-1]):
        return zip[:-1]
    else:
        return 'NULL'


def zip_test():
    """ Audits and cleans zipcode values from OSMFILE, prints results """
    zip_count = zip_audit(OSMFILE)
    pprint.pprint(zip_count)

    for zip in zip_count.keys():
        better_zip = update_zip(zip)
        if zip != better_zip:
            print zip, '=>', better_zip


#######################################
#   CITIES, COUNTIES, STATE, COUNTRY  #
#######################################

def audit(osmfile, field):
    """ Counts unique values for given field in osmfile

    Args: osmfile name
          str 'k' field from file to be audited
    Returns: dict with unique values of the field, and counts as values

    """
    osm_file = open(osmfile, "r")
    count = {}

    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if tag.attrib['k'] == field:
                    v = tag.attrib['v']
                    if v in count.keys():
                        count[v] += 1
                    else:
                        count[v] = 1

    osm_file.close()
    return count

def update_state(state):
    return 'Colorado'


city_typos = {'Auroraa': 'Aurora',
              'CONIFER': 'Conifer',
              'Centenn': 'Centennial',
              'Dener': 'Denver',
              'ENGLEWOOD': 'Englewood',
              'Edgwater': 'Edgewater',
              'Hemderson': 'Henderson',
              'Littleton co': 'Littleton',
              'PARKER': 'Parker',
              'Thorton': 'Thornton',
              'Westminister': 'Westminster',
              'WestminsterO': 'Westminster',
              '+' : 'NULL',
              'CO': 'NULL',
              'CO 80129' : 'NULL'}

def update_city(city):
    """ Cleans city str using city_typos dict """

    city = city[0].upper() + city[1:]
    if ', CO' in city:
        city = city.split(',')[0]
    if city in city_typos.keys():
        city = city_typos[city]
    return city


def test(field):
    """ Audits and cleans all values of given field in OSMFILE and prints results """

    count = audit(OSMFILE, field)
    pprint.pprint(count)

    if field == 'addr:city':
        for city in count.keys():
            better_city = update_city(city)
            if city != better_city:
                print city, '=>', better_city

####################
#   WRITE TO CSV   #
####################
# adapted from Udacity exercise

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = csv_schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'way':
        for field in way_attr_fields:
            way_attribs[field] = element.attrib[field]

        pos_counter = 0
        for node in element.iter('nd'):
            node_dict = {}

            node_dict['id'] = element.attrib['id']
            node_dict['node_id'] = node.attrib['ref']
            node_dict['position'] = pos_counter

            pos_counter += 1
            way_nodes.append(node_dict)

    elif element.tag == 'node':
        for field in node_attr_fields:
            node_attribs[field] = element.attrib[field]

    for tag in element.iter('tag'):
        if not problem_chars.search(tag.attrib['k']):
            tag_dict = {}
            tag_dict['id'] = element.attrib['id']

            #change fields that I cleaned
            if tag.attrib['k'] == 'addr:street':
                tag_dict['value'] = update_st_name(tag.attrib['v'], mapping)
            elif tag.attrib['k'] == 'addr:state':
                tag_dict['value'] = update_state(tag.attrib['v'])
            elif tag.attrib['k'] == 'addr:postcode':
                tag_dict['value'] = update_zip(tag.attrib['v'])
            elif tag.attrib['k'] == 'addr:city':
                tag_dict['value'] = update_city(tag.attrib['v'])
            else:
                tag_dict['value'] = tag.attrib['v']

            if ':' not in tag.attrib['k']:
                tag_dict['key'] = tag.attrib['k']
                tag_dict['type'] = default_tag_type
            else:
                k = tag.attrib['k'].split(':')
                tag_dict['type'] = k[0]
                tag_dict['key'] = ':'.join(k[1:])

            tags.append(tag_dict)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
                                                    k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in
                                                    row.iteritems()
                                                    })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])




if __name__ == '__main__':
    # street_name_test()
    # zip_test()
    # test('addr:city')
    # test('addr:county')     # all same format, no need for cleaning
    # test('addr:state')
    # test('addr:country')      # all same format, no need for cleaning

    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSMFILE, validate=True)