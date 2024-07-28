# Japanese Credit Card statement reader

## How to install

```
./install.sh
```

## Add script to your system .bashrc or .zshrc

```
export PATH=$HOME/read_statement:$PATH
```

## How to uninstall

Remove read_statement from your home directory and remove the path setup from .bashrc/.zshrc

## How to use

```
read_statement image_file.jpg
# Can work with multiple files
read_statement image_file1.jpg image_file2.jpg
```

## Supported statement type

Currently only SMBC credit card. Might have a plan to add more in the future.
