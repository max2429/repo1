#include "generator.h"
#include <stdio.h>


static PyObject* generator_new(PyTypeObject* type, PyObject* args, PyObject* kwargs) {
    // Parse arguments (iterator: set of dicts)
    PyObject *sequence;
    if (!PyArg_ParseTuple(args, "O", &sequence)) {
        return NULL;
    }

    // Check arguments
    if (!PySequence_Check(sequence)) {
        PyErr_SetString(PyExc_TypeError, "First parameter should be Iterable");
        return NULL;
    }
    Py_ssize_t len = PySequence_Length(sequence);
    if (len == -1) {
        return NULL;
    }

    // Create new GeneratorState and initialize its state
    GeneratorState* gen = (GeneratorState*)type->tp_alloc(type, 0);
    if (gen == NULL) {
        return NULL;
    }

    // Initialize generator
    Py_INCREF(sequence);
    gen->sequence = sequence;
    gen->seq_index = 0;

    return (PyObject*)gen;
}


static void generator_dealloc(GeneratorState* gen) {
    // We need `XDECREF` here because when the generator is exhausted, `gen->sequence` is cleared
    // with `Py_CLEAR` which sets it to NULL
    Py_XDECREF(gen->sequence);
    Py_TYPE(gen)->tp_free(gen);
}


static PyObject* generator_next(GeneratorState* gen) {
    PyObject* elem = PySequence_GetItem(gen->sequence, gen->seq_index);
    if (elem) {
        gen->seq_index++;
        return elem;
    }
    // The reference to the sequence is cleared in the first generator call after its exhaustion
    // (after the call that returned the last element). Py_CLEAR will be harmless for subsequent
    // calls since it's idempotent on NULL
    if (PyErr_ExceptionMatches(PyExc_IndexError) || PyErr_ExceptionMatches(PyExc_StopIteration)) {
        PyErr_Clear();
        gen->seq_index = -1;
        Py_CLEAR(gen->sequence);
    }
    return NULL;
}


PyTypeObject PyGenerator_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "generator",                   // tp_name
    sizeof(GeneratorState),        // tp_basicsize
    0,                             // tp_itemsize
    (destructor)generator_dealloc, // tp_dealloc
    0,                             // tp_print
    0,                             // tp_getattr
    0,                             // tp_setattr
    0,                             // tp_reserved
    0,                             // tp_repr
    0,                             // tp_as_number
    0,                             // tp_as_sequence
    0,                             // tp_as_mapping
    0,                             // tp_hash
    0,                             // tp_call
    0,                             // tp_str
    0,                             // tp_getattro
    0,                             // tp_setattro
    0,                             // tp_as_buffer
    Py_TPFLAGS_DEFAULT,            // tp_flags
    0,                             // tp_doc
    0,                             // tp_traverse
    0,                             // tp_clear
    0,                             // tp_richcompare
    0,                             // tp_weaklistoffset
    PyObject_SelfIter,             // tp_iter
    (iternextfunc)generator_next,  // tp_iternext
    0,                             // tp_methods
    0,                             // tp_members
    0,                             // tp_getset
    0,                             // tp_base
    0,                             // tp_dict
    0,                             // tp_descr_get
    0,                             // tp_descr_set
    0,                             // tp_dictoffset
    0,                             // tp_init
    PyType_GenericAlloc,           // tp_alloc
    generator_new,                 // tp_new
};
