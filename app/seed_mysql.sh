#!/bin/bash
/usr/bin/mysqld_safe &
sleep 5
/usr/bin/mysql -u root -e "CREATE DATABASE geo1_development;"
/usr/bin/mysql -u root geo1_development < sql.txt
