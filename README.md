# Metapype for EML

#### A lightweight metadata generator for the Ecological Metadata Language

[![Build Status](https://travis-ci.org/PASTAplus/metapype-eml.svg?branch=master)](https://travis-ci.org/PASTAplus/metapype-eml)


<hr />

Metapype is a Python 3 library for building, saving, and exporting scientific
metadata using a flexible metadata content model in a hierarchical tree-like
structure. Metapype only provides the primitives (as a Python application
programmable interface) for operating on metadata; it is expected that client
applications will use the Metapype API to build more robust and user friendly
applications.

This version of Metapype is designed to reflect the content structure of the
Ecological Metadata Language (EML) XML schema; it is not, however, locked
into a specific version of EML. As such, Metapype can support multiple
versions of metadata standards.

Metapype is divided into a metadata content model and a set of validation
rules that enforce model compliance to a specific metadata standard, including
its version. Compliance only implies that the metadata model conforms to the
syntactical requirements of the metadata standard, but not necessarily to
semantic requirements, like adherence to a particular controlled vocabulary
for keywords or requiring additional descriptive content within the model when
the standard does not require it. As an extension to the validation component
of Metapype, there is also an evaluation process that ensures the model
conforms to practices and requirements beyond the metadata standard.

#### Metadata Content Model

The metadata content model is designed as an [ordered
tree](https://en.wikipedia.org/wiki/Tree_(graph_theory)#Ordered_tree). Node
children follow a rule-based order and can be reached via directed edges from
their parent node. Each child node can have only one parent, which is
represented by a single reverse edge from the child to its parent; only the
root node may be without a "true" parent.

Metapype uses a `Node` class for modeling elements of the EML XML schema. Node
instances must be constructed with a `name` parameter, which corresponds to
the element name as declared in the schema\*. Node edges for either parent or
children are constructed of the node's respective address in memory. Node
instances capture the primary characteristics of the corresponding EML element
being modeled, including XML attributes, content, and sub-elements of complex
types. Attributes of a node instance may be accessed through setters and
getters (see the Node API).

<p align="center"><img src="https://raw.githubusercontent.com/PASTAplus/metapype-eml/master/docs/node.png" /></p>

A compliant EML 2.1.1 metadata content model tree is found in the following
diagram (this diagram represents an instance of a Metapype tree model):

<p align="center"><img src="https://raw.githubusercontent.com/PASTAplus/metapype-eml/master/docs/eml_model.png"/></p>

#### Metadata Validation Rules

Metadata validation is critical to ensure that the working model complies with
all requirements and constraints declared within the metadata standard, and in
this case, the EML XML schema. A valid metadata content model implies that
every node of the tree complies with the syntax of the metadata standard being
modeled. Metapype can process the model instance through a series of
*validation* rules to ensure compliance with the EML XML schema. A critical
exception is raised if any node within the model fails validation during
processing.

A metadata standard validation rule is a codified set of constraints that
follow the same (or similar) requirements that are declared within the
corresponding metadata standard. In this version of Metapype (for EML), these
rules are written in accordance with the element definitions as declared in
the EML XML schema and are written as unique Python functions. Each rule
enforces content requirements, the presence of XML attributes, and if a
"complex" XML element is being modeled, the sequence or choice of descendant
elements, including descendant cardinality (rules do not, however, support
all XML schema constructs such as `groups` or `all`). Rule functions implicitly
return `None` unless an exception occurs during the evaluation process;
exceptions are of the class `exceptions.MetapypeRuleError`.

Rules are divided into three parts for validating the components of an EML
element: 1) element specific constraints, 2) attributes, and 3) sub-
elements complex types, if present.

Element specific constraints, if any, are written as Python conditional
statements (e.g., `if`, `else`, or `elif`) and provide a "fail fast" method
for node validation. Element specific constraints are best used for enforcing
content data types, enumerations, or other detailed constraints declared in
the XML schema. Conditional statements may be chained together for validating
multiple or different constraints imposed by the corresponding element.

