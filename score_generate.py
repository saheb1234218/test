import json
import logging
import os
import socket
import sys

import requests

## Global variables and functions
scores = {}
logs_directory = '/home/ubuntu/'

def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    print("Attempting to connect to {} on port {}".format(address, port))
    try:
        s.connect((address, port))
        print( "Connected to %s on port %s" % (address, port))
        return True
    except socket.error:
        print ("Connection to %s on port %s failed" % (address, port))
        return False
    finally:
        s.close()

class ScoreGenerate:
    def __init__(self, user):
        self.HEADERS = {"Content-Type": "application/json"}
        self.localhost = 'http://localhost:8081/'
        self.score = 0

        self.SAMPLE_URL = 'https://cwod-assessment-images.s3.ap-south-1.amazonaws.com/images/'
        self.FIRST_POST_ID = ''
        self.FIRST_POST = '130.png'

    ### Helper functions
    def get_api(self, endpoint):
        print ('Making a GET request to ' + endpoint)
        response = requests.get(self.localhost+endpoint, headers = self.HEADERS)
        print('Received response with status code:' + str(response.status_code))
        return response

    def post_api(self, endpoint, body):
        print('Making a POST request to ' + endpoint + ' with body ')
        print(body)
        response = requests.post(self.localhost + endpoint, headers = self.HEADERS, data = body)
        print('Received response with status code:' + str(response.status_code))
        return response

    def decode_and_load_json(self, response):
        try:
            data = json.loads(response.content.decode('utf-8'))
        except Exception as e:
            print("Except")
            logging.exception(str(e))
            return response
        return data
    ### Helper functions end here

    def get_on_empty_db_test(self):
        try:
            endpoint = 'memes/'
            response = self.get_api(endpoint)
            if response.status_code == 200:
                data = self.decode_and_load_json(response)
                # Should be an empty array.
                if data == []:
                    print('PASS: Congrats, you scored some points')
                else:
                    print('FAIL: Are you not starting with an empty DB?')
            else:
                print('FAIL: Error, you might have to debug')

        except Exception as e:
            logging.exception('get_on_empty_db_test failed')

    # First Post
    def first_post_test(self):
        try:
            endpoint = 'memes'
            body = {
                'name': 'crio-test-name',
                'caption': 'crio-test-caption',
                'url': self.SAMPLE_URL + self.FIRST_POST
            }
            response = self.post_api(endpoint, json.dumps(body))
            if response.status_code == 201 or response.status_code == 200:
                data = self.decode_and_load_json(response)
                print('First post data: ', data)
                self.FIRST_POST_ID = data['id']
                print('PASS: First post id which will be used for further tests: ' + self.FIRST_POST_ID)
            else:
                print('FAIL: Your POST request did not go through')

        except Exception as e:
            logging.exception('FAIL: Your POST request did not go through')

    def base_score_generator(self):
        logging.info('GetOnEmptyDbTest')
        self.get_on_empty_db_test()
        logging.info('FirstPostTest')
        self.first_post_test()

if __name__ == "__main__":
    try:
        user = sys.argv[1]
        test_mode = sys.argv[2]

        logging.basicConfig(filename=logs_directory + user + '_python.log', level=logging.DEBUG)

        print("Starting test script for: ", user)
        log_file_name = logs_directory + user + '_log.log'
        if not check_server('localhost', 8081):
            print("FAIL: Localhost not running")
            os.system('echo "Localhost not running:" > ' + log_file_name)
            exit(-1)

        if (test_mode == 'BASE'):
            print ('Generate base scores')
            ScoreGenerate(user).base_score_generator()

    except Exception as e:
        logging.exception('FAIL: Main')
