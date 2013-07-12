#!/usr/bin/env bash
sudo yum update -y && sudo yum upgrade -y
sudo yum install bash-completion -y
sudo yum install system-config-firewall-base -y
sudo yum install salt salt-minion -y
sudo yum install git -y
sudo yum install rsyslog -y
rm -rf ~/.ssh/id_rsa
rm -rf ~/.ssh/id_rsa.pub
echo "Generating SSH Key"
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N '' -q

echo "Configuring Salt Minion"
sudo lokkit -p 22:tcp -p 4506:tcp -p 4505:tcp -p 4511:tcp -p 4510:tcp

#minion needs /etc/salt/minion for grains and/or salt-master ID
sudo chown ec2-user.ec2-user /etc/salt/minion
sudo echo "master: salt-test.dev.next.opinionlab.com" >> /etc/salt/minion 
sudo chown root.root /etc/salt/minion

sudo salt-minion -d -l info
sudo systemctl enable salt-minion.service
sudo systemctl restart  iptables.service
exit 0