The rule section for XML attributes is represented as a Python dictionary, where
attribute names are the "keys" and their optional or required status the
"values". Attributes, as defined in a node instance, are validated against
those of the rule's attribute dictionary using a function called
`validate._attributes`. Errors during this step may result from the
presence of illegal attributes or attributes that are required, but missing
from the node. The literal value of node attributes are not evaluated during
this validation phase, but can be codified as a node-specific constraint
described earlier (see example below).

The rule section for sub-element validation is declared as a nested Python
list that contains the children of the node instance. This data structure is a
"list-of-lists": the outer list specifies the sequence in which children may
occur, while the inner list(s) specifies what child node (or children, if a
choice) may occur at the current location in the sequence. The cardinality
(i.e., minimum and maximum occurrence) of each child node is always set to the
last two positions of the inner list, thereby making the values accessible
through list slicing (i.e., `rule[-2:]`). The "list-of-lists" data structure
is passed to a function, called `validate._children`, that
iterates through both the rule-based list and the list of children from the
node instance to validate compliance as specified in the given rule.
Validation failure at this point indicates that the node contains illegal
children, children occurring in the wrong sequence, or children occurring too
few or too many times (a cardinality violation).

The following is an example of the "access" rule as codified in Python:

```Python
def access_rule(node: Node):
    # Specific constraint section
    if 'order' in node.attributes:
        allowed = ['allowFirst', 'denyFirst']
        if node.attributes['order'] not in allowed:
            msg = '"{0}:order" attribute must be one of "{1}"'.format(node.name, allowed)
            raise MetapypeRuleError(msg)

    # Attribute section
    attributes = {
        'id': OPTIONAL,
        'system': OPTIONAL,
        'scope': OPTIONAL,
        'order': OPTIONAL,
        'authSystem': REQUIRED
    }
    _attributes(attributes, node)

    # Children section
    children = [
        ['allow', 'deny', 1, INFINITY]
    ]
    _children(children, node)
```

This `access_rule` example demonstrates the use of all three rule sections: 1)
The element specific constraints validate the value of a specific node attribute.
In this case, the `order` attribute, if defined, must have a value of either
`allowFirst` or `denyFirst` only. 2) The XML attributes rule defines the
set of acceptable attributes to be `id`, `system`, `order`, and `authSystem`;
all defined attributes are *optional* with the exception of `authSystem`,
which is *required*. And finally, 3) the sub-element children section defines a
single node choice of either an `allow` or `deny` child, along with the
cardinality of 1 to infinity.

### Metadata Evaluation Rules

Similar to the process used for validation of a model instance to the EML XML
schema, Metapype also supports a process to *evaluate* a model instance
against rules that are more semantic in nature. Evaluation rules differ from
validation rules in that they do not result in an exception, but rather
evaluate one or more nodes to somewhat "soft" requirements (e.g., the number
of active words in a title or that an `individaulName` node has both `surName`
**AND** `givenName` children, even though the EML XML schema does not require
both) and only return information about the evaluation outcome for a node.
And because evaluation rules do not have to test every node in the model
instance, there can be fewer rules that need to be executed.

Evaluation rules are written as Python conditional statements (e.g., `if`,
`else`, or `elif`), but do not follow any typical pattern because of the wide
difference in the constraints declared for various nodes. Evaluation rules
simply return a Unicode string value with an explanation of the evaluation
result, which could be the string `PASS` if the evaluation is acceptable or a
recommendation for improving the node content. The user accessible function
`evaluate.tree` requires an empty Python dictionary to be passed as a
parameter. This dictionary is recursively populated with evaluation results
from the `evaluate.node` function and assigned to the `node_id` key.

As an example, the following evaluation rule inspects the title node:

```Python
def _title_rule(node: Node) -> str:
    evaluation = PASS
    title = node.content
    if title is not None:
        length = len(title.split(' '))
        if length < 10:
            _ = ('"{0}" is too short, should '
                 'have at least 10 words')
            evaluation = _.format(title)
    return evaluation
```

The resulting dictionary from running the `evaluate.tree` function returns
the following:

```Text
{
    140101084713592: '(title) "Green sea turtle counts: Tortuga Island 20017" is too short, should have at least 10 words',
    140101084713704: '(individualName) Should have both a "givenName" and "surName"',
    140101084713872: '(individualName) PASS'
}
```


### Using Metapype for EML

