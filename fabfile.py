from fabric.api import *
from fabric.contrib.files import *

env.user = 'root'

# Heavy lifting
def build_server():
	base_host_setup()
	setup_security()
	install_git()
	install_postgres()
	install_nginx()

	restart_nginx()

def base_host_setup():

	# Create local sudoer user, then upgrade Ubuntu.
	prompt('Specify new username: ', 'new_username')
	prompt('Speciry new password: ', 'new_password')
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


# Installs
def install_fail2ban():
	runcmd('apt-get -y install fail2ban')

def install_git():
	runcmd('apt-get -y install git-core')

def install_postgres():
	runcmd('apt-get install -y postgresql postgresql-contrib')
	# runcmd('su - postgres')
	# runcmd('psql template1 < /usr/share/postgresql/*/contrib/adminpack.sql && exit')
	# runcmd('exit')
	
	# # Set new password
	# runcmd('passwd postgres')


def install_nginx():
	# TODO: Clean up old nginx if installed
	# TODO: Add optional 3rd party paramaters
	runcmd('apt-get install -y libpcre3-dev build-essential libssl-dev')
	with cd('/opt/'):
		runcmd('wget http://nginx.org/download/nginx-1.2.4.tar.gz')
		runcmd('tar -zxvf nginx*')
	
	with cd('/opt/nginx*/'):
		runcmd('./configure --prefix=/opt/nginx --user=nginx --group=nginx --with-http_ssl_module')
		runcmd('make && make install')

	runcmd('adduser --system --no-create-home --disabled-login --disabled-password --group nginx')
	
	runcmd('wget -O init-deb.sh http://library.linode.com/assets/660-init-deb.sh')
	runcmd('mv init-deb.sh /etc/init.d/nginx')
	runcmd('chmod +x /etc/init.d/nginx')
	runcmd('/usr/sbin/update-rc.d -f nginx defaults')

	if not exists('/opt/nginx/conf/sites-available/'):
		runcmd('mkdir /opt/nginx/conf/sites-available/')

	if not exists('/opt/nginx/conf/sites-enabled/'):
		runcmd('mkdir /opt/nginx/conf/sites-enabled/')

	runcmd('rm /opt/nginx/conf/nginx.conf')
	upload_template('.//nginx.conf.template', '/opt/nginx/conf/nginx.conf', use_sudo=True)


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


def create_db(db_name, root_user, root_password, new_user, new_user_password):
	pass

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


def restart_nginx():
	runcmd('/etc/init.d/nginx restart')

def setup_website(domain_name):
	# Create folder in /var/www
	if not exists('/var/www/'):
		runcmd('mkdir /var/www/')

	if not exists('/var/www/{domain_name}/'.format(domain_name=domain_name)):
		runcmd('mkdir /var/www/{domain_name}/'.format(domain_name=domain_name))
	
	# TODO handle permissions

	# Add nginx conf
	upload_template('.//nginx.server.template', 
				    '/opt/nginx/conf/sites-available/{domain_name}.conf'.format(domain_name=domain_name), 
				    context={'domain' : domain_name}, 
				    use_sudo=True)

	# ln conf
	runcmd('ln -s /opt/nginx/conf/sites-available/{domain_name}.conf /opt/nginx/conf/sites-enabled/{domain_name}.conf'.format(domain_name=domain_name))


def runcmd(arg):
	if env.user != "root":
		sudo("%s" % arg, pty=True)
	else:
		run("%s" % arg, pty=True)