package main

import (
	"bufio"
	"compress/gzip"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path"
	"path/filepath"
	"sync"

	"github.com/bradfitz/gomemcache/memcache"
)

const NORMAL_ERR_RATE = 0.01

type str_parse struct {
	device_type string
	dev_id      string
	lat         float32
	lon         float32
	apps        string
}

func get_rawlines_from_file(path_file string) (chan []byte, chan error, error) {
	rawlines := make(chan []byte)
	errs := make(chan error)
	file, err := os.Open(path_file)
	if err != nil {
		log.Println("Невозможно открыть указанный файл, возникла ошибка:", err)
	}
	defer file.Close()
	file_reader, err := gzip.NewReader(file)
	if err != nil {
		log.Println("Возникла ошибка при попытке открыть файл:", err)
	}
	buff_contents := bufio.NewReader(file_reader)

	go func(rawlines chan []byte, errs chan error, contents *bufio.Reader) {
		defer func(rawlines chan []byte, errs chan error) {
			close(rawlines)
			close(errs)
		}(rawlines, errs)
		for {
			line, err := buff_contents.ReadBytes('\n')
			rawlines <- line
			if err != nil {
				if err != io.EOF {
					errs <- err
				}
				return
			}
		}
	}(rawlines, errs, buff_contents)
	return rawlines, errs, nil
}

func parse_lines_file(rawlines chan []byte) int {
	return 0
}

func main() {

	device_memc := make(map[string]*string, 4)
	pattern_files := flag.String("pattern", "data/appsinstalled/*.tsv.gz", "Путь к директории с файлами")
	device_memc["idfa"] = flag.String("idfa", "127.0.0.1:33013", "Адрес и порт куда будут отправляться данные для idfa")
	device_memc["gaid"] = flag.String("gaid", "127.0.0.1:33014", "Адрес и порт куда будут отправляться данные для gaid")
	device_memc["adid"] = flag.String("adid", "127.0.0.1:33015", "Адрес и порт куда будут отправляться данные для adid")
	device_memc["dvid"] = flag.String("dvid", "127.0.0.1:33016", "Адрес и порт куда будут отправляться данные для dvid")
	workers := flag.Int("workers", 10, "Число воркеров для обработки файла")
	wg := new(sync.WaitGroup)
	flag.Parse()
	fmt.Println(device_memc)

	memcache_connector := make(map[string]*memcache.Client, 4)

	for key, value := range device_memc {
		memcache_connector[key] = memcache.New(*value)
		memcache_connector[key].Timeout = 10
	}

	files, err := filepath.Glob(*pattern_files)
	if err != nil {
		log.Fatal(err)
	}

	for _, file := range files {
		path_file := filepath.ToSlash(path.Clean(file))
		rawlines, _, err := get_rawlines_from_file(path_file)
		if err != nil {
			log.Println("Возникла ошибка при чтении файла: ", err)
		}
		for i := 0; i < *workers; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				parse_line := parse_lines_file(rawlines)
				fmt.Println(parse_line)
			}()
		}
		dir, file_name := path.Split(path_file)
		new_path := path.Join(dir, "."+file_name)
		err = os.Rename(path_file, new_path)
		if err != nil {
			fmt.Println("Не удалось переименовать файл из-за ошибки: ", err)
		} else {
			fmt.Println("Файл переименован: ", new_path)
		}

	}
	wg.Wait()

}
