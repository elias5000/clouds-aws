# clouds-aws
clouds-aws is a tool that aims to ease the handling of Cloudformation stacks as code from the command line or scripts.

## Features

*   Create, update, and delete stacks from the command line or in scripts
*   Support for change sets
*   Supports JSON and YAML templates
*   Local file representation of template/parameters of a stack for easy use with SCM
*   Quickly get the most often required information about your stacks on the commandline or for use in scripts
*   Normalized template format for better Diffs and human readability (JSON only)

## Installation

    pip install clouds-aws

## Install requirements
*   boto3
*   PyYAML
*   scandir
*   tabulate

## Commands
For a list of all commands and features run:

    clouds --help
    clouds [command] --help

### clone
Clone a local stack.

### delete
Delete a stack in AWS.

Example:

    clouds delete --force app-server

This will delete the stack. Notice that deletions always require --force as a measure to protect against unintentional deletions.

You can run the command blocking to make it wait for the stack deletion to finish before terminating by using --wait or --events:

    clouds delete --force --events app-server


### describe
Outputs a stack's Outputs, Parameters, and Resources to stdout. You can chose between line output (default) or JSON (using --json flag).

### dump
Dump one or several stacks from AWS to local stack representation.

Example:

    clouds dump app-server

The above will dump the stack named 'app-server' into a subdirectory 'stacks/app-server' in the current directory. The local stack representation consists if two files 'template.json' and 'parameters.yaml'. If the stack does not make use of parameters only 'template.json' will be writen.

You can dump all stacks in a region by using --all flag:

    clouds dump --all

### events
Output all stack's events since its creation.

### format
Reformat the 'template.json' file of a local stack to a format that serves two purposes:

*   support diffs by indentation and sorting dictionary keys
*   make it slightly more human readable by reformatting some common structures

Example:

    clouds format app-server

You can format all local stacks at once:

    clouds format --all

Format also has a pipe mode which is useful in conjunction with e.g. vim. It takes the json template on stdin and outputs it to stdout.

Example:

    cat template.json | clouds format --pipe > formatted-template.json

You can use it in vim to reformat the current document using a keybinding in your .vimrc (the example binds <Ctrl+j>):

    map <C-j> :!clouds format --pipe<CR>

### list
List all local and remote stacks.

### update
Update a stack in AWS from local representation.

Example:

    clouds update app-server

You can run the command blocking to make it wait for the stack update to finish before terminating by using --wait or --events:

    clouds update --events app-server

### change
Use change sets to preview changes that will be performed on the stack

Examples:

    # create new change set
    clouds change create app-server new-elb-certificate -d "Update the ELB to use the new certificate"
    
    # get an overview of changes
    clouds change describe app-server new-elb-certificate
    
    # get a detailed description of all the changes
    clouds change describe app-server new-elb-certificate --yaml
    
    # execute a change set (and tail all the stack events until finished)
    clouds change execute --events app-server new-elb-certificate

## local stacks folder
Clouds assumes the stacks to be located in a folder named 'stacks' inside the current work directory.
Each stack is represented by a folder identical with the stack name which must contain one template file in either
yaml or json format named 'template.yaml' or 'template.json'. It may additionally contain a file 'parameters.yaml' which
contains a hash defining all values to be applied to parameters of the template during stack creation and update.
The parameters.yaml must be present if the template contains at least one parameter that has no default value defined.
Please note that numeric values must be quoted if the parameter is of a string type.

    stacks
    └── mystack
        ├── parameters.yaml
        └── template.json

## Attribution
[clouds](https://github.com/cristim/clouds) was first written in Ruby by [Cristian Măgherușan-Stanciu](https://github.com/cristim). Since it is no longer actively developed I completely rewrote clouds in Python adding all the features I missed while using the original clouds almost every day since it was first developed. Thanks Cristian, for all the hours of work I saved!
