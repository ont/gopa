from parsy import generate, seq, string
from base import pd, sp, ident, matching, lcmt, commented
from values import vstr, decl_init
from typedef import decl, type_ref, type_def, func_params, optional_ptr_to
from containers import FuncReceiver, DeclFunc, DeclBlock, Package


# function definition
# TODO: move from typedef.py
@generate
def decl_func():
    # function part: receiver
    func_receiver = seq(
        name=pd >> string("(") >> pd >> ident << sp,
        type=optional_ptr_to(type_ref) << pd + string(")"),  # TODO: bad: non-local (package!=None) receivers allowed here
    ).combine_dict(FuncReceiver)

    yield string("func")
    receiver = yield func_receiver.optional()

    yield sp if not receiver else pd  # between func and name only space allowed
    name = yield ident << pd

    args = yield func_params << pd
    result = yield (func_params | type_def).optional() << pd
    body = yield matching('{}').optional()
    return DeclFunc(receiver, name, args, result, body)


def decl_block(name, decl_parser):
    @generate
    def parser():
        yield string(name) + pd
        single_decl = yield decl_parser.optional()
        if single_decl:
            return DeclBlock(name, [single_decl])

        yield string("(") + pd
        decls = yield ((decl_parser | lcmt) << pd).many() << pd << string(")")
        return DeclBlock(name, decls)

    return parser


decl_var = commented(decl_block("var", decl_init))
decl_const = commented(decl_block("const", decl_init))
decl_type = commented(decl_block("type", decl))
decl_import = commented(decl_block("import", vstr))
decl_func = commented(decl_func)


@generate
def decl_file():
    package = commented((string("package") >> sp >> ident << pd).map(Package))
    package = yield package
    print(package)

    decls = yield ((decl_func | decl_type | decl_var | decl_const | decl_import | lcmt) << pd).many()
    return [package, decls]


if __name__ == "__main__":
    from test_utils import T

    t = T(decl_func)
    assert t.must_parse("func ( a *AAA ) aaa( a *int, string , b *SomeStruct, c *kkk.KKK ) ( bool , error ) { zzz }")
    assert t.must_parse("func aaa() { zzz }")

    t = T(decl_var)
    assert t.must_parse("var var1 int = 4")
    assert t.must_parse("var (var1 int = fff(4))")
    assert t.must_parse("var var1 int=fff(4)")
    assert t.must_parse("var var1 = 4")
    assert t.must_parse("var var1 = fff(4)")
    assert t.must_parse("var var1=fff(4)")
    assert t.must_parse("var var1 AAA= AAA{1, 2, 3}")

    t = T(decl_var)
    assert t.must_parse("""var(
        var1 AAA= AAA{1, 2, 3}
        var2 int = 4
    )""")

    t = T(decl_const)
    assert t.must_parse("const(var1 AAA= AAA{1, 2, 3})")

    t = T(decl_type)
    assert t.must_parse("type(ttt int)")

    t = T(decl_import)
    assert t.must_parse('import "some.com/test/repo"')
    assert t.must_parse('''import (
       "some.com/test/repo"
       "another.com/test/module"
    )''')

    code = open("test_go_files/main.go").read()
    r = decl_file.parse(code)
    import pprint
    pprint.pprint(r)
