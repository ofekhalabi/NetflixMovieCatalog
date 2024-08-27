#!/bin/bash
sudo  systemctl daemon-reload
sudo systemctl stop Netflix_instance_UP.service
sudo systemctl start Netflix_instance_UP.service

