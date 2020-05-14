# Yatpd
:swimmer: Yet another tool project for diploma

### Usage
Before starting, try to test the basic functions. Among all the modules, typical parts to test are the three server/proxy implementations:

```shell
$ cd /path/to/project/root/directory

$ PYTHONPATH=. python3 server/static_file.py > log/static.log
$ PYTHONPATH=. python3 server/fastcgi_proxy.py > log/fastcgi.log
$ PYTHONPATH=. python3 server/http_proxy.py > log/http.log
```

Due to the slow connection speed of [httpbin.org](http://httpbin.org/), you may need to use [proxychain](https://github.com/rofl0r/proxychains-ng) to speed up tests of `HTTPProxy`, and possibly an error like `proxychains can't load process` could happen if your terminal uses [dash](https://wiki.ubuntu.com/DashAsBinSh) as the default shell, in this case just specify the shell with `bash -c "python3 file.py"`, full commands are listed below respectively:

```shell
$ PYTHONPATH=. proxychains4 python3 server/http_proxy.py > log/http.log
$ PYTHONPATH=. proxychains4 bash -c "python3 server/http_proxy.py > log/http.log"
```

Finally, you can change configurations in `config/config.yaml`, then start the main server and visit the site to see if everything works well:

```shell
$ PYTHONPATH=. python3 main.py
```

Note that `host:port` pair by default is `localhost:80`, and to bind that kind of "privileged" ports(1-1023) with non-root user, you'll need to set `capability` of python binary, say `/usr/bin/python3`:

```shell
$ sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3
```

Check logs under `log/` if you would like to, `main.log` will record the complete process of all requests and responses, while `(static|fastcgi|http).log` are the results of previously mentioned tests.

### Dependency
Project's FastCGIProxy module communicates with FastCGI using [`cgi-fcgi`](https://manpages.debian.org/testing/libfcgi-bin/cgi-fcgi.1.en.html), which can be installed by `apt-get install libfcgi0ldbl` on Debian series or `yum --enablerepo=epel install fcgi` on CentOS series.

If you are using `application` as the demo project, following PHP dependencies are required:
- `php-mysql` for database connection
- `php-gd` for captcha image generation
- `php-fpm` for running with FastCGI as Unix Socket

### Notes
The buffer size `readbuf.first` is assumed to be big enough to read the entire HTTP head part, because the program uses the header value to determine whether there is still a left part to receive, and if true, read the rest of them using buffer size `readbuf.left`.

Parameter `fastcgi.upstream` can be configured to a TCP `host:port` pair OR a Unix domain socket file, however, there is an unknown problem using `cgi-fcgi` with Unix domain socket on [WSL](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux) platform: The process executed with large input from stdin by pipe terminates with exit code `11` and output no content, while an input size that is a little larger than 65536 still being handled normally. So if there is any need to upload large files AND the project is deployed on WSL, use TCP instead of Unix domain socket as FastCGI upstream.

### Annex
In addition, there are Timer module and Worker module to try, which are written for the purpose of learning, and to be reminded, the latter one is not stable.

Files of Timer module are all located under the directory `timer`, implemented with K-ary Heap or [Red-Black Tree](https://github.com/stanislavkozlovski/Red-Black-Tree) as the data structure. Code of Worker module is in `worker` directory, the design is inspired By [Gunicorn](https://github.com/benoitc/gunicorn)'s [Arbiter](https://github.com/benoitc/gunicorn/blob/master/gunicorn/arbiter.py) and the implementation is not guaranteed to work as expected if you send signals too fast, in which case you should be aware of the zombie processes left.

### Changelog
See :bookmark:[Releases](https://github.com/KingsleyXie/Yatpd/releases)
