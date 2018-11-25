import unittest
import client
import server

class ClientTest(unittest.TestCase):
    def test_get_request_json(self):
        parser = client.create_parser()

        commands = [['-b', '-c', 'reverse', '-a', 'word'],
                    ['-c', 'get_status', '-a', '3'],
                    ['-b', '-c', 'swap', '-a', ''],
                    '-c get_result -ip 192.168.1.1 -a 123'.split()]
        namespaces = [parser.parse_args(command) for command in commands]

        jsons = [{'command':'reverse', 'arg':'word'},
                {'command':'get_status', 'arg':'3'},
                {'command':'swap', 'arg':""},
                 {'command': 'get_result', 'arg':'123'}]

        for i in range(len(commands)):
            self.assertEqual(client.get_request_json(namespaces[i]),
                            jsons[i])


class ServerTest(unittest.TestCase):

    def test_swap(self):
        words = ['Python', '', 'Шалаш', 'Word']
        results = [server.swap(word, 0) for word in words]
        right_results = ['yPhtno', '', 'аШалш', 'oWdr']

        for i in range(len(results)):
            self.assertEqual(results[i], right_results[i])

    def test_reverse(self):
        words = ['Python', '', 'Шалаш', 'Word']
        results = [server.reverse(word, 0) for word in words]
        right_results = ['nohtyP', '', 'шалаШ', 'droW']

        for i in range(len(results)):
            self.assertEqual(results[i], right_results[i])

    def test_get_status(self):
        serv = server.Server(8080)

        serv.in_progress = 3
        serv.waiting_tasks = [{'id':1}, {'id':13}]

        serv.done_tasks = {
            4:{},
            6:{}
        }

        search_id = [1, 5, 13, 3, 4, 6]
        right_results = ['waiting', 'not_found', 'waiting', 'in_progress',
                         'done', 'done']

        results = [serv.get_status(id) for id in search_id]

        for i in range(len(results)):
            self.assertEqual(results[i], right_results[i])

    def test_get_result(self):
        serv = server.Server(8080)

        serv.done_tasks = {
            1: {'result':'123'},
            2: {'result':'1235'}
        }
        search_id = [1,2,3]

        right_results = ['123', '1235', 'not_found']
        results = [serv.get_result(id) for id in search_id]
        for i in range(len(results)):
            self.assertEqual(results[i], right_results[i])

    def test_find_number(self):
        serv = server.Server(8080)
        # test #1
        task_numbers_list = [
            [],
            [2, 3, 5],
            [1, 2, 3, 4],
            [5],
            [1,2,3,5]
        ]

        right_results = [1, 1, 5, 1, 4]

        for i in range(len(right_results)):
            serv.task_numbers = task_numbers_list[i]

            result = serv.find_number()
            self.assertEqual(result, right_results[i])


    def test_add_task(self):
        serv = server.Server(8080)
        # test #1
        task_numbers_list = [
            [],
            [2, 3, 5],
            [1, 2, 3, 4],
            [5],
            [1,2,3,5]
        ]
        commands = [
            {},
            {},
            {},
            {},
            {}
        ]
        right_results = [1, 1, 5, 1, 4]

        for i in range(len(right_results)):
            serv.task_numbers = task_numbers_list[i]

            result = serv.add_task(commands[i])
            self.assertEqual(result, right_results[i])
            self.assertEqual(commands[i], {'id':right_results[i]})



if __name__ == "__main__":
    unittest.main()
        