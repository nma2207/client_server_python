#coding: utf-8
import socket
import sys
import argparse
import json

import threading
import time

class Server:
    '''
    Класс реализующий сервер
    '''
    def __init__(self, port):
        # Занимаемый порт
        self.port = port
        # Очередь задач ожидающих выполнения
        self.waiting_tasks = []
        # Выполненные задачи, ключ - id задачи
        self.done_tasks = {}

        # id выполняемой задачи
        self.in_progress = 0
        # Мьютексы для разделенного достпупа
        self.waiting_tasks_lock = threading.Lock()
        self.done_tasks_lock = threading.Lock()
        self.in_progress_lock = threading.Lock()

        # id всех задач
        self.task_numbers = []
        self.task_numbers_lock = threading.Lock()

        # Поток в котором будут выполняться задачи reverse и swap
        self.thread = threading.Thread(target = self.do_tasks)

        #Семафор - количество ожидающих задач
        self.do_task_semaphore = threading.Semaphore(0)
        

    def run(self):
        '''
        Запускаем сервер
        :return:
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', self.port))
        self.max_client_count = 10
        self.sock.listen(self.max_client_count)

        print('Run server')

        while True:
            client, address = self.sock.accept()
            print('Connected:', address)
            data = client.recv(1024).decode('utf-8')
            data = json.loads(data)

            response = self.execute_command(data)

            response = json.dumps(response)
            client.send(response.encode('utf-8'))
            client.close()

    def start_execute_thread(self):
        '''
        Запускаем поток для выполнения задач
        :return:
        '''
        self.thread.start()

    def execute_command(self, data):
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
        return response


    def get_status(self, id):
        '''

        :param id: id задачи
        :return: статус
        '''
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
        '''

        :param id: номер задачи
        :return: результат или not_found
        '''
        with self.done_tasks_lock:
            #result = self.done_tasks.get(id, 'not_found')
            if id in self.done_tasks:
                result = self.done_tasks[id]['result']
                self.done_tasks.pop(id, None)
                self.task_numbers_lock.acquire()
                if id in self.task_numbers:
                    self.task_numbers.remove(id)
                self.task_numbers_lock.release()

            else:
                result = 'not_found'

            return result

    def add_task(self, command):
        '''

        :param command: команда
        :return: id задачт
        '''

        with self.waiting_tasks_lock:
            number = self.find_number()
            command['id'] = number
            self.waiting_tasks.append(command)
            self.do_task_semaphore.release()
            return number

    def find_number(self):
        '''
        Находит минимальный свободный id.
        нумерация начинается с 1
        :return: id задачи
        '''
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
        '''
        Выполнение команд reverse и swap
        :return:
        '''
        while True:
            # Ожидаем, пока появится задача для выполнения
            self.do_task_semaphore.acquire()
            with self.waiting_tasks_lock:
                task = self.waiting_tasks.pop(0)
            #print('do command')
            with self.in_progress_lock:
                self.in_progress = task['id']

            if task['command'] == 'reverse':
                result = reverse(task['arg'])
            elif task['command'] == 'swap':
                result = swap(task['arg'])

            task['result'] = result
            with self.done_tasks_lock:
                self.done_tasks[task['id']] = task

            with self.in_progress_lock:
                self.in_progress = 0

            
def reverse(word, sleep_time = 3):
    '''

    :param word: переворачиваемое слово
    :param sleep_time: время выполнения команды
    :return: результат выполнения
    '''
    word_list = list(word)
    for i in range(len(word_list) // 2):
        #swap
        word_list[i], word_list[-i - 1] = word_list[-i - 1], word_list[i]
    result = ''.join(word_list)
    time.sleep(sleep_time)
    return result

def swap(word, sleep_time = 7):
    '''

    :param word: обрабатываемое слово
    :param sleep_time: время "выполнения" задачи
    :return: результат выполнения
    '''
    word_list = list(word)

    for i in range(0, len(word_list)//2):
        word_list[2 * i], word_list[2 * i+1] = word_list[2 * i+1], word_list[2 * i]
    result = ''.join(word_list)

    time.sleep(sleep_time)

    return result

def create_parser():
    '''

    :return: парсер командной строки
    '''
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
    server.start_execute_thread()
    server.run()

if __name__ == "__main__":
    main()