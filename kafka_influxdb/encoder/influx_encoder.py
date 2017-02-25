try:
    # Test for mypy support (requires Python 3)
    from typing import Text
except ImportError:
    pass
import logging

class Encoder(object):
    """
        disk,path=/,device=overlay,fstype=overlay,cluster=a,host=192.168.1.22 inodes_free=7127010i,inodes_used=104862i,total=28730269696i,free=25373896704i,used=2087710720i,used_percent=7.602288852820213,inodes_total=7231872i 1488005722000000000
    """    
    @staticmethod
    def encode(msg):
        records = msg.split('\n')
        result = []
        for record in records:
            try:
                if record == '':
                    continue
                segments = record.split(' ')
                if len(segments) > 2:
                    time_stamp = int(segments[2])
                    while time_stamp > 9999999999:
                        time_stamp /= 1000
                    segments[2] = str(time_stamp)
                    result.append(' '.join(segments))
                else:
                    result.append(record)
            except Exception as e:
                logging.warn("Error in input data: %s. Skipping.", e)
            
        return result
