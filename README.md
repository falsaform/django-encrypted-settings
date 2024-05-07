### EYAML
This python module allows for the encryption, decryption and retrieval of variables from a yaml file
using a set custom yaml tags !secret, !encrypted, !default and !required.

#### Problem
As projects get bigger and more complex, large amounts of configuration options and secrets need to be declared 
and passed through to your application.

Typically in a container based deployment any secrets would be passed in as an environment variables. 
This becomes hard to manage and tedious as your project grows.

Solutions like mozilla sops are great, but arent very git or DX friendly, you have no ability to define multiple environments
and you are also required to write logic in your application to capture these environment variables.

In my current job we store the secrets and configuration options in an ansible vault, one per host/group or environment 
We gather our application settings and secrets from ansible, decrypt any vault secrets and pass them into the container
at run time as environment variables. 

For each setting or secret an environment variable input needs to be declared inside the application.

This package aims to solve the problems across all environments in a DX friendly, secure and CICD friendly way.

Configuration is done in a single file, A yml file which is split into environments (!env's) and a set of defaults(!default).
Secrets are encrypted per environment, each with their own password. The default configuration set can also be 
encrypted if there are shared default secrets.



### Base EYAML config
A !default tag set must be defined which allows for project specific configuration to be defined, environmental 
settings override the default configuration and are merged on top.

Encrypted variables in the the default configuration or environment are stored inline using a custom set of tags and encrypted using ansible vault (by default, fernet and another encryption options TBD).

!secret for an unencrypted secret.
!encrypted for encrypted version of the !secret tag.
!default for declaring a default configuration set.
!env for declaring a environmental configuration set.
!required for declaring variables in your !default configuration set than are required to be set in your !env tags.


Helper methods have been written to allow for encryption and decryption of the config file.
There are also helper methods to load this config file into django along with any passwords to unlock them and use the secrets directly without having to redeclare them.

Having all the configuration and settings in a human readable, secure and encrypted file makes PRs which change settings easier 
to understand, read and ensuring you know which secrets changed and when.

The following is an example of a basic eyaml setup. 
the root of the yaml two tags the following should be defined
```
version: 1.0
!default all:
    foo: "bar"
!env development:
    environment: "development"
    env: "dev"    
```
    This file cannot be encrypted as it does not define any secrets


### version
The only version supported is currently 1.0, as new breaking changes are introduced we will release changelogs with new features avaible at different version.


### Custom tags

### !default
The !default tag allows for a common default configuration across all environment, usefull for settings things like app_name or GA keys which wont change across environments. The !default tag can be named anything, typically all or common makes sense.
Only 1 !default tag can be declared.

### !env
The !env tag allows for environment specific configuration to be specified. When decrypting and accessing your envrionmental config you will use the name defined here.


## Encryption !secret and !encrypted tags

In the example below you can see !secret tags
!secret tags are the unencrypted version of an !encrypted tag

define as many !secret tags as you would like, currently only strings, ints and booleans are supported

```
version: 1.0
!default all:
    app_name: test-project
    ga_app_id: GA-123457689
    ga_app_secret: !secret GA-28923891892319

!env development:
    ENVIRONMENT: development
    ENV: dev
    DB_PASSWORD: !secret development-password

!env staging:
    ENVIRONMENT: stage
    ENV: stage
    DB_PASSWORD: !secret staging-db-password

```

run the following command to encrypt the default config

`$ django-encrypt-config -d`
this will ask for a password for the default config, the file will be updated with a !encrypted tag

```
version: 1.0
!default all:
    app_name: test-project
    ga_app_id: GA-123457689
    ga_app_secret: !encrypted $ANSIBLE_VAULT;1.1;AES256|36613231653731343063613033346132353638303263623763653766663564363162313132353338|3961663561333236343631616530373763376130356532380a316536333930376534666630636264|34363165633730663731303431623762636434353538653665353964343365613764373731363232|3462623530313138620a393135613135343732613334373831303064613930663263663233346630|3438|

!env development:
    ENVIRONMENT: development
    ENV: dev
    DB_PASSWORD: !secret development-password

!env staging:
    ENVIRONMENT: stage
    ENV: stage
    DB_PASSWORD: !secret staging-db-password

```

`$ django-encrypt-config -e development`
this will ask for a password to encrypt the development environment, the file will be updated with a !encrypted tag


```
version: 1.0
!default all:
    app_name: test-project
    ga_app_id: GA-123457689
    ga_app_secret: !encrypted $ANSIBLE_VAULT;1.1;AES256|36613231653731343063613033346132353638303263623763653766663564363162313132353338|3961663561333236343631616530373763376130356532380a316536333930376534666630636264|34363165633730663731303431623762636434353538653665353964343365613764373731363232|3462623530313138620a393135613135343732613334373831303064613930663263663233346630|3438|

!env development:
    ENVIRONMENT: development
    ENV: dev
    DB_PASSWORD: !encrypted $ANSIBLE_VAULT;1.1;AES256|36613231653731343063613033346132353638303263623763653766663564363162313132353338|3961663561333236343631616530373763376130356532380a316536333930376534666630636264|34363165633730663731303431623762636434353538653665353964343365613764373731363232|3462623530313138620a393135613135343732613334373831303064613930663263663233346630|3438|

!env staging:
    ENVIRONMENT: stage
    ENV: stage
    DB_PASSWORD: !secret staging-db-password

```

You can provide the following cli args to simplify things for the decrypt and encrypt commands

`$ eyaml encrypt ./path/to/config.yml development -p P@ssw0rd`
`$ eyaml decrypt ./path/to/config.yml development -p P@ssw0rd`

`$ eyaml encrypt ./path/to/config.yml environment_name --password-file=./path/to/password_file`
`$ eyaml decrypt ./path/to/config.yml environment_name --password-file=./path/to/password_file`


This package also comes with an ansible-vars plugin which allows you to use this file to specify your ansible host/group vars using this format
TODO: update docs on how to use ansible-vars plugin

