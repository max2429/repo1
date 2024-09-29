#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <zlib.h>

#include "deviceapps/deviceapps.pb-c.h"
#include "generator/generator.h"


#define MAGIC  0xFFFFFFFF
#define DEVICE_APPS_TYPE 1

typedef struct pbheader_s {
    uint32_t magic;
    uint16_t type;
    uint16_t length;
} pbheader_t;
#define PBHEADER_INIT {MAGIC, 0, 0}

const size_t ERROR_CODE = -1;


size_t serialize_item(PyObject* item, gzFile output_file) {
    DeviceApps msg = DEVICE_APPS__INIT;
    DeviceApps__Device device = DEVICE_APPS__DEVICE__INIT;

    // Device
    PyObject* device_raw = PyDict_GetItemString(item, "device");
    if (device_raw != NULL) {
        if (!PyDict_Check(device_raw)) {
            PyErr_SetString(PyExc_TypeError, "`device` should be a dictionary");
            return ERROR_CODE;
        }
        // Device ID
        PyObject* device_id_raw = PyDict_GetItemString(device_raw, "id");
        if (device_id_raw != NULL) {
            if (!PyUnicode_Check(device_id_raw)) {
                PyErr_SetString(PyExc_TypeError, "`device`.`id` should be a string");
                return ERROR_CODE;
            }
            Py_ssize_t len = 0;
            const char* device_id = PyUnicode_AsUTF8AndSize(device_id_raw, &len);
            device.has_id = 1;
            device.id.data = (uint8_t*)device_id;
            device.id.len = len;
        }
        // Device type
        PyObject* device_type_raw = PyDict_GetItemString(device_raw, "type");
        if (device_type_raw != NULL) {
            if (!PyUnicode_Check(device_type_raw)) {
                PyErr_SetString(PyExc_TypeError, "`device`.`type` should be a string");
                return ERROR_CODE;
            }
            Py_ssize_t len = 0;
            const char* device_type = PyUnicode_AsUTF8AndSize(device_type_raw, &len);
            device.has_type = 1;
            device.type.data = (uint8_t*)device_type;
            device.type.len = len;
        }
        msg.device = &device;
    }

    // Lat
    PyObject* lat_raw = PyDict_GetItemString(item, "lat");
    if (lat_raw != NULL) {
        if (!PyNumber_Check(lat_raw)) {
            PyErr_SetString(PyExc_TypeError, "`lat` should be a float number");
            return ERROR_CODE;
        }
        msg.has_lat = 1;
        msg.lat = PyFloat_AsDouble(lat_raw);
    }

    // Lon
    PyObject* lon_raw = PyDict_GetItemString(item, "lon");
    if (lon_raw != NULL) {
        if (!PyNumber_Check(lon_raw)) {
            PyErr_SetString(PyExc_TypeError, "`lon` should be a float number");
            return ERROR_CODE;
        }
        msg.has_lon = 1;
        msg.lon = PyFloat_AsDouble(lon_raw);
    }

    // Apps
    PyObject* apps_raw = PyDict_GetItemString(item, "apps");
    if (apps_raw != NULL) {
        if (!PyList_Check(apps_raw)) {
            PyErr_SetString(PyExc_TypeError, "`apps` should be a list");
            return ERROR_CODE;
        }
        size_t n_apps = (size_t)PySequence_Size(apps_raw);
        msg.n_apps = n_apps;
        msg.apps = malloc(sizeof(size_t) * msg.n_apps);
        if (!msg.apps) {
            PyErr_SetString(PyExc_MemoryError, "Error while allocating memory");
            return ERROR_CODE;
        }

        for (size_t i = 0; i < n_apps; i++) {
            PyObject* app = PyList_GET_ITEM(apps_raw, i);
            if (app != NULL && PyLong_Check(app)) {
                msg.apps[i] = (uint32_t)PyLong_AsLong(app);
            }
            else {
                PyErr_SetString(PyExc_TypeError, "`apps` item should be an integer");
                free(msg.apps);
                return ERROR_CODE;
            }
        }
    }

    // Finalize data
    size_t len = device_apps__get_packed_size(&msg);
    void* buf = malloc(len);
    if (!buf) {
        PyErr_SetString(PyExc_MemoryError, "Error while allocating memory");
        return ERROR_CODE;
    }
    device_apps__pack(&msg, buf);
    pbheader_t pbheader = PBHEADER_INIT;
    pbheader.type = DEVICE_APPS_TYPE;
    pbheader.length = len;

    // Write to file
    gzwrite(output_file, &pbheader, sizeof(pbheader_t));
    gzwrite(output_file, buf, (unsigned)len);

    // Free acquired resources
    free(msg.apps);
    free(buf);

    return sizeof(pbheader_t) + len;
}


