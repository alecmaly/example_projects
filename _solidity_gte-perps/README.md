# Info

Audit compentition info: [https://code4rena.com/audits/2025-08-gte-perps-and-launchpad](https://code4rena.com/audits/2025-08-gte-perps-and-launchpad)

```bash
sudo mkdir /public
sudo chown $USER /public
sudo chgrp $USER /public
git clone https://github.com/code-423n4/2025-08-gte-perps.git /public/2025-08-gte-perps

cp -r ./_solidity-chainlink/.vscode /public/2025-08-gte-perps/.vscode

# open project in VS Code
code /public/2025-08-gte-perps
```

# Patching local Slither

-- patch so slither will work for this codebase -- 

<local_install_path>/slither/operations/binary.py @L 113
```shell
# commented out to allow to run
assert is_valid_lvalue(result)
```
