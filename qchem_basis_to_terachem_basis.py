
QCHEM_INPUT_FILE = "qchem.in"
TC_BASIS_OUTPUT_FILE = "chromophore_ccpvtz.basis"
TC_BASIS_COMMENT = """
### cc-pvtz
"""

qchem_input_file = open(QCHEM_INPUT_FILE, "r")
qchem_input_lines = qchem_input_file.readlines()
qchem_input_file.close()

qchem_basis_lines = []
basis_started = False
for line in qchem_input_lines:
    if (basis_started):
        qchem_basis_lines.append(line)
    if line.startswith("$basis"):
        basis_started = True
    if (line.startswith("$end") and basis_started):
        basis_started = False
        qchem_basis_lines.pop()

qchem_basis_lines_by_atom = [ [] ]
for line in qchem_basis_lines:
    line = line[:-1] # Remove the last "\n"
    if (line.startswith("****")):
        qchem_basis_lines_by_atom.append([])
    else:
        qchem_basis_lines_by_atom[-1].append(line)
assert (not qchem_basis_lines_by_atom.pop()) # Last list is empty

tc_basis_lines_by_atom = []
for lines_for_one_atom in qchem_basis_lines_by_atom:
    atom_name_line = lines_for_one_atom.pop(0)
    atom_name, zero = atom_name_line.split()
    tc_basis_lines_by_atom.append([])
    tc_basis_lines_by_atom[-1].append("ATOM " + atom_name)

    for line in lines_for_one_atom:
        if (line[0] in ("S", "P", "D", "F", "G", "H")):
            angular, primitive_count, one = line.split()
            tc_basis_lines_by_atom[-1].append(angular + "  " + primitive_count)
        elif not (line[0] in (" ", "\t")):
            raise "Unrecoginized line: " + line
        else:
            exponent, contraction = line.split()
            tc_basis_lines_by_atom[-1].append(line.replace("D", "E"))

tc_basis_lines = [ TC_BASIS_COMMENT + "\n" ]
for lines_for_one_atom in tc_basis_lines_by_atom:
    for line in lines_for_one_atom:
        tc_basis_lines.append(line + "\n")
    tc_basis_lines.append("\n")

tc_basis_file = open(TC_BASIS_OUTPUT_FILE, "w")
tc_basis_file.writelines(tc_basis_lines)
tc_basis_file.close()
