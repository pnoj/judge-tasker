import argparse
import requests
import os
import zipfile
import yaml
import shutil
import traceback
import json
import runner

import isolate

def download(url, path):
    res = requests.get(url)
    res.raise_for_status()
    file_obj = open(path, "wb")
    for chunk in res.iter_content(100000):
        file_obj.write(chunk)
    file_obj.close()

def gen_cmd_args(cmd_dict):
    args = []
    for i in cmd_dict:
        args.append(f"--{i}")
        args.append(cmd_dict[i])
    return args

def main(args):
    download(args['problem_file_url'], "problem.zip")
    download(args['submission_file_url'], "submission")

    with zipfile.ZipFile("problem.zip", "r") as zip_ref:
        zip_ref.extractall("problem")

    shutil.copyfile("submission", "problem/submission")
    shutil.copyfile("runner.py", "problem/runner.py")

    problem_manifest_file = open("problem/manifest.yaml", "r")
    problem_manifest = yaml.safe_load(problem_manifest_file)
    problem_manifest_file.close()

    grader_args = problem_manifest['judge']['args']
    grader_args['grader_base_path'] = "/app"
    grader_args['submission_file'] = "/app/submission"
    grader_args['time_limit'] = problem_manifest['metadata']['limit']['time']
    grader_args['memory_limit'] = problem_manifest['metadata']['limit']['memory']
    grader_args['teller_config'] = dict()
    grader_args['teller_config']['endpoint'] = args['teller_endpoint']
    grader_args['teller_config']['token'] = args['token']
    grader_args['language'] = args['language']
    grader_args['passthrough_url'] = args['passthrough_url']

    if 'url' in problem_manifest['judge']['grader']:
        download(problem_manifest['judge']['grader']['url'], "problem/grader.py")       
    elif 'file' in problem_manifest['judge']['grader']:
        os.rename('problem/{}'.format(problem_manifest['judge']['grader']['file']), 'problem/grader.py')
    else:
        download("https://cdn.paullee.dev/pnoj/graders/standard.py", "problem/grader.py")       

    try:
        isolate.setup()
        submission_result_str = isolate.execute_command(["python3", "/app/grader.py"], os.path.abspath(os.path.join(os.path.dirname(__file__), "problem")), "/app", stdin=json.dumps(grader_args))
        isolate.cleanup()
        submission_result = json.loads(submission_result_str)
    except Exception as e:
        traceback.print_exc()
        submission_result = {'status': 'IE', 'message': str(e)}

    return submission_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_fetch_url")
    args = parser.parse_args()

    response = requests.get(args.task_fetch_url)
    response.raise_for_status()
    task_args = response.json()

    result = main(task_args)

    if 'callback_url' in task_args:
        runner.send_data(task_args['callback_url'], result)

    result_json = json.dumps(result)

    print(result_json)
