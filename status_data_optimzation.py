from get_monitor_dic import get_monitor_host_list
import json,time
from conf import policy, hosts
import redis_connector as redis
from graph import data_storage_interval

latest_status= json.loads(redis.r.get('TriAquae_monitor_status'))
for h,p_index_list in  get_monitor_host_list().items():
	if redis.r.get('STATUS_DATA::%s' % h.hostname) is None:
		print "no data in redis", h.hostname
		redis.r['STATUS_DATA::%s' % h.hostname] = json.dumps({})
	else:
		pass #print redis.r.get('STATUS_DATA::%s' % h.hostname)
	STATUS_DATA = json.loads(redis.r.get('STATUS_DATA::%s' % h.hostname))
	print '\033[45;1m %s \033[0m ' % h.hostname	 
	for p_index in p_index_list:   #policy index list for each host 
	  p = policy.enabled_policy[p_index]
	  for service,obj in  p.services.items(): 
		  if latest_status[h.hostname].has_key(service): # data available from client 
			last_check_stamp = latest_status[h.hostname][service]['last_check']
		  else:
			last_check_stamp = None
		  if STATUS_DATA.has_key(service): #check whether this monitor index has historical data
			#get the last check status data
			last_time_in_db =  STATUS_DATA[service]['Actual'][-1][0] 
			if last_check_stamp is not None:
				if last_check_stamp - last_time_in_db < 10: #minimum 10 s interval
					print '\033[32;1mduplicate point......\033[0m'
					continue
				else:
					STATUS_DATA[service]['Actual'].append( [last_check_stamp] )
			else:continue		
		  else: # add serivce name into dic if it's not in there
			STATUS_DATA[service] = {}
			STATUS_DATA[service]['Actual'] = [[last_check_stamp ] ]
			for dataset_name,interval in data_storage_interval.items(): 
				STATUS_DATA[service][dataset_name] = []
		  #print service, obj.graph_index
		  #print '-------->',latest_status[h.hostname].get(service)
		  for index_name in  obj.graph_index['index']: #graph list 
		    try:
		      #print index_name
		      index_value = latest_status[h.hostname][service][index_name] 
		      STATUS_DATA[service]['Actual'][-1].append(index_value)
		    except KeyError:pass
	redis.r['STATUS_DATA::%s' % h.hostname] = json.dumps(STATUS_DATA)
	for n,v in STATUS_DATA.items():
		print "\033[42;1m %s \033[0m" %n
		#for i in v['Actual']:
		for i,n in v.items():
			if i == 'Actual':
			  for d in n:
				print d, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d[0] ))
			else:
				print i,n
		    #except ValueError:pass
#print latest_status
		      
			
			

