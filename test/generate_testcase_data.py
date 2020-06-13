#!/usr/bin/env python3

import sys
import os

import jinja2 as jj

from systemrdl import RDLCompiler, AddrmapNode, RegfileNode, MemNode, RegNode, FieldNode
from uvm_python_rdl import UVMPythonExporter

#-------------------------------------------------------------------------------

if len(sys.argv) < 3:
    raise Exception('Usage: generate_test_case.py <tc_name> <rdl_file>')

testcase_name = sys.argv[1]
rdl_file = sys.argv[2]
output_dir = os.path.dirname(rdl_file)

# ----------------------------------------------------------------------------
# Generate UVM model
# ----------------------------------------------------------------------------

rdlc = RDLCompiler()
rdlc.compile_file(rdl_file)
root = rdlc.elaborate().top

uvm_exportname = os.path.join(output_dir, testcase_name + "_uvm.py")

uvm_file = os.path.join(output_dir, testcase_name + "_uvm_nofac_reuse_pkg.py")
UVMPythonExporter().export(
    root, uvm_exportname,
    use_uvm_factory=False,
    reuse_class_definitions=True,
    export_as_package=True,
)
os.rename(uvm_exportname, uvm_file)

uvm_file = os.path.join(output_dir, testcase_name + "_uvm_fac_reuse_pkg.py")
UVMPythonExporter().export(
    root, uvm_exportname,
    use_uvm_factory=True,
    reuse_class_definitions=True,
    export_as_package=True,
)
os.rename(uvm_exportname, uvm_file)

uvm_file = os.path.join(output_dir, testcase_name + "_uvm_nofac_noreuse_pkg.py")
UVMPythonExporter().export(
    root, uvm_exportname,
    use_uvm_factory=True,
    reuse_class_definitions=False,
    export_as_package=True,
)
os.rename(uvm_exportname, uvm_file)

# -----------------------------------------------------------------------------
# Generate test logic
# -----------------------------------------------------------------------------

context = {
    'testcase_name': testcase_name,
    'root': root,
    'rn': root.inst_name,
    'isinstance': isinstance,
    'AddrmapNode': AddrmapNode,
    'RegfileNode': RegfileNode,
    'MemNode': MemNode,
    'RegNode': RegNode,
    'FieldNode': FieldNode,
}

# Generates the testbench for generated code
template = jj.Template("""
import unittest
#from .{{testcase_name}}_uvm_fac_reuse_pkg import *
from .{{testcase_name}}_uvm_nofac_noreuse_pkg import *
#from .{{testcase_name}}_uvm_nofac_reuse_pkg *

def ASSERT_EQ_STR(self, a,b):
    self.assertEqual(a, b, "{} != {}".format(a, b))

def ASSERT_EQ_INT(self, a,b):
    self.assertEqual(a, b, "0x{} != 0x{}".format(a, b))


class {{testcase_name}}_wrap:
    def __init__(self, name):
        self.{{rn}} = {{rn}}(name)

class {{testcase_name}}UnitTest(unittest.TestCase):

    def test_basic(self):
        #{{testcase_name}}_uvm.{{testcase_name}} {{rn}}
        #{{rn}} = {{testcase_name}}("{{rn}}")
        {{rn}} = {{testcase_name}}_wrap("{{rn}}").{{rn}}
        {{rn}}.build()
        {{rn}}.lock_model()

        {% for node in root.descendants(unroll=True) %}
        # {{node}}
            {%- if isinstance(node, (AddrmapNode, RegfileNode, MemNode)) %}
        ASSERT_EQ_STR(self, {{node.get_path()}}.get_full_name(), "{{node.get_path()}}")
            {%- endif %}
            {%- if isinstance(node, RegNode) %}
                {%- if node.is_virtual %}
        ASSERT_EQ_STR(self, {{node.parent.get_path() + "." + node.inst_name}}.get_full_name(), "{{node.parent.get_path() + "." + node.inst_name}}")
        ASSERT_EQ_INT(self, {{node.parent.get_path() + "." + node.inst_name}}.get_size(), {{node.inst.n_elements}})
                {%- else %}
        ASSERT_EQ_STR(self, {{node.get_path()}}.get_full_name(), "{{node.get_path()}}")
        ASSERT_EQ_INT(self, {{node.get_path()}}.get_address(), {{"0x%x" % node.absolute_address}})
        ASSERT_EQ_INT(self, {{node.get_path()}}.get_n_bits(), {{node.get_property("regwidth")}})
                {%- endif %}
            {%- endif %}
            {%- if isinstance(node, FieldNode) %}
                {%- if node.is_virtual %}
        ASSERT_EQ_STR(self, {{node.parent.parent.get_path() + "." + node.parent.inst_name + "." + node.inst_name}}.get_full_name(), "{{node.parent.parent.get_path() + "." + node.parent.inst_name + "." + node.inst_name}}")
                {%- else %}
        ASSERT_EQ_STR(self, {{node.get_path()}}.get_full_name(), "{{node.get_path()}}")
        ASSERT_EQ_INT(self, {{node.get_path()}}.get_lsb_pos(), {{node.lsb}})
        ASSERT_EQ_INT(self, {{node.get_path()}}.get_n_bits(), {{node.width}})
                {%- endif %}
            {%- endif %}
        {%- endfor %}

if __name__ == '__main__':
    unittest.main()
""")

template.stream(context).dump(os.path.join(output_dir, testcase_name + "_test.py"))
