{% import 'utils.py' as utils with context %}

from uvm import (UVMRegBlock, uvm_object_utils, UVMMem, sv)

//------------------------------------------------------------------------------
// uvm_reg_block definition for memories
//------------------------------------------------------------------------------
{% macro class_definition(node) -%}
{%- if class_needs_definition(node) %}
# {{get_class_friendly_name(node)}}
class {{get_class_name(node)}}(UVMRegBlock):
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
{%- for child in node.children() if isinstance(child, RegNode) -%}
#rand {{get_class_name(child)}} {{get_inst_name(child)}}
self.{{get_inst_name(child)}} = None
{% endfor -%}
{%- endmacro %}


//------------------------------------------------------------------------------
// new() function
//------------------------------------------------------------------------------
{% macro function_new(node) -%}
def __init__(self, name="{{get_class_name(node)}}"):
    super().__init__(name)
    #rand uvm_mem m_mem
    self.m_mem = None
    {{child_insts(node)|indent}}
{%- endmacro %}


//------------------------------------------------------------------------------
// build() function
//------------------------------------------------------------------------------
{% macro function_build(node) -%}
def build(self):
    self.default_map = self.create_map("reg_map", 0, {{roundup_to(node.get_property('memwidth'), 8) / 8}}, {{get_endianness(node)}})
    self.m_mem = UVMMem("m_mem", {{node.get_property('mementries')}}, {{node.get_property('memwidth')}}, "{{get_mem_access(node)}}")
    self.m_mem.configure(self)
    self.default_map.add_mem(self.m_mem, 0)
    {%- for child in node.children() if isinstance(child, RegNode) -%}
        {{uvm_vreg.build_instance(child)|indent}}
    {%- endfor %}
{%- endmacro %}


//------------------------------------------------------------------------------
// build() actions for uvm_reg_block instance (called by parent)
//------------------------------------------------------------------------------
{% macro build_instance(node) -%}
{%- if node.is_array %}
#foreach(self.{{get_inst_name(node)}}[{{utils.array_iterator_list(node)}}]) begin
for {{utils.array_iterator_list(node)}} in len(self.{{get_inst_name(node)}}):
    {%- if use_uvm_factory %}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = {{get_class_name(node)}}.type_id.create(sv.sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}))
    {%- else %}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}} = {{get_class_name(node)}}(sv.sformatf("{{get_inst_name(node)}}{{utils.array_suffix_format(node)}}", {{utils.array_iterator_list(node)}}))
    {%- endif %}
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.configure(self)
    self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.build()
    self.default_map.add_submap(self.{{get_inst_name(node)}}{{utils.array_iterator_suffix(node)}}.default_map, {{get_array_address_offset_expr(node)}})
{%- else %}
{%- if use_uvm_factory %}
self.{{get_inst_name(node)}} = {{get_class_name(node)}}.type_id.create("{{get_inst_name(node)}}")
{%- else %}
self.{{get_inst_name(node)}} = {{get_class_name(node)}}("{{get_inst_name(node)}}")
{%- endif %}
self.{{get_inst_name(node)}}.configure(self)
self.{{get_inst_name(node)}}.build()
self.default_map.add_submap(self.{{get_inst_name(node)}}.default_map, {{"0x%x" % node.raw_address_offset}})
{%- endif %}
{%- endmacro %}
