import os
import socket
import boto
from boto.route53.connection import Route53Connection
import re
import sys


master_ip = socket.gethostbyname(socket.gethostname())


if __name__ == '__main__':
    domain = sys.argv[1]
    R53_KEY = sys.argv[2]
    R53_SECRET = sys.argv[3]
    r53 = Route53Connection(R53_KEY, R53_SECRET)

    all_zones = r53.get_all_hosted_zones()
    dev_next = [ i for i in all_zones.HostedZones if i.Name == '%s' % domain]
    dn_id = dev_next[0].Id.replace('/hostedzone/','')
    all_rsets = r53.get_all_rrsets(dn_id)
    

    xml_add = """<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2012-02-29/">
   <ChangeBatch>
       <Comment>API call from newly spawned salt-master to register new internal
           IP to domain for minions</Comment>
      <Changes>
         <Change>
            <Action>CREATE</Action>
            <ResourceRecordSet>
               <Name>vpc-salt-master.%s</Name>
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
""" % (domain, master_ip)
    salt_master = [s for s in all_rsets if s.name == 'vpc-salt-master.%s' % domain]
    try:
        salt_master = str(salt_master[0])
        old_ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', salt_master)
    
        xml_del = """<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2012-02-29/">
   <ChangeBatch>
       <Comment>API call from newly spawned salt-master to delete  old internal
           IP to domain to make way for the register call</Comment>
      <Changes>
         <Change>
            <Action>DELETE</Action>
            <ResourceRecordSet>
               <Name>vpc-salt-master.%s</Name>
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
""" % (domain, old_ip[0])
        response_del = r53.change_rrsets(dn_id, xml_del)
        print response_del
    except IndexError as e:
        print "No Existing DNS Record Found: ", e
        pass
    response_add = r53.change_rrsets(dn_id, xml_add)
    print response_add
