#!/usr/bin/env python
import json,os,sys,threading
from conf import policy, hosts
from get_monitor_dic import get_monitor_host_list
import db_connector
from TriAquae.hosts.models import Group,IP
import monitor_data_handle as alert_handle
import time,pickle,subprocess
import redis_connector 

#pull out status data from Redis
monitor_dic = redis_connector.r.get('TriAquae_monitor_status')
if monitor_dic is not None:
	monitor_dic = json.loads(monitor_dic)
else:
	sys.exit("No monitor data found in Redis,please check")

"""
#pull out all the hosts in enabled_policy
def get_monitor_host_list():
	host_dic = {}
	for n,p in  enumerate(policy.enabled_policy):
		if p.groups is not None: 
			for g in p.groups:
			  for h in IP.objects.filter(group__name = g):
				if not host_dic.has_key(h): 
					host_dic[h] = [n] #add policy order into dic 
				else:
					host_dic[h].append(n)

				#host_list.extend( IP.objects.filter(group__name = g) )
		if p.hosts is not None:	
			for h in p.hosts:
				host = IP.objects.get(hostname= h)
				if not host_dic.has_key(host):
					host_dic[host] = [n] #add policy order into dic
				else:
					if n not in host_dic[host]: #will not add the duplicate policy name
						host_dic[host].append(n)
	return host_dic
"""

#host_list =   set(host_list)
def data_handler(host_dic):
	graph_dic = {}
	alert_dic = {}
	for h,p_index_list in  host_dic.items():  #p_index stands for policy_index in enabled_policy list 
	  alert_list = []
	  graph_dic[h.hostname] = [] #initialize the list
	  for p_index in set(p_index_list):
		p = policy.enabled_policy[p_index] #find this host belongs to which policy
		if monitor_dic.has_key(h.hostname): #host needs to be monitored
			if len(monitor_dic[h.hostname]) == 0: 
				alert_list.append({"ServerDown":"No data received from client,is the agent or the host down"} )
				#print "\033[31;1mno data from client, is it done?\033[0m",h.hostname
				break
			else: 
				print "\033[46;1m%s\033[0m" % h.hostname
				for service,alert_index in p.services.items():
				  if  alert_index.graph_index['index'] is not None:
					graph_dic[h.hostname].append( alert_index.graph_index  ) #'||||'
				  try:
					s = alert_handle.handle(service,alert_index,  monitor_dic[h.hostname][service])	
					if len(s) !=0:alert_list.append(s)
				  except KeyError:
					alert_list.append({"NoValidServiceData":(service,"service not exist in client datat")} )
					
		else: #host not in database or not enalbed for monitoring
			print "\033[34;1mnot going to monitor server:\033[0m", h.hostname
	  if hosts.monitored_hosts.has_key(h.hostname):
		customized_policy = hosts.monitored_hosts[h.hostname]
		print "*"*50,'Customized'#,customized_policy.services
		for service,alert_index in customized_policy.services.items():
		  try:	
			s = alert_handle.handle(service,alert_index,  monitor_dic[h.hostname][service])
			if len(s) !=0:alert_list.append(s)
		  except KeyError:
			alert_list.append({"NoValidServiceData":(service,"service not exist in client datat")} )
			
	  #else:
	  #	print 'no customized policy',h
	  alert_dic[h.hostname] = alert_list
	print '\033[41;1m*\033[0m'*50,'ALert LIST\n'
	for host,alerts in  alert_dic.items():
		print '\033[31;1m%s\033[0m' %host
		for msg in  alerts:print msg #for i in alerts:print i


	print '\033[42;1m graph list ----------\033[0m\n'
	for h,g in graph_dic.items():
		print h
		if len(g) >0:
		 for s in  g:
			print s

def multi_job(m_dic):
	def run(name):
		print 'going to run job......',name
	threading.Thread(target=run, args=(m_dic,)).start()


time_counter = time.time()


while True:
	
	monitor_list = get_monitor_host_list()
	data_handler( monitor_list )
	print '033[42;1m-----Executed...>>>>\033[0m '
	"""if time.time() - time_counter > 15:
		print '\033[45;1m-----draw lines----\033[0m'
		time.sleep(10)
		print 'sleep is done....'
		time_counter = time.time()
		#multi_job(monitor_list)
		redis_connector.r['Graph_list'] = pickle.dumps(monitor_list)
	"""
	#p = subprocess.Popen('python /home/alex/tri_client/status_data_optimzation.py', stdout=subprocess.PIPE, shell=True)
	print monitor_list
	time.sleep(10)
