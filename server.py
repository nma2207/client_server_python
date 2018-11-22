#coding: utf-8
import socket
import sys
import argparse
import json

import threading
import time

class Server:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', port))
        self.max_client_count = 10
        self.sock.listen(self.max_client_count)

        self.waiting_tasks = []
        self.done_tasks = {}
        self.in_progress = 0

        self.waiting_tasks_lock = threading.Lock()
        self.done_tasks_lock = threading.Lock()
        self.in_progress_lock = threading.Lock()

        self.task_numbers = []
        self.task_numbers_lock = threading.Lock()

        self.thread = threading.Thread(target = self.do_tasks)
        self.thread.start()

    def run(self):
        print('Run server')

        while True:
            client, address = self.sock.accept()
            print('Connected:', address)
            data = client.recv(1024).decode('utf-8')
            data = json.loads(data)
            self.execute_command(client, data)


    def execute_command(self, client, data):
        if 'command' in data:
            command = data['command']
            if command == 'get_status':
                result = self.get_status(int(data['arg']))
            elif command == 'get_result':
                result = self.get_result(int(data['arg']))
            elif command == 'reverse':
                result = self.add_task(data)
            elif command == 'swap':
                result = self.add_task(data)
            else:
                result = 'Command not found'
        else:
            result = 'Bad request'


        response = {'result': result}
        response = json.dumps(response)

        client.send(response.encode('utf-8'))
        client.close()

    def get_status(self, id):
        self.done_tasks_lock.acquire()
        self.waiting_tasks_lock.acquire()
        self.in_progress_lock.acquire()
        try:
            result = 'not_found'
            if id == self.in_progress:
                result = 'in_progress'
            if id in self.done_tasks:
                result = 'done'
            else:
                for i in self.waiting_tasks:
                    if i['id'] == id:
                        result = 'waiting'
                        break
            return result
        finally:
            self.in_progress_lock.release()
            self.waiting_tasks_lock.release()
            self.done_tasks_lock.release()



    def get_result(self, id):
        with self.done_tasks_lock:
            result = self.done_tasks.get(id, 'not_found')
            if result != 'not_found':
                result = self.done_tasks[id]['result']

            self.task_numbers_lock.acquire()
            self.task_numbers.remove(id)
            self.task_numbers_lock.release()

            return result

    def add_task(self, command):

        with self.waiting_tasks_lock:
            number = self.find_number()
            command['id'] = number
            self.waiting_tasks.append(command)
            return number

    def reverse(self, word):
        print('reverse')
        word_list = list(word)
        for i in range(len(word_list) // 2):
            #swap
            word_list[i], word_list[-i - 1] = word_list[-i - 1], word_list[i]
        result = ''.join(word_list)
        time.sleep(3)
        return result

    def swap(self, word):
        print('swap')
        word_list = list(word)

        for i in range(0, len(word_list)//2):
            word_list[2 * i], word_list[2 * i+1] = word_list[2 * i+1], word_list[2 * i]
        result = ''.join(word_list)

        time.sleep(7)

        return result


    def find_number(self):
        with self.task_numbers_lock:
            self.task_numbers.sort()
            if not self.task_numbers:
                number = 1

            elif self.task_numbers[0] != 1:
                number = 1
            else:
                number = 0
                for i in range(1, len(self.task_numbers)):
                    if self.task_numbers[i] - self.task_numbers[i-1]>1:
                        number = self.task_numbers[i-1]+1

                        break
                if number == 0:
                    number = self.task_numbers[-1]+1

            self.task_numbers.append(number)
            return number

    def do_tasks(self):
        while True:

            time.sleep(0.5)
            with self.waiting_tasks_lock:
                if not self.waiting_tasks:
                    continue

                task = self.waiting_tasks.pop(0)

            with self.in_progress_lock:
                self.in_progress = task['id']

            if task['command'] == 'reverse':
                result = self.reverse(task['arg'])
            elif task['command'] == 'swap':
                result = self.swap(task['arg'])

            task['result'] = result
            with self.done_tasks_lock:
                self.done_tasks[task['id']] = task

            with self.in_progress_lock:
                self.in_progress = 0

def create_parser():
    parser = argparse.ArgumentParser(
        prog = 'Client program',
        description = '''Program for sending command to server''',
        add_help = False
    )

    parent_group = parser.add_argument_group()
    parent_group.add_argument('--help', '-h', action='help', help='Help')
    parser.add_argument('-p','--port', default = 8080, type = int, help = 'Port of server')
    return parser

def main():
    parser = create_parser()

    namespace = parser.parse_args(sys.argv[1:])
    port = namespace.port

    server = Server(port)

    server.run()

if __name__ == "__main__":
    main()