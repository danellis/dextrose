import os, os.path, subprocess
from dextrose.utils import file_is_newer

class CleverCssCompiler(object):
    input_extension = '.ccss'
    output_extension = '.css'
    
    def __init__(self):
        import clevercss
        self.convert = clevercss.convert
    
    def compile(self, input_filename, output_filename):
        with open(input_filename, 'r') as input_file:
            with open(output_filename, 'w') as output_file:
                source = input_file.read()
                output = self.convert(source)
                output_file.write(output)

class CoffeeScriptCompiler(object):
    input_extension = '.coffee'
    output_extension = '.js'
    
    def __init__(self):
        assert subprocess.call(['coffee', '-v'], stdout=subprocess.PIPE) == 0
    
    def compile(self, input_filename, output_filename):
        with open(output_filename, 'w') as output_file:
            subprocess.call(['coffee', '-c', '-p', input_filename], stdout=output_file)

class SassCompiler(object):
    input_extension = '.scss'
    output_extension = '.css'
    
    def __init__(self):
        assert subprocess.call(['sass', '--version'], stdout=subprocess.PIPE) == 0
    
    def compile(self, input_filename, output_filename):
        subprocess.call(['sass', '--scss', input_filename, output_filename])

class StaticFileCompiler(object):
    def __init__(self, compiler_classes):
        compilers = (cls() for cls in compiler_classes)
        self.compilers = dict((compiler.input_extension, compiler) for compiler in compilers)
    
    def compile_all(self, root):
        """Recursively scan from 'root' for files that need to be compiled. Source files and
        non-compiling files are returned as a list of files that should be watched for changes
        in debug mode."""
        
        input_files = []
        for dirname, dirs, filenames in os.walk(root):
            for filename in filenames:
                pathname = os.path.join(dirname, filename)
                output_name = self.compile_file(pathname)
                if output_name:
                    input_files.append(pathname)
        return input_files
    
    def compile_file(self, input_name):
        """Compile a single file if possible. If a suitable compiler is found (based on the file
        extension of the input file), the filename of the compiled output file is returned,
        otherwise None is returned."""

        basename, ext = os.path.splitext(input_name)
        compiler = self.compilers.get(ext, None)
        if compiler is None:
            return None
        output_name = basename + compiler.output_extension
        if file_is_newer(input_name, output_name):
            print "Compiling %s -> %s" % (input_name, output_name)
            compiler.compile(input_name, output_name)
        else:
            print "Skipping compilation of %s" % input_name
        return output_name
