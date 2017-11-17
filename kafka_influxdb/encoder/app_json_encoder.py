try:
    import ujson as json
except ImportError:
    import json

import logging
import os
import time

try:
    # Test for mypy support (requires Python 3)
    from typing import List, Text
except:
    pass

from datetime import datetime
from kafka_influxdb.encoder.escape_functions import influxdb_tag_escaper

class Encoder(object):
    """

    Sample events:
      [{
        "name": "JVM-MemoryUsageGaugeSet-init",
        "tags": {
            "host": "cmt-3534332085-wb3x6",
            "name": "heap",
            "service": "cmt"
        },
        "values": {
            "value": "2147483648i"
        },
        "timestamp": 1487570855266
    },
    {
        "name": "JVM-MemoryUsageGaugeSet-max",
        "tags": {
            "host": "cmt-3534332085-wb3x6",
            "name": "heap",
            "service": "cmt"
        },
        "values": {
            "value": "2058354688i"
        },
        "timestamp": 1487570855266
    }]
     """

    preUpdateTime = 0
    namespaces = ""

    def __init__(self):
        self.escape_tag = influxdb_tag_escaper()

    def encode(self, msg):
        # type: (bytes) -> List[Text]
        global preUpdateTime, namespaces
        now = time.time()
        if now - preUpdateTime > 120:
            preUpdateTime = now
            fo = open("/etc/config/whitelist", "r")
            line = fo.readline()
            if line != namespaces:
                namespaces = line
                logging.info("Namespaces updated:" + namespaces)
            fo.close()

        measurements = []
        try:
            entries = Encoder.parse_line(msg.decode())
        except ValueError as e:
            logging.debug("Error in encoder: %s", e)
            return measurements
        for entry in entries:
            try:
                measurement = entry["name"]
                if measurement.find(".") > 0:
                    continue

                nstags = entry['tags']
                if "namespace" in nstags:
                    namespace = nstags["namespace"]
                    if namespace not in namespaces:
                        continue

                tags = self.format_tags(entry)
                value = self.format_value(entry)
                time = self.format_time(entry)
                measurements.append(self.compose_data(measurement, tags, value, time))
            except Exception as e:
                logging.debug("Error in input data: %s. Skipping.", e)

        return measurements

    @staticmethod
    def parse_line(line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    def compose_data(self, measurement, tags, value, time):
        data = "{0!s},{1!s} {2!s} {3!s}".format(measurement, tags, value, time)
        return data


    def format_tags(self, entry):
        tag_objs = entry['tags']
        tags = []

        for kv in tag_objs.items():
            # to avoid add None as tag value
            if kv[0] != '' and kv[1] != '':
                tags.append("{0!s}={1!s}".format(self.escape_tag(kv[0]), self.escape_tag(kv[1])))

        return ','.join(tags)

    def format_time(self, entry):
        t = entry['timestamp']
        return int(t / 1000)

    def format_value(self, entry):
        val_objs = entry['values']
        vals = []
        for kv in val_objs.items():
            # to avoid add None as tag value
            if kv[0] != '':
                vals.append("{0!s}={1!s}".format(self.escape_tag(kv[0]), kv[1]))

        return ','.join(vals)
