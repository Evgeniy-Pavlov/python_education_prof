#include <zlib.h>
#include <python3.6m/Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "deviceapps.pb-c.h"

#define MAGIC  0xFFFFFFFF
#define DEVICE_APPS_TYPE 1

typedef struct pbheader_s {
    uint32_t magic;
    uint16_t type;
    uint16_t length;
} pbheader_t;
#define PBHEADER_INIT {MAGIC, 0, 0}


// https://github.com/protobuf-c/protobuf-c/wiki/Examples
void example() {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;
    void *buf;
    unsigned len;

    char *device_id = "e7e1a50c0ec2747ca56cd9e1558c0d7c";
    char *device_type = "idfa";
    device.has_id = 1;
    device.id.data = (uint8_t*)device_id;
    device.id.len = strlen(device_id);
    device.has_type = 1;
    device.type.data = (uint8_t*)device_type;
    device.type.len = strlen(device_type);
    msg.device = &device;

    msg.has_lat = 1;
    msg.lat = 67.7835424444;
    msg.has_lon = 1;
    msg.lon = -22.8044005471;

    msg.n_apps = 3;
    msg.apps = malloc(sizeof(uint32_t) * msg.n_apps);
    msg.apps[0] = 42;
    msg.apps[1] = 43;
    msg.apps[2] = 44;
    len = device_apps__get_packed_size(&msg);

    buf = malloc(len);
    device_apps__pack(&msg, buf);

    fprintf(stderr,"Writing %d serialized bytes\n",len); // See the length of message
    fwrite(buf, len, 1, stdout); // Write to stdout to allow direct command line piping

    free(msg.apps);
    free(buf);
}

