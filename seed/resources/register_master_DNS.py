import os
import socket
import boto
from boto.route53.connection import Route53Connection

R53_KEY = 'AKIAIDY6D3ATMJD755VQ'
R53_SECRET = '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'

master_ip = socket.gethostbyname(socket.gethostname())
r53 = Route53Connection(R53_KEY, R53_SECRET)

all_zones = r53.get_all_hosted_zones()

dev_next = [ i for i in all_zones.HostedZones if i.Name == 'dev.next.opinionlab.com.']

dn_id = dev_next[0].Id.replace('/hostedzone/','')

xml = """<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2012-02-29/">
   <ChangeBatch>
       <Comment>API call from newly spawned salt-master to register new internal
           IP to domain for minions</Comment>
      <Changes>
         <Change>
            <Action>CREATE</Action>
            <ResourceRecordSet>
               <Name>salt-master.dev.next.opinionlab.com</Name>
               <Type>A</Type>
               <TTL>300</TTL>
               <ResourceRecords>
                  <ResourceRecord>
                     <Value>%s</Value>
                  </ResourceRecord>
               </ResourceRecords>
            </ResourceRecordSet>
         </Change>
      </Changes>
   </ChangeBatch>
</ChangeResourceRecordSetsRequest>
""" % (master_ip)

response = r53.change_rrsets(dn_id, xml)

