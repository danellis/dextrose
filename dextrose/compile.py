import os, os.path, subprocess

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
        assert subprocess.call('coffee', stdout=subprocess.PIPE) == 0
    
    def compile(self, input_filename, output_filename):
        subprocess.call(['coffee', '-c', input_filename])

class SassCompiler(object):
    input_extension = '.scss'
    output_extension = '.css'
    
    def __init__(self):
        assert subprocess.call(['sass', '--version'], stdout=subprocess.PIPE) == 0
    
    def compile(self, input_filename, output_filename):
        subprocess.call(['sass', '--scss', input_filename, output_filename])

# compiler_classes = [SassCompiler, CoffeeScriptCompiler]
compiler_classes = []

compilers = []
for cls in compiler_classes:
    compiler = cls()
    compilers.append(compiler)

def compile_static_files(root):
    """Recursively scan from 'root' for files that need to be compiled. Source files and
    non-compiling files are returned as a list of files that should be watched for changes
    in debug mode."""
    
    watched_files = []
    for path, dirs, filenames in os.walk(root):
        for filename in filenames:
            base, ext = os.path.splitext(filename)
            compilable = False
            for compiler in compilers:
                input_filename = os.path.join(path, base + compiler.input_extension)
                if ext == compiler.output_extension and os.path.exists(input_filename):
                    compilable = True
                    break
                if ext == compiler.input_extension:
                    compilable = True
                    output_filename = os.path.join(path, base + compiler.output_extension)
                    if (not os.path.exists(output_filename)
                        or os.path.getmtime(input_filename) > os.path.getmtime(output_filename)):
                        print "Compiling: %s -> %s" % (input_filename, output_filename)
                        compiler.compile(input_filename, output_filename)
                    watched_files.append(input_filename)
                    break
            if not compilable:
                watched_files.append(os.path.join(path, filename))
    return watched_files
