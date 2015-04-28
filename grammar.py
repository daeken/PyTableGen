#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CAVEAT UTILITOR
#
# This file was automatically generated by Grako.
#
#    https://pypi.python.org/pypi/grako/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.


from __future__ import print_function, division, absolute_import, unicode_literals
from grako.parsing import graken, Parser


__version__ = (2015, 4, 28, 19, 40, 35, 1)

__all__ = [
    'grammarParser',
    'grammarSemantics',
    'main'
]


class grammarParser(Parser):
    def __init__(self, whitespace=None, nameguard=True, **kwargs):
        super(grammarParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=None,
            eol_comments_re=None,
            **kwargs
        )

    @graken()
    def _tokInteger_(self):
        with self._choice():
            with self._option():
                self._decimalInteger_()
            with self._option():
                self._hexInteger_()
            with self._option():
                self._binInteger_()
            self._error('no available options')

    @graken()
    def _decimalInteger_(self):
        with self._optional():
            with self._choice():
                with self._option():
                    self._token('+')
                with self._option():
                    self._token('-')
                self._error('expecting one of: + -')
        self._pattern(r'[0-9]+')

    @graken()
    def _hexInteger_(self):
        self._token('0x')
        self._pattern(r'[0-9a-fA-F]+')
        self.ast['@'] = self.last_node

    @graken()
    def _binInteger_(self):
        self._token('0b')
        self._pattern(r'[01]+')
        self.ast['@'] = self.last_node

    @graken()
    def _tokIdentifier_(self):
        self._pattern(r'[0-9]*[a-zA-Z_][a-zA-Z_0-9]*')

    @graken()
    def _tokVarName_(self):
        self._pattern(r'\$[a-zA-Z_][a-zA-Z_0-9]*')

    @graken()
    def _ESC_(self):
        with self._choice():
            with self._option():
                self._pattern(r'\\[\'"\\nrtbfv]')
            with self._option():
                self._pattern(r'\\u[a-fA-F0-9]{4}')
            self._error('expecting one of: \\\\[\'"\\\\nrtbfv] \\\\u[a-fA-F0-9]{4}')

    @graken()
    def _tokString_(self):
        self._token('"')

        def block1():
            with self._choice():
                with self._option():
                    self._pattern(r'[^"\n\\]')
                with self._option():
                    self._ESC_()
                self._error('expecting one of: [^"\\n\\\\]')
        self._closure(block1)
        self.ast['@'] = self.last_node
        self._token('"')

    @graken()
    def _tokCodeFragment_(self):
        self._pattern(r'\[\{.*?\]\}')

    @graken()
    def _includeDirective_(self):
        self._token('include')
        self._tokString_()

    @graken()
    def _tableGenFile_(self):

        def block0():
            self._object_()
        self._closure(block0)
        self._check_eof()

    @graken()
    def _object_(self):
        with self._choice():
            with self._option():
                self._tclass_()
            with self._option():
                self._tdef_()
            with self._option():
                self._defm_()
            with self._option():
                self._let_()
            with self._option():
                self._multiClass_()
            with self._option():
                self._foreach_()
            self._error('no available options')

    @graken()
    def _tclass_(self):
        self._token('class')
        self._tokIdentifier_()
        self.ast['name'] = self.last_node
        with self._optional():
            self._templateArgList_()
            self.ast['args'] = self.last_node
        self._baseClassList_()
        self.ast['bases'] = self.last_node
        self._body_()
        self.ast['body'] = self.last_node

        self.ast._define(
            ['name', 'args', 'bases', 'body'],
            []
        )

    @graken()
    def _mdecl_(self):
        self._token(',')
        self._declaration_()
        self.ast['@'] = self.last_node

    @graken()
    def _templateArgList_(self):
        self._token('<')
        with self._group():
            self._declaration_()

            def block1():
                self._mdecl_()
            self._closure(block1)
        self.ast['@'] = self.last_node
        self._token('>')

    @graken()
    def _defaultValue_(self):
        with self._optional():
            self._token('=')
            self._value_()
            self.ast['@'] = self.last_node

    @graken()
    def _declaration_(self):
        self._type_()
        self.ast['type'] = self.last_node
        self._tokIdentifier_()
        self.ast['name'] = self.last_node
        self._defaultValue_()
        self.ast['value'] = self.last_node

        self.ast._define(
            ['type', 'name', 'value'],
            []
        )

    @graken()
    def _type_(self):
        with self._choice():
            with self._option():
                self._token('string')
            with self._option():
                self._token('code')
            with self._option():
                self._token('bit')
            with self._option():
                self._token('int')
            with self._option():
                self._token('dag')
            with self._option():
                self._token('bits')
                self._token('<')
                self._tokInteger_()
                self._token('>')
            with self._option():
                self._listType_()
            with self._option():
                self._classID_()
            self._error('expecting one of: bit code dag int string')

    @graken()
    def _classID_(self):
        self._tokIdentifier_()

    @graken()
    def _listType_(self):
        self._token('list')
        self._token('<')
        self._type_()
        self.ast['type'] = self.last_node
        self._token('>')

        self.ast._define(
            ['type'],
            []
        )

    @graken()
    def _value_(self):
        self._simpleValue_()
        self.ast['value'] = self.last_node

        def block1():
            self._valueSuffix_()
            self.ast['suffix'] = self.last_node
        self._closure(block1)

        self.ast._define(
            ['value', 'suffix'],
            []
        )

    @graken()
    def _valueSuffix_(self):
        with self._choice():
            with self._option():
                self._token('{')
                self._rangeList_()
                self._token('}')
            with self._option():
                self._token('[')
                self._rangeList_()
                self._token(']')
            with self._option():
                self._token('.')
                self._tokIdentifier_()
            self._error('no available options')

    @graken()
    def _rangeList_(self):
        self._rangePiece_()

        def block0():
            self._token(',')
            self._rangePiece_()
        self._closure(block0)

    @graken()
    def _rangePiece_(self):
        with self._choice():
            with self._option():
                self._tokInteger_()
            with self._option():
                self._tokInteger_()
                self._token('-')
                self._tokInteger_()
            with self._option():
                self._tokInteger_()
                self._tokInteger_()
            self._error('no available options')

    @graken()
    def _stringJoin_(self):

        def block0():
            self._tokString_()
        self._positive_closure(block0)

    @graken()
    def _simpleValue_(self):
        with self._choice():
            with self._option():
                self._tokIdentifier_()
            with self._option():
                self._tokInteger_()
            with self._option():
                self._stringJoin_()
            with self._option():
                self._tokCodeFragment_()
            with self._option():
                self._token('?')
            with self._option():
                self._token('{')
                self._valueList_()
                self._token('}')
            with self._option():
                self._classID_()
                self._token('<')
                self._valueListNE_()
                self._token('>')
            with self._option():
                self._simpleList_()
            with self._option():
                self._token('(')
                self._dagArg_()
                self._dagArgList_()
                self._token(')')
            with self._option():
                self._bangValue_()
            self._error('expecting one of: ?')

    @graken()
    def _simpleList_(self):
        self._token('[')
        self._valueList_()
        self.ast['values'] = self.last_node
        self._token(']')
        with self._optional():
            self._token('<')
            self._type_()
            self.ast['type'] = self.last_node
            self._token('>')

        self.ast._define(
            ['values', 'type'],
            []
        )

    @graken()
    def _valueList_(self):
        with self._optional():
            self._valueListNE_()

    @graken()
    def _mvalue_(self):
        self._token(',')
        self._value_()
        self.ast['@'] = self.last_node

    @graken()
    def _valueListNE_(self):
        self._value_()

        def block0():
            self._mvalue_()
        self._closure(block0)

    @graken()
    def _marg_(self):
        self._token(',')
        self._dagArg_()
        self.ast['@'] = self.last_node

    @graken()
    def _dagArgList_(self):
        self._dagArg_()

        def block0():
            self._marg_()
        self._closure(block0)

    @graken()
    def _dagArg_(self):
        with self._choice():
            with self._option():
                self._value_()
                self.ast['value'] = self.last_node
                with self._optional():
                    self._token(':')
                    self._tokVarName_()
                    self.ast['name'] = self.last_node
            with self._option():
                self._tokVarName_()
                self.ast['name'] = self.last_node
            self._error('no available options')

        self.ast._define(
            ['value', 'name'],
            []
        )

    @graken()
    def _bangOperator_(self):
        with self._choice():
            with self._option():
                self._token('!eq')
            with self._option():
                self._token('!if')
            with self._option():
                self._token('!head')
            with self._option():
                self._token('!tail')
            with self._option():
                self._token('!con')
            with self._option():
                self._token('!add')
            with self._option():
                self._token('!shl')
            with self._option():
                self._token('!sra')
            with self._option():
                self._token('!srl')
            with self._option():
                self._token('!and')
            with self._option():
                self._token('!cast')
            with self._option():
                self._token('!empty')
            with self._option():
                self._token('!subst')
            with self._option():
                self._token('!foreach')
            with self._option():
                self._token('!listconcat')
            with self._option():
                self._token('!strconcat')
            self._error('expecting one of: !add !and !cast !con !empty !eq !foreach !head !if !listconcat !shl !sra !srl !strconcat !subst !tail')

    @graken()
    def _bangValue_(self):
        self._bangOperator_()
        self.ast['operator'] = self.last_node
        with self._optional():
            self._token('<')
            self._type_()
            self.ast['type'] = self.last_node
            self._token('>')
        self._token('(')
        self._valueListNE_()
        self.ast['args'] = self.last_node
        self._token(')')

        self.ast._define(
            ['operator', 'type', 'args'],
            []
        )

    @graken()
    def _baseClassList_(self):
        with self._optional():
            self._token(':')
            self._baseClassListNE_()
            self.ast['@'] = self.last_node

    @graken()
    def _mcref_(self):
        self._token(',')
        self._subClassRef_()
        self.ast['@'] = self.last_node

    @graken()
    def _baseClassListNE_(self):
        self._subClassRef_()

        def block0():
            self._mcref_()
        self._closure(block0)

    @graken()
    def _subClassRef_(self):
        with self._group():
            with self._choice():
                with self._option():
                    self._classID_()
                with self._option():
                    self._multiClassID_()
                self._error('no available options')
        self.ast['id'] = self.last_node
        with self._optional():
            self._token('<')
            self._valueList_()
            self.ast['args'] = self.last_node
            self._token('>')

        self.ast._define(
            ['id', 'args'],
            []
        )

    @graken()
    def _defmID_(self):
        self._tokIdentifier_()

    @graken()
    def _body_(self):
        with self._choice():
            with self._option():
                self._token(';')
            with self._option():
                self._token('{')
                self._bodyList_()
                self.ast['@'] = self.last_node
                self._token('}')
            self._error('expecting one of: ;')

    @graken()
    def _bodyList_(self):

        def block0():
            self._bodyItem_()
        self._closure(block0)

    @graken()
    def _bodyItem_(self):
        with self._choice():
            with self._option():
                self._declaration_()
                self.ast['@'] = self.last_node
                self._token(';')
            with self._option():
                self._bodyLet_()
            self._error('no available options')

    @graken()
    def _bodyLet_(self):
        self._token('let')
        self._tokIdentifier_()
        self.ast['name'] = self.last_node
        with self._optional():
            self._rangeList_()
            self.ast['range'] = self.last_node
        self._token('=')
        self._value_()
        self.ast['value'] = self.last_node
        self._token(';')

        self.ast._define(
            ['name', 'range', 'value'],
            []
        )

    @graken()
    def _tdef_(self):
        self._token('def')
        self._tokIdentifier_()
        self.ast['name'] = self.last_node
        self._baseClassList_()
        self.ast['bases'] = self.last_node
        self._body_()
        self.ast['body'] = self.last_node

        self.ast._define(
            ['name', 'bases', 'body'],
            []
        )

    @graken()
    def _defm_(self):
        self._token('defm')
        with self._optional():
            self._tokIdentifier_()
        self.ast['name'] = self.last_node
        self._token(':')
        self._baseClassListNE_()
        self.ast['bases'] = self.last_node
        self._token(';')

        self.ast._define(
            ['name', 'bases'],
            []
        )

    @graken()
    def _foreach_(self):
        with self._choice():
            with self._option():
                self._token('foreach')
                self._declaration_()
                self._token('in')
                self._token('{')

                def block0():
                    self._object_()
                self._closure(block0)
                self._token('}')
            with self._option():
                self._token('foreach')
                self._declaration_()
                self._token('in')
                self._object_()
            self._error('no available options')

    @graken()
    def _let_(self):
        with self._choice():
            with self._option():
                self._token('let')
                self._letList_()
                self.ast['items'] = self.last_node
                self._token('in')
                self._token('{')

                def block2():
                    self._object_()
                self._closure(block2)
                self.ast['body'] = self.last_node
                self._token('}')
            with self._option():
                self._token('let')
                self._letList_()
                self.ast['items'] = self.last_node
                self._token('in')
                self._object_()
                self.ast.setlist('body', self.last_node)
            self._error('no available options')

        self.ast._define(
            ['items', 'body'],
            ['body']
        )

    @graken()
    def _mlitem_(self):
        self._token(',')
        self._letItem_()
        self.ast['@'] = self.last_node

    @graken()
    def _letList_(self):
        self._letItem_()

        def block0():
            self._mlitem_()
        self._closure(block0)

    @graken()
    def _letItem_(self):
        self._tokIdentifier_()
        with self._optional():
            self._rangeList_()
        self._token('=')
        self._value_()

    @graken()
    def _multiClass_(self):
        self._token('multiclass')
        self._tokIdentifier_()
        self.ast['name'] = self.last_node
        with self._optional():
            self._templateArgList_()
            self.ast['args'] = self.last_node
        with self._optional():
            self._token(':')
            self._baseMultiClassList_()
            self.ast['bases'] = self.last_node
        self._token('{')

        def block4():
            self._multiClassObject_()
        self._positive_closure(block4)

        self.ast['body'] = self.last_node
        self._token('}')

        self.ast._define(
            ['name', 'args', 'bases', 'body'],
            []
        )

    @graken()
    def _mmcls_(self):
        self._token(',')
        self._multiClassID_()
        self.ast['@'] = self.last_node

    @graken()
    def _baseMultiClassList_(self):
        self._multiClassID_()

        def block0():
            self._mmcls_()
        self._closure(block0)

    @graken()
    def _multiClassID_(self):
        self._tokIdentifier_()

    @graken()
    def _multiClassObject_(self):
        with self._choice():
            with self._option():
                self._tdef_()
            with self._option():
                self._defm_()
            with self._option():
                self._let_()
            with self._option():
                self._foreach_()
            self._error('no available options')


