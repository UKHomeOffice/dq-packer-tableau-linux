#!/bin/sh
# Get the instance region and inject it in the conf
REGION=$(ec2metadata --availability-zone | head -c-2)
sed -i -e 's/.*region.*/region = '$REGION'/' /var/awslogs/etc/aws.conf

# Restart the awslogs agent
service awslogs restart