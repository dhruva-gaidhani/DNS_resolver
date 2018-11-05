import sys
import dns.name
import dns.query
import dns.resolver
import dns.message
import time
import datetime

#Get the user input domain and query type: A, NS or MX
domain = sys.argv[1]
qtype = sys.argv[2]

tm = 0 #Variable to hold time

#List of root servers
ROOT_SERVERS = ("198.41.0.4","192.228.79.201","192.33.4.12",
            "199.7.91.13","192.203.230.10","192.5.5.241",
            "192.112.36.4","198.97.190.53","192.36.148.17",
            "192.58.128.30","193.0.14.129","199.7.83.42",
            "202.12.27.33")

#Find a working root servers
for rs in ROOT_SERVERS:
    try:
        nameserver = rs
        query = dns.message.make_query('www.google.com', dns.rdatatype.TXT,3)
        response = dns.query.udp(query, nameserver)

    except dns.exception.Timeout:
        print('Failed communication with ',rs)
        continue


print('\nActive root detected: ',nameserver,'\n')

def dns_resolve(domain, qtype, nameserver):
    init_ns = nameserver
    global tm
    while(True):
        if qtype == 'NS': #To get NS Records
            query = dns.message.make_query(domain, dns.rdatatype.NS)
        elif qtype == 'MX':#To get MX Records
            query = dns.message.make_query(domain, dns.rdatatype.MX)
        elif qtype == 'A':#To get A Records
            query = dns.message.make_query(domain, dns.rdatatype.A)
        else:
            print('Invalid query.')
            exit()
        response = dns.query.udp(query, nameserver) #Get a UDP query response
        tm = tm + int(response.time*1000) #Count the RTT for the query
        #print(response.to_text())

        #print(response.flags)
        #Check if the authority section comtains data about CNAME
        if len(response.authority)>0 and len(response.additional) == 0:
            for res_au in response.authority:
                li = res_au.to_text()
                lu = li.split(' ')
                if 'SOA' in lu:
                    return response
                domain = str(lu[-1])
                #print('-------------',domain)
                nameserver = init_ns

        #Extract the next response target
        if len(response.additional)>0:
            for res_ad in response.additional:
                li = res_ad.to_text()
                lu = li.split(' ')
                nameserver = str(lu[-1])
                break

        #Check if the AA part of flag is set
        if response.flags == 34048:
            for item in response.answer:
                check1 = item.to_text()
                check2 = check1.split(' ')
                domain = check2[-1]
                nameserver = init_ns

                #Check if the current answer has a CNAME record
                if 'CNAME' in check2:
                    print(check1)
                    break
                return response


print('QUESTION SECTION:')
print(domain,'\tIN  ',qtype)

print('\nANSWER SECTION: ')

#Call the dns resolver
iter1 = dns_resolve(domain,qtype,nameserver)

#Formating the way the answer is displayed
for item in iter1.answer:
    result = item.to_text()
    print(result)
    break

print('\nQuery time: ', tm)
print('WHEN: ',datetime.datetime.now())
print('\nMSG SIZE rcvd: ',response.__sizeof__())
#print(iter1.to_text())
'''
check1 = iter1.answer[-1].to_text()
check2 = check1.split(' ')
if 'CNAME' in check2:
    iter2 = dns_resolve(check2[-1],qtype,nameserver)
'''
