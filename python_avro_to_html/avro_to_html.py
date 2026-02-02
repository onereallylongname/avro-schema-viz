import os
from pathlib import Path
import sys
import json

# configs

DEBUG = False
DRY_RUN = False

# consts

header_part_1= '''<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
'''
header_part_2= '''<style>
.collapsible {
  background-color: #eee;
  color: #444;
  cursor: pointer;
  padding: 4px;
  padding-left: 10px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
  border-radius: 10px;
  border-style: none none groove none;
}

.active:hover, .collapsible:hover {
  background-color: #ccc;
}

.info.collapsible {
  width: 30%;
  padding: 2px;
  background-color: #fff;
  border-style: none none ridge none;
}

.collapsible.highlight{
  border-style: ridge ridge ridge ridge;
  border-color: yellow;
}

.content {
  padding-left: 12px;
  background-color: white;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.2s ease-out;
}

.record.collapsible, .array.collapsible, .map.collapsible {
    background-color: #ddd;
}

.array:before {
  padding-right: 2px;
  content: '[⫢]';
}
.map:before {
  padding-right: 2px;
  content: '🗺️';
}

.custom:before {
  padding-right: 10px;
  content: '\\00A0⇭';
}

.custom.collapsible {
  background-color: #eee;
}

.enum:before {
  padding-right: 6px;
  content: 'Ⓔ';
}

.record:before {
  padding-right: 6px;
  content: '{\\00A0}';
}
	
.long_timestamp-millis:before {
  padding-right: 2px;
  content: '🕛';
}

.int_date:before {
  padding-right: 2px;
  content: '📅';
}

.string:before {
  padding-right: 2px;
  content: '🔤';
}

.bytes_decimal:before {
  padding-right: 10px;
  content: '\\26A0';
}

.int:before {
  padding-right: 2px;
  content: '🔢';
}

.long:before {
  padding-right: 2px;
  content: '🔢';
}

.boolean:before {
  padding-right: 4px;
  content: 'Ⓑ';
}

.fixed:before {
  padding-right: 4px;
  content: 'Ⓕ';
}

.collapsible:after {
  content: '\\02795'; /* Unicode character for "plus" sign (+) */
  font-size: 13px;
  color: white;
  float: right;
  margin-left: 12px;
}

.active:after {
  content: "\\2796"; /* Unicode character for "minus" sign (-) */
}

table {
  border-collapse: collapse;
  word-wrap:break-word;
}

th {
  border-bottom: 2px solid #dddddd;
  padding: 2px;
  text-align: left;
  width: 30%;
}

td {
  padding: 2px;
  text-align: left;
  word-wrap:break-word;
  white-space: normal;
  width: 70%;
}

/* Create two unequal columns that floats next to each other */
.column {
  float: left;
}

.left {
  width: 35%;
}

.right {
  width: 65%;
}

#myTable:hover {
  cursor: pointer;
}

input {
  width: 90%;
  padding: 4px;
}

</style>
</head>
<body>
'''
body_start_col1 = '''<div class="row">
    <div id="left_coll" class ="column left">
        <input type="text" id="myInput" onkeyup="filterFunc()" placeholder="Search for names t:type p:parent">
'''

body_end_col1 = '''</div>
<div id="right_coll" class="column right">
'''

body_after_schema = '''
  </div>
</div>
'''

footer_part = '''
<script>
function toggleNode(node) {
    node.classList.toggle("active");
    var content = node.nextElementSibling;
    if (content.style.maxHeight == allHeights + "px"){
      content.style.maxHeight = "0px";
    } else {
      content.style.maxHeight = allHeights + "px";
    }
}

function goToNode(nodeId) {
    let pickNode = document.getElementById(nodeId);
    let target = pickNode;
    let goLoop = true;
    while (goLoop) {
        if (!pickNode.classList.contains('active')) {
            toggleNode(pickNode)
        } 

        if (pickNode.parentElement.id == 'right_coll') {
            goLoop = false;
        } else {
            pickNode = pickNode.parentElement.previousElementSibling;
        }
    }

    target.scrollIntoView({ behavior: "smooth", block: "start"});
}
// Source - https://stackoverflow.com/a
// Posted by Ahmed Tag Amer, modified by community. See post 'Timeline' for change history
// Retrieved 2026-01-20, License - CC BY-SA 4.0

var allHeights = 0;
var contents = document.getElementsByClassName("content");
var j;

for (j = 0; j < contents.length; j++) {
  var h = document.getElementsByClassName("content")[j].scrollHeight;
  allHeights += h;
}

var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    toggleNode(this);
  });
  if (!coll[i].classList.contains("with_no_children") && !coll[i].classList.contains("info")) {
    toggleNode(coll[i]);
  }
}

function openAll() {
    var coll = document.getElementsByClassName("collapsible");
    var i;
    for (i = 0; i < coll.length; i++) {
        if (!coll[i].classList.contains("info") && !coll[i].classList.contains('active')) {
          toggleNode(coll[i]);
        }
    }
}
function closeAll() {
    var coll = document.getElementsByClassName("collapsible");
    var i;
    for (i = 0; i < coll.length; i++) {
        if (coll[i].classList.contains("with_no_children") && coll[i].classList.contains('active')) {
          toggleNode(coll[i]);
        }
    }
}


function fuzzy(str, pattern) {
    var hay = str.toLowerCase(), i = 0, n = -1, l;
    pattern = pattern.toLowerCase();
    for (; l = pattern[i++] ;) if (!~(n = hay.indexOf(l, n + 1))) return false;
    return true;
}

function filterFunc() {
  var input, filter, ul, li, i, txtValue;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  ul = document.getElementById("myTable").children;
  for (i = 0; i < ul.length; i++) {
    li = ul[i];
    if (li) {
      txtValue = li.getAttribute("data-search");

      if (filter.includes("T:")) {
        txtValue += " t: " + li.getAttribute("data-search-type");
      }

      if (filter.includes("P:")) {
        txtValue += " p: " + li.getAttribute("data-search-parent");
      }

      if (fuzzy(txtValue, filter)) {
        li.style.display = "";
      } else {
        li.style.display = "none";
      }
    }
  }
  document.getElementById("myInput").focus();
}

function highlightNode(element) {
  node = document.getElementById(element.getAttribute("data-id-str"));
  node.classList.toggle("highlight");
}
</script>

</body>
</html>
'''

