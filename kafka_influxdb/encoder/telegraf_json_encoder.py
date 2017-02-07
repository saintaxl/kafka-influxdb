try:
    import ujson as json
except ImportError:
    import json

import logging

try:
    # Test for mypy support (requires Python 3)
    from typing import List, Text
except:
    pass

from kafka_influxdb.encoder.escape_functions import influxdb_tag_escaper

class Encoder(object):
    """    
    Sample measurements:
     {"fields":
             {"free":3921006592,
              "inodes_free":0,
              "inodes_total":0,
              "inodes_used":0,
              "total":40948989952,
              "used":27731570688,
              "used_percent":87.61236231313926},
       "name":"disk",
       "tags":{"cluster":"e2e",
              "device":"sda2",
              "fstype":"btrfs",
              "host":"10.58.9.95",
              "path":"/mnt/hosts"},
       "timestamp":1486434722}
    
   """

    
    def __init__(self):
        self.escape_tag = influxdb_tag_escaper()

    def encode(self, msg):
        # type: (bytes) -> List[Text]
        measurements = []

        try:
            entry = self.parse_line(msg.decode())
        except ValueError as e:
            logging.debug("Error in encoder: %s", e)
            return measurements
        
        try:                    
            measurement = entry["name"]
            tags = self.format_tags(entry)
            value = self.format_value(entry)
            time = self.format_time(entry)
            measurements.append(self.compose_data(measurement, tags, value, time))
        except Exception as e:
            logging.debug("Error in input data: %s. Skipping.", e)

        return measurements

    def parse_line(self, line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    # following methods are added to support customizing measurement name, tags much more flexible
    def compose_data(self, measurement, tags, value, time):
        data = "{0!s},{1!s} {2!s} {3!s}".format(measurement, tags, value, time)
        return data

    def format_tags(self, entry):
        tag = []
        tags = entry["tags"]
        if tags == '':
            return ''
                
        for kv in tags.items():
            # to avoid add None as tag value
            if kv[0] != '' and kv[1] != '':
                tag.append("{0!s}={1!s}".format(self.escape_tag(kv[0]), self.escape_tag(kv[1])))
                
        return ','.join(tag)

    def format_time(self, entry):
        return entry["timestamp"]
 
    def format_value(self, entry):
        fields=entry["fields"]
        value_pairs=[]
        
        for kv in fields.items():
            if kv[0] != '' and kv[1] != '':
                value_pairs.append("{0!s}={1!s}".format(self.escape_tag(kv[0]), kv[1]))
        
        return ','.join(value_pairs)
