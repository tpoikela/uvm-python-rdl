{% import 'uvm_reg.py' as uvm_reg with context %}
{% import 'uvm_vreg.py' as uvm_vreg with context %}
{% import 'uvm_reg_block-mem.py' as uvm_reg_block_mem with context %}
{% import 'uvm_reg_block.py' as uvm_reg_block with context %}


{% macro top() -%}
    {%- for node in top_node.descendants(in_post_order=True) -%}
        {{child_def(node)}}
    {%- endfor -%}
    {{child_def(top_node)}}
{%- endmacro %}


{% macro child_def(node) -%}
    {%- if isinstance(node, RegNode) -%}
        {%- if node.is_virtual -%}
            {{uvm_vreg.class_definition(node)}}
        {%- else -%}
            {{uvm_reg.class_definition(node)}}
        {%- endif -%}
    {%- elif isinstance(node, (RegfileNode, AddrmapNode)) -%}
        {{uvm_reg_block.class_definition(node)}}
    {%- elif isinstance(node, MemNode) -%}
        {{uvm_reg_block_mem.class_definition(node)}}
    {%- endif -%}
{%- endmacro %}
