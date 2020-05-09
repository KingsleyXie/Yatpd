# Yatpd
:swimmer: Yet another tool project for diploma

### Usage
Firstly, try to test the basic functions. Among all the modules, typical parts to test are the three server/proxy implementations:

```shell
$ cd /path/to/project/root/directory

$ PYTHONPATH=. python3 server/fastcgi_proxy.py > log/fastcgi.log
$ PYTHONPATH=. python3 server/static_file.py > log/static.log
$ PYTHONPATH=. python3 server/http_proxy.py > log/http.log
```

Due to the slow connection speed of [httpbin.org](http://httpbin.org/), you may need to use [proxychain](https://github.com/rofl0r/proxychains-ng) to speed up tests of `HTTPProxy`, and possibly an error like `proxychains can't load process` could happen if the terminal uses [dash](https://wiki.ubuntu.com/DashAsBinSh) as default shell, in this case just specify the shell with `bash -c "python3 file.py"`, full commands are listed below respectively:

```shell
$ PYTHONPATH=. proxychains4 python3 server/http_proxy.py > log/http.log
$ PYTHONPATH=. proxychains4 bash -c "python3 server/http_proxy.py > log/http.log"
```

Finally you can start the server entrance and visit site to see if everything works well:

```shell
$ PYTHONPATH=. python3 entrance.py
```

Note that in default configuration, `host:port` pair is `localhost:80`, and to bind that kind of "privileged" ports(1-1023) without root privilege, you'll need to set `capability` of python binary, say `/usr/bin/python3`:

```shell
$ sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3
```

Check logs under `log/` if you would like to, `main.log` will record the complete process of every requests and responses, while `(fastcgi|static|http).log` are the results of previously mentioned tests.

### Dependency
Project's FastCGIProxy module communicates with FastCGI using [`cgi-fcgi`](https://manpages.debian.org/testing/libfcgi-bin/cgi-fcgi.1.en.html), which can be installed by `apt-get install libfcgi0ldbl` on Debian series or `yum --enablerepo=epel install fcgi` on CentOS series.

Change the config in `config/config.yaml` according to the sample file, `sockfile` is exactly the socket file location of FastCGI server.

If you are using `application` as demo project, following PHP dependencies are required:
- `php-mysql` for database connection
- `php-gd` for captcha image generation
- `php-fpm` for running with FastCGI as Unix Socket

### Annex
In addition, there are Timer module and Worker module to try, which are wrote for the purpose of learning, and to be reminded, the latter one is not stable.

Files of timer module are all located under the directory `timer`, implemented with K-ary Heap or [Red-Black Tree](https://github.com/stanislavkozlovski/Red-Black-Tree) as data structure.
