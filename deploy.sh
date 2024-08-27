#!/bin/bash
sudo  systemctl daemon-reload
sudo systemctl stop Netflix_instance_UP.service
sudo systemctl start Netflix_instance_UP.service
if [ -e /home/ubuntu/app/mykey.pem ]; then
  rm /home/ubuntu/app/mykey.pem
fi

