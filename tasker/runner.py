import requests

def create_executor(teller_config, language):
    teller_endpoint = teller_config["endpoint"]
    teller_token = teller_config["token"]
    post_data = {'token': teller_token, 'lang': language}
    response = requests.post(f'{teller_endpoint}/create/executor', data=post_data)
    response.raise_for_status()
    return response.text

def compile_submission(teller_config, executor_id, submission_file):
    teller_endpoint = teller_config["endpoint"]
    teller_token = teller_config["token"]
    post_data = {'token': teller_token, 'executor-id': executor_id}
    response = requests.post(f'{teller_endpoint}/send/submission', files={'submission': submission_file}, data=post_data)
    response.raise_for_status()
    return response.json()

def run(teller_config, executor_id, testdata, time_limit=None, memory_limit=None):
    teller_endpoint = teller_config["endpoint"]
    teller_token = teller_config["token"]
    post_data = {'token': teller_token, 'executor-id': executor_id, 'stdin': testdata, 'time_limit': time_limit, 'memory_limit': memory_limit}
    response = requests.post(f'{teller_endpoint}/send/testcase', data=post_data)
    response.raise_for_status()
    return response.json()

def delete_executor(teller_config, executor_id):
    teller_endpoint = teller_config["endpoint"]
    teller_token = teller_config["token"]
    post_data = {'token': teller_token, 'executor-id': executor_id}
    response = requests.post(f'{teller_endpoint}/delete/executor', data=post_data)
    response.raise_for_status()
    return response.text

def send_data(submission_url, data):
    # post_data = {'data': data}
    response = requests.post(submission_url, json=data)
    response.raise_for_status()
    return response.text
