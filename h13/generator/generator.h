#ifndef PB_GENERATOR_H
#define PB_GENERATOR_H

#include <Python.h>


typedef struct {
    PyObject_HEAD
    Py_ssize_t seq_index;
    PyObject* sequence;
} GeneratorState;

extern PyTypeObject PyGenerator_Type;

#endif
