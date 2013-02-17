from fabric.api import *
from fabric.contrib.files import *
from fabric.contrib.console import *

env.user = 'root'

# apt-get install libevent-dev
# apt-get install python-all-dev
# easy_install greenlet
# easy_install gevent

# Heavy lifting
def build_server():
	base_host_setup()
	setup_security()
	install_git()
	install_postgres()
	install_redis()
	install_nginx()
	install_supervisor()

	restart_server()

def base_host_setup():

	# Create local sudoer user, then upgrade Ubuntu.
	prompt('Specify new username: ', 'new_username')
	prompt('Specify new password: ', 'new_password')
	prompt('Specify IP4: ', 'host')
	prompt('Specify IP6: ', 'host_ip6', '')
	prompt('Specify hostname (IE: name of server): ', 'host_name')
	prompt('Specify company (used for FQDN): ', 'company_name', default="example")


	# Host name
	runcmd('echo %s > /etc/hostname && hostname -F /etc/hostname' % env.host_name)

	# Update /etc/hosts
	append('/etc/hosts', '{host}    {host_name}.{company_name}.com    {host_name}'.format(host=env.host, host_name=env.host_name, company_name=env.company_name), use_sudo=True)
	if env.host_ip6 != '':
		append('/etc/hosts', '{host_ip6}    {host_name}.{company_name}.com    {host_name}'.format(host_ip6=env.host_ip6, host_name=env.host_name, company_name=env.company_name), use_sudo=True) 

	new_user(env.new_username, env.new_password)
	upgrade_host()

	runcmd('apt-get -y install python-setuptools')
	runcmd('easy_install pip')
	runcmd('pip install virtualenv')


# Installs

def install_supervisor():
	runcmd('sudo apt-get -y install supervisor')

def install_redis():
	runcmd('add-apt-repository ppa:rwky/redis')
	runcmd('apt-get update & apt-get -y install redis-server')
	# runcmd('apt-get install -y build-essential')
	# with cd('/opt/'):
	# 	runcmd('mkdir redis')
	# 	runcmd('wget http://redis.googlecode.com/files/redis-{ver}.tar.gz'.format(ver=ver))
	# 	runcmd('tar -zxvf /opt/redis-{ver}.tar.gz'.format(ver=ver))
	# with cd('/opt/redis-*'):
	# 	runcmd('make')
	# runcmd('cp /opt/redis-*/redis.conf /opt/redis/redis.conf.default')
	# runcmd('cp /opt/redis-*/src/redis-benchmark /opt/redis/')
	# runcmd('cp /opt/redis-*/src/redis-cli /opt/redis/')
	# runcmd('cp /opt/redis-*/src/redis-server /opt/redis/')
	# runcmd('cp /opt/redis-*/src/redis-check-aof /opt/redis/')
	# runcmd('cp /opt/redis-*/src/redis-check-dump /opt/redis/')

	# runcmd('cp /opt/redis/redis.conf.default /opt/redis/redis.conf')

	# with cd('/opt/'):
	# 	runcmd('wget -O init-deb.sh http://library.linode.com/assets/629-redis-init-deb.sh')
	# 	with settings(warn_only=True):
	# 		runcmd('adduser --system --no-create-home --disabled-login --disabled-password --group redis')
	# 	runcmd('mv /opt/init-deb.sh /etc/init.d/redis')
	# 	runcmd('chmod +x /etc/init.d/redis')
	# 	runcmd('chown -R redis:redis /opt/redis')
	# 	runcmd('touch /var/log/redis.log')
	# 	runcmd('chown redis:redis /var/log/redis.log')
	# 	runcmd('update-rc.d -f redis defaults')

	# sed('/opt/redis/redis.conf', 'daemonize no', 'daemonize yes', use_sudo=True)
	# sed('/opt/redis/redis.conf', 'timeout 0', 'timeout 300', use_sudo=True)
	# sed('/opt/redis/redis.conf', 'loglevel verbose', 'loglevel notice', use_sudo=True)
	# sed('/opt/redis/redis.conf', 'dir ./', 'dir /opt/redis/', use_sudo=True)
	# sed('/opt/redis/redis.conf', 'appendonly no', 'appendonly yes', use_sudo=True)

	# with settings(warn_only=True):
	# 	runcmd('/etc/init.d/redis stop')
	# runcmd('/etc/init.d/redis start')
	

