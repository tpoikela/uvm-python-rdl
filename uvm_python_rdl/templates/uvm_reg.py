{% import 'utils.py' as utils with context %}

from uvm import (UVMReg, UVMRegField, UVM_NO_COVERAGE, sv)

#------------------------------------------------------------------------------
# uvm_reg definition
#------------------------------------------------------------------------------
{% macro class_definition(node) -%}
{%- if class_needs_definition(node) %}
# {{get_class_friendly_name(node)}}
class {{get_class_name(node)}}(UVMReg):
    {{function_new(node)|indent}}

    {{function_build(node)|indent}}

{%- if use_uvm_factory %}
uvm_object_utils({{get_class_name(node)}})
{%- endif %}
{% endif -%}
{%- endmacro %}


//------------------------------------------------------------------------------
// Child instances
//------------------------------------------------------------------------------
{% macro child_insts(node) -%}
{%- for field in node.fields() -%}
#rand uvm_reg_field {{get_inst_name(field)}}
self.{{get_inst_name(field)}} = None
{% endfor -%}
{%- endmacro %}


//------------------------------------------------------------------------------
// new() function
//------------------------------------------------------------------------------
{% macro function_new(node) -%}
def __init__(self, name="{{get_class_name(node)}}"):
    super().__init__(name, {{node.get_property('regwidth')}}, UVM_NO_COVERAGE)
    {{child_insts(node)|indent}}
{%- endmacro %}


//------------------------------------------------------------------------------
// build() function
//------------------------------------------------------------------------------
{% macro function_build(node) -%}
def build(self):
    {%- for field in node.fields() %}
    {%- if use_uvm_factory %}
    self.{{get_inst_name(field)}} = UVMRegField.type_id.create("{{get_inst_name(field)}}")
    {%- else %}
    self.{{get_inst_name(field)}} = UVMRegField("{{get_inst_name(field)}}")
    {%- endif %}
    self.{{get_inst_name(field)}}.configure(self, {{field.width}},
        {{field.lsb}}, "{{get_field_access(field)}}",
        {{field.is_volatile|int}}, {{"0x%x" % field.get_property('reset', default=0)}}, 1, 1, 0)
    {%- endfor %}
{%- endmacro %}


//------------------------------------------------------------------------------
// build() actions for uvm_reg instance (called by parent)
//------------------------------------------------------------------------------
{% macro build_instance(node) -%}
{%- if node.is_array %}
#for {{utils.array_iterator_list(node)}} in len(self.{{get_inst_name(node)}}):
for {{utils.array_iterator_list(node)}} in {{utils.get_product(node)}}:
    {%- if use_uvm_factory %}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = {{get_class_name(node)}}.type_id.create(sv.sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}))
    {%- else %}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = {{get_class_name(node)}}(sv.sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}))
    {%- endif %}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.configure(self)
    {{add_hdl_path_slices(node, get_inst_name(node) + utils.array_iterator_suffix(node))|trim|indent}}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.build()
    self.default_map.add_reg(self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}, {{get_array_address_offset_expr(node)}})
{%- else %}
{%- if use_uvm_factory %}
self.{{get_inst_name(node)}} = {{get_class_name(node)}}.type_id.create("{{get_inst_name(node)}}")
{%- else %}
self.{{get_inst_name(node)}} = new("{{get_inst_name(node)}}")
{%- endif %}
self.{{get_inst_name(node)}}.configure(self)
{{add_hdl_path_slices(node, get_inst_name(node))|trim}}
self.{{get_inst_name(node)}}.build()
self.default_map.add_reg(self.{{get_inst_name(node)}}, {{"0x%x" % node.raw_address_offset}})
{%- endif %}
{%- endmacro %}

//------------------------------------------------------------------------------
// Load HDL path slices for this reg instance
//------------------------------------------------------------------------------
{% macro add_hdl_path_slices(node, inst_ref) -%}
{%- if node.get_property('hdl_path') %}
self.{{inst_ref}}.add_hdl_path_slice("{{node.get_property('hdl_path')}}", -1, -1)
{%- endif -%}

{%- if node.get_property('hdl_path_gate') %}
self.{{inst_ref}}.add_hdl_path_slice("{{node.get_property('hdl_path_gate')}}", -1, -1, 0, "GATE")
{%- endif -%}

{%- for field in node.fields() %}
{%- if field.get_property('hdl_path_slice') is none -%}
{%- elif field.get_property('hdl_path_slice')|length == 1 %}
self.{{inst_ref}}.add_hdl_path_slice("{{field.get_property('hdl_path_slice')[0]}}", {{field.lsb}}, {{field.width}})
{%- elif field.get_property('hdl_path_slice')|length == field.width %}
{%- for slice in field.get_property('hdl_path_slice') %}
{%- if field.msb > field.lsb %}
self.{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb - loop.index0}}, 1)
{%- else %}
self.{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb + loop.index0}}, 1)
{%- endif %}
{%- endfor %}
{%- endif %}
{%- endfor -%}

{%- for field in node.fields() %}
{%- if field.get_property('hdl_path_gate_slice') is none -%}
{%- elif field.get_property('hdl_path_gate_slice')|length == 1 %}
self.{{inst_ref}}.add_hdl_path_slice("{{field.get_property('hdl_path_gate_slice')[0]}}", {{field.lsb}}, {{field.width}}, 0, "GATE")
{%- elif field.get_property('hdl_path_gate_slice')|length == field.width %}
{%- for slice in field.get_property('hdl_path_gate_slice') %}
{%- if field.msb > field.lsb %}
self.{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb - loop.index0}}, 1, 0, "GATE")
{%- else %}
self.{{inst_ref}}.add_hdl_path_slice("{{slice}}", {{field.msb + loop.index0}}, 1, 0, "GATE")
{%- endif %}
{%- endfor %}
{%- endif %}
{%- endfor %}
{%- endmacro %}
