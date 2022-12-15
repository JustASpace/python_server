Конюшенко Данил Сергеевич ФТ-104 (ФТ-204)

WebServer

Обрабатывает HTTP-запросы по загрузке или получению файла
Принимает запросы вида "GET/POST имя_файла HTTP/1.1\r\nHost: имя_хоста\r\n\r\n"
В случае отсутствия файла с данным именем на сервере отправляет ошибку
Также нельзя загрузить файл с именем, файл с которым уже существует на сервере
Сервер можно конфигурировать посредством внесения изменений в config.ini

Можно добавлять несколько серверов для одновременного запуска в config.ini
(виртуальные сервера)

Так же добавлена поддержка reverse-proxy сервера, который, в свою очередь, настраивается
через proxy_config.ini. В данный момент прокси-сервер проверяет формат загружаемого/получаемого
файла, определяет, какой локальный сервер будет осуществлять с ним работу, а так же
может ограничивать доступ к сереверам к этим серверам. В данный момент поддерживают 2 сервера
'image_server' (работает с форматами .jpg и .png) и 'txt-server' (формат .txt).