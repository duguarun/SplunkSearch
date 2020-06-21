
# Installation Procedure 

## Dependencies  
```bash
pip install -r requirements.txt
```
## Configuration
Option-1:
    Manually configure all the variables like splunk username, password, url, search queries in 'splunk_config.ini' as shown below
     ```bash
        custom_search = index="_internal" 
        username = xxxx
        password = yyy
        url = https://localhost:8009
        
        ```
        
Option-2:
    Assign values in dict variable 'data' of 'create_splunk_config.py' and execute the below command this will create the 'splunk_config.ini'

    ```bash
    python create_splunk_config.py

    ```


## Usage
```bash
python splunk_search.py

```
## Expected Results
```bash
Events are capturted in 'splunk_results.json' file
Initiating Email....
Mail sent
```
After executing 'splunk_search.py' file it will generate the json output file 'splunk_results.json' with all the events in the same directory where 'splunk_search.py' resides also it will initiate email with json file to the to_addr which is configured in 'splunk_config.ini'


