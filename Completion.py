import sublime
import sublime_plugin
import pprint
import os
import os.path
import re
from os.path import basename


class Method:
    _name = ""
    _signature = ""
    _filename = ""

    def __init__(self, name, signature, filename):
        self._name = name
        self._filename = filename
        self._signature = signature

    def name(self):
        return self._name

    def signature(self):
        return self._signature

    def filename(self):
        return self._filename


class Completion(sublime_plugin.EventListener):

    _php_opened_files = []
    _methods = []

    def get_methods_completions(self, prefix):
        completions = []
        for method in self._methods:
            if prefix in method.name():
                str_to_show = method.name()+'('+method.signature()+')'
                str_to_complete = method.name()+'('+method.signature().replace('$', '\$')+')'
                completions.append((str_to_show+'\t'+method.filename(), str_to_complete))
        return completions

    def load_opened_files(self, views):
        if views is not None:
            for view in views:
                if view.file_name() is not None and '.php' in view.file_name():
                    self._php_opened_files.append(view.file_name())

    def build_methods_list(self):
        for file in self._php_opened_files:
            self.load_methods_per_file(file)

    def load_methods_per_file(self, file_name):
        if os.path.exists(file_name):

            file_lines = open(file_name, 'rU')
            class_name = ''
            signature = ''
            name = ''

            for line in file_lines:
                class_match = re.search('[c|C]lass[\s]+(\w+)[\s\S]*', line)

                if class_match is not None and class_match.group(1) != class_name:
                    class_name = class_match.group(1)

                if "function" in line:
                    methods_matches = re.search('[\S\s]*\sfunction\s(\w+)\((.*)\)', line)

                    if methods_matches is not None:
                        class_name = class_name if class_name is not None else basename(file_name)

                        if "static" in line:
                            name = class_name+'::'+methods_matches.group(1)
                        else:
                            name = methods_matches.group(1)

                        signature = methods_matches.group(2)
                        self.add_function(name, signature, class_name)

    def add_function(self, name, signature, file_name):
        self._methods.append(Method(name, signature, file_name))

    def on_post_save(self, view):
        self.clear()
        self.load_opened_files(view.window().views())
        self.build_methods_list()

    def on_query_completions(self, view, prefix, locations):
        completions = self.get_methods_completions(prefix)
        return (completions, sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def clear(self):
        self._methods = []
        self._php_opened_files = []
