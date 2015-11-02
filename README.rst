===============================
Farms List
===============================

Getting Started
----------------

You will need to have Postgres SQL Installed on your machine (`You can get it here <http://www.postgresql.org/download/>`_.) and you will need to have it started and create a farmslistadmin user with priviledges. You will also have to add the postgis extension to the database:

::

    $ psql template1


::

    # CREATE USER urbanlandlocatoradmin;
    # CREATE DATABASE urban_land_locator;
    # ALTER DATABASE urban_land_locator OWNER TO urbanlandlocatoradmin;
    # CREATE EXTENSION postgis;
    # \q


Then run the following commands to bootstrap your environment:


::

    git clone https://github.com/codeforamerica/westsac-urban-land-locator.git
    cd westsac-urban-land-locator/


Now, you'll need to `install the virtualenv tool <https://virtualenv.pypa.io/en/latest/installation.html>`_ and then setup the environment:


::

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements/dev.txt


Finally, you'll want to initialize the database and start the server. We have to modify the upgrade file after it's created because we are using postgis. Between steps two and three, you'll have to follow `these steps <https://docs.google.com/document/d/1KPrTyPMVI-w1ILHd5NDzeD6XYTO9RQUfMSzrRrw-62g>`_:

::

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py server


You should then be able to view the app at localhost:5001 in your local web browser.


Deployment
----------

In your production environment, make sure the ``FARMSLIST_ENV`` environment variable is set to ``"prod"``.


Shell
-----

To open the interactive shell, run ::

    python manage.py shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Running Tests
-------------

To run all tests, run ::

    python manage.py test


Migrations
----------

Whenever a database migration needs to be made. Refer to `this document <https://docs.google.com/document/d/16Jv7O9yW8iPfMswYMPU2_xSG5qVDY7ckyMZHlSGa01k/>`_. Using the postgis extension in postgres complicates the sqlalchemy migration and upgrade process. To add new geometry columns, you'll also need to reference `these steps <https://docs.google.com/document/d/1KPrTyPMVI-w1ILHd5NDzeD6XYTO9RQUfMSzrRrw-62g>`_.

For a full migration command reference, run ``python manage.py db --help``.
