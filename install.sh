#!/usr/bin/env bash

sudo apt-get update && sudo apt-get install -y gnupg software-properties-common

wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg

gpg --no-default-keyring \
--keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
--fingerprint

echo 'The gpg command will report the key fingerprint:'
echo
echo '/usr/share/keyrings/hashicorp-archive-keyring.gpg'
echo '-------------------------------------------------'
echo 'pub   rsa4096 XXXX-XX-XX [SC]'
echo 'AAAA AAAA AAAA AAAA'
echo 'uid           [ unknown] HashiCorp Security (HashiCorp Package Signing) <security+packaging@hashicorp.com>'
echo 'sub   rsa4096 XXXX-XX-XX [E]'
echo
echo

read -p "Continue? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
fi


echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update

sudo apt-get install terraform

terraform -help

echo 'Installed terraform :)'