The Metapype Python API can be used to generate metadata that is compliant
with the Ecological Metadata Language standard. Using Metapype for this
purpose is typically separated into two steps: first, build a Metapype model
instance beginning with an "eml" node as the *root* node, followed by
validating the model instance to ensure it complies with the EML standard.
Validation can be performed on a single node using the `validate.node`
function or on an entire model tree beginning with a specified *root* node
using the `validate.tree` function (to validate for EML compliance, the model
root node as defined by  the "eml" name should be passed).

The following code example demonstrates these two steps:

```Python
import logging

from metapype.eml.exceptions import MetapypeRuleError
import metapype.eml.names as names
import metapype.eml.validate as validate
from metapype.model.node import Node

def main():

    eml = Node(names.EML)
    eml.add_attribute('packageId', 'edi.23.1')
    eml.add_attribute('system', 'metapype')

    access = Node(names.ACCESS, parent=eml)
    access.add_attribute('authSystem', 'pasta')
    access.add_attribute('order', 'allowFirst')
    eml.add_child(access)

    allow = Node(names.ALLOW, parent=access)
    access.add_child(allow)

    principal = Node(names.PRINCIPAL, parent=allow)
    principal.content = 'uid=gaucho,o=EDI,dc=edirepository,dc=org'
    allow.add_child(principal)

    permission = Node(names.PERMISSION, parent=allow)
    permission.content = 'all'
    allow.add_child(permission)

    dataset = Node(names.DATASET, parent=eml)
    eml.add_child(dataset)

    title = Node(names.TITLE, parent=dataset)
    title.content = 'Green sea turtle counts: Tortuga Island 20017'
    dataset.add_child(title)

    creator = Node(names.CREATOR, parent=dataset)
    dataset.add_child(creator)

    individualName_creator = Node(names.INDIVIDUALNAME, parent=creator)
    creator.add_child(individualName_creator)

    surName_creator = Node(names.SURNAME, parent=individualName_creator)
    surName_creator.content = 'Gaucho'
    individualName_creator.add_child(surName_creator)

    contact = Node(names.CONTACT, parent=dataset)
    dataset.add_child(contact)

    individualName_contact = Node(names.INDIVIDUALNAME, parent=contact)
    contact.add_child(individualName_contact)

    surName_contact = Node(names.SURNAME, parent=individualName_contact)
    surName_contact.content = 'Gaucho'
    individualName_contact.add_child(surName_contact)

    try:
        validate.tree(eml)
    except MetapypeRuleError as e:
        logging.error(e)
        
    return 0

if __name__ == "__main__":
    main()

``` 

In the above example, the "eml" node is created and used as the anchor node for the root of the model tree. Sub-element descendant nodes are created and then added to higher-level nodes as children. Although this example is quite small, it does produce metadata that conforms to EML 2.1.1 standard.

Metapype can convert a model instance tree to either EML-specific *XML* or to
*JSON* Unicode strings by using either the `export.to_xml` or `io.to_json`
functions, respectively. The string value can then be saved directly to the file
system or passed to other functions for additional processing. Metapype can also
convert a Metapype valid JSON Unicode string back into a model instance tree by
using the `io.from_json` function. This is important for saving incomplete or
sub-tree instances to the file system (e.g., for reusable model components),
which can be reloaded at a later time. The following code example demonstrates
using both the *XML* and *JSON* functions:

```Python
import json
import metapype.eml.export
import metapype.eml.names as names
import metapype.model.metapype_io
from metapype.model.node import Node

# Write EML XML
eml = Node(names.EML)
eml.add_attribute('packageId', 'edi.23.1')
eml.add_attribute('system', 'metapype')

xml_str = metapype.eml.export.to_xml(eml)
with open('test_eml.xml', 'w') as f:
    f.write(xml_str)

# Write JSON
json_str = metapype.model.metapype_io.to_json(eml)
with open('test_eml.json', 'w') as f:
    f.write(json_str)

# Read JSON
with open('test_eml.json', 'r') as f:
    json_str = f.read()
eml = metapype.model.metapype_io.from_json(json.loads(json_str))

```

<hr/>

\*Actually, the metadata content model may contain any hierarchical content that
can be entered into the existing Node data structure, but will not validate as
an EML metadata content model either at the node or the tree level.
