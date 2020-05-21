# pywebscan.py

A simple threaded web scanner written in Python using urllib3 and ThreadPoolExecutor. It takes a host (single or list) argument, plus a path list, and returns request results matching a defined set of status codes (ie. found resources via HTTP 200). 

See the top of the script for additional tuning capabilities.

## usage

`pywebscan.py [https://example.com | 192.168.1.1 | hosts.txt] paths.txt`

## reference

Writeup and additional information available in the associated [Medium post](https://levelup.gitconnected.com/how-to-create-a-threaded-web-scanner-in-python-de954d31b042?source=friends_link&sk=888874fe3ca30b267e6699a9c9d5d458)

## license

ISC