class grammarSemantics(object):
    def tokInteger(self, ast):
        return ast

    def decimalInteger(self, ast):
        return ast

    def hexInteger(self, ast):
        return ast

    def binInteger(self, ast):
        return ast

    def tokIdentifier(self, ast):
        return ast

    def tokVarName(self, ast):
        return ast

    def ESC(self, ast):
        return ast

    def tokString(self, ast):
        return ast

    def tokCodeFragment(self, ast):
        return ast

    def includeDirective(self, ast):
        return ast

    def tableGenFile(self, ast):
        return ast

    def object(self, ast):
        return ast

    def tclass(self, ast):
        return ast

    def mdecl(self, ast):
        return ast

    def templateArgList(self, ast):
        return ast

    def defaultValue(self, ast):
        return ast

    def declaration(self, ast):
        return ast

    def type(self, ast):
        return ast

    def classID(self, ast):
        return ast

    def listType(self, ast):
        return ast

    def value(self, ast):
        return ast

    def valueSuffix(self, ast):
        return ast

    def rangeList(self, ast):
        return ast

    def rangePiece(self, ast):
        return ast

    def stringJoin(self, ast):
        return ast

    def simpleValue(self, ast):
        return ast

    def simpleList(self, ast):
        return ast

    def valueList(self, ast):
        return ast

    def mvalue(self, ast):
        return ast

    def valueListNE(self, ast):
        return ast

    def marg(self, ast):
        return ast

    def dagArgList(self, ast):
        return ast

    def dagArg(self, ast):
        return ast

    def bangOperator(self, ast):
        return ast

    def bangValue(self, ast):
        return ast

    def baseClassList(self, ast):
        return ast

    def mcref(self, ast):
        return ast

    def baseClassListNE(self, ast):
        return ast

    def subClassRef(self, ast):
        return ast

    def defmID(self, ast):
        return ast

    def body(self, ast):
        return ast

    def bodyList(self, ast):
        return ast

    def bodyItem(self, ast):
        return ast

    def bodyLet(self, ast):
        return ast

    def tdef(self, ast):
        return ast

    def defm(self, ast):
        return ast

    def foreach(self, ast):
        return ast

    def let(self, ast):
        return ast

    def mlitem(self, ast):
        return ast

    def letList(self, ast):
        return ast

    def letItem(self, ast):
        return ast

    def multiClass(self, ast):
        return ast

    def mmcls(self, ast):
        return ast

    def baseMultiClassList(self, ast):
        return ast

    def multiClassID(self, ast):
        return ast

    def multiClassObject(self, ast):
        return ast


