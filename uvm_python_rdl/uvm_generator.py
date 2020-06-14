#! /usr/bin/env python

import sys
import os

import jinja2 as jj

from systemrdl import (RDLCompiler, AddrmapNode, RegfileNode, MemNode,
    RegNode, FieldNode)
from uvm_python_rdl import UVMPythonExporter

# Template for unit tests (TODO: Move to separate file)
template_data = """
import unittest
from .{{testcase_name}}_uvm_fac_reuse_pkg import *
#from .{{testcase_name}}_uvm_nofac_noreuse_pkg import *
#from .{{testcase_name}}_uvm_nofac_reuse_pkg import *


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
        self.assertEqual({{node.get_path()}}.get_full_name(), "{{node.get_path()}}")
            {%- endif %}
            {%- if isinstance(node, RegNode) %}
                {%- if node.is_virtual %}
        self.assertEqual({{node.parent.get_path() + "." + node.inst_name}}.get_full_name(), "{{node.parent.get_path() + "." + node.inst_name}}")
        self.assertEqual({{node.parent.get_path() + "." + node.inst_name}}.get_size(), {{node.inst.n_elements}})
                {%- else %}
        self.assertEqual({{node.get_path()}}.get_full_name(), "{{node.get_path()}}")
        self.assertEqual({{node.get_path()}}.get_address(), {{"0x%x" % node.absolute_address}})
        self.assertEqual({{node.get_path()}}.get_n_bits(), {{node.get_property("regwidth")}})
        ok = {{node.get_path()}}.randomize()
        self.assertTrue(ok, "{{node.inst_name}} can be randomized")
                {%- endif %}
            {%- endif %}
            {%- if isinstance(node, FieldNode) %}
                {%- if node.is_virtual %}
        self.assertEqual( {{node.parent.parent.get_path() + "." + node.parent.inst_name + "." + node.inst_name}}.get_full_name(), "{{node.parent.parent.get_path() + "." + node.parent.inst_name + "." + node.inst_name}}")
                {%- else %}
        self.assertEqual({{node.get_path()}}.get_full_name(), "{{node.get_path()}}")
        self.assertEqual({{node.get_path()}}.get_lsb_pos(), {{node.lsb}})
        self.assertEqual({{node.get_path()}}.get_n_bits(), {{node.width}})
                {%- endif %}
            {%- endif %}
        {%- endfor %}

if __name__ == '__main__':
    unittest.main()
"""


class UVMGenerator():

    def __init__(self, outdir, usefact=True, reuse=True):
        self.outdir = outdir
        self.use_fact = usefact
        self.reuse = reuse
        self.export_as_pkg = True

    def get_pkg_name(self):
        if [self.use_fact, self.reuse] == [True, True]:
            return "uvm_fac_reuse_pkg.py"
        elif [self.use_fact, self.reuse] == [False, True]:
            return "uvm_nofac_reuse_pkg.py"
        elif [self.use_fact, self.reuse] == [True, False]:
            return "uvm_fac_noreuse_pkg.py"
        else:
            return "uvm_nofac_noreuse_pkg.py"

    def export_reg_models(self, root, tc_name):
        fname = tc_name + self.get_pkg_name()
        uvm_exportname = os.path.join(self.outdir, tc_name + "_uvm.py")
        uvm_file = os.path.join(self.outdir, fname)

        UVMPythonExporter().export(
            root, uvm_exportname,
            use_uvm_factory=self.use_fact,
            reuse_class_definitions=self.reuse,
            export_as_package=self.export_as_pkg,
        )
        os.rename(uvm_exportname, uvm_file)

    def generate_test_logic(self, root, tc_name):
        context = {
            'testcase_name': tc_name,
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
        template = jj.Template(template_data)
        template.stream(context).dump(os.path.join(self.outdir,
            tc_name + "_test.py"))


# ----------------------------------------------------------------------------
# Generate UVM model
# ----------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        raise Exception('Usage: generate_test_case.py <tc_name> <rdl_file>')
    
    testcase_name = sys.argv[1]
    rdl_file = sys.argv[2]
    output_dir = os.path.dirname(rdl_file)

    rdlc = RDLCompiler()
    rdlc.compile_file(rdl_file)
    root = rdlc.elaborate().top

    UVMGenerator(output_dir, False, True).export_reg_models(root, testcase_name)

    UVMGenerator(output_dir, True, True).export_reg_models(root, testcase_name)

    UVMGenerator(output_dir, True, False).export_reg_models(root, testcase_name)

    # Generate test logic
    UVMGenerator(output_dir, True, True).generate_test_logic(root, testcase_name)


if __name__ == '__main__':
    main()
