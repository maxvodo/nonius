#!/usr/bin/python

import vallus

import re
from os import path

v = vallus.Vallus()
v.depend_include('catch')

v.test_runner()
v.documentation()

def customise_build(tools, ninja):
    stringize_tool = 'tools/stringize.py'
    ninja.rule('stringize',
            command = ' '.join(['python', stringize_tool, '$in', '$out']),
            description = 'STRINGIZE $in')
    html_report_template = 'include/nonius/detail/html_report_template.g.h++'
    ninja.build(html_report_template, 'stringize',
            inputs = 'tpl/html_report.tpl',
            implicit = stringize_tool)
    ninja.build('templates', 'phony',
            inputs = html_report_template)

    single_header_tool = 'tools/single_header.py'
    ninja.rule('header',
            command = ' '.join(['python', single_header_tool, '$in', '$out']),
            description = 'HEADER $out')

    hdr_files = list(vallus.get_files('include', '*.h++'))
    header = path.join('dist', 'nonius.h++')
    ninja.build(header, 'header',
            inputs = path.join('include', 'nonius', 'nonius_single.h++'),
            implicit = hdr_files + [single_header_tool],
            order_only = 'templates')
    ninja.build('header', 'phony',
            inputs = header)

    example_files = list(vallus.get_files('examples', '*.c++'))
    examples = []
    for fn in example_files:
        ninja.build(vallus.object_file(fn), 'cxx',
                inputs = fn,
                implicit = path.join('dist', 'nonius.h++'),
                variables = { 'extraflags': tools.include('dist') },
                order_only = 'templates')
        name = re.sub(r'\.c\+\+$', '', path.basename(fn))
        example = path.join('bin', 'examples', tools.program_name(name))
        ninja.build(example, 'link',
                inputs = [vallus.object_file(fn)])
        ninja.build(name, 'phony',
                inputs = example)
        examples.append(name)

    ninja.build('examples', 'phony',
                inputs = examples)

v.bootstrap(default = 'header', custom = customise_build)
