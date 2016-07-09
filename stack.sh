#!/user/bin/env bash

#
#Global setup
#
CONTROLLER='10.10.10.5'
KEYSTONERC=/root/keystonerc_admin
MYSQL_DB_PASS="bb26631c99f747e6"

#
#All fuge setup
#
FUGE_DB_PASS=$(openssl rand -hex 12)
FUGE_USER_PWD=$(openssl rand -hex 12)


#
#Install openstack-fuge and python-fuge
#
function yum_install()
{
echo "Install fuge packages..."
yum install -y openstack-fuge* python-fuge* 
}

#
# Create fuge db
#
function create_db()
{
echo "Create fuge database now..."
	
mysql -uroot -p$MYSQL_DB_PASS <<EOF
DROP DATABASE IF EXISTS fuge;
CREATE DATABASE fuge;
GRANT ALL PRIVILEGES ON fuge.* TO 'fuge'@'localhost' IDENTIFIED BY '$FUGE_DB_PASS';
GRANT ALL PRIVILEGES ON fuge.* TO 'fuge'@'%' IDENTIFIED BY '$FUGE_DB_PASS';
FLUSH PRIVILEGES;
EOF
sleep 1

echo "The fuge database has been created already."
}

#
#Create fuge user and add role in OpenStack
#
function create_fuge_user_service_endpoint()
{
echo "Create fuge user, service, endpoint and add role in OpenStack now..."

source $KEYSTONERC
keystone user-create --name=fuge --pass=$FUGE_USER_PWD>/dev/null
keystone user-role-add --user=fuge --tenant=service --role=admin>/dev/null
keystone service-create --name=fuge --type=container --description="OpenStack Container Service">/dev/null
SERVICE_ID=$(keystone service-list 2>/dev/null | awk '/fuge / { print $2 }')
keystone endpoint-create \
--service-id=$SERVICE_ID \
--publicurl=http://$CONTROLLER:16888 \
--internalurl=http://$CONTROLLER:16888 \
--adminurl=http://$CONTROLLER:16888 \
--region=RegionOne

echo "Created done!!!"
}

#
#Setup fuge.conf and api-paste.ini
#
function setup_fuge()
{
echo "Setup fuge..."
openstack-config --set /etc/fuge/fuge.conf database connection mysql://fuge:$FUGE_DB_PASS@$CONTROLLER/fuge

AMQP_PWD=$(openstack-config --get /etc/nova/nova.conf oslo_messaging_rabbit rabbit_password)
AMQP_HOST=$(openstack-config --get /etc/nova/nova.conf oslo_messaging_rabbit rabbit_host)
AMQP_PORT=$(openstack-config --get /etc/nova/nova.conf oslo_messaging_rabbit rabbit_port)
AMQP_USERID=$(openstack-config --get /etc/nova/nova.conf oslo_messaging_rabbit rabbit_userid)

openstack-config --set /etc/fuge/fuge.conf DEFAULT rpc_backend rabbit
openstack-config --set /etc/fuge/fuge.conf oslo_messaging_rabbit rabbit_host $AMQP_HOST
openstack-config --set /etc/fuge/fuge.conf oslo_messaging_rabbit rabbit_port $AMQP_PORT
openstack-config --set /etc/fuge/fuge.conf oslo_messaging_rabbit rabbit_userid $AMQP_USERID
openstack-config --set /etc/fuge/fuge.conf oslo_messaging_rabbit rabbit_password $AMQP_PWD

openstack-config --set /etc/fuge/fuge.conf keystone_authtoken auth_uri http://$CONTROLLER:35357
openstack-config --set /etc/fuge/fuge.conf keystone_authtoken identity_uri http://$CONTROLLER:35357
openstack-config --set /etc/fuge/api_paste.ini filter:authtoken admin_user fuge
openstack-config --set /etc/fuge/api_paste.ini filter:authtoken admin_tenant_name service
openstack-config --set /etc/fuge/api_paste.ini filter:authtoken admin_password $FUGE_USER_PWD

echo "Setup done!!!"
}

yum_install
create_db
create_fuge_user_service_endpoint
setup_fuge

fuge-db-manage upgrade
systemctl enable openstack-fuge-api
systemctl start openstack-fuge-api