def install_fail2ban():
	runcmd('apt-get -y install fail2ban')

def install_git():
	runcmd('apt-get -y install git-core')

def install_postgres():
	runcmd('apt-get install -y libpq-dev python-dev') # Necessary for psycopg2 to work
	runcmd('apt-get install -y postgresql postgresql-contrib')
	sudo('psql template1 < /usr/share/postgresql/*/contrib/adminpack.sql', user='postgres')
	
	sed('/etc/postgresql/*/main/pg_hba.conf', 
		'local   all         all                               ident',
		'local   all         all                               md5',
		use_sudo=True)

	runcmd('/etc/init.d/postgresql-* restart')


def install_nginx():
	# TODO: Clean up old nginx if installed
	# TODO: Add optional 3rd party paramaters
	# runcmd('apt-get install -y libpcre3-dev build-essential libssl-dev')
	runcmd('apt-get install -y python-software-properties')
	runcmd('add-apt-repository ppa:nginx/stable && apt-get update')
	runcmd('apt-get install -y nginx')	



	# with cd('/opt/'):
	# 	runcmd('wget http://nginx.org/download/nginx-1.2.4.tar.gz')
	# 	runcmd('tar -zxvf nginx*')
	
	# with cd('/opt/nginx*/'):
	# 	runcmd('./configure --prefix=/opt/nginx --user=nginx --group=nginx --with-http_ssl_module')
	# 	runcmd('make && make install')

	# runcmd('adduser --system --no-create-home --disabled-login --disabled-password --group nginx')
	
	# runcmd('wget -O init-deb.sh http://library.linode.com/assets/660-init-deb.sh')
	# runcmd('mv init-deb.sh /etc/init.d/nginx')
	# runcmd('chmod +x /etc/init.d/nginx')
	# runcmd('/usr/sbin/update-rc.d -f nginx defaults')

	# if not exists('/opt/nginx/conf/sites-available/'):
	# 	runcmd('mkdir /opt/nginx/conf/sites-available/')

	# if not exists('/opt/nginx/conf/sites-enabled/'):
	# 	runcmd('mkdir /opt/nginx/conf/sites-enabled/')

	# runcmd('rm /opt/nginx/conf/nginx.conf')
	# upload_template('.//nginx.conf.template', '/opt/nginx/conf/nginx.conf', use_sudo=True)


# Tools
def setup_security():
	configure_firewall()
	install_fail2ban()

def configure_firewall():
	upload_template('.//iptables.firewall.rules.template', '/etc/iptables.firewall.rules', use_sudo=True)
	runcmd('iptables-restore < /etc/iptables.firewall.rules')
	upload_template('.//firewall.template', '/etc/network/if-pre-up.d/firewall', use_sudo=True)
	runcmd('chmod +x /etc/network/if-pre-up.d/firewall')

def upgrade_host():
	runcmd('apt-get -y update && apt-get -y upgrade --show-upgraded')

def create_db_user(db_user):
	"""
	Postgres
	"""
	with settings(warn_only=True):
		sudo('createuser -d -P {db_user}'.format(db_user=db_user), user='postgres')

def create_db(db_name, db_user):
	"""
	Postgres
	"""
	create_db_user(db_user)
	with settings(warn_only=True):
		sudo('createdb -O {db_user} {db_name}'.format(db_name=db_name, db_user=db_user), user='postgres')

