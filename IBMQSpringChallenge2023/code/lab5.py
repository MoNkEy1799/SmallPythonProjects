from qiskit import transpile, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_ibm_provider import IBMProvider
from ibmq_challenge import traverse_map

# Preparing registers
quantum_register = QuantumRegister(127)
classical_register = ClassicalRegister(127)

# map physical qubits to the logical qubits directly using the same number
initial_layout = list(range(127))

# 54 qubits for GHZ-state
ghz_qubits = [0, 2, 4, 6, 8, 10, 12, 18, 20, 22, 24, 26, 28, 30, 32, 37, 39, 41, 43, 45, 47, 49, 51, 56, 58, 60, 62, 64, 66,
              68, 70, 75, 77, 79, 81, 83, 85, 87, 89, 94, 96, 98, 100, 102, 104, 106, 108, 114, 116, 118, 120, 122, 124, 126]

# stabilizer qubits (not all excess qubits are used stabilizers, only those with 2 GHZ-qubit connections)
stabilizer_qubits = [1, 3, 5, 7, 9, 11, 14, 15, 16, 17, 19, 21, 23, 25, 27, 29, 31, 33, 34, 35, 36, 38, 40, 42, 44, 46, 48, 50, 52, 53, 54, 55, 57, 59, 61, 63, 65, 67,
                     69, 71, 72, 73, 74, 76, 78, 80, 82, 84, 86, 88, 90, 91, 92, 93, 95, 97, 99, 101, 103, 105, 107, 109, 110, 111, 112, 115, 117, 119, 121, 123, 125]
   
# get CNOT connections for (optimal) starting qubit 62
cnot_connections = [c for connections in traverse_map(62)[0].values() for c in connections]

### EX: 1 ###

def generate_ghz127():
    qc = QuantumCircuit(quantum_register, classical_register)
    # apply H gate to starting qubit
    qc.h(62)
    for c in cnot_connections:
        # apply CNOTs according to optimal mapping to entangle rest of the qubits with starting qubit
        qc.cnot(*c)
    return qc

### EX: 2 ###

def deentangle_qubits():
    # deentangles all qubits not used for GHZ-state
    qc = QuantumCircuit(quantum_register, classical_register)
    for qubit in initial_layout:
        if qubit not in ghz_qubits:
            for c in cnot_connections:
                if qubit == c[1]:
                    qc.cnot(*c)
                    break
    return qc

def measure_stabilizers():
    qc = QuantumCircuit(quantum_register, classical_register)
    qc.measure(stabilizer_qubits, stabilizer_qubits)
    return qc

def measure_ghz():
    qc = QuantumCircuit(quantum_register, classical_register)
    qc.measure(ghz_qubits, ghz_qubits)
    return qc

simple_ghz = (generate_ghz127().compose(deentangle_qubits()).compose(measure_stabilizers()).compose(measure_ghz()))

# only works with Challenge access
backend = IBMProvider().get_backend("ibm_sherbrooke", instance="{hub}/{group}/{project}")

# -> transpiled circuit depth of only 59
qc_transpiled = transpile(simple_ghz, backend, initial_layout=initial_layout)
