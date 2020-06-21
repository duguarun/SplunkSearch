from configparser import ConfigParser
from requests.auth import HTTPBasicAuth
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import json
import urllib3
import requests
import smtplib, ssl
import os

# disabling InsecureRequestWarning as we're using ssl certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 


class Email():
    def __init__(self):
        '''
            Initialize all the SMTP associated variables from 'splunk_config.ini' SMTP section.
        '''
        try:
            self.smtp_username = config['smtp']['username']
            self.smtp_password = config['smtp']['password']
            self.smtp_server = config['smtp']['smtp_server']
            self.smtp_port = config['smtp']['smtp_port']
            self.subject = "Splunk Search Resutls"
            self.body_content = """\
                    Hi,
                    
                    Please find the attached file for splunk search results
                    
                    Regards,
                    Arunkumar D"""
        except KeyError as e: 
            print("Attribute {} is missing in 'splunk_config.ini'".format(e))
            
        
    
    def set_subject(self, subject):
        '''
            sets custom subject line for email
        '''
        self.subject = subject
        
    def set_body(self, body):
        '''
            sets custom body for email
        '''
        self.body_content = body
    
    def sendEmail(self):
        '''
            Forms Email with attachement using splunk_results.json and sends it to the to_addr of spunk_config.ini
        '''
        
        self.sender_email = config['smtp']['sender_email']
        self.receiver_email = config['smtp']['to_addr']
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = self.subject
        self.message["From"] = self.sender_email
        self.message["To"] = self.receiver_email
        self.body = MIMEText(self.body_content, "plain")
        self.message.attach(self.body)
        self.attachement = MIMEBase('application', "octet-stream")
        with open( os.path.join(base_dir, 'splunk_results.json'), 'r') as fo:
            self.attachement.set_payload(fo.read())
        encoders.encode_base64(self.attachement)
        self.attachement.add_header('Content-Disposition', 'attachment; filename="splunk_results.json"')
        self.message.attach(self.attachement)
        self.context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port , context=self.context) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(
                    self.sender_email, self.receiver_email, self.message.as_string()
                )
                
        except smtplib.SMTPAuthenticationError:
            print("Invalid credential please check username/password on 'splunk_config.ini'")
            return 'failed'
        else:
            print("Mail sent")
            return True
        
            
    
        
        
        


class SplunkSearch():
    def __init__(self):
        '''
            Initialize all the variable associated with splunk search from 'splunk_config.ini'
        '''
        try: 
            self.url = config['splunk']['url']
            self.username = config['splunk']['username']
            self.password = config['splunk']['password']
            self.search = 'search '+ config['splunk']['custom_search'].strip()
            self.post_data = {}
        except KeyError as e: 
            print("Attribute {} is missing in 'splunk_config.ini'".format(e))
            
        
            

        
    def set_query(self, query):
        '''
            change/set the serach query using this method
        '''
        self.search = 'search ' + str(query).strip()

    def prepare_post_data(self):
        '''
           preparing the data which is required to post the request to create job with requested search query
        '''
        self.post_data = {
            'rf': config['splunk']['rf'],
            'auto_cancel': config['splunk']['auto_cancel'],
            'status_buckets': config['splunk']['status_buckets'],
            'output_mode': config['splunk']['output_mode'], 
            'custom.display.page.search.mode': config['splunk']['custom_display_page_search_mode'],
            'custom.dispatch.sample_ratio': config['splunk']['custom_dispatch_sample_ratio'],
            'custom.workload_pool': config['splunk']['custom_workload_pool'],
            'custom.display.page.search.tab': config['splunk']['custom_display_page_search_tab'],
            'custom.search': config['splunk']['custom_search'],
            'custom.dispatch.earliest_time': config['splunk']['earliest_time'],
            'custom.dispatch.latest_time': config['splunk']['latest_time'],
            'search': self.search,
            'earliest_time': config['splunk']['earliest_time'],
            'latest_time': config['splunk']['latest_time'],
            'ui_dispatch_app': config['splunk']['ui_dispatch_app'],
            'preview':config['splunk']['preview']
            
        }
        return self.post_data
        
        
    def execute_query(self):
        '''
            Excutes the requested search query and collects the events in json file as output
        '''
        with requests.Session() as s:
            s.verify = False # disable ssl verification
            s.auth = HTTPBasicAuth(self.username, self.password)
            try:
                r = s.post('{}/services/search/jobs'.format(self.url),data=self.prepare_post_data())
                if r.status_code in [200, 201]:
                    sid = json.loads(r.content)['sid']
                    r =  s.get('{}/services/search/jobs/{}?output_mode=json'.format(self.url,sid))
                    for key, value in json.loads(r.content)['entry'][0]['links'].items():
                        if 'events' in value: #checking only the events
                            r = s.get('{}/{}?output_mode=json'.format(self.url, value))
                            with open( os.path.join(base_dir,"splunk_results.json"),'w') as fo:
                                json_data = json.loads(r.content)
                                json.dump(json_data, fo)
                            return True
                elif r.status_code == 401:
                    print("Unauthorized! Please check your splunk username and password in splunk_config.ini")
                    return False
                else:
                    print("HTTP Response- {}:: {}".format(r.status_code, json.loads(r.content)[0]['text']))
                    return False
            except Exception as e:
                print(e)
                return False
                
        
        
        

if __name__=="__main__":
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Parse splunk_config.ini
    config = ConfigParser()
    config.read(os.path.join(base_dir, 'splunk_config.ini'))
    
    # Initialize SplunkSearch and Email class  
    splunk = SplunkSearch()
    mail = Email()
    try:
        if splunk.execute_query():
            print("Events are capturted in 'splunk_results.json' file")
            print("Initiating Email....")
            mail.sendEmail() 
    except AttributeError as e: 
        print(e)
    except Exception as e:
        print(e)
        