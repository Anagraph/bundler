#!/usr/bin/env python

import os, sys, glob, yaml, zipfile

# Append yaml dependences in yaml_file ('import' files) to another yaml file (full_yaml_file)
def addDependencies(file_list, filename):
    file_list.append(os.path.normpath(filename))
    folder = os.path.dirname(filename)
    yaml_file = yaml.safe_load(open(filename))

    # TODO:
    #   - Check if any url actually exist and is local before doing nothing

    # Search for fonts urls
    if 'fonts' in yaml_file:
        for font in yaml_file['fonts']:
            # initial Tangram font support
            if 'url' in yaml_file['fonts'][font]:
                file_list.append(os.path.normpath(folder + '/' + yaml_file['fonts'][font]['url']))

            # newer Tangram font support
            for weight in yaml_file['fonts'][font]:
                if 'url' in weight:
                    file_list.append(os.path.normpath(folder + '/' + weight['url']))

    # Search for textures urls
    if 'textures' in yaml_file:
        for font in yaml_file['textures']:
            if 'url' in yaml_file['textures'][font]:
                file_list.append(os.path.normpath(folder + '/' + yaml_file['textures'][font]['url']))

    # Search for u_envmap or u_ramp urls
    if 'styles' in yaml_file:
        for style in yaml_file['styles']:
            if 'shaders' in yaml_file['styles'][style]:
                if 'uniforms' in yaml_file['styles'][style]['shaders']:
                    if 'u_envmap' in yaml_file['styles'][style]['shaders']['uniforms']:
                        try:
                            file_list.append(os.path.normpath(folder + '/' + yaml_file['textures'][ yaml_file['styles'][style]['shaders']['uniforms']['u_envmap'] ]['url']))
                        except Exception:
                            print "\tskipping: shader texture (none found)"
                    if 'u_ramp' in yaml_file['styles'][style]['shaders']['uniforms']:
                        try:
                            file_list.append(os.path.normpath(folder + '/' + yaml_file['textures'][ yaml_file['styles'][style]['shaders']['uniforms']['u_ramp'] ]['url']))
                        except Exception:
                            print "\tskipping: shader texture (none found)"

    # Search for inner dependencies
    if 'import' in yaml_file:
        if (type(yaml_file['import']) is str):
            addDependencies(file_list, folder + '/' + yaml_file['import'])
        else:
            for file in yaml_file['import']:
                addDependencies(file_list, folder + '/' + file)

# ================================== Main functions
def bundler(full_filename):
    print full_filename, os.getcwd()
    filename, file_extension = os.path.splitext(full_filename)
    if file_extension == '.yaml':
        all_dependencies = []

        # 1st order dependencies
        addDependencies(all_dependencies, './'+full_filename)

        # 2nd order theme dependencies
        try:
            for file in os.listdir(os.getcwd() + "/themes"):
                if file.endswith(".yaml"):
                    # track like normal
                    all_dependencies.append("themes/" + file)
                    # some themes require additional assets
                    print "looking at dependencies for: %s" % (file,)
                    addDependencies(all_dependencies, "themes/" + file)
        except Exception:
            print "\tskipping: themes (none found)"

        files = list(set(all_dependencies))

        print "Bundling ",filename,"width",len(files),"dependencies, into ",filename+".zip"
        zipf = zipfile.ZipFile(filename+'.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in files:
            zipf.write(file)
        zipf.close()
    else:
        print 'Error: file',

def main():
    if len(sys.argv) > 1:
        bundler(sys.argv[1])
    else:
        bundler(raw_input("What Tangram YAML scene file do you want to bundle into a zipfile?: "))

if __name__ == "__main__":
    exit(main())
