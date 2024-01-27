package main

import (
	"bufio"
	"compress/gzip"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"

	"github.com/bradfitz/gomemcache/memcache"
)

const NORMAL_ERR_RATE = 0.01

type str_parse struct {
	Device_type string  `json:"Device_type"`
	Dev_id      string  `json:"Dev_id"`
	Lat         float64 `json:"lat"`
	Lon         float64 `json:"lon"`
	Apps        string  `json:"apps"`
}

type apps struct {
	device_type string
	value       []byte
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

func parse_lines_file(done chan struct{}, rawlines chan []byte) chan apps {
	var st_p str_parse
	var msg apps
	parsed_lines := make(chan apps)

	go func() {
		defer close(parsed_lines)
		for rawline := range rawlines {
			line := string(rawline)
			line_split := strings.Split(line, "\t")
			if len(line_split) < 4 {
				return
			}

			if line_split[0] != "idfa" && line_split[0] != "gaid" && line_split[0] != "adid" && line_split[0] != "dvid" {
				log.Println(line_split[0], " не является используемым для обработки типом устройства")
			} else {
				st_p.Device_type = line_split[0]
			}
			st_p.Dev_id = line_split[1]
			lat, err := strconv.ParseFloat(line_split[2], 32)
			if err != nil {
				log.Println("Указанное значение невозможно преобразовать в lat float64")
			} else {
				st_p.Lat = lat
			}

			lon, err := strconv.ParseFloat(line_split[3], 32)
			if err != nil {
				log.Println("Указанное значение невозможно преобразовать в lon float64")
			} else {
				st_p.Lon = lon
			}
			st_p.Apps = line_split[4]
			msg.device_type = st_p.Device_type
			value, err := json.Marshal(st_p)
			if err != nil {
				log.Println("Невозможно сериализовать указанную структуру")
			}
			msg.value = value

			select {
			case parsed_lines <- msg:
			case <-done:
				return
			}

		}
	}()
	return parsed_lines
}

func send_to_memc(parsed_lines chan apps, connector map[string]*memcache.Client, success *uint64, errors *uint64) {
	for line := range parsed_lines {
		atomic.AddUint64(success, 1)
		client := connector[line.device_type]
		result := &memcache.Item{Key: line.device_type, Value: line.value}
		err := client.Set(result)
		if err != nil {
			atomic.AddUint64(errors, 1)
			continue
		}

	}
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
	done_ch := make(chan struct{})
	var success, errors uint64

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
				parse_line := parse_lines_file(done_ch, rawlines)
				send_to_memc(parse_line, memcache_connector, &success, &errors)
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
	rate := float64(errors) / float64(success)
	if rate < NORMAL_ERR_RATE {
		fmt.Println("Загрузка данных прошла успешно, процент ошибок: ", rate)
	} else {
		fmt.Println("Загрузка данных прошла с ошибками, процент ошибок: ", rate)
	}

}
