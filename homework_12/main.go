package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path"
	"path/filepath"

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

func main() {

	device_memc := make(map[string]*string, 4)
	pattern_files := flag.String("pattern", "data/appsinstalled/*.tsv.gz", "Путь к директории с файлами")
	device_memc["idfa"] = flag.String("idfa", "127.0.0.1:33013", "Адрес и порт куда будут отправляться данные для idfa")
	device_memc["gaid"] = flag.String("gaid", "127.0.0.1:33014", "Адрес и порт куда будут отправляться данные для gaid")
	device_memc["adid"] = flag.String("adid", "127.0.0.1:33015", "Адрес и порт куда будут отправляться данные для adid")
	device_memc["dvid"] = flag.String("dvid", "127.0.0.1:33016", "Адрес и порт куда будут отправляться данные для dvid")
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
		dir, file_name := path.Split(path_file)
		new_path := path.Join(dir, "."+file_name)
		err := os.Rename(path_file, new_path)
		if err != nil {
			fmt.Println("Не удалось переименовать файл из-за ошибки: ", err)
		} else {
			fmt.Println("Файл переименован: ", new_path)
		}
	}

}
