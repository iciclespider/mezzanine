========
Overview
========

This is a fork of Stephen McDonald's Mezzanine project
found here:  https://github.com/stephenmcd/mezzanine

This implementations has the following items not currently
found in the original Mezzanine project:

  * Multiple domains.
  * Content Pages as the home page.
  * Content Page's contents are rendered as Django templates.
  * "Template" model for supplying Django templates.
  * Media file handling within templates.
  * Themes driving by the user entered settings.

===========
Test Server
===========

This project is requires Django version 1.2 and Grappelli version 2.2.

Steps to run a sample test server:

  * Ensure Django version 1.2 is available when "django" is imported.
  * Ensure Grappelli version 2.2 is available when "grappelli" is imported.
  * Run the syncdb Django management command.
  * Run the runserver Django management command.

When running the server, it needs to be informed where the admin media
is.  Generally, just pointing to the grappelli media directory is good
enough, at least for testing.  I also like to test using the non loop
network interface, which creates the effect of a differently domain
being accessed.  So the runserver command I use is something like this:  

  $ mezzanine/manage.py runserver --adminmedia=~/src/grappelli/grappelli/media 0.0.0.0:8000 

This provides an empty installation with no web site.  Opening a url,
such as "http://127.0.0.1:8000/" will echo back the domain used.  The /admin/
page should allow for logging in so sites can be created.

===================
Creating a Web Site
===================

A virtual domain or host is created by adding a Site under Site->Sites.
Each Site is associated with a set of Settings, which determines what
is displayed for that domain.  A set of Setting can have more than one
Site referring to it, allowing for different domain names displaying
the same content.

So to create a simple, initial site, add a new Settings record under
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
  * STYLE_CONTENTPAGE - Style applied to the html in the TEMPLATE_CONTENTPAGE
  template.

An initial shell of a simple web site associated with the "localhost" domain
showing an example of using most of the above Settings can be loaded by
loading the "localhost" fixture via the following command:

  mezzanine/manage.py loaddata localhost

The templates loaded in the localhost fixture demonstrate one way to
utilize the above template hierarchy.
