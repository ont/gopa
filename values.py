from parsy import regex, seq, string
from base import matching, word, ident, ident_ctx, commented, pd
from typedef import type_def
from containers import DeclInit

vint = regex(r"\d+")
vfloat = regex(r"\d+\.\d+")  # TODO: better parsing
vstr = matching('""', escaping=True)
vfunc_call = seq(
    name=ident_ctx,
    args=matching('()'),
)
vtype_init = seq(
    type=type_def,
    args=matching('{}'),
)

# value declaration (4.0, "some", func(...), List{1,2,3}, ...)
value = vfunc_call | vtype_init | vstr | vfloat | vint | word


# declaration of initialization: {name} {type} = {initializer}
decl_init = commented(seq(
    name=ident << pd,
    type=type_def.optional() << pd << string("=") << pd,
    value=value,
).combine_dict(DeclInit))


if __name__ == "__main__":
    from test_utils import T

    t = T(value)

    assert t.must_parse("4.0")
    assert t.must_parse("4")
    assert t.must_parse("fff(4, 3, 7, aaa(), Struct{})")
    assert t.must_parse("ctx.fff(4, 3, 7, aaa(), Struct{})")
    assert t.must_parse("Struct{1,2,3,4}")
    assert t.must_parse("""Struct{
        field: 123,
        field2: Struct2{1,2,3},
    }""")
    assert t.must_parse('"simple string"')
    assert t.must_parse('"escaped \\" string"')
