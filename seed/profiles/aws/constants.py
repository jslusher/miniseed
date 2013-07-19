from argparse import Namespace

i386 = Namespace(ami="ami-6f640c06", 
        user="ec2-user", 
        group="www-data", 
        driver="aws", )
x86_64 = Namespace(ami="ami-b71078de",
        user="ec2-user",
        group="www-data",
        driver="aws", )
def get_aws_ports():
    
    ports = []
    ip_ranges = ['127.0.0.1', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
    desired_ports = [4505, 4506]
    protocol_store = {
        4505: 'master',
        4506: 'minion'}

    for subnet in ip_ranges:
        for port in desired_ports:
            ports.append({
                'from_port': port,
                'to_port': None,
                'cidr_ip': subnet,
                'protocol': protocol_store.get(port, 'protocol-tag-not-found')
            })

    return ports
