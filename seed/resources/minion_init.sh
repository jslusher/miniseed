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
sudo service iptables restart
sudo iptables -F
#sudo salt-minion -d -l info
exit 0