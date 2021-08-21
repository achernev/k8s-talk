# Gitlab in Vagrant

This will install Gitlab and a Gitlab runner inside two VMs.

Please see the notes in the parent directory's README.md on how to achieve this.

Once installed you need to add a line in your `/etc/hosts` (UNIX-likes)
or `%WINDIR%\system32\drivers\etc\hosts` (Windows) file:

```
192.168.50.50 gitlab.example.com
```

Then you can log on to Gitlab at https://gitlab.example.com/. Ignore the certificate warning and continue to the
website. The password for user `root` can be found in the file `gitlab-root-password` in this directory.

Create a user for yourself in Gitlab and mark yourself as an admin. Log on with that user. It is terrible practice to
use `root` users without good reason.
