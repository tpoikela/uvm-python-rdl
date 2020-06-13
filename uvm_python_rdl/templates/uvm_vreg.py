{% import 'utils.py' as utils with context %}

from uvm import (UVMVReg, uvm_object_utils)

//------------------------------------------------------------------------------
// uvm_vreg definition
//------------------------------------------------------------------------------
{% macro class_definition(node) -%}
{%- if class_needs_definition(node) %}
# {{get_class_friendly_name(node)}}
class {{get_class_name(node)}}(UVMVReg):
    {{function_new(node)|indent}}

    {{function_build(node)|indent}}
#endclass : {{get_class_name(node)}}
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
#rand uvm_vreg_field {{get_inst_name(field)}}
self.{{get_inst_name(field)}} = None
{% endfor -%}
{%- endmacro %}


//------------------------------------------------------------------------------
// new() function
//------------------------------------------------------------------------------
{% macro function_new(node) -%}
def __init__(self, name="{{get_class_name(node)}}"):
    super().__init__(name, {{node.get_property('regwidth')}})
    {{child_insts(node)|indent}}
{%- endmacro %}


//------------------------------------------------------------------------------
// build() function
//------------------------------------------------------------------------------
{% macro function_build(node) -%}
def build(self):
    {%- for field in node.fields() %}
    {%- if use_uvm_factory %}
    self.{{get_inst_name(field)}} = UVMVRegField.type_id.create("{{get_inst_name(field)}}")
    {%- else %}
    self.{{get_inst_name(field)}} = UVMVRegField("{{get_inst_name(field)}}")
    {%- endif %}
    self.{{get_inst_name(field)}}.configure(self, {{field.width}}, {{field.lsb}})
    {%- endfor %}
{%- endmacro %}


//------------------------------------------------------------------------------
// build() actions for uvm_reg instance (called by parent)
//------------------------------------------------------------------------------
{% macro build_instance(node) -%}
{%- if use_uvm_factory %}
self.{{get_inst_name(node)}} = {{get_class_name(node)}}.type_id.create("{{get_inst_name(node)}}")
{%- else %}
self.{{get_inst_name(node)}} = {{get_class_name(node)}}("{{get_inst_name(node)}}")
{%- endif %}
self.{{get_inst_name(node)}}.configure(self, self.m_mem, {{node.inst.n_elements}})
self.{{get_inst_name(node)}}.build()
{%- endmacro %}
