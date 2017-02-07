'''
Created on Feb 7, 2017

@author: i041966
'''
import unittest

from kafka_influxdb.encoder import telegraf_json_encoder

class Test(unittest.TestCase):


    def setUp(self):
        self.encoder = telegraf_json_encoder.Encoder()

    def testEncoder(self):
        msg = b'{"fields":{"usage_guest":0,"usage_guest_nice":0,"usage_idle":71.19016249465245,"usage_iowait":0.06587615283339686,"usage_irq":0.15371102327726027,"usage_nice":0,"usage_softirq":0,"usage_steal":0,"usage_system":13.460693895512584,"usage_user":15.129556433936004},"name":"cpu","tags":{"cluster":"e2e","cpu":"cpu-total","host":"10.58.9.95"},"timestamp":1486436554}'
        encoded_message = self.encoder.encode(msg)        
        print encoded_message
        expected_msg = ['cpu,cluster=e2e,host=10.58.9.95,cpu=cpu-total usage_guest_nice=0,usage_nice=0,usage_steal=0,usage_iowait=0.0658761528334,usage_guest=0,usage_idle=71.1901624947,usage_user=15.1295564339,usage_softirq=0,usage_irq=0.153711023277,usage_system=13.4606938955 1486436554']       
        self.assertEqual(encoded_message, expected_msg)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()