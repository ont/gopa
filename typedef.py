from parsy import string_from, string, seq, regex, generate
from base import matching, sp, sp_no_nl, pd, sep, ident, ident_ctx
from containers import TypeSlice, TypeMap, TypeStruct, StructField,\
    TypeRef, TypePtr, TypeBase, TypeChan, Decl, TypeFunc

# basic simple types
type_base = string_from(
    "error",
    "bool",
    "string",
    "int", "int8", "int16", "int32", "int64",
    "uint", "uint8", "uint16", "uint32", "uint64", "uintptr",
    "byte", "rune",
    "float32", "float64",
    "complex64", "complex128"
).map(TypeBase)

# complex type: slice
type_slice = seq(
    len=string("[") >> regex(r'\d+').map(int).optional() << string("]"),
    value=type_base,  # TODO: replace with general type
).combine_dict(TypeSlice)

# complex type: map
type_map = seq(
    key=string("map") >> matching("[]"),  # TODO: parse type
    value=type_base,  # TODO: replace with general type
).combine_dict(TypeMap)


# optional pointer (TypePtr) to something
def optional_ptr_to(parser):
    @generate
    def new_parser():
        ptr = yield string("*").optional()
        content = yield parser
        return TypePtr(to=content) if ptr else content
    return new_parser


# complex type: struct
@generate
def type_struct():
    yield string("struct") + pd + string("{") + pd
    anonymous_decl = optional_ptr_to(type_base | type_ref)

    # struct field parser (later "type" and "tag" fields will be repacked into StructField struct)
    struct_field = seq(
        decl=(decl | anonymous_decl) << sep,
        tag=(matching('``') << sep).optional(),
    )

    fields = yield struct_field.many()  # NOTE: recursive to decl which reference to type_struct
    yield string("}")

    return TypeStruct(
        anonymous=[
            StructField(name=None, type=x['decl'], tag=x['tag'])
            for x in fields if type(x['decl']) is not Decl
        ],
        fields=[
            StructField(name=x['decl'].name, type=x['decl'].type, tag=x['tag'])
            for x in fields if type(x['decl']) is Decl
        ]
    )


# complex type: channel
@generate
def type_chan():
    read = yield string("<-").optional().map(bool)
    yield string("chan")
    write = yield string("<-").optional().map(bool) << sp
    typ = yield type_def
    return TypeChan(read, write, typ)


# complex type: callback function (receiver part and name are not allowed)
@generate
def type_func():
    yield string("func") + pd
    args = yield func_params << pd
    result = yield (func_params | type_def).optional() << pd
    return TypeFunc(args=args, result=result)


# reference to type (i.e. name of type `MyAwesomeStruct`, `MyCustomMap`...)
type_ref = ident_ctx.combine_dict(TypeRef)

# type definition - all possible variants of type constructions: callbacks,
# structs, maps, slices, simple types...
type_def = optional_ptr_to(type_func | type_struct | type_map | type_slice | type_chan | type_base | type_ref)

# declaration of something (variable, new type) - name + type definition
decl = seq(
    name=ident << sp_no_nl,
    type=type_def,
).combine_dict(Decl)

# universal container for function arguments and returned values
func_params = \
    string("(") + pd >> \
    ((decl | type_def) << (pd + string(",") + pd).optional()).many() \
    << pd + string(")")


if __name__ == "__main__":
    from test_utils import T

    r = type_slice.parse("[]int")
    assert r.len is None
    assert r.value.name == "int"

    r = type_slice.parse("[10]string")
    assert r.len == 10
    assert r.value.name == "string"

    r = type_map.parse("map[int8]bool")
    assert r.key == "int8"
    assert r.value.name == "bool"

    r = decl.parse("""MyStruct struct{
        SomeRef `some tags`
        callback func(bbb *int) ccc `some_valid:"tag"`
    }""")
    print(r)

    t = T(decl)
    assert t.must_parse("MyStruct struct{ int; *int ; SomeRef; aaa.SomeAAA; some string; name struct{ fname string ; lname string } }")
    assert t.must_parse("callback func(bbb *int) ccc")
    assert t.must_parse("""MyStruct struct{
        SomeRef
        callback func(bbb *int) ccc
    }""")
    assert t.must_parse("""MyStruct struct{
        SomeRef `some tags`
        callback func(bbb *int) ccc `some_valid:"tag"`
    }""")
    assert t.must_parse("c *chan<- int""")

    t = T(type_func)
    assert t.must_parse("func(a *AAA) error")
    assert t.must_parse("func()")
    assert t.must_parse("func() error")
    assert t.must_parse("func(int, b string) *error")
    assert t.must_parse("func(int, b string) (err *error)")
