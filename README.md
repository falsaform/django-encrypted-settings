### EYAML
This python module allows for the encryption, decryption and retreval of settings from a custom yaml file.

As projects get bigger and more complex, large amounts of configuration options and secrets need to be declared and passed through to your application.

Typically in a container based deployment any secrets would be passed in as an environment variables. 
This becomes hard to manage and tedious as your project grows.

Solutions like mozilla sops are great, but arent very git or DX friendly, you have no ability to defined multiple environments
and you are also required to right logic in your application to capture these environment variables.

In my current job we store the secrets and configuration options in an ansible vault, one per host/group or environment 
We gather our application settings and secrets from ansible, decrypted any vault secrets and pass them into the container
at run time as environment variables. 

For each setting or secret an environment variable input needs to be declared inside the application.


Lets say you need to debug an issue with production:

You can look at logs for production, exec into the running container and debug from there, 
or download and run the production container, but if the secrets have changed in your source of truth,
production is not replicable, nor can rollbacks to previous deployments or containers be relied upon.


We have to declare the variables in a django settings partials and use django-environs to pull these variables in.

This package aims to solve the problems across all environments in a DX friendly, secure and CICD friendly way.

Configuration is done in a single file, A yml file which is split into environments (envs) and a set of defaults.
Secrets are encrypted per environment, each with their own password. The default set of configuration can also be 
encrypted if there are shared default secrets.



### Base EYAML config
A default configuration set must be defined which allows for project specific configuration to be defined, environmental 
settings override the default configuration and are merged on top.

The default environment can also be encrypted, if required.

Encrypted variables in the the default configuration or environment are stored inline using a custom set of tags and encrypted using ansible vault.

!secret for an unencrypted secret.
!encrypted for encrypted version of the !secret tag.

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

version
!default
and !env

This file cannot be encrypted as it does not define any secrets



The settings defined can be utilized in django via a helper function to allow for environment specific overrides of configuration


Any variables which are all uppercase automatically declare a django-environ entry,
allowing the value to be overriden via a environment varaible if declared, otherwise defaulting to the value declared in the config for the selected environment.

For example

```
version: 1.0
!default all:
    foo: "bar"
!env development:
    environment: "development"
    env: "dev"
    API_KEY_ID: 12ens01sns0-1
    API_KEY_SECRET: !secret    
```

./manage.py 


```
from django.conf import settings

settings.API_KEY_SECRET

```





### Custom tags

### !version
The only version supported is currently 1.0, as new breaking changes are introduced we will release changelogs with new features avaible at different version.

### !default
The !default tag allows for a common default configuration across all environment, usefull for settings things like app_name or GA keys which wont change across environments. The !default tag can be named anything, typically all or common makes sense.
Only 1 !default tag can be declared.

### !env
The !env tag allows for environment specific configuration to be specified. When decrypting and accessing your envrionmental config you will use the name defined here. Optionally you can choose to include the default options as well, it is on by default.




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


`$ django-decrypt-config -e development`
this will ask for a password to decrypt development environment, and a password for decrypting the default config
If your default config does not contain any secrets, it will not need to be decrypted so only the specified envrionment will need its password

You can provide the following cli args to simplify things for the decrypt and encrypt commands

--dp, --default-password "password" (pulls the password from the cl)
--dpf, --default-password-file ./path/to/password_in_plain_text (pulls the password from a plaintext file)
--dpv, --default-password-var DEFAULT_PASSWORD_ENVIRONMENT_VAR_NAME (pulls the secrets from an env var)

-e, --env "development"
--ep, --environment-password "password" (pulls the password from the cl)
--epf, --environment-password-file ./path/to/password_in_plain_text (pulls the password from a plaintext file)
--epv, --environment-password-var DEVLOPMENT_PASSWORD_ENVIRONMENT_VAR_NAME (pulls the secrets from an env var)


