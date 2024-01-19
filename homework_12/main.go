package main

import (
	"fmt"
	"log"
	"os"
	"path"
	"path/filepath"
)

func main() {

	pattern_files := "data/appsinstalled/*.tsv.gz"
	files, err := filepath.Glob(pattern_files)
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