static PyObject* deserialize_item(DeviceApps* msg) {
    PyObject* dict = PyDict_New();
    if (!dict) {
        PyErr_SetString(PyExc_MemoryError, "Error while constructing Python value");
        goto error;
    }

    // Device
    if (msg->device) {
        PyObject* device = PyDict_New();
        // Device ID
        if (msg->device->has_id) {
            PyObject* value_py = Py_BuildValue("s#", msg->device->id.data, msg->device->id.len);
            if (!value_py) {
                PyErr_SetString(PyExc_MemoryError, "Error while constructing Python value");
                goto error;
            }
            PyDict_SetItemString(device, "id", value_py);
            Py_DECREF(value_py);
        }
        // Device type
        if (msg->device->has_type) {
            PyObject* value_py = Py_BuildValue("s#", msg->device->type.data, msg->device->type.len);
            PyDict_SetItemString(device, "type", value_py);
            if (!value_py) {
                PyErr_SetString(PyExc_MemoryError, "Error while constructing Python value");
                goto error;
            }
        }
        PyDict_SetItemString(dict, "device", device);
        Py_DECREF(device);
    }

    // Apps
    PyObject* apps = PyList_New(0);
    if (msg->n_apps > 0) {
        for (size_t i = 0; i < msg->n_apps; i++) {
            PyObject* value_py = PyLong_FromLong(msg->apps[i]);
            if (!value_py) {
                PyErr_SetString(PyExc_MemoryError, "Error while constructing Python value");
                goto error;
            }
            PyList_Append(apps, value_py);
            Py_DECREF(value_py);
        }
    }
    PyDict_SetItemString(dict, "apps", apps);
    Py_DECREF(apps);

    // Lat
    if (msg->has_lat) {
        PyObject* value_py = PyFloat_FromDouble(msg->lat);
        if (!value_py) {
            PyErr_SetString(PyExc_MemoryError, "Error while constructing Python value");
            goto error;
        }
        PyDict_SetItemString(dict, "lat", value_py);
        Py_DECREF(value_py);
    }

    // Lon
    if (msg->has_lat) {
        PyObject* value_py = PyFloat_FromDouble(msg->lon);
        if (!value_py) {
            PyErr_SetString(PyExc_MemoryError, "Error while constructing Python value");
            goto error;
        }
        PyDict_SetItemString(dict, "lon", value_py);
        Py_DECREF(value_py);
    }

    return dict;

error:
    Py_XDECREF(dict);
    return NULL;
}


// Read iterator of Python dicts
// Pack them to DeviceApps protobuf and write to file with appropriate header
// Return number of written bytes as Python integer
static PyObject* py_deviceapps_xwrite_pb(PyObject* self, PyObject* args) {
    // Parse arguments (iterator: set of dicts, string: file path)
    PyObject* o;
    const char* path;
    if (!PyArg_ParseTuple(args, "Os", &o, &path)) {
        return NULL;
    }

    // Get iterator
    PyObject* iterator = PyObject_GetIter(o);
    if (!iterator) {
        PyErr_SetString(PyExc_TypeError, "First parameter should be Iterable");
        return NULL;
    }

    // Prepare output file
    gzFile output_file = gzopen(path, "wb");
    if (output_file == NULL) {
        PyErr_SetString(PyExc_OSError, "Error while opening output file");
        Py_DECREF(iterator);
        return NULL;
    }

    // Process items
    PyObject* item;
    size_t total_bytes = 0;
    while ((item = PyIter_Next(iterator))) {
        if (PyDict_Check(item)) {
            size_t len = serialize_item(item, output_file);
            if (len == ERROR_CODE) {
                Py_DECREF(item);
                break;
            }
            total_bytes += len;
        }
        else {
            PyErr_SetString(PyExc_ValueError, "`deviceapps` should be a dictionary");
        }
        Py_DECREF(item);
    }

    // Free acquired resources
    gzclose(output_file);
    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
        return NULL;
    }
    return PyLong_FromSize_t(total_bytes);
}


// Unpack only messages with type == DEVICE_APPS_TYPE
// Return iterator of Python dicts
static PyObject* py_deviceapps_xread_pb(PyObject* self, PyObject* args) {
    // Parse arguments (string: file path)
    const char* path;
    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL;
    }

    // Read output file
    gzFile input_file = gzopen(path, "rb");
    if (input_file == NULL) {
        PyErr_SetString(PyExc_OSError, "Error while opening input file");
        return NULL;
    }
    
    // Process data
    PyObject* output_list = PyList_New(0);

    while (!gzeof(input_file)) {
        // Read header
        pbheader_t pbheader;
        size_t bytes = gzread(input_file, &pbheader, sizeof(pbheader_t));
        if (bytes > 0) {
            // Read body
            void* buf = malloc(pbheader.length);
            if (!buf) {
                PyErr_SetString(PyExc_MemoryError, "Error while allocating memory");
                goto free_res;
            }
            bytes = gzread(input_file, buf, pbheader.length);

            // Parse message
            DeviceApps* msg = device_apps__unpack(NULL, pbheader.length, buf);
            PyObject* dict = deserialize_item(msg);
            if (dict != NULL) {
                PyList_Append(output_list, dict);
                Py_DECREF(dict);
            }
            else {
                PyErr_SetString(PyExc_OSError, "Error while parsing message");
            }

            // Free acquired resources
            device_apps__free_unpacked(msg, NULL);
            free(buf);
        }
        else {
            break;
        }
    }
    
    // Free acquired resources
free_res:
    gzclose(input_file);

    if (PyErr_Occurred()) {
        return NULL;
    }
    // PyObject* gen = PySeqIter_New(output_list);
    PyObject* gen = PyObject_CallFunction((PyObject*)&PyGenerator_Type, "(O)", output_list);
    Py_DECREF(output_list);
    return gen;
}


static PyMethodDef PBMethods[] = {
     {"deviceapps_xwrite_pb", py_deviceapps_xwrite_pb, METH_VARARGS,
      "Write serialized protobuf to file fro iterator"},
     {"deviceapps_xread_pb", py_deviceapps_xread_pb, METH_VARARGS,
      "Deserialize protobuf from file, return iterator"},
     {NULL, NULL, 0, NULL}
};
static PyModuleDef PBModule = {
    PyModuleDef_HEAD_INIT,
    "pb", // Name of module
    "Protobuf (de)serializer", // Module documentation
    -1, // Size of per-interpreter state of module
    PBMethods
};


// Python 3
PyMODINIT_FUNC PyInit_pb(void) {
    PyObject* module = PyModule_Create(&PBModule);

    if (PyType_Ready(&PyGenerator_Type) < 0) {
        return NULL;
    }
    return module;
}