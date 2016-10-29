"""
SmartCamConfig class : handles config for the balloon_finder project

balloon_finder.cnf file is created in the local directory

other classes or files wishing to use this class should add
    import balloon_config

"""

from os.path import expanduser
from StringIO import StringIO
import numpy as np
import ConfigParser

class SmartCamConfig(object):

    def __init__(self):
        # create the global parser object
        self.parser = ConfigParser.SafeConfigParser()

        #load default config file
        self.get_file()


    #get_file - open a config file
    def get_file(self,name='Smart_Camera'):
        # default config file
        self.config_file = expanduser("~/"+ name + ".cnf")

        # read the config file into memory
        self.read()

    # read - reads the contents of the file into the dictionary in RAM
    def read(self):
        try:
            self.parser.read(self.config_file)
        except IOError as e:
            print 'Error {0} reading config file: {1}: '.format(e.errno, e.strerror)
        return
    
    # save - saves the config to disk
    def save(self):
        try:
            with open(self.config_file, 'wb') as configfile:
                self.parser.write(configfile)
        except IOError as e:
            print 'Error {0} writing config file: {1}: '.format(e.errno, e.strerror)
        return

    # check_section - ensures the section exists, creates it if not
    def check_section(self, section):
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        return

    # get_balloon - returns the boolean found in the specified section/option or the default if not found
    def get_boolean(self, section, option, default):
        try:
            return self.parser.getboolean(section, option) 
        except ConfigParser.Error:
            return default

    # set_boolean - sets the boolean to the specified section/option
    def set_boolean(self, section, option, new_value):
        self.check_section(section) 
        self.parser.set(section, option, str(bool(new_value)))
        return

    # get_integer - returns the integer found in the specified section/option or the default if not found
    def get_integer(self, section, option, default):
        try:
            return self.parser.getint(section, option)
        except ConfigParser.Error:
            return default

    # set_integer - sets the integer to the specified section/option
    def set_integer(self, section, option, new_value):
        self.check_section(section)
        self.parser.set(section, option, str(int(new_value)))
        return

    # get_float - returns the float found in the specified section/option or the default if not found
    def get_float(self, section, option, default):
        try:
            return self.parser.getfloat(section, option)
        except ConfigParser.Error:
            return default

    # set_float - sets the float to the specified section/option
    def set_float(self, section, option, new_value):
        self.check_section(section)
        self.parser.set(section, option, str(float(new_value)))
        return

    # get_string - returns the string found in the specified section/option or the default if not found
    def get_string(self, section, option, default):
        try:
            return self.parser.get(section, option)
        except ConfigParser.Error:
            return default

    # set_string - sets the string to the specified section/option
    def set_string(self, section, option, new_value):
        self.check_section(section)
        self.parser.set(section, option, str(new_value))
        return

    # get_array - returns the array found in the specified section/option or the default if not found
    def get_array(self, section, option, default):
        try:
            raw = self.parser.get(section, option)
            return np.loadtxt(StringIO(raw))
        except (ValueError, ConfigParser.Error):
            return default

    #set_array - sets the array to the specific section/option. Can only handle balanced 1D/2D primative type nparrays
    def set_array(self, section, option, new_value):
        self.check_section(section)
        try:
            #create iterator
            itr = np.nditer(new_value)
            colSize = new_value.shape[0]
            #deliminate columns by whitespace and rows by newline
            arr = ''
            for x in range(0,itr.itersize):
                arr += str(itr.next())
                if x%colSize == colSize -1:
                    arr += '\n'
                else:
                    arr += ' '

            self.parser.set(section, option, arr)

        except TypeError:
            self.parser.set(section, option, 'None')
        return

    # main - tests BalloonConfig class
    def main(self):
        #open file
        self.get_file("test_config")

        # print welcome message
        print "SmartCamConfig v0.1 test"
        print "config file: %s" % self.config_file

        # write and read a boolean
        section = 'Test_Section1'
        option = 'Test_boolean'
        print "Writing %s/%s = True" % (section,option)
        self.set_boolean(section,option,True)
        print "Read %s/%s : %s" % (section, option, self.get_boolean(section, option, False))

        # write and read an integer
        section = 'Test_Section1'
        option = 'Test_integer'
        print "Writing %s/%s = 11" % (section,option)
        self.set_integer(section,option,11)
        print "Read %s/%s : %s" % (section, option, self.get_integer(section, option, 99))

        # write and read a float
        section = 'Test_Section1'
        option = 'Test_float'
        print "Writing %s/%s = 12.345" % (section,option)
        self.set_float(section,option,12.345)
        print "Read %s/%s : %s" % (section, option, self.get_float(section, option, 0.01))

        #write and read an array
        section = 'Test_Section1'
        option = 'Test_array'
        arr = np.array([[2.3,345,56],[2,-3,3.14],[45,1,5]])
        print "writing %s/%s = [[2.3,345,56]\n[2,-3,3.14]\n[45,1,5]]" % (section,option)
        self.set_array(section,option,arr)
        print "Read %s/%s : %s" % (section, option, self.get_array(section, option, np.array([0,2])))


        # read an undefined number to get back the default
        section = 'Test_Section2'
        option = 'test_default'
        print "Read %s/%s : %s" % (section, option, self.get_float(section, option, 21.21))



        # save the config file
        self.save()

        return

# declare global smartcam config object
config = SmartCamConfig()

# run the main routine if this is file is called from the command line
if __name__ == "__main__":
    config.main()