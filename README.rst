========
Overview
========

This is a fork of Stephen McDonald's Mezzanine project
found here:  https://github.com/stephenmcd/mezzanine

This implementations has the following items not currently
found in the original Mezzanine project:

  * Support for multiple web site behind multiple domains.
  * Content Pages as the home page.
  * Content Page's contents are rendered as Django templates.
  * "Template" model for supplying Django templates.
  * Media file handling within templates.
  * Themes driven by the user entered settings.
  * Integration with CleverCSS

===========
Test Server
===========

This project is requires Django version 1.2, Grappelli version 2.2,
and the latest version of filebrowser.

Steps to run a sample test server:

  * Ensure Django version 1.2 is available when "django" is imported.
  * Ensure Grappelli version 2.2 is available when "grappelli" is imported.
  * Ensure the "filebrowser" can be imported.
  * Run the syncdb Django management command.

When running the server, it needs to be informed where the admin media
is.  Generally, just pointing to the grappelli media directory is good
enough (filebrowser does work quite right though).  I also like to test
using all network interfaces, which creates the effect of access from
several different domains.  There is also a fixture called "localhost",
which provides a very simple Hello World example web site.

The typical sequence of management commands to run a demo test server is:

  $ mezzanine/manage.py syncdb

  $ mezzanine/manage.py loaddata localhost

  $ mezzanine/manage.py runserver --adminmedia=grappelli/media 0.0.0.0:8000

===================
Creating a Web Site
===================

A virtual domain or host is created by adding a Site under Site->Sites.
Each Site is associated with a set of Settings, which determines what
is displayed for that domain.  A set of Settings can have more than one
Site referring to it, allowing for different domain names displaying
the same content.

To create a simple, initial site, add a new Settings record under
Configuration->Settings and give it a name.  The current items available
for configuration drive a template and css hierarchy which allows
for the implementation of a wide variety of different types of themes.

The current intent in the template hierarchy is the following:

  * TEMPLATE_HTML - The root template.  This establishes a "blank slate" html page and deals with structuring the non-body html elements.
  * TEMPLATE_BODY - The body template.  Defines the overall structure of a given web site.  Extends TEMPLATE_HTML.
  * TEMPLATE_PAGE - Structures the html at the base Page level.  Extends TEMPLATE_BODY.
  * TEMPLATE_CONTENTPAGE - Structures the html for ContentPages.  Extends TEMPLATE_CONTENTPAGE.

Then, there are following Settings values to associate a collection of
CSS settings with these above template levels:

  * STYLE_BODY - Styles applied to the html in the TEMPLATE_STYLE template.
  * STYLE_PAGE - Styles applied to the html in the TEMPLATE_PAGE template.
  * STYLE_CONTENTPAGE - Style applied to the html in the TEMPLATE_CONTENTPAGE template.

Any of the above settings can be changed in the Settings to enable
a different "theme" for that part of the rendered html page.

An initial shell of a simple web site associated with the "localhost" domain
showing an example of using most of the above Settings can be loaded by
loading the "localhost" fixture via the following command:

  mezzanine/manage.py loaddata localhost

The templates loaded in the localhost fixture demonstrate one way to
utilize the above template hierarchy.

Now, the url "http://localhost:8000/" should have a web site running
against it.

Opening a url that does not have a domain configured for it,
such as "http://127.0.0.1:8000/", will echo back the domain used.
