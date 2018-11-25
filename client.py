#conding: utf-8

import argparse
import json
import socket
import sys
import time


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

    parser.add_argument('-b', '--batch', action = 'store_const',
                        const = True, default = False,
                        help = 'If is set, use batch type')
    parser.add_argument('-ip', '--ip', default = 'localhost', type = str,
                        help = 'Ip-address of server')
    parser.add_argument('-p', '--port', default = 8080, type = int,
                        help = 'Port of server')
    parser.add_argument('-c', '--command',
                        choices = ['reverse', 'swap', 'get_status', 'get_result'],
                        help = '''Sending command. Can be:\n
                        "reverse" - to reverse argument \n
                        "get_status" - to get task status \n
                        "get_result" - to get result of task''')
    parser.add_argument('-a', '--argument', help = 'argument to command', type = str)

    return parser

def get_request_json(namespace):
    '''
    :param namespace: параметры
    :return: json описание команды
    '''
    return {'command': namespace.command,
            'arg': namespace.argument}


def send_one_command(ip, port, request):
    '''

    :param ip: ip сервера
    :param port: port сервера
    :param request: json описание команды
    :return:
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, port))
        request_str = json.dumps(request)
        sock.send(request_str.encode('utf-8'))

        data = sock.recv(1024).decode('utf-8')
        data = json.loads(data)

        return data
    except:
        print('oops')
    finally:
        sock.close()

def send_batch(namespace):
    '''
    Пакетный способ опроса сервера
    :param namespace: параметры командной строки
    :return:
    '''
    ip = namespace.ip
    port = namespace.port

    request = get_request_json(namespace)

    data = send_one_command(ip, port, request)

    if 'result' in data:
        result = data.get('result')
    else:
        print('bad response from server')
    if namespace.command == 'get_result':
        print('Result:', result)
        return

    isDone = False

    id = result
    if namespace.command == 'get_status':
        isDone = result == 'done'
        id = namespace.argument


    while not isDone:
        try:
            time.sleep(1)
            request = {'command': 'get_status', 'arg':id}
            data = send_one_command(ip, port, request)
            if 'result' in data:
                if data['result'] == 'done':
                    isDone = True
                elif data['result'] == 'not_found':
                    print('server failed')
                    return
                print('Task status:', data['result'])
        except KeyboardInterrupt:
            print('Command running stop')
            return


    request = {'command': 'get_result', 'arg': id}
    data = send_one_command(ip, port, request)

    if 'result' in data:
        print('Result :', data['result'])




def main():
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.batch:
        send_batch(namespace)
    else:
        data = send_one_command(namespace.ip, namespace.port, get_request_json(namespace))
        if 'result' in data:
            print('Result:', data['result'])


if __name__ == "__main__":
    main()