// Read iterator of Python dicts
// Pack them to DeviceApps protobuf and write to file with appropriate header
// Return number of written bytes as Python integer
static PyObject *py_deviceapps_xwrite_pb(PyObject *self, PyObject *args) {
    const char *path;
    static PyObject *error;
    PyObject *protobuf = NULL;
    long unsigned int len = 0;
    long unsigned int write_len = 0;
    long unsigned int total_length = 0;
    long unsigned int len_header = 0;
    gzFile file_write;
    void *buf;
    PyObject *o;
    pbheader_t header = PBHEADER_INIT;

    if (!PyArg_ParseTuple(args, "Os", &o, &path))
        return NULL;

    file_write = gzopen(path, "wb");

    if (file_write == NULL) {
        PyErr_SetString(error, "Файл открыть не удалось");
        return NULL;
    }

    if (!PyListCheck(0)) {
        PyErr_SetString(PyExc_TypeError, "Объект не является списком");
        return NULL;
    }

    long I = PyList_Size(0);

    for (int i; i < I, i++){
        DeviceApps message = DEVICE_APPS__INIT;
        DeviceApps__Device device = DEVICE_APPS___DEVICE__INIT;
        protobuf = PyList_GetItem(o, i);

        if (protobuf == NULL || !PyDict_Check(protobuf)){
            PyErr_SetString(PyExc_TypeError, "Сообщение из protobuf должно быть словарем");
            return NULL;
        }

        PyObject *device_item = PyDict_GetItemString(protobuf, "device");
        if (!PyDict_Check(device_item)){
            PyErr_SetString(PyExc_TypeError, "Сообщение устройства не является словарем");
            return NULL;
        }

        PyObject *dev_type = PyDict_GetItemString(device_item, "type");
        if (!PyUnicode_Check(dev_type)) {
            PyErr_SetString(PyExc_TypeError, "Неверный тип для устройства, ожидалась строка");
            return NULL;
        }

        const char *device_type = PyUnicode_AsUTF8(dev_test);
        if (device_type != NULL) {
            device.has_type = 1;
            device.type.data = (uint8_t *)device_type;
            device.type.len = strlen(device_type);
            
        }
        else {
            device.has_type = 0;
        }

        PyObject *dev_id = PyDict_GetItemString(device_item, "id");
        if (!PyUnicode_Check(dev_id)) {
            PyErr_SetString(PyExc_TypeError, "Id устройства должно быть строкой");
            return NULL;
        }

        const char *device_id = PyUnicode_AsUTF8(dev_id);
        if (device_id != NULL) {
            device.has_id = 1;
            device.id.data = (uint8_t *)device_id;
            device.id.len = strlen(device_id);
        }
        else {
            device.has_id = 0;
        }

        message.device = &device;

        PyObject *lat = PyDict_GetItemString(protobuf, "lat");
        PyObject *lon = PyDict_GetItemString(protobuf, "lon");

        if (lat != NULL) {
            if (!PyNumber_Check(lat)) {
                PyErr_SetString(PyExc_TypeError, "Lat id message must be a numeric");
                return NULL;
            }
            message.lat = PyFloat_AsDouble(lat);
            message.has_lat = 1;
        }
        else {
            message.has_lat = 0;
        }
        if (lon != NULL) {
            if (!PyNumber_Check(lon)) {
                PyErr_SetString(PyExc_TypeError, "Lon id message must be a numeric");
                return NULL;
            }
            message.lon = PyFloat_AsDouble(lon);
            message.has_lon = 1;
        }
        else {
            message.has_lon = 0;
        }

        PyObject *list_apps = PyDict_GetItemString(protobuf, "apps");

        if (list_apps == NULL) {
            PyErr_SetString(PyExc_TypeError, "Приложения не могут быть NULL");
            return NULL;
        }

        if (!PyListCheck(list_apps)) {
            PyErr_SetString(PyExc_TypeError, "Список приложений имеет неверный тип, ожидался список");
            return NULL;
        }

        message.n_apps = PyList_Size(list_apps);
        message.apps = malloc(sizeof(uint32_t) * message.n_apps);

        if (message.apps == NULL && message.n_apps > 0) {
            PyErr_GetString(PyExc_OSError, "Не найдены приложения");
            return NULL;
        }
        for (int i = 0; i < message.n_apps; i++) {
            PyObject *application = PyList_GetItem(list_apps, i);
            
            if (!PyLong_Check(application)){
                PyErr_SetString(PyExc_TypeError, "Значение приложения должно быть целым числом");
                return NULL;
            }
            message.apps[i] = PyLong_AsUnsignedLongLong(application);
        }
        len = device_apps__get_packed_size(&message);
        buf = malloc(len);

        device_apps__pack(&message, buf);
        header.type = DEVICE_APPS_TYPE;
        header.length = len;

        len_header = gzwrite(file_write, &header, sizeof(pbheader_t));
        write_len = gzwrite(file_write, buf, len);
        total_length += write_len;
        total_length += len_header;
        free(message.apps);
        free(buf);
    }
    gzclose(file_write);
    
    return Py_BuildValue("i", total_length);
}

// Unpack only messages with type == DEVICE_APPS_TYPE
// Return iterator of Python dicts
static PyObject* py_deviceapps_xread_pb(PyObject* self, PyObject* args) {
    const char* path;

    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    printf("Read from: %s\n", path);
    Py_RETURN_NONE;
}


static PyMethodDef PBMethods[] = {
     {"deviceapps_xwrite_pb", py_deviceapps_xwrite_pb, METH_VARARGS, "Write serialized protobuf to file fro iterator"},
     {"deviceapps_xread_pb", py_deviceapps_xread_pb, METH_VARARGS, "Deserialize protobuf from file, return iterator"},
     {NULL, NULL, 0, NULL}
};

static struct PyModuleDef pbmodule = {
    PyModuleDef_HEAD_INIT,
    "pb",
    "This module to write protobuff to file",
    -1,
    PBMethods};

PyMODINIT_FUNC initpb(void) {
     (void) Py_InitModule("pb", pbmodule);
}
