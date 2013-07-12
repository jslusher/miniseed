from argparse import Namespace

i386 = Namespace(ami="ami-6f640c06", 
        user="ec2-user", 
        group="www-data", 
        driver="aws", )
x86_64 = Namespace(ami="ami-b71078de",
        user="ec2-user",
        group="www-data",
        driver="aws", )
