# tcp-chat
[![Code Climate](https://codeclimate.com/github/rvsosn/tcp-chat/badges/gpa.svg)](https://codeclimate.com/github/rvsosn/tcp-chat)
Пользователь запускает клиент и подключается к серверу, далее любое сообщение от клиента будет оправлено всем подключенным пользователям. Для запроса у сервера списка всех клиентов пользователь вводит conn. Используется Protobuf для сериализации данных.
## Использование
### Сервер
```
python3 -m tcp_chat --server --port 8001
```
### Клиент
```
python3 -m tcp_chat --client --port 8001
```
