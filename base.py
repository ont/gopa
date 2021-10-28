from containers import Comment
from parsy import seq, string, regex, Parser, Result, generate


def matching(pair, escaping=False):
    s, e = pair[0], pair[1]

    @Parser
    def matching_parser(stream, index):
        if index > len(stream) - 1 or stream[index] != s:
            return Result.failure(index, "matching " + pair)

        res, cnt = "", 1
        for i in range(index + 1, len(stream)):
            # if target symbol is escaped, skip it
            if stream[i] in (s, e) and escaping:
                if stream[i - 1] == "\\":
                    continue

            if stream[i] == e:
                cnt -= 1
            elif stream[i] == s:
                cnt += 1

            if cnt == 0:
                return Result.success(i+1, res)

            res += stream[i]

        # can't find closing pair, failure
        return Result.failure(index, "matching " + pair)

    return matching_parser


ident = regex('[a-zA-Z][a-zA-Z0-9_]*')
ident_ctx = seq(
    package=(ident << string(".")).optional(),
    name=ident,
)
word = regex(r'\S+')
sp = regex(r'\s+')           # spacer
sp_no_nl = regex(r'[ \t]+')  # non breakable spacer
pd = regex(r'\s*')           # padding (optional spacer)
sep = regex(r'\s*[;]?\s*')   # separator (spacer which eats ";" characters)

lcmt = regex(r'//.*\n').map(lambda x: Comment(x.strip()))


def commented(parser):
    @generate
    def new_parser():
        comments = yield (lcmt << pd).many().optional() << pd
        res = yield parser
        res.comments = [x.text for x in comments]
        return res

    return new_parser
