fabric-server-deploy
====================

A buildout for a web/db server with nginx, fail2ban, firewall and postgres. Still needs some tweaking to handle more options, like MySQL and Mongo.

I use this to build out my Linode slices with Ubuntu 10.04.

Running `fab build_server` will build out the following:
* Prompt user for new username/pw for non root user, hostnames, etc
* Update Ubuntu
* Install proper firewall and Fail2Ban
* virtualenv and pip
* Git
* Postgres
* Redis
* nginx
* Supervisor

Running `fab setup_website:domain,project` will:
* Create a folder of domain and optional virtualenv
* Create user:group of project
* Add conf file to nginx
* Add program to supervisor
* Create media/static folders in /var/www/public_html/
* Set permissions

Based off of: https://github.com/btompkins/CodeBetter.Com-Fabric