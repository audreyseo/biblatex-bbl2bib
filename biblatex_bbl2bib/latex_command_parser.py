from lark import Lark, Tree, Token

grammar = r"""
?start: command

?command: SLASH identifier
        | SLASH identifier list_of_args

?list_of_args: ("{" arg_content "}")+
#             | "{" arg_content "}" list_of_args

?arg_content: NOT_RBRACE?
            | key_list
            | list_of_args
           
?key_list: key ("," key)*
        #  | key "," key_list

?key: identifier "=" arg_content

?identifier: IDENT

IDENT: /[a-zA-Z]+/
SLASH: /\\/
COMMENT: "%" /[^\n]*/ NEWLINE
NEWLINE: "\n"
NOT_RBRACE: /[^}]+/



%import common.WS

%ignore WS
%ignore COMMENT
%ignore NEWLINE
"""

command_parser = Lark(grammar, parser="earley")

def parse_key(k):
    assert(isinstance(k, Tree))
    assert(k.data == "key")
    return str(k.children[0]), str(k.children[1])

def parse_key_list(keylist):
    assert(isinstance(keylist, Tree))
    assert(keylist.data == "key_list")
    keys = {}
    for c in keylist.children:
        k, v = parse_key(c)
        keys[k] = v
        pass
    return keys
        

def parse_list_of_args(listofargs):
    args = []
    for c in listofargs.children:
        print(c)
        if isinstance(c, Token):
            args.append(str(c))
            pass
        elif isinstance(c, Tree):
            if c.data == "list_of_args":
                innerargs = parse_list_of_args(c)
                if not innerargs:
                    args.append("")
                    pass
                else:
                    args.append({
                        "args": innerargs
                    })
                    pass
                pass
            elif c.data == "key_list":
                args.append(parse_key_list(c))
                pass
            elif c.data == "key":
                k, v = parse_key(c)
                args.append({
                    k: v
                })
        pass
    return args

def parse_command(com):
    tree = command_parser.parse(com)
    print(tree)
    print("Data:", tree.data)
    print("Children:", tree.children)
    parsed = {}
    if len(tree.children) >= 2:
        # the command's name
        parsed["name"] = str(tree.children[1])
        if len(tree.children) == 3:
            argslist = tree.children[2]
            assert(isinstance(argslist, Tree))
            parsed["args"] = parse_list_of_args(argslist)
            # for c in argslist.children:
            #     print(c)
            #     if isinstance(c, Token):
            #         parsed["args"].append(str(c))
            #         pass
            #     elif isinstance(c, Tree):
                    
            #         pass
            #     pass
            pass
        pass
    print(parsed)
        
        


if __name__ == '__main__':
    location_example = r"""\list{location}{1}{%
        {Berlin, Heidelberg}%
      }"""
    
    author_example = r"""\name{author}{1}{}{%
        {{hash=448045e4531c99f2a2552ae1affe65fe}{%
           family={Appel},
           familyi={A\bibinitperiod},
           given={Andrew\bibnamedelima W.},
           giveni={A\bibinitperiod\bibinitdelim W\bibinitperiod}}}%
      }"""
      
    endverb_example = r"""\endverb"""
    # print(command_parser.parse(location_example))
    
    # print(command_parser.parse(author_example))
    parse_command(endverb_example)
    parse_command(location_example)
    parse_command(author_example)
    
    
    