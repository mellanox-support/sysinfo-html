# coding: utf-8
__author__ = 'luis'

import pystache
import optparse
import pickle
import os
import sys
import ast

class MellanoxRenderer(pystache.Renderer):
    def __init__(self, template_directories=None, template_extension=None, hash_directories=None, hash_extension=None):
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

        super(MellanoxRenderer, self).__init__(search_dirs=self.template_directories,
                                               file_extension=self.template_extension)

        self.hash_directories = hash_directories
        self.hash_extension = hash_extension
        if self.hash_extension is None:
            self.hash_extension = "hash"

    def _load_hash(self, name):
        """

        :param name: name of the hash within the hash directory
        """
        os.chdir(self.hash_directories)
        fname = '{0}/{1}.{2}'.format(self.hash_directories, name, self.hash_extension)
        #print fname
        return ast.literal_eval(open(fname, 'r').read())

    def _find_name_in_directory(self, name, directory):
        for listing in os.listdir(directory):
            if name in listing:
                return True
        return False

class Wizard:
    def __init__(self, config='mustache', settings = {}):
        """

        :param config_name:
        :param settings:
        :param t_dirs:
        :param h_dirs:
        :param o_dirs:
        :return:
        """
        self.config = config
        self.settings = settings

        #fill settings as defaults
        self.settings['templates'] = None
        self.settings['hashes'] = None
        self.settings['outputs'] = None

        try:
            #Check if file exists
            with open('{0}.conf'.format(self.config)):pass
        except:
            #if file does not exist, dump default settings to create file
            pickle.dump(self.settings, open('{0}.conf'.format(self.config), 'w'))
        self.settings = pickle.load(open('{0}.conf'.format(self.config),'r'))



    def run(self, reset=False):
        """


        :param reset:
        :rtype : settings dictionary
        """

        if reset:
            self.wipe()

        if self.settings['templates'] is None:
            self.settings['templates'] = self.askForTemplateDir()
        if self.settings['hashes'] is None:
            self.settings['hashes'] = self.askForHashDir()
        if self.settings['outputs'] is None:
            self.settings['outputs'] = self.askForOutputDir()

        print 'Storing configuration...'
        self.__storeSettingsInConfig__(self.settings)
        print 'Configuration saved'
        for item in self.settings.keys():
            try:
                self.__createDir__(self.settings[item])
                print '{0} created...'.format(item)
            except:
                pass

        print 'Please run {0} -c'.format(sys.argv[0])

    def __createDir__(self, directory):
        os.mkdir(directory)

    def __storeSettingsInConfig__(self, settings):
        """

        :param settings:
        """
        try:
            pickle.dump(settings, open('{0}.conf'.format(self.config), 'w'))
        except:
            os.remove('{0}.conf'.format(self.config))

    def __retrieveSettingsInConfig__(self):
        try:
            f = open('{0}.conf'.format(self.config), 'r')
            return pickle.load(f)
        except:
            self.__storeSettingsInConfig__(self.settings)
            self.__retrieveSettingsInConfig__()

    def wipe(self):
        """



        :rtype : object
        """
        self.__askForWipe__()

    def __askForWipe__(self):
        '''
        Wipe settings and re-run wizard
        '''
        answer = raw_input('Would you like to wipe settings? [n]')
        if answer is '':
            answer = 'n'
        if answer in 'Yy':
            self.settings = self.__retrieveSettingsInConfig__()
            settings_list = self.settings.keys()
            for key in settings_list:
                self.settings[key] = None
            self.__storeSettingsInConfig__(self.settings)
            self.run()
        if answer not in 'NnYy':
            print('Please choose either Y or N')
            self.__askForWipe__()
        else:
            return False

    def __getCurrentSettings__(self):
        return self.settings

    def __askForDir__(self, category, default):
        dir = raw_input('Please provide a directory for your {0} files [{1}]: '.format(category, default))
        if dir.strip() is '':
            dir = '{0}'.format(default)
        return dir

    def askForTemplateDir(self):
        return self.__askForDir__('Template', '{0}/Template'.format(os.getcwd()))

    def askForHashDir(self):
        return self.__askForDir__('Hash', '{0}/Hashes'.format(os.getcwd()))

    def askForOutputDir(self):
        return self.__askForDir__('Output', '{0}/Output'.format(os.getcwd()))

    def runFolderCompile(self):
        renderer = MellanoxRenderer(template_directories=self.settings['templates'], hash_directories=self.settings['hashes'])
        for item in os.listdir(self.settings['templates']):
            t_name = item[:-9]
            h_name = t_name
            completed = renderer.render(renderer.load_template(t_name), renderer._load_hash(h_name))
            fname = '{0}.html'.format(t_name)
            os.chdir(self.settings['outputs'])
            open(fname, 'w').write(completed)
            print 'compiled: {0}'.format(fname)


class CLI:
    def __init__(self):
        self.setup = False
        self.opts, self.args = self.setupOptParse()
        self.wizard = Wizard()

    def setupOptParse(self):
        """
        :return: opts, args
        """
        self.parser = optparse.OptionParser()
        self.parser.add_option('-w', '--wizard', dest='run_wizard', metavar='BOOL', action='store_true', default=False,
                               help='run the directory configuration wizard')
        self.parser.add_option('-r', '--reset', dest='run_reset', metavar='BOOL', action='store_true', default=False,
                               help='reset the settings for all directories')
        self.parser.add_option('-c', '--compile', dest='run_compile', metavar='COMMAND', action='store_true',
                               default=False, help='compile all templates and hashes into the output directory')
        self.setup = True
        return self.parser.parse_args()

    def run(self):
        if self.setup:
            if self.opts.run_wizard:
                self.wizard.run()
            if self.opts.run_reset:
                self.wizard.wipe()
            if self.opts.run_compile:
                self.wizard.runFolderCompile()

    def __storeSettingsInConfig__(self, settings):
        """

        :param settings:
        """
        try:
            pickle.dump(settings, open('{0}.conf'.format(self.config), 'w'))
        except:
            os.remove('{0}.conf'.format(self.config))

    def __retrieveSettingsInConfig__(self):
        try:
            f = open('{0}.conf'.format(self.config), 'r')
            return pickle.load(f)
        except:
            self.__storeSettingsInConfig__(self.settings)
            self.__retrieveSettingsInConfig__()


a = CLI()
a.run()

