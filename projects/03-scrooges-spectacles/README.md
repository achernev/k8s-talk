# Scrooge McDuck's Spectacles

To look at, you see!

![Scrooge McDuck](docs/scrooge.png "Scrooge McDuck")

## Installing Scrooge McDuck from GitLab's Package Registry

The `requirements.txt` file references the `scrooge-mcduck` build artefact from that project. In order to authenticate
to GitLab in your development environment, you must create a personal access token as
described [in the documentation][1].
Then you must export two environment variables in the shell session in which you run the `pip3` command:

```shell
# This literal string is the username; no replacement is necessary.
export CI_REGISTRY_USER='__token__'
# Replace with the actual token.
export CI_JOB_TOKEN='<the token you created for yourself>'

# Install the project dependencies.
pip3 install -r requirements.txt
```

There are also [other methods to authenticate with the package registry][2].

[1]: https://docs.gitlab.com/ce/user/profile/personal_access_tokens.html
[2]: https://docs.gitlab.com/ce/user/packages/pypi_repository/#authenticate-with-the-package-registry
