The program has been written in python 3.6.

It uses the following libraries:

dnspython - to send udp queries, etc.
sys - to get input from commandline
time and datetime - to print the current date in the result

It can be run using the following command:

python my_dns.py DOMAIN OPTIONS

where DOMAIN is the url that you want to resolve
and OPTIONS include MX, NS and A