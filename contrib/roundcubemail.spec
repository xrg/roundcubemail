%define git_repo roundcubemail

Summary:	A PHP-based webmail server
Name:		roundcubemail
Version:	%git_get_ver
Release:	%mkrel %git_get_rel
Group:		System/Servers
License:	GPLv3
# Use the -dep tarballs. These use system copies of the PHP stuff
# rather than including them, which is better for our purposes.
# - AdamW 2007/07
URL:		http://www.roundcube.net/
Source0:	%git_bs_source %{name}-%{version}.tar.gz
Epoch:		1
Requires:	apache-mod_php
Requires:	php-gd
Requires:	php-gettext
Requires:	php-iconv
Requires:	php-mbstring
Requires:	php-mcrypt
Requires:	php-openssl
Requires:	php-pspell
Requires:	php-session
Requires:	php-pear-Auth_SASL
Requires:	php-pear-Mail_Mime
Requires:	php-pear-Net_SMTP
Requires:	php-pear-Net_LDAP2
Requires:	php-pear-MDB2
Requires:	php-pear-Net_IDNA2
# The installer suggests the use of these, but they're not
# required - AdamW 2011/01
Suggests:	php-fileinfo
Suggests:	php-intl
# Most people will probably use mysql, but you can use sqlite or
# pgsql, so not a hard require - AdamW 2008/10
Suggests:	php-pear-MDB2_Driver_mysql

BuildArch:	noarch
# rpm-build / rpm macros does not seem to require php-cli in cooker
BuildRequires:	php-cli
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
RoundCube Webmail is a browser-based multilingual IMAP client with an
application-like user interface. It provides full functionality you expect
from an e-mail client, including MIME support, address book, folder
manipulation, message searching and spell checking. RoundCube Webmail is
written in PHP and requires a MySQL or PostgreSQL database. The user
interface is fully skinnable using XHTML and CSS 2.

%prep
%git_get_source
%setup -q

%build

%install

# tell it that we're moving the configuration files
for i in installer/index.php program/include/iniset.php; do \
	sed -i \
		-e "s,INSTALL_PATH . 'config','%{_sysconfdir}/%{name}',g" \
		$i; \
done
# use systemwide log dir and temp dir
sed -i \
    -e 's,logs/,%{_logdir}/%{name}/,g' \
    -e 's,temp/,/tmp/,g' \
    config/main.inc.php.dist
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_logdir}/%{name}
cp -a config/db.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/db.inc.php
cp -a config/db.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/db.inc.php.dist
cp -a config/main.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/main.inc.php
cp -a config/main.inc.php.dist %{buildroot}%{_sysconfdir}/%{name}/main.inc.php.dist
rm -rf config
rm -rf temp
rm -rf logs
cp -a * %{buildroot}%{_datadir}/%{name}

pushd %{buildroot}%{_datadir}/%{name}
rm -f CHANGELOG INSTALL UPGRADING LICENSE README.md
popd


cat <<EOF > README.urpmi

This package conforms to the Mandriva web applications policy:
http://wiki.mandriva.com/Policies/Web_Applications

It therefore differs from a standard installation in the following
ways:

* Logs are stored to /var/log/roundcubemail
* Temporary files are placed in /tmp
* Configuration files (main.inc.php and db.inc.php) are placed in
  /etc/roundcubemail

You will need to edit /etc/roundcubemail/main.inc.php and
/etc/roundcubemail/db.inc.php appropriately for your site before you
can use Roundcube. You must at least configure an appropriate mail
server and port in main.inc.php, and change the 
$rcmail_config['des_key'] setting. In db.inc.php you must configure
an appropriate database location and user; in the most simple
configuration, you would create a new user and database both named
'roundcubemail' on a MySQL server running on the same machine, give
the roundcubemail user full read/write access to the roundcubemail
database, and set db.inc.php appropriately. Roundcubemail ships with
an installer which can help you do all this, but it is disabled by
default for security reasons. You can enable it in main.inc.php by
setting the 'enable_installer' variable to 'true'. Then browse to
http://server/roundcubemail/installer to use the installer.
EOF

mkdir -p %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/%{name}.conf <<EOF
Alias /%{name} %{_datadir}/%{name}

<Directory %{_datadir}/%{name}>
    Order allow,deny
    Allow from all
</Directory>

<Directory %{_datadir}/%{name}/SQL>
    Order deny,allow
    Deny from all
</Directory>

php_value suhosin.session.encrypt Off
EOF


%files
%defattr(-,root,root)
%doc CHANGELOG README.md README.urpmi UPGRADING
%{_datadir}/%{name}
%dir %{_sysconfdir}/%{name}
%{_logdir}/%{name}
# these store the default values, the installer refers to them
# no need to edit them so they're not tagged config - AdamW 2011/01
%{_sysconfdir}/%{name}/db.inc.php.dist
%{_sysconfdir}/%{name}/main.inc.php.dist
%config(noreplace) %{_sysconfdir}/%{name}/db.inc.php
%config(noreplace) %{_sysconfdir}/%{name}/main.inc.php
%config(noreplace) %{_webappconfdir}/%{name}.conf

%changelog -f %{_sourcedir}/%{name}-changelog.gitrpm.txt