def main(filename, startrule, trace=False, whitespace=None, nameguard=None):
    import json
    with open(filename) as f:
        text = f.read()
    parser = grammarParser(parseinfo=False)
    ast = parser.parse(
        text,
        startrule,
        filename=filename,
        trace=trace,
        whitespace=whitespace,
        nameguard=nameguard)
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(ast, indent=2))
    print()

if __name__ == '__main__':
    import argparse
    import string
    import sys

    class ListRules(argparse.Action):
        def __call__(self, parser, namespace, values, option_string):
            print('Rules:')
            for r in grammarParser.rule_list():
                print(r)
            print()
            sys.exit(0)

    parser = argparse.ArgumentParser(description="Simple parser for grammar.")
    parser.add_argument('-l', '--list', action=ListRules, nargs=0,
                        help="list all rules and exit")
    parser.add_argument('-n', '--no-nameguard', action='store_true',
                        dest='no_nameguard',
                        help="disable the 'nameguard' feature")
    parser.add_argument('-t', '--trace', action='store_true',
                        help="output trace information")
    parser.add_argument('-w', '--whitespace', type=str, default=string.whitespace,
                        help="whitespace specification")
    parser.add_argument('file', metavar="FILE", help="the input file to parse")
    parser.add_argument('startrule', metavar="STARTRULE",
                        help="the start rule for parsing")
    args = parser.parse_args()

    main(
        args.file,
        args.startrule,
        trace=args.trace,
        whitespace=args.whitespace,
        nameguard=not args.no_nameguard
    )
