# coding: utf-8
__author__ = 'luis'

import sys

class MellanoxRenderer(pystache.Renderer):
    def __init__(self, template_directories=None, template_extension=None, hash_directories=None, hash_extension = None ):
        """



        :param template_extension: the extension of templates ex. .template (string must not have period)
        :param hash_extension: the extension of hashes ex. .template (string must not have period)
        :type self: object
        :param template_directories: a list of absolute directory paths where templates will reside
        :param hash_directories: a list of absolute directory paths where hash files will reside
        """

        self.template_directories = template_directories
        self.template_extension = template_extension
        if self.template_extension is None:
            self.template_extension = 'mustache'

        super(MellanoxRenderer, self).__init__(search_dirs=self.template_directories, file_extension=self.template_extension)

        self.hash_directories = hash_directories
        self.hash_extension = hash_extension
        if self.hash_extension is None:
            self.hash_extension = "hash"

    def _load_hash(self, name):
        """

        :param name: name of the hash within the hash directory
        """
        for directory in self.hash_directories:
            if self._find_name_in_directory(name, directory):
                os.chdir(directory)
                return ast.literal_eval(open(name + '.' + self.hash_extension, 'r').read())

    def _find_name_in_directory(self, name, directory):
        for listing in os.listdir(directory):
            if name in listing:
                return True
        return False

renderer = MellanoxRenderer(template_directories=[sys.argv[2]], hash_directories=[sys.argv[3]])
print renderer.render(renderer.load_template(sys.argv[1]), renderer._load_hash(sys.argv[1]))