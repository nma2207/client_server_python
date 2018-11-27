Тествое задание: написать клиент серверное приложение на Python.
===

Инструкция по запуску server.py:
---
	
	Принимает в качестве аргументов:
	
	* -p/--port - порт, который будет слушать, по умолчанию равен 8080
	* --help - Справка
	
	Пример:
	python server.py -p 8000
	или 
	python server.py
	
Инструкция по запуску client.py
---

	Принимает в качестве аргументов:
	
	* флаг -b - если установлен, то используется пакетный режим
	* -ip/--ip - ip адрес сервера
	* -p/--port - порт который слушает сервер
	* -с/--сommand команда (reverse, swap, get_status, get_result)
	* -a/--argument аргументы для команды. Слово для reverse и swap, id команды для get_status и get_result
	* --help - справка
	
	Пример:
	python client.py -b -c reverse -a "I love Python"
	python client.py -c get_status -a 12
	python client.py -b -ip localhost -p 8123 -c swap -a "I am programer"
