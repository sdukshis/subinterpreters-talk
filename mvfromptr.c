#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

static PyObject *FastInt_Add(PyObject *self, PyObject *args)
{
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b))
    {
        return NULL;
    }

    return Py_BuildValue("i", a + b);
}

static PyObject *memviewfrombuffer(PyObject *self, PyObject *args) {
    char* buf;
    Py_ssize_t size;
    if (!PyArg_ParseTuple(args, "kn", &buf, &size))
    {
        return NULL;
    }
    return PyMemoryView_FromMemory((char*)buf, size, PyBUF_READ);    
}

static PyMethodDef FastIntMethods[] = {
    {"add",  FastInt_Add, METH_VARARGS, "Add two integers."},
    {"memviewfrombuffer",  memviewfrombuffer, METH_VARARGS, "Create memoryview from buf"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef FastIntModule = {
    PyModuleDef_HEAD_INIT,
    "fastint",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    FastIntMethods
};

PyMODINIT_FUNC PyInit_fastint()
{
    return PyModule_Create(&FastIntModule);
}