# classes

class Node:

    primitives = ['null', 'boolean', 'int', 'long', 'float', 'double', 'bytes', 'string', 'bytes_decimal', 'int_date', 'long_timestamp-millis']
    complex = ['enum', 'record', 'array', 'map', 'fixed']
    with_children = ['record', 'array', 'map']
    record = 'record'
    array = 'array'

    def __init__(self, name, namespace, description, node_type, nullable, default, details=None, parent = None):
        self.parent = parent
        self.name = name
        self.namespace = namespace 
        self.description = description
        self.details = details
        self.node_type = node_type
        self.nullable = nullable
        self.default = default
        self.children = []

    def parent_name(self):
        if self.parent:
            return self.parent.name
        
        return ""

    def add_children(self, node):
        if node.namespace == None:
            node.namespace = self.namespace

        node.parent = self
        self.children.append(node)

    def is_primitive(self):
        return self.node_type in self.primitives

    def is_custom(self, node_type):
        return not node_type in self.primitives and not node_type in self.complex

    def can_have_children(self, node_type):
        return node_type in self.with_children

    def printToHtmlList(self):
        base_html = '<ul id="myTable">\n'
        base_html_end = '</ul>\n'
        nodes = [];
        self.printToHtmlListInner(nodes)
        nodes.sort()
        list_body = ""
        for n in nodes:
            isCustom = self.is_custom(n[1])
            list_body += f"<li class=\"{n[1] if not isCustom else "custom" }\" onmouseout=\"highlightNode(this)\" onmouseover=\"highlightNode(this)\" onclick=\"goToNode(this.getAttribute('data-id-str'))\" data-id-str=\"{n[2]}_{n[0]}_{n[1]}\" data-search-parent=\"{n[2]}\" data-search-type=\"{n[1]}\" data-search=\"{n[0]}\">{n[0]}</li>\n"

        return base_html + list_body + base_html_end

    def printToHtmlListInner(self, nodes_list):
        nodes_list.append([self.name, self.node_type, self.parent_name()])
        for c in self.children:
            c.printToHtmlListInner(nodes_list)

    def printToHtml(self):
        hasNoChildren = not self.can_have_children(self.node_type)
        isCustom = self.is_custom(self.node_type)
        strTo = ""
        strTo = strTo + f"<button id=\"{self.parent_name()}_{self.name}_{self.node_type}\" class=\"collapsible{" with_no_children" if hasNoChildren else "" } {self.node_type if not isCustom else "custom" }\">{self.name}</button>\n"
        strTo = strTo + '<div class="content">\n'

        # pre behavior for complex types
        if not hasNoChildren:
            strTo = strTo + f"<button class=\"collapsible info\">info</button>\n"
            strTo = strTo + '<div class="content info">\n'

        strTo = strTo + '<table>'
        strTo = strTo +   "<tr>"
        strTo = strTo +     "<th>Description</th>"
        strTo = strTo +    f"<td>{self.description}</td>"
        strTo = strTo +   "</tr>"
        strTo = strTo +   "<tr>"
        strTo = strTo +     "<th>Type</th>"
        strTo = strTo +    f"<td>{self.node_type}</td>"
        strTo = strTo +   "</tr>"
        strTo = strTo +   "<tr>"
        strTo = strTo +     "<th>Namespace</th>"
        strTo = strTo +    f"<td>{self.namespace}</td>"
        strTo = strTo +   "</tr>"
        strTo = strTo +   "<tr>"
        strTo = strTo +     "<th>Nullability</th>"
        strTo = strTo +    f"<td>{"Nullable" if self.nullable else "Required"}</td>"
        strTo = strTo +   "</tr>"

        if self.node_type == 'record':
            strTo = strTo +   "<tr>"
            strTo = strTo +     "<th># Fildes</th>"
            strTo = strTo +    f"<td>{len(self.children)}</td>"
            strTo = strTo +   "</tr>"
            strTo = strTo + "</table>"
            strTo = strTo + '</div>'
            for child in self.children:
                strTo = strTo + child.printToHtml()

        elif self.node_type == 'array':
            strTo = strTo + "</table>"
            strTo = strTo + '</div>'
            for child in self.children:
                strTo = strTo + child.printToHtml()

        else:
            strTo = strTo +   "<tr>"
            strTo = strTo +     "<th>Default</th>"
            strTo = strTo +    f"<td>{self.default}</td>"
            strTo = strTo +   "</tr>"
            if self.details != None:
                strTo = strTo +   "<tr>"
                strTo = strTo +     "<th>Details</th>"
                strTo = strTo +    f"<td>{self.details}</td>"
                strTo = strTo +   "</tr>"
            strTo = strTo + "</table>"

        strTo = strTo + '</div>'
        return strTo

    def to_dict(self):
        out = self.__dict__

        if self.parent:
            out['parent'] = self.parent.name

        children = []
        if not self.is_primitive():
            for c in self.children:
                children.append(c.to_dict())

            out['children'] = children
        else:
            out['children'] = None
        return out

