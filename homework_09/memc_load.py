#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import gzip
import glob
import logging
import threading
import collections
import multiprocessing
from optparse import OptionParser
# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
import appsinstalled_pb2
# pip install python-memcached
import memcache

NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])
thread_semaphore = threading.BoundedSemaphore(10)
lock_thread = threading.RLock()


def dot_rename(path):
    """Функция переименовывает файл после выполнения анализа его содержимого.
    Перед названием устанавливается точка."""
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(appsinstalled, dry_run=False):
    """Фунция отправляет разобранную информацию из строки файла в мемкэш."""
    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    ua.apps.extend(appsinstalled.apps)
    packed = ua.SerializeToString()
    # @TODO persistent connection
    # @TODO retry and timeouts!
    if dry_run:
        logging.debug("%s - %s -> %s" % (memc_addr, key, str(ua).replace("\n", " ")))
    else:
        return (key, packed)



def parse_appsinstalled(line):
    """Функция парсинга строк файлов. Строка разбирается на составляющие
    после чего в случае успеха возвращает именованный кортеж в качестве результата. """
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)

def work_with_file(args):
    """Функция работы с файлом. Функция принимает в качестве аргументов несколько значений.
    fn - файловое имя, device_memc - словарь с id устройств, options - аргументы из аргпарсера,
    queue - объект очереди.
    Процесс открывает на чтение файл, выполняет вложенную функцию work_with_lines, 
    На каждую 1000 строк создается новый поток обработки строк. После чего он высвобождается.
    После выполнения вызывается функция dot_rename переименовывающая файл который был обработан."""
    fn, device_memc, options, queue = args
    processed = errors = 0
    logging.info('Processing %s' % fn)
    fd = gzip.open(fn, "rt", encoding="UTF-8")
    lines_list = []
    threads_list = []
    memclients_dict = {'idfa': memcache.Client([options.idfa]), 'gaid': memcache.Client([options.gaid]), 
    'adid': memcache.Client([options.adid]), 'dvid': memcache.Client([options.dvid])}
    insert_app_dict = {}
    def work_with_lines(lines, thread_semaphore):
        nonlocal processed, errors
        with thread_semaphore:
            for line in lines:
                line = line.strip()
                if not line:
                    return 
                appsinstalled = parse_appsinstalled(line)
                if not appsinstalled:
                    errors += 1
                    return 
                memc_addr = device_memc.get(appsinstalled.dev_type)
                if not memc_addr:
                    errors += 1
                    logging.error("Unknow device type: %s" % appsinstalled.dev_type)
                    return
                key, packed = insert_appsinstalled(appsinstalled, options.dry)
                insert_app_dict[key] = packed
                with lock_thread:
                    if len(insert_app_dict) >= 4:
                        try:
                            ok = memclients_dict[appsinstalled.dev_type].set_multi(insert_app_dict)
                            processed += 1
                        except Exception as e:
                            logging.exception("Cannot write to memc %s: %s" % (memc_addr, e))
                            errors += 1
                        
    for line in fd:
        lines_list.append(line)
        if len(lines_list) == 1000:
            thread = threading.Thread(target=work_with_lines, args=(lines_list, thread_semaphore))
            threads_list.append(thread)
            thread.start()
            queue.put(10)
            if len(threads_list) >= 10:
                [x.join() for x in threads_list]
                threads_list.clear()
            lines_list.clear()
    if len(lines_list):
        thread = threading.Thread(target=work_with_lines, args=(lines_list, thread_semaphore))
        threads_list.append(thread)
        thread.start()
        queue.put(len(lines_list))
    [x.join() for x in threads_list]
    threads_list.clear()
    if not processed:
        fd.close()
        dot_rename(fn)
    err_rate = float(errors) / processed
    if err_rate < NORMAL_ERR_RATE:
        logging.info("Acceptable error rate (%s). Successfull load" % err_rate)
    else:
        logging.error("High error rate (%s > %s). Failed load" % (err_rate, NORMAL_ERR_RATE))
    fd.close()
    dot_rename(fn)


def main(options):
    """Мэйн функция."""
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
        }
    process_pool = multiprocessing.Pool(processes=options.workers)
    process_manager = multiprocessing.Manager()
    queue = process_manager.Queue()
    args_list = [(fn, device_memc, options, queue) for fn in glob.iglob(options.pattern)]
    try:
        process_pool.map(work_with_file, args_list)
    finally:
        process_pool.close()
        process_pool.join()
    queue.put(-1)


def prototest():
    """Тестовая функция проверки разбора строки и работы с протобуфом."""
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="./data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    op.add_option("--workers", action="store", default=2, type=int)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
