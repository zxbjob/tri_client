import global_setting
import json,os,sys,threading
from conf import templates, hosts
import db_connector
from triWeb.models import Group,IP
from django.core.exceptions import ObjectDoesNotExist
def get_monitor_host_list():
  host_dic = {}
  try: 
        for n,p in  enumerate(templates.enabled_templates):
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
  except  ObjectDoesNotExist,err:
	print 'get_monitor_dic.py:',err

#print get_monitor_host_list()
