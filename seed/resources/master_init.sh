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

echo "Generating SSH Keys"
rm -rf ~/.ssh/id_rsa
rm -rf ~/.ssh/id_rsa.pub
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N '' -q

# File Roots
#sudo echo "file_roots:" >> /etc/salt/master
#sudo echo "  base:" >> /etc/salt/master
#sudo echo "    - /srv/salt/base" >> /etc/salt/master
#sudo echo "  dev:" >> /etc/salt/master
#sudo echo "    - /srv/salt/dev" >> /etc/salt/master

# Configure logging
#sudo echo "log_level: error # console-messages" >> /etc/salt/master
#sudo echo "log_level_logfile: error # log-files..." >> /etc/salt/master
#sudo echo "log_file: file:///dev/log # point logs to syslog" >> /etc/salt/master

echo "Setting up firewall"
sudo lokkit -p 22:tcp -p 4506:tcp -p 4505:tcp -p 8000:tcp
sudo systemctl restart  iptables.service

echo "Setting up salt"
sudo salt-master -d -l info
sudo systemctl enable salt-master.service

echo "adding user git"
sudo useradd -m git
sudo mkdir /home/git/.ssh
sudo chown git.git /home/git/.ssh

echo "Installing developer tools"
sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel
sudo yum -y install supervisor

echo "Initializing git repo in /srv"
sudo su - git -c "cd /srv && git init" 
sudo chown -R git.git /srv
sudo mkdir /srv/salt
sudo chown -R git.git /srv/salt

## to include later if Django-based GUI is needed 
#sudo yum -y install postgresql postgresql-devel postgresql-server

echo "Running salt-cloud on default map_file."
sudo salt-cloud -y -m /etc/salt/dev_map

exit 0 # manually flag that we're done executing this script
