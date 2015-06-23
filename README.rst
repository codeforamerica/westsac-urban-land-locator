===============================
Farms List
===============================

Getting Started
----------------

You will need to have Postgres SQL Installed on your machine (`You can get it here <http://www.postgresql.org/download/>`_.) and you will need to have it started and create a farmslistadmin user with priviledges:

.. code-block:: psql template1

    CREATE USER urbanlandlocatoradmin;
    CREATE DATABASE urban_land_locator;
    ALTER DATABASE urban_land_locator OWNER TO urbanlandlocatoradmin;
    \q


Then run the following commands to bootstrap your environment:


::

    git clone https://github.com/codeforamerica/westsac-urban-land-locator.git
    cd westsac-urban-land-locator/


Now, you'll need to install the virtualenv tool and then setup the environment:


::

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements/dev.txt


Finally, you'll want to initialize the database and start the server:

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

Whenever a database migration needs to be made. Run the following commmands:
::

    python manage.py db migrate

This will generate a new migration script. Then run:
::

    python manage.py db upgrade

To apply the migration.

For a full migration command reference, run ``python manage.py db --help``.
