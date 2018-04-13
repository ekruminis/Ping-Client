#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii  

from random import randint


ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages
#array = []

# calculates the checksum for the packet

def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = ord(string[count+1]) * 256 + ord(string[count]) 
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + ord(string[len(string) - 1])
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)
	
	if sys.platform == 'darwin':
		answer = socket.htons(answer) & 0xffff
	else:
		answer = socket.htons(answer)

	return answer 
	
def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
	timeSent = sendOnePing(icmpSocket, destinationAddress, ID)
	# Wait for the socket to receive a reply
	received = select.select([icmpSocket],[],[],timeout)
	# Once received, record time of receipt, otherwise, handle a timeout
	timess = time.time() + timeout
	# Unpack the packet header for useful information, including the ID
	while True:
		nowtime = time.time()
		if nowtime > timess:
			break
		if received == 0:
			print("Error: Packet not received")
			return
		else:
			timeReceived = time.time()
			# Compare the time of receipt to time of sending, producing the total network delay
			delay = timeReceived - timeSent
			result = icmpSocket.recv(1024)
			header = result[20:28];
			type, code, checksum, p_id, sequence = struct.unpack('BBHHH', header)
			# Check that the ID matches between the request and reply
			if p_id == ID:
				# Return total network delay
				return delay
			else:
				print("fail")
	
def sendOnePing(icmpSocket, destinationAddress, ID):
	# Build ICMP header
	header = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, 0, ID, 1)
	# Checksum ICMP packet using given function
	checksumResult = checksum(header)
	# Insert checksum into packet
	header = struct.pack('BBHHH', ICMP_ECHO_REQUEST, 0, checksumResult, ID, 1)
	# Send packet using socket
	packet = header
	icmpSocket.sendto(packet, (destinationAddress, 80))
	# Record time of sending
	timeSent = time.time()
	return timeSent


def doOnePing(destinationAddress, timeout): 	
	# Create ICMP socket
	PROTO2 = socket.getprotobyname('icmp')
	ID = randint(1, 25000)
	sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, PROTO2)
	# Call receiveOnePing function
	timetaken = receiveOnePing(sock, destinationAddress, ID, timeout)
	# Close ICMP socket
	sock.close()
	# Return total network delay
	return timetaken

def ping(host, timeout, count):
	# create array that holds the times
	array = []
	# Look up hostname, resolving it to an IP address
	address = socket.gethostbyname(host)
	print("\nPING " + host + "(" + str(address) + ")\n")
	starttime=time.time()
	n = 1
	# Continue this process n times
	while(n <= count):
		# Call doOnePing function, approximately every second
		try:
			delay = doOnePing(address, timeout)
			# add time to array
			array.append(delay)
			# Print out the returned delay
			if delay is None:
				# packet not reached or timeout reached
				print(str(n) + ". Error: Timeout exceeded")
			else:
				print(str(n) + ". delay = " + str(delay*1000) + "ms")
			n+=1
			time.sleep(1.0 - ((time.time() - starttime) % 1.0))
		except KeyboardInterrupt:
			# if array empty
			if not any(array):
				print("\nNo packets received")
				sys.exit()
			# calculate and print the stats, eg. min, avg, max delays
			else:
				transmitted = len(array)
				received = len(array) - array.count(None)
				failed = array.count(None)
				percent = (float(failed) / float(transmitted)) * 100
				array = filter(None, array)
				minT = min(array)*1000
				avgT = sum(array) / float(len(array))*1000
				maxT = max(array)*1000
				print("\n<<<PING statistics>>>")
				print(str(transmitted) + " packets transmitted,"),
				print(str(received) + " received,"),
				print(str(percent) + "% packet loss")
				print("min: " + str(minT) + "ms, avg: " + str(avgT) + "ms, max: " + str(maxT) + "ms")
				sys.exit()
	else:
		return array
		sys.exit()
		
def main():
	# ask for user input
	try:
		print("Website to ping: "),
		hostChoice = raw_input("")
		print("Timeout in secs: "),
		timeChoice = raw_input()
		print("Times to ping: "),
		pingChoice = raw_input()
		# call ping
		array = ping(hostChoice, float(timeChoice), int(pingChoice))
		if not any(array):
			print("\nNo packets received")
			sys.exit()
		else:
			transmitted = len(array)
			received = len(array) - array.count(None)
			failed = array.count(None)
			percent = (float(failed) / float(transmitted)) * 100
			array = filter(None, array)
			minT = min(array)*1000
			avgT = sum(array) / float(len(array))*1000
			maxT = max(array)*1000
			print("\n<<<PING statistics>>>")
			print(str(transmitted) + " packets transmitted,"),
			print(str(received) + " received,"),
			print(str(percent) + "% packet loss")
			print("min: " + str(minT) + "ms, avg: " + str(avgT) + "ms, max: " + str(maxT) + "ms")
	except KeyboardInterrupt:
		print("EXIT")
		sys.exit()
		
main()

#call file with sudo/admin privileges 
