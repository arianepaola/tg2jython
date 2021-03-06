.. _deploy:

Deploying projects which use ToscaWidgets
=========================================

Introduction
------------

During development ToscaWidgets' middleware takes care of serving static
resources needed by widgets in readable, commented source.

However, this is setup is suboptimal for production since valuable Python
threads/processes will get tied up when serving static files which a fast web
server like Apache or Nginx can serve order of magnitude faster and with a
lower memory footprint

ToscaWidgets provides a Setuptools command which can be used to gather all
static files from all widgets that are being used in a project and copy them
to a directory in which they can be served from bypassing python completely.

Optionally, CSS and JavaScript files can be filtered using ``YUICompressor``
to strip away comments, extra white-space and optionally mangle private
symbols (also known as "obfuscation") so further reduce size. Theoretically,
these trasformations generate code that behaves in the same way as the original.

The :class:`setuptools.Command`
-------------------------------

.. autoclass:: tw.core.command.archive_tw_resources


Configuring your web server
---------------------------

Your web-server should be configured to serve the files in the command's
output directory whenever the URL begins with the prefix you specify in TW's
middleware (Usually /toscawidgets)

Sample Apache Configuration::

    Alias /toscawidgets/ /home/someuser/public_html/toscawidgets/
    <Directory /home/someuser/public_html/toscawidgets/>
       Options -FollowSymLinks
       AllowOverride None
       Order allow,deny
       Allow from all
    </Directory>

Sample Nginx configuration::

    location /toscawidgets {
        root /home/someuser/public_html;
        autoindex on;
    }
    
It is recommended that apache/nginx is configured to gzip this content and
set it an Expires header in the far future so browsers and proxies cache it

In order to avoid clients using stale resources because they haven't
refreshed their cache (avoiding frequent refreshes is the idea of setting
a far-future Expires) it is advised to configure TW's middleware with a
prefix that includes changing data. For example::

    app = tw.api.make_middleware(app, {
        'toscawidgets.middleware.prefix': '/toscawidgets-08060201'
        })

Links generated by TW for resources (non-external obviously) will inlcude
this prefix so with just changing it different links will be generated
forcing the browser to fetch them.

If adding a dynamic part like explained above the web server should be
configured accordingly (with an AliasMatch or ~ location). Please refer
to your server's documentation for more details.

Available command options
-------------------------

::

    Options for 'archive_tw_resources' command:
      --output (-o)         Output directory. If it doesn't exist it will be
                            created.
      --force (-f)          If output dir exists, it will be ovewritten
      --onepass             If given, yuicompressor will only be called once for
                            each kind of file with a all files together and then
                            separated back into smaller files
      --compresslevel (-c)  Compression level: 0) for no compression (default). 1)
                            for js-minification. 2) for js & css compression
      --yuicompressor       Name of the yuicompressor jar.
      --distributions (-d)  List of widget dists. to include resources from
                            (dependencies will be handled recursively). Note that
                            these distributions need to define a
                            'toscawidgets.widgets' 'widgets' entrypoint pointing
                            to a a module where resources are located.

    
The ``--onepass`` option is an optmization that prevents starting up
YUICompressor for every single file. With this option enabled, all files of the
same type will be multiplexed into a single file, compressed and
finally demultiplexed. This option only works with YUICompressor >= 2.3.5
and, as of 2.3.5, doesn't work properly with CSS files so these are not
processed in this way.

.. warning:: A single syntax error will make the whole build fail if this
   option is enabled.
