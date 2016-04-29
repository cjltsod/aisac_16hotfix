# aisac_16hotfix

# 部署 pyenv:
```
$ sudo yum groupinstall "Development Tools"
$ yum install sqlite-devel openssl-devel bzip2-devel readline-devel
$ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
$ nano ~/.bash_profile
```
加入 ~/.bash_profile
```
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```
重新登入

# 安裝 Python
```
$ pyenv install 3.5.1
$ pyenv global 3.5.1
$ pip install pip --upgrade
```

# 安裝aisac_16hotfix 與相依套件
```
$ sudo yum install java-1.8.0-openjdk-devel libffi-devel mysql-devel
$ pip install git+git://github.com/cjltsod/aisac_16hotfix
$ pip install git+git://github.com/kivy/pyjnius.git
```

# 產生基礎設定檔並修改
```
$ python
>>> import aisac_16hotfix
>>> aisac_16hotfix.handle_config(None)
>>> exit()
$ nano aisac_16hotfix.cfg
```

# 產生執行檔
```$ nano run.py```
```
import aisac_16hotfix
aisac_16hotfix.main(None)
```
```$ python run.py```
