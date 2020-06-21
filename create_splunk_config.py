from configparser import ConfigParser
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
data = {
        'splunk' : {'output_mode': 'json', 
                    'url': 'https://localhost:8089',
                    'username': 'xxxx',
                    'password': 'yyyyy',
                    'rf': '*',
                    'auto_cancel': '30',
                    'status_buckets': '300',
                    'output_mode': 'json', 
                    'custom_display_page_search_mode': 'verbose',
                    'custom_dispatch_sample_ratio': '1',
                    'custom_workload_pool': '',
                    'custom_display_page_search_tab': 'events',
                    'custom_search': 'index=\"_internal\" | top sourcetype',
                    'earliest_time': '-24h@h',
                    'latest_time': 'now',
                    'ui_dispatch_app':'app',
                    'preview':'1'
                   },
        'smtp': {'username': 'xxxx@gmail.com',
                 'password': 'yyyyy',
                 'sender_email': 'xxxxx@gmail.com',
                 'to_addr': 'xxxxx@gmail.com',
                 'smtp_server': 'smtp.gmail.com',
                 'smtp_port': '465'
                }
    
 }
config = ConfigParser()
config.read_dict(data)
with open( os.path.join(base_dir ,'splunk_config.ini'), 'w') as fo:
    config.write(fo)
