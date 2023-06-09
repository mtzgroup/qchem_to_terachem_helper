
QCHEM_FCHK_FILE = "qchem.fchk" # Generated by "gui 2" keyword in qchem.in "$rem" section
TC_c0_OUTPUT_FILE = "c0.qchem"

QCHEM_FCHK_C_TITLE = "Alpha MO coefficients"
QCHEM_FCHK_SHELLTYPE_TITLE = "Shell types"

MAX_L = 3
BASIS_REORDER_QCHEM_TO_TC = [
    [0],
    [0,1,2],
    [3,4,5,0,1,2], # xx, yy, zz, xy, xz, yz -> xy, xz, yz, xx, yy, zz
    [7,8,9,2,1,3,5,6,4,0], # xxx, yyy, zzz, xyy, xxy, xxz, xzz, yzz, yyz, xyz -> xyz, xxy, xyy, xxz, yyz, xzz, yzz, xxx, yyy, zzz
                           # This order was obtained by pure try and error on a metal system.
]
def shelltype_to_nao(L): return (L + 1) * (L + 2) // 2

import re
import numpy as np

qchem_fchk_file = open(QCHEM_FCHK_FILE, "r")
qchem_fchk_lines = qchem_fchk_file.readlines()
qchem_fchk_file.close()

qchem_C_lines = []
C_started = False
for line in qchem_fchk_lines:
    if (C_started):
        if ("=" in line): # Sign of termination
            C_started = False
        else:
            qchem_C_lines.append(line)
    if line.startswith(QCHEM_FCHK_C_TITLE):
        C_started = True
        match = re.findall("N=\s*(\d+)", line)
        nao_square = int(match[0])
        nao = int(np.sqrt(nao_square))
        assert (nao * nao == nao_square)

C_qchem = np.zeros(nao * nao)
i_cummulate = 0
for line in qchem_C_lines:
    fields = line.split()
    for field in fields:
        C_qchem[i_cummulate] = float(field)
        i_cummulate += 1
assert(i_cummulate == nao * nao)

C_qchem = C_qchem.reshape(nao, nao)

qchem_shelltype_lines = []
shelltype_started = False
for line in qchem_fchk_lines:
    if (shelltype_started):
        if ("=" in line): # Sign of termination
            shelltype_started = False
        else:
            qchem_shelltype_lines.append(line)
    if line.startswith(QCHEM_FCHK_SHELLTYPE_TITLE):
        shelltype_started = True
        match = re.findall("N=\s*(\d+)", line)
        nshell = int(match[0])

shelltypes = [0] * nshell
i_cummulate = 0
for line in qchem_shelltype_lines:
    fields = line.split()
    for field in fields:
        shelltypes[i_cummulate] = int(field)
        i_cummulate += 1
assert(i_cummulate == nshell)

C_tc = np.zeros((nao, nao))
i_ao_tc = 0
for L in range(MAX_L + 1):
    i_ao_qchem = 0
    for i_shell in range(nshell):
        shelltype = shelltypes[i_shell]
        if (shelltype == L):
            n_angular = shelltype_to_nao(L)
            for i_angular in range(n_angular):
                C_tc[i_ao_tc + BASIS_REORDER_QCHEM_TO_TC[L][i_angular], :] = C_qchem[:, i_ao_qchem + i_angular]
            i_ao_tc += n_angular
        i_ao_qchem += shelltype_to_nao(shelltype)
    assert (i_ao_qchem == nao)
assert (i_ao_tc == nao)

C_tc = C_tc.reshape(nao * nao)

C_tc.tofile(TC_c0_OUTPUT_FILE)

# C_real = np.fromfile("scr.geom/c0")
# C_real = C_real.reshape(nao, nao)

# print(np.max(np.abs(np.abs(C_tc) - np.abs(C_real))))
