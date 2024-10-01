## MemcLoad Concurrency

### Требования

- Python 3.x
- Memcached


### Установка memcached в докере

```
docker-compose up -d memcached
```


### Установка зависимостей

```
pip3 install -r requirements.txt
```

Сгениерировать `appsinstalled_pb2.py` (для создания проекта с нуля):

```
cd appsinstalled
protoc --python_out=. appsinstalled.proto
```



### Использование

```
$ python3 memc_load_fast.py -h

Usage: memc_load_fast.py [options]

optional arguments:
  -h, --help            show this help message and exit
  -t, --test            
  -l LOG, --log=LOG     
  --dry                 
  --pattern=PATTERN     
  --idfa=IDFA           
  --gaid=GAID           
  --adid=ADID           
  --dvid=DVID           
  -w WORKERS, --workers=WORKERS
  -a ATTEMPTS, --attempts=ATTEMPTS
```

### Установка в докере:

```
docker-compose up -d --build
```



### Запуск

один поток:

```
$ time python3 memc_load.py --pattern=./data/*.tsv.gz


```

несколько потоков:

```
$ time python3 memc_load_fast.py --pattern=./data/*.tsv.gz

```