def new_user(admin_username, admin_password):
	env.user='root'

	# Create the admin group and add it to the sudoers file
	admin_group='admin'
	with settings(warn_only=True):
		runcmd('addgroup {group}'.format(group=admin_group))
	runcmd('echo "%{group} ALL=(ALL) ALL" >> /etc/sudoers'.format(group=admin_group))
	

	# Create the new admin user (default group=username); add to admin group
	runcmd('adduser {username} --disabled-password --gecos ""'.format(username=admin_username))
	runcmd('adduser {username} {group}'.format(
		username=admin_username,
		group=admin_group))
	

	# Set the password for the new admin user
	runcmd('echo "{username}:{password}" | chpasswd'.format(
		username=admin_username,
		password=admin_password))


def restart_server():
	runcmd('shutdown -r now')

def restart_nginx():
	runcmd('/etc/init.d/nginx restart')

def setup_website(domain_name, project_name):

	# Create folder in /var/www
	if not exists('/var/www/'):
		runcmd('mkdir /var/www/')

	if not exists('/var/www/public_html/'):
		runcmd('mkdir /var/www/public_html/')

	# Add user for site
	with settings(warn_only=True):
		runcmd('adduser --no-create-home {project_name}'.format(project_name=project_name))
	runcmd('echo "%{project_name} ALL=(ALL) ALL" >> /etc/sudoers'.format(project_name=project_name))

	if confirm('Create virtualenv?', default=False):
		if not exists('/var/www/.virtualenvs/'):
			runcmd('mkdir /var/www/.virtualenvs/')
		with cd('/var/www/.virtualenvs/'):
			runcmd('virtualenv --distribute {domain_name}'.format(domain_name=domain_name))

		runcmd('chown {project_name}:{project_name} -R /var/www/.virtualenvs/{domain_name}/'.format(project_name=project_name, domain_name=domain_name))

	if not exists('/var/www/{domain_name}/'.format(domain_name=domain_name)):
		runcmd('mkdir /var/www/{domain_name}/'.format(domain_name=domain_name))

	# Add nginx conf
	if not exists('/etc/nginx/sites-available/{domain_name}.conf'.format(domain_name=domain_name)):
		upload_template('.//nginx.server.template', 
					    '/etc/nginx/sites-available/{domain_name}.conf'.format(domain_name=domain_name), 
					    context={'domain' : domain_name}, 
					    use_sudo=True)

	# ln conf
	if not exists('/etc/nginx/sites-enabled/{domain_name}.conf'.format(domain_name=domain_name)):
		runcmd('ln -s /etc/nginx/sites-available/{domain_name}.conf /etc/nginx/sites-enabled/{domain_name}.conf'.format(domain_name=domain_name))

	if exists('/etc/supervisor/'):
		if not exists('/etc/supervisor/conf.d/{domain_name}.conf'.format(domain_name=domain_name)):
			if confirm('Add this to supervisor?', default=False):

				# Add supervisor conf
				upload_template('.//supervisor.conf.template', 
							    '/etc/supervisor/conf.d/{domain_name}.conf'.format(domain_name=domain_name), 
							    context={'domain' : domain_name, 'project' : project_name}, 
							    use_sudo=True)

				# Add gunicorn.conf.py to project folder
				upload_template('.//gunicorn.conf.py.template',
							    '/var/www/{domain_name}/gunicorn.conf.py'.format(domain_name=domain_name),
							    use_sudo=True)

	# Add media area
	if not exists('/var/www/public_html/{domain_name}/'.format(domain_name=domain_name)):
		runcmd('mkdir /var/www/public_html/{domain_name}/'.format(domain_name=domain_name))
		runcmd('mkdir /var/www/public_html/{domain_name}/static/'.format(domain_name=domain_name))
		runcmd('mkdir /var/www/public_html/{domain_name}/media/'.format(domain_name=domain_name))
		runcmd('chown {project_name}:{project_name} -R /var/www/public_html/{domain_name}/'.format(project_name=project_name, domain_name=domain_name))

	# Modify ownership
	runcmd('chown {project_name}:{project_name} -R /var/www/{domain_name}/'.format(project_name=project_name, domain_name=domain_name))




def runcmd(arg):
	if env.user != "root":
		sudo("%s" % arg, pty=True)
	else:
		run("%s" % arg, pty=True)