������� �������: �������� ������ ��������� ���������� �� Python.

���������� �� ������� server.py:
	��������� � �������� ����������:
	* -p/--port - ����, ������� ����� �������, �� ��������� ����� 8080
	* --help - �������
	������:
	python server.py -p 8000
	��� 
	python server
	
���������� �� ������� client.py
	��������� � �������� ����������:
	* ���� -b - ���� ����������, �� ������������ �������� �����
	* -ip/--ip - ip ����� �������
	* -p/--port - ���� ������� ������� ������
	* -�/--�ommand ������� (reverse, swap, get_status, get_result)
	* -a/--argument ��������� ��� �������. ����� ��� reverse � swap, id ������� ��� get_status � get_result
	* --help - �������
	
	������:
	python client.py -b -c reverse -a "I love Python"
	python client.py -c get_status -a 12
	python client.py -b -ip localhost -p 8123 -c swap -a "I am programer"