# functions

def make_header(name):
    return header_part_1 + "<title>" + name + "</title>\n" + header_part_2

def make_body_title(name, file_name):
    return "<h1>" + name + "</h1>\n" + "<p>" + file_name + "</p>\n"

def get_type(original_type):
    if type(original_type) is list:
        for t in original_type:
            if t != "null":
                if type(t) is str:
                    return t
                elif type(t) is dict:
                    if 'logicalType' in t:
                        return f"{t['type']}_{t['logicalType']}"
                    else:
                        return t['type']
                else:
                    pass

        return "ERROR"

    elif type(original_type) is dict:
        return original_type['type']

    else:
        return original_type

def is_nullable(original_type):
    if type(original_type) is list:
        return "null" in original_type

    return False

def avro_json_field_into_node(json):

    node_type = get_type(json["type"])
    root = Node(json["name"], json["namespace"] if "namespace" in json else None, json["doc"] if "doc" in json else "", node_type, is_nullable(json["type"]), json["default"] if "default" in json else None)

    if node_type.startswith("bytes"):
        details = ""
        for t in json["type"]:
            if t != "null":
                if type(t) is str:
                    return t
                elif type(t) is dict:
                    if 'logicalType' in t:
                        for key, value in t.items():
                            details += key + ': ' + str(value) + '; '

        root.details = details

    return root

def avro_json_into_node(json):
    root = avro_json_field_into_node(json)

    if root.node_type == 'record':
        fields = []

        if type(json['type']) is list:
            for t in json['type']:
                if type(t) is dict and t['type'] == 'record':
                    fields = t['fields']
        elif type(json['type']) is dict:
            fields = json['type']['fields']
        else:
            fields = json['fields']

        for field in fields:
            node = avro_json_into_node(field)
            root.add_children(node)

    elif root.node_type == 'array':
        if type(json['type']) is dict:
            items = json['type']['items']
            if type(items) is str:
                node = Node(root.name, root.namespace, "", items, is_nullable(json), None)
                root.add_children(node)
            else:
                node = avro_json_into_node(items)
                root.add_children(node)
        elif type(json['type']) is list:
            for t in json['type']:
                if type(t) is dict and t['type'] == 'array':
                    items = t['items']
                    if type(items) is str:
                        node = Node(root.name, root.namespace, "", items, is_nullable(json), None)
                        root.add_children(node)
                    else:
                        node = avro_json_into_node(items)
                        root.add_children(node)


    return root

# main

if __name__ == "__main__":

    page = ""
    for a in sys.argv[1:]:
        loop_page = ""
        file_name = os.path.basename(a)

        with open(a, 'r') as file:
            data = json.load(file)
            node = avro_json_into_node(data)

            loop_page = loop_page + make_header(node.name)
            loop_page = loop_page + make_body_title(node.name, file_name)
            loop_page = loop_page + body_start_col1
            loop_page = loop_page + node.printToHtmlList()
            loop_page = loop_page + body_end_col1
            loop_page = loop_page + node.printToHtml()
            loop_page = loop_page + body_after_schema
            loop_page = loop_page + footer_part

            if not DRY_RUN:
                with open(f"{Path(file_name).stem}.html", "w", encoding="utf-8") as f:
                    f.write(loop_page)

            page = page + loop_page

            if DEBUG:
                print(json.dumps(node.to_dict()))
