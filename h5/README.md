# Web Server

Веб-сервер написан, используя "ванильный" python.
Не используются сторонние библиотеки для работы с http.

Сервер масштабируется на несколько воркеров. Для задания их количества используется аргумент `-w`.

Аргумент `-p` задает прослушаваемый порт.
Путь `DOCUMENT_ROOT`, по которому будут возвращаться файлы, задается аргументом `-r`.

#### Пример запуска:
    python3 httpd.py -r / -p 8080 -w 2


#### Пример тестов:
    python httptest.py


#### Результат нагрузочного тестирования c двумя воркерами:

ab -n 50000 -c 100 -r http://localhost:8080/


This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        python
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        129 bytes

Concurrency Level:      100
Time taken for tests:   3.857 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      16450000 bytes
HTML transferred:       6450000 bytes
Requests per second:    12963.16 [#/sec] (mean)
Time per request:       7.714 [ms] (mean)
Time per request:       0.077 [ms] (mean, across all concurrent requests)
Transfer rate:          4164.92 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.2      0      12
Processing:     1    7   1.8      7      20
Waiting:        0    6   1.8      6      20
Total:          4    8   1.7      7      22

Percentage of the requests served within a certain time (ms)
  50%      7
  66%      8
  75%      8
  80%      8
  90%      9
  95%     11
  98%     13
  99%     15
 100%     22 (longest request)

