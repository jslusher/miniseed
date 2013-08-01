#!/usr/bin/env bash
sudo yum update -y && sudo yum upgrade -y
sudo yum install bash-completion -y
sudo yum install system-config-firewall-base -y
sudo yum install salt salt-master -y
sudo yum install git -y
sudo yum install python-pip -y
sudo pip install apache-libcloud
sudo pip install --upgrade boto 
sudo pip install --upgrade salt-cloud

echo "Installing developer tools"
sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel
sudo yum -y install supervisor

#This command references the python file that registers the new master's internal IP with route53
echo "executing register script"
/home/ec2-user/r53_register_command.sh
rm -f /home/ec2-user/r53_register_command.sh
echo "removed register command script"

echo "Placing salt-cloud files"
sudo mv /home/ec2-user/cloud /etc/salt/cloud
sudo mv /home/ec2-user/cloud.profiles /etc/salt/cloud.profiles
sudo mv /home/ec2-user/dev_map /etc/salt/.
sudo mv /home/ec2-user/salt-cloud-dev.pem /etc/salt/salt-cloud-dev.pem
sudo chown ec2-user.ec2-user /etc/salt/salt-cloud-dev.pem
sudo chmod 600 /etc/salt/salt-cloud-dev.pem

echo "Placing private key for github access"
rm -rf ~/.ssh/id_rsa
rm -rf ~/.ssh/id_rsa.pub
sudo mv /home/ec2-user/ec2_git.rsa /home/ec2-user/.ssh/id_rsa
sudo chown ec2-user.ec2-user /home/ec2-user/.ssh/id_rsa
sudo chmod 600 /home/ec2-user/.ssh/id_rsa
echo "git key in place"

echo "Setting up firewall"
sudo lokkit -p 22:tcp -p 4506:tcp -p 4505:tcp -p 8000:tcp
sudo systemctl restart  iptables.service

echo "Setting up salt"
sudo cat /home/ec2-user/salt_master_add.txt >> /etc/salt/master
sudo salt-master -d -l info
sudo systemctl enable salt-master.service

echo "Pulling salt-states from github"
#first we must automatically add github's fingerprint to the known_hosts file to avoid being prompted interactively
touch /home/ec2-user/.ssh/known_hosts
ssh-keyscan -t rsa,dsa github.com 2>&1 | sort -u - ~/.ssh/known_hosts > ~/.ssh/tmp_hosts
cat ~/.ssh/tmp_hosts >> ~/.ssh/known_hosts
sudo chown ec2-user.ec2-user /srv
cd /srv && git clone git@github.com:opinionlab/salt.git

echo "Running salt-cloud on default map_file."
sudo salt-cloud -y -m /etc/salt/dev_map

echo "executing salt highstate"
sudo salt '*' state.highstate > /home/ec2-user/highstate.out

exit 0 # manually flag that we're done executing this script
